"""Tests for the ticketing mock. They use a small seed of their own, not the data pack."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from mockapi.faults import FaultInjector
from mockapi.main import MockSettings, create_app
from mockapi.models import FaultSettings

KEY = {"X-API-Key": "test-key"}
NEW_TICKET = {
    "requester_id": "E1001",
    "short_description": "VPN fails with error 809",
    "description": "SecureTunnel will not connect from home.",
    "category": "Network & VPN",
    "subcategory": "VPN",
}
SEED = [
    {
        "ticket_id": "INC0020001",
        "created_at": "2026-11-12T09:00:00Z",
        "updated_at": "2026-11-12T10:00:00Z",
        "requester_id": "E1001",
        "short_description": "Laptop fan very loud",
        "description": "The fan runs at full speed all day.",
        "category": "Hardware & Devices",
        "subcategory": "Performance",
        "priority": "P4",
        "assignment_group": "Service Desk L1",
        "status": "Awaiting User",
        "comments": [
            {
                "author_id": "E1002",
                "created_at": "2026-11-12T10:00:00Z",
                "body": "Please restart and tell us.",
                "internal": False,
            }
        ],
    },
    {
        "ticket_id": "INC0020002",
        "created_at": "2026-11-13T08:00:00Z",
        "updated_at": "2026-11-13T08:00:00Z",
        "requester_id": "E1002",
        "short_description": "Printer not working",
        "description": "Cannot print. 100% of jobs fail.",
        "category": "Hardware & Devices",
        "subcategory": "Printing",
        "priority": "P3",
        "assignment_group": "Service Desk L1",
        "status": "New",
        "comments": [],
    },
]


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    seed = tmp_path / "open_tickets.json"
    seed.write_text(json.dumps(SEED), encoding="utf-8")
    employees = tmp_path / "employees.csv"
    employees.write_text(
        "employee_id,full_name\nE1001,Ada Example\nE1002,Ben Example\n", encoding="utf-8"
    )
    app = create_app(MockSettings(api_key="test-key", seed_path=seed, employees_path=employees))
    return TestClient(app, headers=KEY)


def set_faults(client: TestClient, **settings: object) -> None:
    assert client.put("/admin/faults", json=settings).status_code == 200


def test_health_needs_no_key_and_counts_seed(client: TestClient) -> None:
    response = client.get("/health", headers={"X-API-Key": ""})
    assert response.status_code == 200
    assert response.json()["tickets"] == 2


def test_requests_without_a_valid_key_are_rejected(client: TestClient) -> None:
    response = client.get("/tickets", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"


def test_create_assigns_next_id_and_defaults(client: TestClient) -> None:
    response = client.post("/tickets", json=NEW_TICKET)
    assert response.status_code == 201
    ticket = response.json()
    assert ticket["ticket_id"] == "INC0020003"
    assert (ticket["status"], ticket["priority"], ticket["assignment_group"]) == (
        "New",
        "P3",
        "Service Desk L1",
    )
    assert (
        client.get(f"/tickets/{ticket['ticket_id']}").json()["description"]
        == NEW_TICKET["description"]
    )


def test_invalid_input_returns_structured_error(client: TestClient) -> None:
    response = client.post("/tickets", json={**NEW_TICKET, "category": "Coffee", "surprise": 1})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert {item["field"] for item in error["details"]["fields"]} == {"category", "surprise"}


def test_unknown_requester_is_refused(client: TestClient) -> None:
    response = client.post("/tickets", json={**NEW_TICKET, "requester_id": "E9999"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unknown_requester"


def test_idempotency_key_prevents_duplicates(client: TestClient) -> None:
    headers = {"Idempotency-Key": "request-123"}
    first = client.post("/tickets", json=NEW_TICKET, headers=headers)
    second = client.post("/tickets", json=NEW_TICKET, headers=headers)
    assert (first.status_code, second.status_code) == (201, 200)
    assert second.headers["Idempotent-Replay"] == "true"
    assert second.json()["ticket_id"] == first.json()["ticket_id"]
    assert client.get("/health").json()["tickets"] == 3

    reused = client.post("/tickets", json={**NEW_TICKET, "priority": "P2"}, headers=headers)
    assert reused.status_code == 409
    assert reused.json()["error"]["code"] == "idempotency_key_reused"


def test_search_filters_and_pages(client: TestClient) -> None:
    mine = client.get("/tickets", params={"requester_id": "E1001"}).json()
    assert [t["ticket_id"] for t in mine["items"]] == ["INC0020001"]
    assert mine["items"][0]["comments"][0]["body"].startswith("Please restart")

    assert client.get("/tickets", params={"q": "printer"}).json()["total"] == 1
    assert client.get("/tickets", params={"q": "100%"}).json()["total"] == 1
    assert client.get("/tickets", params={"q": "%"}).json()["total"] == 1  # a literal percent sign

    page = client.get("/tickets", params={"limit": 1, "offset": 1}).json()
    assert (page["total"], len(page["items"])) == (2, 1)
    assert page["items"][0]["ticket_id"] == "INC0020001"  # newest first, so the older one is second

    assert client.get("/tickets", params={"status": "Banana"}).status_code == 422


def test_update_rules(client: TestClient) -> None:
    moved = client.patch(
        "/tickets/INC0020002",
        json={"assignment_group": "Workplace Engineering", "status": "In Progress"},
    )
    assert moved.status_code == 200
    assert moved.json()["assignment_group"] == "Workplace Engineering"

    no_notes = client.patch("/tickets/INC0020002", json={"status": "Resolved"})
    assert no_notes.status_code == 422
    assert no_notes.json()["error"]["code"] == "resolution_notes_required"

    closed = client.patch(
        "/tickets/INC0020002", json={"status": "Closed", "resolution_notes": "Queue re-added."}
    )
    assert closed.json()["status"] == "Closed"

    again = client.patch("/tickets/INC0020002", json={"priority": "P1"})
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "ticket_closed"

    assert client.patch("/tickets/INC0099999", json={"priority": "P1"}).status_code == 404


def test_comments(client: TestClient) -> None:
    created = client.post(
        "/tickets/INC0020002/comments",
        json={"author_id": "E1001", "body": "Tried again.", "internal": True},
    )
    assert created.status_code == 201
    comments = client.get("/tickets/INC0020002/comments").json()
    assert [(c["author_id"], c["internal"]) for c in comments] == [("E1001", True)]
    assert client.get("/tickets/INC0099999/comments").json()["error"]["code"] == "ticket_not_found"


def test_error_fault_fails_before_any_work(client: TestClient) -> None:
    set_faults(client, error_rate=1.0)
    response = client.post("/tickets", json=NEW_TICKET)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"
    assert (
        client.get("/health").json()["tickets"] == 2
    )  # health is never faulted; nothing was created
    assert client.delete("/admin/faults").json()["error_rate"] == 0
    assert client.post("/tickets", json=NEW_TICKET).status_code == 201


def test_rate_limit_fault_answers_429_with_retry_after(client: TestClient) -> None:
    set_faults(client, rate_limit_per_minute=2)
    statuses = [client.get("/tickets").status_code for _ in range(3)]
    assert statuses == [200, 200, 429]
    limited = client.get("/tickets")
    assert 1 <= int(limited.headers["Retry-After"]) <= 60
    assert limited.json()["error"]["details"]["retry_after_seconds"] >= 1


def test_timeout_fault_does_the_work_then_answers_late(client: TestClient) -> None:
    set_faults(client, timeout_rate=1.0, timeout_seconds=0.2)
    headers = {"Idempotency-Key": "slow-1"}
    started = time.perf_counter()
    late = client.post("/tickets", json=NEW_TICKET, headers=headers)
    assert time.perf_counter() - started >= 0.2
    assert late.headers["X-Fault-Injected"] == "timeout"
    assert (
        client.get("/health").json()["tickets"] == 3
    )  # the ticket exists although the answer was late

    client.delete("/admin/faults")
    retry = client.post("/tickets", json=NEW_TICKET, headers=headers)
    assert retry.json()["ticket_id"] == late.json()["ticket_id"]
    assert (
        client.post("/tickets", json=NEW_TICKET).status_code == 201
    )  # no key: a blind retry duplicates
    assert client.get("/health").json()["tickets"] == 4


def test_reset_restores_the_seed(client: TestClient) -> None:
    client.post("/tickets", json=NEW_TICKET)
    client.patch("/tickets/INC0020001", json={"priority": "P1"})
    assert client.post("/admin/reset").json() == {"status": "reset", "tickets": 2}
    assert client.get("/tickets/INC0020001").json()["priority"] == "P4"
    assert client.post("/tickets", json=NEW_TICKET).json()["ticket_id"] == "INC0020003"


def test_rate_limit_window_slides() -> None:
    faults = FaultInjector(FaultSettings(rate_limit_per_minute=2))
    assert [faults.decide("k", now=t).kind for t in (0.0, 1.0, 2.0)] == [
        "none",
        "none",
        "rate_limited",
    ]
    assert faults.decide("k", now=2.0).retry_after == 58
    assert faults.decide("other", now=2.0).kind == "none"  # limits are per API key
    assert faults.decide("k", now=60.5).kind == "none"  # the first request has left the window


def test_seeded_faults_are_repeatable() -> None:
    def run() -> list[str]:
        faults = FaultInjector(FaultSettings(error_rate=0.3, timeout_rate=0.2, seed=7))
        return [faults.decide("k", now=float(i)).kind for i in range(40)]

    kinds = run()
    assert kinds == run()
    assert {"none", "error", "timeout"} <= set(kinds)
