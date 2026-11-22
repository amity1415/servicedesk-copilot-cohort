"""Fixed password-reset intake through the existing ticketing adapter."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

import httpx
import yaml

from copilot.tools.ticketing import TicketDraft

log = logging.getLogger(__name__)


def policy_path(filename: str) -> Path:
    source = Path(__file__).resolve().parents[3] / "policies" / filename
    return source if source.is_file() else Path("policies") / filename


ACTION_POLICY_PATH = policy_path("actions.yaml")
RISK_TIERS = ("read", "low_risk_write", "approval_required", "forbidden")
PASSWORD_RESET_PLAN = {"get_employee": "read", "create_ticket": "low_risk_write"}
PASSWORD_RESET = re.compile(
    r"\b(?:password[\s-]+reset|reset\s+(?:(?:my|the|a)\s+)?password|forgot\s+(?:my\s+)?password)\b",
    re.IGNORECASE,
)


def action_tiers() -> dict[str, str]:
    policy = yaml.safe_load(ACTION_POLICY_PATH.read_text(encoding="utf-8"))
    if (
        not isinstance(policy, dict)
        or policy.get("version") != 1
        or policy.get("default") != "deny"
    ):
        raise ValueError("The action policy must use version 1 with default deny")
    tiers = {}
    for tier in RISK_TIERS:
        actions = policy.get(tier, [])
        if not isinstance(actions, list):
            raise TypeError(f"The {tier} action tier must list action names")
        for action in actions:
            if not isinstance(action, str) or not action.strip() or action in tiers:
                raise ValueError("Every action needs exactly one risk tier")
            tiers[action] = tier
    return tiers


def asks_for_password_reset(question: str) -> bool:
    return PASSWORD_RESET.search(question) is not None


def open_password_reset_ticket(actor: str, thread: str, ticketing) -> dict:
    tiers = action_tiers()
    if any(tiers.get(action) != required for action, required in PASSWORD_RESET_PLAN.items()):
        raise PermissionError("action policy denied the password-reset workflow")

    steps = list(PASSWORD_RESET_PLAN)
    if ticketing is not None:
        draft = TicketDraft(
            category="Access & Identity",
            priority="P3",
            summary="Password reset request",
            steps_tried=["Employee requested password reset assistance"],
            asset="not applicable",
            assignment_group="Identity & Access",
        )
        digest = hashlib.sha256(f"{actor}\0{thread}".encode()).hexdigest()
        try:
            ticket = ticketing.create(actor, draft, f"password-reset:{digest}")
        except httpx.HTTPError as exc:
            log.warning("Password reset ticketing call failed (%s)", type(exc).__name__)
        else:
            return {
                "answer": f"I opened ticket {ticket['ticket_id']} for your password reset request.",
                "status": "ticket_created",
                "steps": steps,
                "ticket": ticket,
            }
    return {
        "answer": "Ticketing is unavailable. Retry the request in this chat.",
        "status": "ticket_unavailable",
        "steps": steps,
    }
