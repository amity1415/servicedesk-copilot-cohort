"""Bounded HTTP tool adapter; stable idempotency key survives retries."""

import time

import httpx
from pydantic import BaseModel, Field

from copilot.logging_setup import request_id_var
from copilot.telemetry import outbound_headers, traced


class TicketDraft(BaseModel):
    category: str
    priority: str = Field(pattern=r"^P[1-4]$")
    summary: str = Field(min_length=3, max_length=160)
    steps_tried: list[str]
    asset: str
    assignment_group: str


class TicketingClient:
    def __init__(self, base_url: str, key: str, transport=None):
        self.base_url, self.key, self.transport = base_url, key, transport

    @traced("tool.create_ticket")
    def create(self, employee: str, draft: TicketDraft, idempotency_key: str) -> dict:
        body = {
            "requester_id": employee,
            "short_description": draft.summary,
            "description": f"Asset: {draft.asset}\nSteps tried: " + "; ".join(draft.steps_tried),
            "category": draft.category,
            "priority": draft.priority,
            "assignment_group": draft.assignment_group,
        }
        headers = {**outbound_headers(), "X-API-Key": self.key, "Idempotency-Key": idempotency_key}
        if request_id := request_id_var.get():
            headers["X-Request-ID"] = request_id
        with httpx.Client(base_url=self.base_url, timeout=5, transport=self.transport) as client:
            for attempt in range(3):
                try:
                    response = client.post("/tickets", json=body, headers=headers)
                    response.raise_for_status()
                    return response.json()
                except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code not in {
                        429,
                        502,
                        503,
                        504,
                    }:
                        raise
                    if attempt == 2:
                        raise
                    time.sleep(0.1 * 2**attempt)
        raise RuntimeError("unreachable")
