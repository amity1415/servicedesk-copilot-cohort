"""Verify the Session 17 workflow with local PostgreSQL and real ticketing HTTP."""

from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx
import psycopg
from psycopg.conninfo import conninfo_to_dict

from copilot.api.app import create_app
from copilot.api.verify import MAC_QUESTION, running_server
from copilot.config import Settings
from copilot.tools.password_reset import PASSWORD_RESET_PLAN, action_tiers
from copilot.tools.ticketing import TicketingClient

EMPLOYEE = "E1261"
BEARER = "workflow-fixture"
RESET_QUESTION = "I forgot my password. Please help me reset it."
LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def seeded_directory(database_url: str) -> dict:
    if conninfo_to_dict(database_url).get("host") not in LOOPBACK:
        raise ValueError("Use the local seeded PostgreSQL service for workflow verification")
    with psycopg.connect(
        database_url, connect_timeout=5, options="-c statement_timeout=5000"
    ) as db:
        employees, devices, assigned = db.execute(
            """SELECT (SELECT count(*) FROM employees),
                      (SELECT count(*) FROM devices),
                      (SELECT count(*) FROM devices d JOIN employees e
                          ON e.employee_id = d.assigned_to WHERE e.employee_id = %s)""",
            (EMPLOYEE,),
        ).fetchone()
    if (employees, devices) != (300, 450) or not assigned:
        raise RuntimeError("The PostgreSQL service is missing the expected course directory seed")
    return {"employees": employees, "devices": devices, "test_employee_devices": assigned}


@contextmanager
def copilot_client(data: Path, state: Path, ticket_url: str, key: str):
    ticketing = TicketingClient(ticket_url, key)
    app = create_app(data, state, {BEARER: EMPLOYEE}, ticketing=ticketing)
    with (
        running_server(app) as url,
        httpx.Client(
            base_url=url, timeout=25, trust_env=False, headers={"Authorization": f"Bearer {BEARER}"}
        ) as client,
    ):
        if client.get("/health").raise_for_status().json()["status"] != "ok":
            raise RuntimeError("The copilot service is not ready")
        yield client


def ask(client: httpx.Client, thread: str, question: str = RESET_QUESTION) -> tuple[dict, str]:
    response = client.post(
        "/ask", json={"question": question, "thread_id": thread}
    ).raise_for_status()
    request_id = response.headers["X-Request-ID"]
    UUID(request_id)
    return response.json(), request_id


def count_tickets(client: httpx.Client) -> int:
    health = client.get("/health").raise_for_status().json()
    if health["status"] != "ok" or not isinstance(health["tickets"], int):
        raise RuntimeError("Start the local ticketing mock before running the workflow check")
    return health["tickets"]


def verify_ticket(copilot: httpx.Client, tickets: httpx.Client) -> tuple[dict, dict]:
    before = count_tickets(tickets)
    question, _ = ask(copilot, uuid4().hex, MAC_QUESTION)
    documents = sorted({citation["document_id"] for citation in question["citations"]})
    if documents != ["KB-1017"] or count_tickets(tickets) != before:
        raise RuntimeError("The existing authenticated VPN route did not stay read-only")

    thread = uuid4().hex
    first, request_id = ask(copilot, thread)
    replay, replay_request_id = ask(copilot, thread)
    if first["status"] != "ticket_created" or replay != first or request_id == replay_request_id:
        raise RuntimeError("The password-reset workflow did not replay the same ticket")
    ticket_id = first["ticket"]["ticket_id"]
    stored = tickets.get(f"/tickets/{ticket_id}").raise_for_status().json()
    if (
        stored["requester_id"] != EMPLOYEE
        or stored["category"] != "Access & Identity"
        or stored["assignment_group"] != "Identity & Access"
        or count_tickets(tickets) - before != 1
        or first["steps"] != list(PASSWORD_RESET_PLAN)
    ):
        raise RuntimeError("The ticketing API did not store one correctly routed employee ticket")
    return (
        {
            "previous_vpn_documents": documents,
            "requester_id": stored["requester_id"],
            "assignment_group": stored["assignment_group"],
            "category": stored["category"],
            "steps": first["steps"],
            "ticket_count_delta": 1,
            "idempotent_replay": True,
        },
        {"ticket_id": ticket_id, "request_id": request_id, "replay_request_id": replay_request_id},
    )


def verify_failure(data: Path, state: Path) -> dict:
    mock_directory = Path(__file__).resolve().parents[3] / "services/ticketing_mock"
    with patch.object(sys, "path", [str(mock_directory), *sys.path]):
        from mockapi.main import MockSettings
        from mockapi.main import create_app as create_ticketing
        from mockapi.models import FaultSettings

    mock = create_ticketing(
        MockSettings(
            api_key="fault-fixture",
            seed_path=data / "tickets/open_tickets.json",
            employees_path=data / "db/csv/employees.csv",
            faults=FaultSettings(error_rate=1),
        )
    )
    with (
        running_server(mock) as url,
        httpx.Client(
            base_url=url, timeout=5, trust_env=False, headers={"X-API-Key": "fault-fixture"}
        ) as tickets,
        copilot_client(data, state, url, "fault-fixture") as copilot,
    ):
        before = count_tickets(tickets)
        fault_status = tickets.get("/tickets").status_code
        thread = uuid4().hex
        failed, _ = ask(copilot, thread)
        if (
            fault_status != 503
            or failed["status"] != "ticket_unavailable"
            or count_tickets(tickets) != before
        ):
            raise RuntimeError("The forced ticketing outage did not fail without writing a ticket")

        tickets.delete("/admin/faults").raise_for_status()
        recovered, _ = ask(copilot, thread)
        if recovered["status"] != "ticket_created" or count_tickets(tickets) - before != 1:
            raise RuntimeError("The original thread did not recover after the ticketing outage")

    return {
        "upstream_status": fault_status,
        "after_outage": failed["status"],
        "after_recovery": recovered["status"],
    }


def verify_workflow(data: Path, settings: Settings) -> dict:
    url = urlsplit(settings.ticketing_base_url)
    if url.scheme != "http" or url.hostname not in LOOPBACK:
        raise ValueError("Use the local ticketing mock for workflow verification")
    key = settings.ticketing_api_key.get_secret_value()
    directory = seeded_directory(settings.database_url.get_secret_value())
    config = {
        "COPILOT_ANSWER_MODE": "extractive",
        "COPILOT_RETRIEVAL_BACKEND": "tfidf",
        "COPILOT_TRANSPORT": "direct",
    }
    with TemporaryDirectory() as folder, patch.dict(os.environ, config):
        state = Path(folder)
        with (
            copilot_client(
                data, state / "runtime.sqlite3", settings.ticketing_base_url, key
            ) as copilot,
            httpx.Client(
                base_url=settings.ticketing_base_url,
                timeout=5,
                trust_env=False,
                headers={"X-API-Key": key},
            ) as tickets,
        ):
            contract, observed = verify_ticket(copilot, tickets)
        outage = verify_failure(data, state / "outage.sqlite3")
    return {
        "mode": "live-local-ticketing-workflow",
        "directory": directory,
        "policy": {"default": "deny", "action_tiers": action_tiers()},
        "workflow": contract,
        "outage": outage,
        "observed": observed,
        "paid_calls": 0,
    }


def run_check(settings: Settings) -> int:
    result = verify_workflow(settings.data_dir, settings)
    reports = Path(os.getenv("COHORT_REPORT_DIR", "reports/integrated/workflows"))
    reports.mkdir(parents=True, exist_ok=True)
    output = reports / "workflow-verify.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "observed": result["observed"]}))
    return 0
