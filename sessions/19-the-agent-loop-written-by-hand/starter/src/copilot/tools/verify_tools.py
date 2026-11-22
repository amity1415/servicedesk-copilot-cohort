"""Verify typed tool calls through the copilot API and a fresh HTTP ticketing mock."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import UUID

import httpx

from copilot.api.app import create_app
from copilot.api.verify import MAC_QUESTION, running_server
from copilot.llm.service_desk import contract_digest
from copilot.tools.service_desk import TOOLS
from copilot.tools.ticketing import TicketingClient
from copilot.tools.verify_workflow import RESET_QUESTION, count_tickets, seeded_ticketing

EMPLOYEE = "E1261"
ANALYST = "E1203"
MAC_ASSET = "LH-L-00261"
OTHER_ASSET = "LH-L-00166"
KEY = "tool-runtime-fixture"
DRAFT = {
    "category": "Network & VPN",
    "priority": "P3",
    "summary": "VPN disconnects on a Mac",
    "steps_tried": ["Restarted the VPN client"],
    "asset": MAC_ASSET,
    "assignment_group": "Network Operations",
}


def exercise_tools(api: httpx.Client, tickets: httpx.Client) -> dict:
    employee = {"Authorization": "Bearer employee-fixture"}
    analyst = {"Authorization": "Bearer analyst-fixture"}
    create_headers = {**employee, "Idempotency-Key": "runtime-vpn-ticket"}
    health = api.get("/health").raise_for_status().json()
    available = api.get("/tools", headers=employee).raise_for_status().json()
    employee_tools = sorted(row["name"] for row in available)
    operator_tools = sorted(
        row["name"] for row in api.get("/tools", headers=analyst).raise_for_status().json()
    )
    start = count_tickets(tickets)
    if (
        health["status"] != "ok"
        or start != 60
        or set(employee_tools) != TOOLS.keys() - {"update_ticket"}
        or set(operator_tools) != TOOLS.keys()
        or api.get("/tools").status_code != 401
    ):
        raise RuntimeError("The tool service or its scoped discovery is not ready")

    def read(name, arguments):
        return (
            api.post(f"/tools/{name}", headers=employee, json=arguments).raise_for_status().json()
        )

    answer = read("search_kb", {"query": MAC_QUESTION, "os_name": "macos"})
    documents = sorted({citation["document_id"] for citation in answer["citations"]})
    profile = read("get_employee", {})
    devices = read("get_assets", {})["rows"]
    incidents = read("check_service_status", {"service": "FollowMe Printing"})["rows"]
    if (
        documents != ["KB-1017"]
        or profile["employee_id"] != EMPLOYEE
        or MAC_ASSET not in {device["asset_tag"] for device in devices}
        or any(device["assigned_to"] != EMPLOYEE for device in devices)
        or not any(
            incident["incident_id"] == "2" and incident["region"] == "EMEA"
            for incident in incidents
        )
        or count_tickets(tickets) != start
    ):
        raise RuntimeError("The typed read tools returned results outside their expected scope")

    create = "/tools/create_ticket"
    invalid_draft = api.post(
        create, headers=create_headers, json={"draft": {**DRAFT, "category": "invented"}}
    )
    other_asset = api.post(
        create, headers=create_headers, json={"draft": {**DRAFT, "asset": OTHER_ASSET}}
    )
    missing_key = api.post(create, headers=employee, json={"draft": DRAFT})
    if (invalid_draft.status_code, other_asset.status_code, missing_key.status_code) != (
        422,
        403,
        400,
    ) or count_tickets(tickets) != start:
        raise RuntimeError("A rejected create-ticket call changed the ticketing state")

    created = api.post(create, headers=create_headers, json={"draft": DRAFT}).raise_for_status()
    replay = (
        api.post(create, headers=create_headers, json={"draft": DRAFT}).raise_for_status().json()
    )
    UUID(created.headers["X-Request-ID"])
    ticket_id = created.json()["ticket_id"]
    if (
        replay != created.json()
        or replay["requester_id"] != EMPLOYEE
        or count_tickets(tickets) != start + 1
    ):
        raise RuntimeError("Create-ticket did not bind or replay the authenticated request")

    update = "/tools/update_ticket"
    changes = {"ticket_id": ticket_id, "changes": {"status": "Awaiting User"}}
    denied = api.post(update, headers=employee, json=changes)
    if denied.status_code != 403:
        raise RuntimeError("The employee was allowed to update a ticket")
    api.post(update, headers=analyst, json=changes).raise_for_status()
    stored = tickets.get(f"/tickets/{ticket_id}").raise_for_status().json()
    if stored["status"] != "Awaiting User" or stored["requester_id"] != EMPLOYEE:
        raise RuntimeError("The ticketing service did not preserve ticket ownership after update")

    ask = {"question": RESET_QUESTION, "thread_id": "session-17-smoke"}
    workflow = api.post("/ask", headers=employee, json=ask).raise_for_status().json()
    if workflow["status"] != "ticket_created" or count_tickets(tickets) != start + 2:
        raise RuntimeError("The inherited password-reset workflow failed")
    return {
        "employee_tools": employee_tools,
        "analyst_tools": operator_tools,
        "search_documents": documents,
        "employee": profile["employee_id"],
        "assets": sorted(row["asset_tag"] for row in devices),
        "incident_ids": sorted(row["incident_id"] for row in incidents),
        "rejected_calls": {
            "invalid_draft": 422,
            "foreign_asset": 403,
            "missing_idempotency_key": 400,
            "employee_update": 403,
        },
        "ticket": {"ticket_id": ticket_id, "status": stored["status"], "idempotent_replay": True},
        "inherited_password_reset": workflow["ticket"]["ticket_id"],
    }


def verify_tools(data: Path) -> dict:
    config = {
        "COPILOT_ANSWER_MODE": "extractive",
        "COPILOT_RETRIEVAL_BACKEND": "tfidf",
        "COPILOT_TRANSPORT": "direct",
    }
    mock = seeded_ticketing(data, KEY)
    with (
        TemporaryDirectory() as folder,
        patch.dict(os.environ, config),
        running_server(mock) as ticket_url,
    ):
        app = create_app(
            data,
            Path(folder) / "runtime.sqlite3",
            {"employee-fixture": EMPLOYEE, "analyst-fixture": ANALYST},
            ticketing=TicketingClient(ticket_url, KEY),
        )
        with (
            running_server(app) as base,
            httpx.Client(base_url=base, timeout=15, trust_env=False) as api,
            httpx.Client(
                base_url=ticket_url, timeout=5, trust_env=False, headers={"X-API-Key": KEY}
            ) as tickets,
        ):
            return {
                "mode": "live-loopback-service-desk-tools",
                "contract_sha256": contract_digest(),
                "paid_calls": 0,
                **exercise_tools(api, tickets),
            }


def run_check(data: Path) -> int:
    reports = Path(os.environ.get("COHORT_REPORT_DIR", "reports/integrated/tools"))
    reports.mkdir(parents=True, exist_ok=True)
    result = verify_tools(data)
    output = reports / "tools-verify.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "mode": result["mode"]}))
    return 0
