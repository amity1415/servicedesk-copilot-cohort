"""Authorize and serialize LangGraph diagnostic turns around PostgreSQL checkpoints."""

from __future__ import annotations

from threading import Lock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from copilot.agents.diagnostic_graph import build_diagnostic_graph
from copilot.tools.service_desk import ServiceDeskTools


class DiagnosticTurn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    thread_id: str = Field(min_length=1, max_length=128)
    operation: Literal["diagnose", "resume", "create_ticket"]
    question: str | None = Field(default=None, min_length=1, max_length=2000)
    stream: bool = False

    @model_validator(mode="after")
    def validate_question(self):
        if self.operation == "resume" and self.question is not None:
            raise ValueError("resume uses the saved question")
        if self.operation != "resume" and self.question is None:
            raise ValueError("provide a question for diagnosis or ticket creation")
        return self


class DiagnosticConflict(RuntimeError):
    pass


class DiagnosticNotFound(LookupError):
    pass


class CheckpointedDiagnostics:
    def __init__(self, url: str, tools: ServiceDeskTools, *, interrupt_after_tool: bool = False):
        self.url = url
        self.tools = tools
        self.interrupt_after_tool = interrupt_after_tool
        self.ready = False
        self.setup_lock = Lock()

    def prepare(self, saver) -> None:
        with self.setup_lock:
            if self.ready:
                return
            db = saver.conn
            lock = "hashtextextended(current_schema() || ':copilot:diagnostic_setup', 0)"
            db.execute(f"SELECT pg_advisory_lock({lock})")
            try:
                saver.setup()
                db.execute("""
                    CREATE TABLE IF NOT EXISTS copilot_diagnostic_owners (
                        thread_id text PRIMARY KEY,
                        actor text NOT NULL
                    )
                """)
                self.ready = True
            finally:
                db.execute(f"SELECT pg_advisory_unlock({lock})")

    def authorize(self, db, actor: str, turn: DiagnosticTurn) -> None:
        locked = db.execute(
            "SELECT pg_try_advisory_lock("
            "hashtextextended(current_schema() || ':copilot:diagnostic:' || %s, 0)) AS acquired",
            (turn.thread_id,),
        ).fetchone()
        if not locked["acquired"]:
            raise DiagnosticConflict("a diagnostic turn is already running for this thread")
        owner = db.execute(
            "SELECT actor FROM copilot_diagnostic_owners WHERE thread_id = %s", (turn.thread_id,)
        ).fetchone()
        if owner is None:
            if turn.operation != "diagnose":
                raise DiagnosticNotFound("diagnostic thread was not found")
            db.execute(
                "INSERT INTO copilot_diagnostic_owners(thread_id, actor) VALUES (%s, %s)",
                (turn.thread_id, actor),
            )
        elif owner["actor"] != actor:
            raise PermissionError("diagnostic thread belongs to another employee")

    def events(self, actor: str, turn: DiagnosticTurn):
        from langgraph.checkpoint.postgres import PostgresSaver

        with PostgresSaver.from_conn_string(self.url) as saver:
            self.prepare(saver)
            self.authorize(saver.conn, actor, turn)
            graph = build_diagnostic_graph(
                self.tools, saver, interrupt_after_tool=self.interrupt_after_tool
            )
            config = {"configurable": {"thread_id": f"copilot:diagnostics:{turn.thread_id}"}}
            snapshot = graph.get_state(config)
            if snapshot.values and snapshot.values["actor"] != actor:
                raise PermissionError(
                    "diagnostic checkpoint identity differs from thread ownership"
                )
            run, inputs = prepare_turn(actor, turn, snapshot)
            yield {
                "event": "start",
                "data": {"thread_id": turn.thread_id, "operation": turn.operation},
            }
            if run:
                for update in graph.stream(
                    inputs, config, stream_mode="updates", durability="sync"
                ):
                    if (update.get("tools") or {}).get("events"):
                        yield {"event": "step", "data": update["tools"]["events"][-1]}
                    if (update.get("ticket") or {}).get("result", {}).get(
                        "status"
                    ) == "ticket_created":
                        yield {
                            "event": "step",
                            "data": {"tool": "create_ticket", "outcome": "observed"},
                        }
                snapshot = graph.get_state(config)
            checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
            if snapshot.next:
                yield {
                    "event": "paused",
                    "data": {
                        "status": "paused",
                        "checkpoint_id": checkpoint_id,
                        "events": snapshot.values["events"],
                        "next_nodes": list(snapshot.next),
                    },
                }
            else:
                yield {
                    "event": "result",
                    "data": {**snapshot.values["result"], "checkpoint_id": checkpoint_id},
                }


def prepare_turn(actor: str, turn: DiagnosticTurn, snapshot) -> tuple[bool, dict | None]:
    if turn.operation == "diagnose":
        if snapshot.values:
            return False, None
        return True, {
            "actor": actor,
            "thread_id": turn.thread_id,
            "intent": "diagnose",
            "question": turn.question,
            "decisions": 0,
            "events": [],
            "observations": {},
        }
    if not snapshot.values:
        raise DiagnosticNotFound("there is no saved checkpoint for this thread")
    if turn.operation == "resume":
        return bool(snapshot.next), None
    if snapshot.next:
        raise DiagnosticConflict(
            "resume the pending diagnostic turn before requesting a new action"
        )
    status = snapshot.values["result"]["status"]
    if status == "ticket_created":
        return False, None
    if status not in {"suggested_fixes", "ticket_unavailable"}:
        raise DiagnosticConflict("finish the laptop diagnosis before requesting a ticket")
    return True, {"intent": "create_ticket", "failure_report": turn.question}
