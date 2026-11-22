"""Prove diagnostic restart and ticket replay against real PostgreSQL checkpoints."""

from __future__ import annotations

import json
import multiprocessing
import os
import socket
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from unittest.mock import patch
from uuid import uuid4

import httpx
import psycopg
import uvicorn
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from copilot.agents.diagnostics import SLOW_REQUEST
from copilot.agents.verify_react import ASSET, EMPLOYEE, HEADERS, TOKENS, successful_trajectory
from copilot.api.app import create_app
from copilot.api.verify import running_server
from copilot.config import Settings
from copilot.tools.ticketing import TicketingClient
from copilot.tools.verify_workflow import (
    LOOPBACK,
    count_tickets,
    seeded_directory,
    seeded_ticketing,
)

MOCK_KEY = "graph-ticketing-fixture"
THREAD = "session-20-slow-laptop"
FOLLOWUP = "It still does not work after trying the fixes. Please raise a ticket."
ROUTE = "/diagnostics/graph"


@contextmanager
def isolated_database(url: str):
    config = conninfo_to_dict(url)
    if config.get("host") not in LOOPBACK:
        raise ValueError("Use the local Compose PostgreSQL service for restart verification")
    schema = f"copilot_s20_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True, connect_timeout=5) as db:
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            options = f"{config.get('options', '')} -c search_path={schema}"
            yield schema, make_conninfo(url, options=options, connect_timeout=5)
        finally:
            db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


def serve_worker(
    listener, data: Path, state: Path, db_url: str, ticket_url: str, pause: bool
) -> None:
    app = create_app(
        data,
        state,
        TOKENS,
        ticketing=TicketingClient(ticket_url, MOCK_KEY),
        diagnostic_database_url=db_url,
        graph_interrupt_after_tool=pause,
    )
    uvicorn.Server(uvicorn.Config(app, log_level="warning")).run(sockets=[listener])


@contextmanager
def running_worker(data: Path, state: Path, db_url: str, ticket_url: str, *, pause: bool = False):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        url = f"http://127.0.0.1:{listener.getsockname()[1]}"
        context = multiprocessing.get_context("spawn")
        worker = context.Process(
            target=serve_worker, args=(listener, data, state, db_url, ticket_url, pause)
        )
        worker.start()
        try:
            with httpx.Client(base_url=url, timeout=12, trust_env=False, headers=HEADERS) as client:
                deadline = monotonic() + 45
                while worker.is_alive() and monotonic() < deadline:
                    try:
                        ready = client.get("/health", timeout=0.4)
                    except httpx.RequestError:
                        sleep(0.1)
                        continue
                    if ready.is_success and ready.json()["documents"] > 0:
                        yield worker.pid, client
                        return
                    sleep(0.1)
                if not worker.is_alive():
                    raise RuntimeError(
                        f"The graph API exited before readiness (code {worker.exitcode})"
                    )
                raise RuntimeError("The graph API did not become ready within 45 seconds")
        finally:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
            if worker.is_alive():
                worker.kill()
                worker.join(timeout=5)
            if worker.is_alive():
                raise RuntimeError("The verification worker did not stop")
            worker.close()


def streamed_turn(client: httpx.Client, operation: str, question: str | None = None) -> list[dict]:
    body = {"thread_id": THREAD, "operation": operation, "question": question, "stream": True}
    messages = []
    with client.stream("POST", ROUTE, json=body) as response:
        response.raise_for_status()
        if not response.headers["content-type"].startswith("text/event-stream"):
            raise RuntimeError("The graph did not stream its updates")
        event = None
        for line in response.iter_lines():
            if line.startswith("event: "):
                event = line.removeprefix("event: ")
            elif line.startswith("data: ") and event:
                messages.append({"event": event, "data": json.loads(line.removeprefix("data: "))})
                event = None
    if not messages or messages[0]["event"] != "start":
        raise RuntimeError("The graph did not emit a start event")
    return messages


def step_names(messages: list[dict]) -> list[str]:
    return [message["data"]["tool"] for message in messages if message["event"] == "step"]


def exercise_restart(
    data: Path, folder: Path, db_url: str, ticket_url: str, tickets: httpx.Client
) -> tuple[dict, dict]:
    with running_worker(data, folder / "first.sqlite3", db_url, ticket_url, pause=True) as (
        first_pid,
        first,
    ):
        initial = streamed_turn(first, "diagnose", SLOW_REQUEST)
        paused = initial[-1]["data"]
        if (
            initial[-1]["event"] != "paused"
            or step_names(initial) != ["get_assets"]
            or paused["next_nodes"] != ["decision"]
        ):
            raise RuntimeError(
                "The initial process did not pause immediately after observing the laptop"
            )

    thread_key = f"copilot:diagnostics:{THREAD}"
    with psycopg.connect(db_url) as db:
        saved = db.execute(
            "SELECT 1 FROM checkpoints WHERE thread_id = %s AND checkpoint_id = %s",
            (thread_key, paused["checkpoint_id"]),
        ).fetchone()
        if saved is None:
            raise RuntimeError(
                "The paused checkpoint was not durable after stopping the first process"
            )

    with running_worker(data, folder / "second.sqlite3", db_url, ticket_url) as (
        resumed_pid,
        second,
    ):
        resume = {"thread_id": THREAD, "operation": "resume"}
        denied = second.post(ROUTE, json=resume, headers={"Authorization": "Bearer mac-fixture"})
        if denied.status_code != 403 or denied.json() != {"error": "access denied"}:
            raise RuntimeError(
                "A second identity was allowed to inspect the saved diagnostic thread"
            )
        resumed = streamed_turn(second, "resume")
        diagnosis = resumed[-1]["data"]
        if resumed[-1]["event"] != "result" or step_names(resumed) != [
            "check_service_status",
            "search_kb",
        ]:
            raise RuntimeError("The new process did not resume from the next uncompleted node")
        proof = successful_trajectory(diagnosis)
        if count_tickets(tickets) != 60:
            raise RuntimeError("Diagnosis created a ticket before an explicit request")
        action = {"thread_id": THREAD, "operation": "create_ticket", "question": FOLLOWUP}
        created = second.post(ROUTE, json=action).raise_for_status().json()
        if created["status"] != "ticket_created":
            raise RuntimeError("The explicit escalation did not create a ticket through the graph")

    with running_worker(data, folder / "third.sqlite3", db_url, ticket_url) as (replay_pid, third):
        replay = third.post(ROUTE, json=action).raise_for_status().json()
        if (
            replay["ticket"] != created["ticket"]
            or replay["checkpoint_id"] != created["checkpoint_id"]
        ):
            raise RuntimeError("The second restart did not preserve the written ticket")
    ticket = tickets.get(f"/tickets/{created['ticket']['ticket_id']}").raise_for_status().json()
    if (
        len({first_pid, resumed_pid, replay_pid}) != 3
        or ticket["requester_id"] != EMPLOYEE
        or ticket["category"] != "Hardware & Devices"
        or ticket["priority"] != "P3"
        or ticket["assignment_group"] != "Workplace Engineering"
        or ASSET not in ticket["description"]
        or FOLLOWUP not in ticket["description"]
        or count_tickets(tickets) != 61
    ):
        raise RuntimeError(
            "The separate processes did not resolve request 3 with exactly one complete ticket"
        )
    return (
        {
            "initial_tools": step_names(initial),
            "resumed_tools": step_names(resumed),
            "documents": proof["documents"],
            "foreign_resume_status": denied.status_code,
            "ticket_id": ticket["ticket_id"],
            "ticket_category": ticket["category"],
            "ticket_priority": ticket["priority"],
            "ticket_requester": ticket["requester_id"],
            "ticket_asset": ASSET,
            "ticket_assignment_group": ticket["assignment_group"],
            "tickets_created": 1,
            "ticket_replayed_after_restart": True,
        },
        {
            "process_ids": [first_pid, resumed_pid, replay_pid],
            "paused_checkpoint": paused["checkpoint_id"],
            "resumed_checkpoint": diagnosis["checkpoint_id"],
            "ticket_checkpoint": created["checkpoint_id"],
        },
    )


def verify_graph(data: Path, settings: Settings) -> dict:
    url = settings.database_url.get_secret_value()
    directory = seeded_directory(url)
    config = {
        "COPILOT_ANSWER_MODE": "extractive",
        "COPILOT_RETRIEVAL_BACKEND": "tfidf",
        "COPILOT_TRANSPORT": "direct",
    }
    mock = seeded_ticketing(data, MOCK_KEY)
    with (
        TemporaryDirectory() as folder,
        patch.dict(os.environ, config),
        isolated_database(url) as (schema, db_url),
        running_server(mock) as ticket_url,
        httpx.Client(
            base_url=ticket_url, trust_env=False, headers={"X-API-Key": MOCK_KEY}
        ) as tickets,
    ):
        proof, observed = exercise_restart(data, Path(folder), db_url, ticket_url, tickets)
    return {
        "mode": "live-postgres-langgraph",
        "directory": directory,
        "request_3": proof,
        "observed": {"schema": schema, **observed},
        "paid_calls": 0,
    }


def run_check(settings: Settings) -> int:
    result = verify_graph(settings.data_dir, settings)
    directory = Path(os.getenv("COHORT_REPORT_DIR", "reports/integrated/agents"))
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "graph-verify.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "mode": result["mode"]}))
    return 0
