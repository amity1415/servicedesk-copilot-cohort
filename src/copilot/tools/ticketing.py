"""Bounded HTTP tool adapter; stable idempotency key survives retries."""

import time
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from copilot.llm.classify import Classification
from copilot.logging_setup import request_id_var
from copilot.telemetry import outbound_headers, traced

AssignmentGroup = Literal[
    "Service Desk L1",
    "Identity & Access",
    "Network Operations",
    "Workplace Engineering",
    "Messaging & Collaboration",
    "Software Packaging",
    "Security Operations",
    "Onboarding Team",
]


class TicketDraft(Classification):
    model_config = ConfigDict(extra="forbid")

    steps_tried: list[str]
    asset: str = Field(pattern=r"^(?:LH-[LP]-[0-9]{5}|unknown|not applicable)$")
    assignment_group: AssignmentGroup

    @field_validator("summary")
    @classmethod
    def meaningful_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("provide a ticket summary")
        return value


class TicketChanges(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    summary: str | None = Field(
        default=None, min_length=3, max_length=160, serialization_alias="short_description"
    )
    priority: Literal["P1", "P2", "P3", "P4"] | None = None
    assignment_group: AssignmentGroup | None = None
    status: (
        Literal["New", "In Progress", "Awaiting User", "On Hold", "Resolved", "Closed"] | None
    ) = None
    resolution_notes: str | None = Field(default=None, min_length=1, max_length=4000)

    @model_validator(mode="after")
    def check_changes(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError("provide at least one ticket change")
        if self.status in {"Resolved", "Closed"} and self.resolution_notes is None:
            raise ValueError("resolution notes are required to resolve or close a ticket")
        return self


class TicketingClient:
    def __init__(self, base_url: str, key: str, transport=None):
        self.base_url, self.key, self.transport = base_url, key, transport

    def headers(self) -> dict[str, str]:
        headers = {**outbound_headers(), "X-API-Key": self.key}
        if request_id := request_id_var.get():
            headers["X-Request-ID"] = request_id
        return headers

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
        headers = {**self.headers(), "Idempotency-Key": idempotency_key}
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

    @traced("tool.update_ticket")
    def update(self, ticket_id: str, changes: TicketChanges) -> dict:
        payload = changes.model_dump(exclude_none=True, by_alias=True)
        with httpx.Client(base_url=self.base_url, timeout=5, transport=self.transport) as client:
            response = client.patch(f"/tickets/{ticket_id}", json=payload, headers=self.headers())
            return response.raise_for_status().json()
