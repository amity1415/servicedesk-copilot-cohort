"""Authenticated teaching API. Tokens map to identities on the server."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from copilot.agents.engine import Engine
from copilot.api.http import (
    ASK_RESPONSES,
    Answer,
    Ask,
    Health,
    IngestResult,
    completed_result,
    configured_tokens,
    identify_with,
    register_http,
)
from copilot.api.tools import register_tools
from copilot.config import get_settings
from copilot.rag.grounded import configured_rag
from copilot.rag.pipeline import ingest
from copilot.telemetry import configure, dashboard
from copilot.tools.runtime import Runtime
from copilot.tools.service_desk import ServiceDeskTools
from copilot.tools.ticketing import TicketingClient


class Decision(BaseModel):
    decision: str


def create_app(
    data: Path = Path("data"),
    state: Path = Path(".work/runtime.sqlite3"),
    tokens: dict[str, str] | None = None,
    ticketing=None,
) -> FastAPI:
    configured = configured_tokens(tokens)
    runtime = Runtime(state, data)
    for employee_id in configured.values():
        runtime.employee(employee_id)
    engine = Engine(runtime, configured_rag(data), ticketing)
    app = FastAPI(title="Larkhaven Copilot", version="0.2.0")
    app.state.runtime = runtime
    identify = identify_with(configured)
    ingestion_lock = Lock()
    register_http(app)
    register_tools(app, ServiceDeskTools(runtime, engine.retriever, ticketing), identify)

    def remote_tools(actor):
        from copilot.tools.remote import RemoteTools

        token = next(token for token, employee in configured.items() if employee == actor)
        urls = {
            name: os.environ[f"COPILOT_{name.upper()}_MCP_URL"]
            for name in ("documents", "assets_db", "ticketing")
        }
        return RemoteTools(token, urls)

    @app.get("/health", response_model=Health)
    def health():
        return {
            "status": "ok",
            "mode": engine.retriever.mode,
            "documents": len(engine.retriever.chunks),
        }

    @app.post(
        "/ask", response_model=Answer, response_model_exclude_unset=True, responses=ASK_RESPONSES
    )
    def ask(body: Ask, actor: str = Depends(identify)):
        selected_engine = engine
        if os.getenv("COPILOT_TRANSPORT", "direct") == "mcp":
            from copilot.tools.remote import RemoteRetriever, RemoteRuntime, RemoteTicketing

            remote = remote_tools(actor)
            selected_engine = Engine(
                RemoteRuntime(runtime, remote),
                RemoteRetriever(remote),
                RemoteTicketing(remote),
                onboard_handler=lambda candidate, start: remote.call(
                    "ticketing", "onboard", {"candidate_id": candidate, "start_date": start}
                ),
            )
        result = selected_engine.run(actor, body.question, body.thread_id)
        return completed_result(result, body.stream)

    @app.post("/ingest", response_model=IngestResult)
    def ingest_documents(actor: str = Depends(identify)):
        if runtime.employee(actor)["role"] != "admin":
            raise HTTPException(403, "ingestion requires admin")
        with ingestion_lock:
            return ingest(data, state.parent / "documents.json")

    @app.get("/approvals")
    def approvals(actor: str = Depends(identify)):
        with runtime.connect() as db:
            return [
                dict(r)
                for r in db.execute(
                    "SELECT * FROM requests WHERE (approver=? OR data_owner=?) "
                    "AND status='pending'",
                    (actor, actor),
                )
            ]

    @app.post("/approvals/{request_id}")
    def decide(request_id: int, body: Decision, actor: str = Depends(identify)):
        try:
            if os.getenv("COPILOT_TRANSPORT", "direct") == "mcp":
                return remote_tools(actor).call(
                    "ticketing",
                    "decide_access",
                    {"request_id": request_id, "decision": body.decision},
                )
            return runtime.decide(actor, request_id, body.decision)
        except (KeyError, ValueError) as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.post("/approvals/{request_id}/fulfil")
    def fulfil(request_id: int, actor: str = Depends(identify)):
        if os.getenv("COPILOT_TRANSPORT", "direct") == "mcp":
            return remote_tools(actor).call(
                "ticketing", "fulfil_access", {"request_id": request_id}
            )
        return runtime.fulfil(actor, request_id)

    @app.delete("/memory")
    def delete_memory(actor: str = Depends(identify)):
        runtime.memory(actor, delete=True)
        return {"deleted": True}

    @app.post("/feedback")
    def feedback(body: dict, actor: str = Depends(identify)):
        if body.get("rating") not in {1, -1}:
            raise HTTPException(422, "rating must be 1 or -1")
        runtime.audit(actor, "feedback", str(body["rating"]))
        return {"recorded": True}

    @app.get("/metrics")
    def metrics(actor: str = Depends(identify)):
        if runtime.employee(actor)["role"] not in {"admin", "analyst"}:
            raise HTTPException(403, "metrics requires an operator role")
        return dashboard()

    return app


def production_app():
    configure("copilot-api")
    settings = get_settings()
    ticketing = TicketingClient(
        settings.ticketing_base_url, settings.ticketing_api_key.get_secret_value()
    )
    return create_app(data=settings.data_dir, ticketing=ticketing)
