"""Authenticated teaching API. Tokens map to identities on the server."""

from __future__ import annotations

import json
import os
import secrets
import time
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from copilot.agents.engine import Engine
from copilot.rag.grounded import configured_rag
from copilot.rag.pipeline import ingest
from copilot.telemetry import configure, dashboard, span
from copilot.tools.runtime import Runtime
from copilot.tools.ticketing import TicketingClient


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    thread_id: str = Field(min_length=1, max_length=128)
    stream: bool = False


class Decision(BaseModel):
    decision: str


def create_app(
    data: Path = Path("data"),
    state: Path = Path(".work/runtime.sqlite3"),
    tokens: dict[str, str] | None = None,
    ticketing=None,
) -> FastAPI:
    configured = (
        tokens if tokens is not None else json.loads(os.environ.get("COPILOT_AUTH_TOKENS", "{}"))
    )
    runtime = Runtime(state, data)
    for token, employee_id in configured.items():
        if not token:
            raise ValueError("empty bearer tokens are forbidden")
        runtime.employee(employee_id)
    engine = Engine(runtime, configured_rag(data), ticketing)
    app = FastAPI(title="Larkhaven Copilot", version="0.2.0")
    app.state.runtime = runtime

    def remote_tools(actor):
        from copilot.tools.remote import RemoteTools

        token = next(token for token, employee in configured.items() if employee == actor)
        urls = {
            name: os.environ[f"COPILOT_{name.upper()}_MCP_URL"]
            for name in ("documents", "assets_db", "ticketing")
        }
        return RemoteTools(token, urls)

    def identity(authorization: str = Header(default="")) -> str:
        supplied = authorization.removeprefix("Bearer ")
        for token, employee in configured.items():
            if secrets.compare_digest(supplied, token):
                return employee
        raise HTTPException(401, "invalid bearer token")

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        start = time.monotonic()
        with span("api.request", dict(request.headers)):
            response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Elapsed-Seconds"] = f"{time.monotonic() - start:.4f}"
        return response

    @app.exception_handler(PermissionError)
    async def permission_error(request, exc):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=403, content={"error": str(exc)})

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "mode": engine.retriever.mode,
            "documents": len(engine.retriever.chunks),
        }

    @app.post("/ask")
    def ask(body: Ask, actor: str = Depends(identity)):
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
        if body.stream:
            # Event stream of completed workflow output, not fake model tokens.
            return StreamingResponse(
                iter(["event: result\ndata: " + json.dumps(result) + "\n\n"]),
                media_type="text/event-stream",
            )
        return result

    @app.post("/ingest")
    def ingest_documents(actor: str = Depends(identity)):
        if runtime.employee(actor)["role"] != "admin":
            raise HTTPException(403, "ingestion requires admin")
        return ingest(data, state.parent / "documents.json")

    @app.get("/approvals")
    def approvals(actor: str = Depends(identity)):
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
    def decide(request_id: int, body: Decision, actor: str = Depends(identity)):
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
    def fulfil(request_id: int, actor: str = Depends(identity)):
        if os.getenv("COPILOT_TRANSPORT", "direct") == "mcp":
            return remote_tools(actor).call(
                "ticketing", "fulfil_access", {"request_id": request_id}
            )
        return runtime.fulfil(actor, request_id)

    @app.delete("/memory")
    def delete_memory(actor: str = Depends(identity)):
        runtime.memory(actor, delete=True)
        return {"deleted": True}

    @app.post("/feedback")
    def feedback(body: dict, actor: str = Depends(identity)):
        if body.get("rating") not in {1, -1}:
            raise HTTPException(422, "rating must be 1 or -1")
        runtime.audit(actor, "feedback", str(body["rating"]))
        return {"recorded": True}

    @app.get("/metrics")
    def metrics(actor: str = Depends(identity)):
        if runtime.employee(actor)["role"] not in {"admin", "analyst"}:
            raise HTTPException(403, "metrics requires an operator role")
        return dashboard()

    return app


def production_app():
    configure("copilot-api")
    ticketing = TicketingClient(
        os.getenv("COPILOT_TICKETING_BASE_URL", "http://localhost:8081"),
        os.environ["COPILOT_TICKETING_API_KEY"],
    )
    return create_app(ticketing=ticketing)
