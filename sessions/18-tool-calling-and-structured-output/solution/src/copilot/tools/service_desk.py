"""Validate and authorize the six service desk tools before dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from copilot.tools.directory import Directory
from copilot.tools.password_reset import action_tiers, policy_path
from copilot.tools.ticketing import TicketChanges, TicketDraft, TicketingClient

PERMISSIONS_PATH = policy_path("tool_permissions.yaml")


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SearchKB(ToolArguments):
    query: str = Field(min_length=1, max_length=8000)
    os_name: Literal["macos", "windows", "linux", "ios", "android"] | None = None


class GetAssets(ToolArguments):
    employee_id: str | None = Field(
        default=None, pattern=r"^E[0-9]{4}$", description="Use null for the signed-in employee."
    )


class CheckServiceStatus(ToolArguments):
    service: str | None = Field(default=None, min_length=1, max_length=80)


class CreateTicket(ToolArguments):
    draft: TicketDraft


class UpdateTicket(ToolArguments):
    ticket_id: str = Field(
        pattern=r"^INC[0-9]{7,12}$", description="Ticket ID, such as INC0020042."
    )
    changes: TicketChanges


@dataclass(frozen=True)
class ToolSpec:
    input: type[ToolArguments]
    description: str
    risk: Literal["read", "low_risk_write"]


TOOLS = {
    "search_kb": ToolSpec(
        SearchKB, "Find IT instructions or troubleshoot an issue using the knowledge base.", "read"
    ),
    "get_employee": ToolSpec(
        ToolArguments,
        "Read the signed-in employee's directory profile, role, office, or region.",
        "read",
    ),
    "get_assets": ToolSpec(
        GetAssets,
        "List devices assigned to an employee, including asset tags and operating systems.",
        "read",
    ),
    "check_service_status": ToolSpec(
        CheckServiceStatus,
        "Check current or recent outages and incidents affecting an IT service.",
        "read",
    ),
    "create_ticket": ToolSpec(
        CreateTicket,
        "Open a new service desk ticket for the signed-in employee. "
        "Use asset 'unknown' unless its tag was supplied.",
        "low_risk_write",
    ),
    "update_ticket": ToolSpec(
        UpdateTicket,
        "Apply requested changes to an existing ticket identified by its ticket ID.",
        "low_risk_write",
    ),
}


class MissingIdempotencyKey(ValueError):
    pass


class TicketingUnavailable(RuntimeError):
    pass


class ServiceDeskTools:
    def __init__(self, directory: Directory, retriever, ticketing: TicketingClient | None):
        self.directory = directory
        self.retriever = retriever
        self.ticketing = ticketing
        self.tiers = action_tiers()
        self.permissions = yaml.safe_load(PERMISSIONS_PATH.read_text(encoding="utf-8"))
        if not isinstance(self.permissions, dict) or self.permissions.get("default") != "deny":
            raise ValueError("The role policy must use default deny")

    def allowed(self, role: str, name: str) -> bool:
        tools = self.permissions.get(role, {}).get("tools", [])
        return name in tools and self.tiers.get(name) == TOOLS[name].risk

    def describe(self, actor: str) -> list[dict]:
        role = self.directory.employee(actor)["role"]
        return [
            {
                "name": name,
                "description": spec.description,
                "risk": spec.risk,
                "input_schema": spec.input.model_json_schema(),
            }
            for name, spec in TOOLS.items()
            if self.allowed(role, name)
        ]

    def execute(
        self, actor: str, name: str, arguments: dict, *, idempotency_key: str | None = None
    ) -> dict:
        spec = TOOLS[name]
        employee = self.directory.employee(actor)
        if not self.allowed(employee["role"], name):
            raise PermissionError("tool is unavailable to this identity")
        request = spec.input.model_validate(arguments)
        if name == "search_kb":
            return self.retriever.answer(
                request.query,
                role=employee["role"],
                os_name=request.os_name,
                region=employee["region"],
            )
        if name == "get_employee":
            return employee
        if name == "get_assets":
            return {"rows": self.directory.assets(actor, request.employee_id or actor)}
        if name == "check_service_status":
            service = request.service.casefold() if request.service else None
            return {
                "rows": [
                    row
                    for row in self.directory.rows("service_incidents")
                    if row["region"].casefold() in {employee["region"].casefold(), "global"}
                    and (service is None or row["service"].casefold() == service)
                ]
            }
        if self.ticketing is None:
            raise TicketingUnavailable("the ticketing service is not configured")
        if name == "update_ticket":
            return self.ticketing.update(request.ticket_id, request.changes)

        asset = request.draft.asset
        if asset not in {"unknown", "not applicable"} and not any(
            row["asset_tag"] == asset for row in self.directory.assets(actor, actor)
        ):
            raise PermissionError("ticket asset is outside the requester's scope")
        if not idempotency_key or not idempotency_key.strip():
            raise MissingIdempotencyKey("provide an idempotency key when creating a ticket")
        digest = sha256(f"{actor}\0{idempotency_key}".encode()).hexdigest()
        return self.ticketing.create(actor, request.draft, f"service-desk:{digest}")
