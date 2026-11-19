"""One OpenAI-compatible transport, with bounded retries and explicit offline mode."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

import httpx

from copilot.telemetry import outbound_headers, traced

log = logging.getLogger(__name__)


@dataclass
class Completion:
    text: str
    tokens: int
    latency_s: float
    model: str


class ModelClient:
    def __init__(
        self,
        model: str = "offline",
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        timeout: float = 30,
        attempts: int = 3,
        transport=None,
    ):
        if attempts < 1:
            raise ValueError("attempts must be positive")
        self.model, self.base_url, self.api_key = model, base_url, api_key
        self.timeout, self.attempts, self.transport = timeout, attempts, transport

    @traced("model.complete")
    def complete(
        self, messages: list[dict], temperature: float = 0, tools: list | None = None
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
        if tools:
            body["tools"] = tools
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            for attempt in range(self.attempts):
                try:
                    response = client.post(
                        self.base_url.rstrip("/") + "/chat/completions",
                        headers={**outbound_headers(), "Authorization": f"Bearer {self.api_key}"},
                        json=body,
                    )
                    if response.status_code == 429 or response.status_code >= 500:
                        response.raise_for_status()
                    response.raise_for_status()
                    data = response.json()
                    result = Completion(
                        data["choices"][0]["message"].get("content")
                        or json.dumps(data["choices"][0]["message"].get("tool_calls", [])),
                        data.get("usage", {}).get("total_tokens", 0),
                        time.monotonic() - start,
                        self.model,
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
