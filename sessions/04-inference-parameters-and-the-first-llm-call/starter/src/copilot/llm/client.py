"""One OpenAI-compatible transport, with bounded retries and explicit offline mode."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from copilot.telemetry import traced

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
        self.model, self.base_url, self.api_key = (model, base_url, api_key)
        self.timeout, self.attempts, self.transport = (timeout, attempts, transport)

    @traced("model.complete")
    def complete(
        self, messages: list[dict], temperature: float = 0, tools: list | None = None
    ) -> Completion:
        """TODO: implement complete following this session's BUILD_GUIDE.md"""
        raise NotImplementedError(
            "TODO: implement complete following this session's BUILD_GUIDE.md"
        )
