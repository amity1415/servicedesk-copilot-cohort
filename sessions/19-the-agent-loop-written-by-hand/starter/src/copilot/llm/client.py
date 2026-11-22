"""One OpenAI-compatible transport, with bounded retries and explicit offline mode."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

import httpx

from copilot.telemetry import outbound_headers, traced

log = logging.getLogger(__name__)
LUNA_MODEL = "gpt-6-luna"


@dataclass
class Completion:
    text: str
    tokens: int
    latency_s: float
    model: str
    tool_calls: tuple[dict, ...] = ()
    finish_reason: str | None = None
    refused: bool = False
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider_model: str | None = None


class ModelClient:
    def __init__(
        self,
        model: str = "offline",
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        timeout: float = 30,
        attempts: int = 3,
        transport=None,
        max_tokens: int | None = None,
        *,
        json_response: bool = False,
    ):
        if attempts < 1:
            raise ValueError("attempts must be positive")
        self.model, self.base_url, self.api_key = model, base_url, api_key
        self.timeout, self.attempts, self.transport = timeout, attempts, transport
        self.max_tokens = max_tokens
        self.json_response = json_response

    @traced("model.complete")
    def complete(
        self,
        messages: list[dict],
        temperature: float = 0,
        tools: list | None = None,
        *,
        require_tool: bool = False,
        response_schema: dict | None = None,
    ) -> Completion:
        start = time.monotonic()
        if self.model == "offline":
            return Completion(
                json.dumps(
                    {
                        "mode": "offline",
                        "message": "No model called; use extractive retrieval for the local demo.",
                    }
                ),
                0,
                0,
                "offline",
            )
        if not self.api_key:
            raise ValueError("a live model requires an API key")
        body = {"model": self.model, "messages": messages, "temperature": temperature}
        token_field = "max_tokens"
        if self.model == LUNA_MODEL:
            # Passage selection and classification can run without reasoning tokens.
            body.update(reasoning_effort="none", service_tier="default")
            token_field = "max_completion_tokens"
        if self.max_tokens is not None:
            body[token_field] = self.max_tokens
        if response_schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": response_schema}
        elif self.json_response:
            body["response_format"] = {"type": "json_object"}
        if tools:
            body["tools"] = tools
        if require_tool:
            if not tools:
                raise ValueError("a required tool call needs tool definitions")
            body.update(tool_choice="required", parallel_tool_calls=False)
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            for attempt in range(self.attempts):
                try:
                    response = client.post(
                        self.base_url.rstrip("/") + "/chat/completions",
                        headers={**outbound_headers(), "Authorization": f"Bearer {self.api_key}"},
                        json=body,
                    )
                    response.raise_for_status()
                    data = response.json()
                    choice = data["choices"][0]
                    message = choice["message"]
                    calls = message.get("tool_calls") or []
                    usage = data.get("usage") or {}
                    result = Completion(
                        message.get("content") or json.dumps(calls),
                        usage.get("total_tokens", 0),
                        time.monotonic() - start,
                        self.model,
                        tool_calls=tuple(calls),
                        finish_reason=choice.get("finish_reason"),
                        refused=bool(message.get("refusal")),
                        input_tokens=usage.get("prompt_tokens"),
                        output_tokens=usage.get("completion_tokens"),
                        provider_model=data.get("model"),
                    )
                    log.info(
                        "model=%s tokens=%d latency_s=%.3f",
                        result.model,
                        result.tokens,
                        result.latency_s,
                    )
                    return result
                except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                    retryable = (
                        not isinstance(exc, httpx.HTTPStatusError)
                        or exc.response.status_code == 429
                        or exc.response.status_code >= 500
                    )
                    if not retryable or attempt + 1 == self.attempts:
                        raise
                    time.sleep(min(2**attempt, 4))
        raise RuntimeError("unreachable")
