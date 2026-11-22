"""Fault injection: makes the mock fail the way real enterprise systems do.

Three kinds of fault, each teaching a different handling rule (session 24):

- error:        answered 503 before any work is done. Safe to retry.
- rate limit:   answered 429 with a Retry-After header. Wait, then retry.
- timeout:      the request IS processed, then answered late. A client that
                gives up and retries without an idempotency key creates a duplicate.
"""

from __future__ import annotations

import random
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from mockapi.models import FaultSettings

WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class Decision:
    kind: str  # none | error | rate_limited | timeout
    latency: float = 0.0
    retry_after: int = 0


class FaultInjector:
    def __init__(self, settings: FaultSettings | None = None) -> None:
        self._lock = threading.Lock()
        self.configure(settings or FaultSettings())

    def configure(self, settings: FaultSettings) -> None:
        with self._lock:
            self.settings = settings
            self._rng = random.Random(settings.seed)
            self._hits: dict[str, deque[float]] = defaultdict(deque)

    def decide(self, client: str, now: float | None = None) -> Decision:
        """Decide what happens to one request from `client` (its API key)."""
        now = time.monotonic() if now is None else now
        with self._lock:
            settings = self.settings
            latency = settings.latency_ms / 1000

            if settings.rate_limit_per_minute:
                hits = self._hits[client]
                while hits and now - hits[0] >= WINDOW_SECONDS:
                    hits.popleft()
                if len(hits) >= settings.rate_limit_per_minute:
                    retry_after = max(1, round(WINDOW_SECONDS - (now - hits[0])))
                    return Decision("rate_limited", latency, retry_after)
                hits.append(now)

            roll = self._rng.random()
            if roll < settings.error_rate:
                return Decision("error", latency)
            if roll < settings.error_rate + settings.timeout_rate:
                return Decision("timeout", latency)
            return Decision("none", latency)
