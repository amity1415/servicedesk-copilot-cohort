"""Exercise the laptop agent and its runaway case through the normal HTTP route."""

import json
import os
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx

from copilot.agents.diagnostics import SLOW_REQUEST
from copilot.agents.react import DIAGNOSTIC_TOOLS
from copilot.api.app import create_app
from copilot.api.verify import running_server
from copilot.tools.ticketing import TicketingClient
from copilot.tools.verify_workflow import count_tickets, seeded_ticketing

EMPLOYEE = "E1166"
ASSET = "LH-L-00166"
KEY = "diag-ticketing-fixture"
TOKENS = {"slow-fixture": EMPLOYEE, "mac-fixture": "E1261"}
HEADERS = {"Authorization": "Bearer slow-fixture"}


def loop_digest() -> str:
    source = Path(__file__).parent
    files = (source / "react.py", source / "diagnostics.py")
    code = "\n".join(path.read_text(encoding="utf-8") for path in files)
    return sha256(code.encode()).hexdigest()


def successful_trajectory(result: dict) -> dict:
    path = result["events"]
    documents = sorted({citation["document_id"] for citation in result["citations"]})
    if (
        result["status"] != "suggested_fixes"
        or result["steps"] != list(DIAGNOSTIC_TOOLS)
        or [step["outcome"] for step in path] != ["observed"] * 3
    ):
        raise RuntimeError("Laptop diagnostics did not complete all three scoped reads")
    assets = path[0]["observation"]["devices"]
    incidents = path[1]["observation"]["active_incidents"]
    if (
        documents != ["KB-1054"]
        or not any(asset["asset_tag"] == ASSET and asset["os"] == "windows" for asset in assets)
        or not any(
            incident["incident_id"] == "1" and incident["region"] == "APAC"
            for incident in incidents
        )
        or path[-1]["arguments"].get("os_name") != "windows"
        or not result["answer"].strip()
    ):
        raise RuntimeError(
            "Laptop diagnostics did not observe the expected device, incident, and Windows article"
        )
    return {
        "status": result["status"],
        "decision_source": result["decision_source"],
        "documents": documents,
        "events": path,
        "answer": result["answer"],
    }


def post_ask(client: httpx.Client, thread: str) -> dict:
    body = {"question": SLOW_REQUEST, "thread_id": thread}
    return client.post("/ask", headers=HEADERS, json=body).raise_for_status().json()


def exercise_trajectory(data: Path, state: Path, ticketing: TicketingClient, decision=None) -> dict:
    app = create_app(data, state, TOKENS, ticketing=ticketing, diagnostic_decision=decision)
    with (
        running_server(app) as base,
        httpx.Client(base_url=base, timeout=40, trust_env=False) as api,
    ):
        health = api.get("/health").raise_for_status().json()
        if health["status"] != "ok" or health["documents"] <= 0:
            raise RuntimeError("The diagnostic API is not ready")
        existing = api.post("/tools/get_assets", headers=HEADERS, json={}).raise_for_status().json()
        if not any(row["asset_tag"] == ASSET for row in existing["rows"]):
            raise RuntimeError(
                "The inherited Session 18 asset tool did not return the assigned laptop"
            )
        trajectory = successful_trajectory(post_ask(api, "session-19-slow"))
        return {"readiness": health, "inherited_asset_tool": ASSET, "trajectory": trajectory}


def exercise_runaway(data: Path, state: Path, ticketing: TicketingClient) -> dict:
    def repeat(query, events):
        return {"tool": "get_assets"}

    app = create_app(
        data, state, TOKENS, ticketing=ticketing, diagnostic_decision=repeat, diagnostic_max_steps=2
    )
    with (
        running_server(app) as base,
        httpx.Client(base_url=base, timeout=15, trust_env=False) as api,
    ):
        result = post_ask(api, "session-19-runaway")
    if (
        result["status"] != "escalated"
        or result["reason"] != "step_limit"
        or result["steps"] != ["get_assets", "get_assets"]
        or [event["outcome"] for event in result["events"]] != ["observed", "observed"]
    ):
        raise RuntimeError("A repeating decision did not stop at the configured two-step limit")
    return {"status": result["status"], "reason": result["reason"], "steps": result["steps"]}


def verify_react(data: Path, *, decision=None) -> dict:
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
        ticketing = TicketingClient(ticket_url, KEY)
        with httpx.Client(
            base_url=ticket_url, trust_env=False, headers={"X-API-Key": KEY}
        ) as tickets:
            before = count_tickets(tickets)
            if before != 60:
                raise RuntimeError("The ticketing mock did not load the course seed")
            result = exercise_trajectory(
                data, Path(folder) / "diagnosis.sqlite3", ticketing, decision
            )
            runaway = exercise_runaway(data, Path(folder) / "runaway.sqlite3", ticketing)
            written = count_tickets(tickets) - before
    if written:
        raise RuntimeError("The read-only diagnostic loop changed ticketing state")
    return {
        "mode": "live-loopback-diagnostics",
        "loop_sha256": loop_digest(),
        **result,
        "runaway": runaway,
        "tickets_written": written,
    }


def run_check(data: Path) -> int:
    report = verify_react(data)
    folder = Path(os.getenv("COHORT_REPORT_DIR", "reports/integrated/agents"))
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / "react-verify.json"
    output.write_text(json.dumps({**report, "paid_calls": 0}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "mode": report["mode"]}))
    return 0
