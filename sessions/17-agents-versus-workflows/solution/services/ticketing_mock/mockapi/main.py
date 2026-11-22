"""HTTP API of the ticketing mock.

Run locally:   uvicorn mockapi.main:app --port 8081   (from services/ticketing_mock)
API docs:      http://localhost:8081/docs

Every error has the same shape, so a client can branch on `error.code`:
    {"error": {"code": "ticket_not_found", "message": "...", "details": {...}}}
"""

from __future__ import annotations

import asyncio
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from mockapi import __version__
from mockapi.faults import FaultInjector
from mockapi.models import (
    GROUPS,
    Category,
    Comment,
    CommentCreate,
    FaultSettings,
    Group,
    Priority,
    Status,
    Ticket,
    TicketCreate,
    TicketPage,
    TicketUpdate,
)
from mockapi.store import StoreError, TicketStore

# Paths that fault injection applies to. Health and admin always answer normally.
FAULTED_PREFIXES = ("/tickets", "/assignment-groups")


class ApiKeyError(Exception):
    """The X-API-Key header is missing or wrong."""


@dataclass(frozen=True)
class MockSettings:
    api_key: str = "dev-ticketing-key"
    db_path: str = ":memory:"
    seed_path: Path | None = None
    employees_path: Path | None = None
    faults: FaultSettings = field(default_factory=FaultSettings)

    @classmethod
    def from_env(cls) -> MockSettings:
        def path(name: str, default: str) -> Path:
            return Path(os.environ.get(name, default))

        env = os.environ
        return cls(
            api_key=env.get("TICKETING_API_KEY", cls.api_key),
            db_path=env.get("TICKETING_DB", ":memory:"),
            seed_path=path("TICKETING_SEED", "data/tickets/open_tickets.json"),
            employees_path=path("TICKETING_EMPLOYEES", "data/db/csv/employees.csv"),
            faults=FaultSettings(
                error_rate=float(env.get("FAULT_ERROR_RATE", 0)),
                timeout_rate=float(env.get("FAULT_TIMEOUT_RATE", 0)),
                timeout_seconds=float(env.get("FAULT_TIMEOUT_SECONDS", 30)),
                rate_limit_per_minute=int(env.get("FAULT_RATE_LIMIT_PER_MINUTE", 0)),
                latency_ms=int(env.get("FAULT_LATENCY_MS", 0)),
                seed=int(env["FAULT_SEED"]) if env.get("FAULT_SEED") else None,
            ),
        )


def error_response(
    status: int, code: str, message: str, details: object = None, headers=None
) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "details": details or {}}}
    return JSONResponse(status_code=status, content=body, headers=headers)


def create_app(settings: MockSettings | None = None) -> FastAPI:
    settings = settings or MockSettings.from_env()
    store = TicketStore(settings.db_path, settings.seed_path, settings.employees_path)
    faults = FaultInjector(settings.faults)

    app = FastAPI(
        title="Larkhaven ticketing mock",
        version=__version__,
        description="A stand-in for the company ticketing system. Synthetic data only.",
    )
    app.state.store = store
    app.state.faults = faults

    def require_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
            raise ApiKeyError

    @app.exception_handler(ApiKeyError)
    async def handle_api_key(request: Request, exc: ApiKeyError) -> JSONResponse:
        return error_response(401, "invalid_api_key", "Send a valid key in the X-API-Key header.")

    @app.exception_handler(StoreError)
    async def handle_store_error(request: Request, exc: StoreError) -> JSONResponse:
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {"field": ".".join(str(part) for part in error["loc"][1:]), "problem": error["msg"]}
            for error in exc.errors()
        ]
        return error_response(
            422, "validation_error", "The request is not valid.", {"fields": fields}
        )

    @app.middleware("http")
    async def inject_faults(request: Request, call_next):
        if not request.url.path.startswith(FAULTED_PREFIXES):
            return await call_next(request)
        decision = faults.decide(request.headers.get("x-api-key", "anonymous"))
        if decision.latency:
            await asyncio.sleep(decision.latency)
        if decision.kind == "rate_limited":
            return error_response(
                429,
                "rate_limited",
                f"Too many requests. Retry after {decision.retry_after} seconds.",
                {"retry_after_seconds": decision.retry_after},
                headers={"Retry-After": str(decision.retry_after)},
            )
        if decision.kind == "error":
            return error_response(
                503,
                "service_unavailable",
                "The ticketing system is temporarily unavailable. Nothing was changed.",
            )
        response = await call_next(request)
        if decision.kind == "timeout":
            # The work is done; only the answer is late. This is what makes blind retries dangerous.
            await asyncio.sleep(faults.settings.timeout_seconds)
            response.headers["X-Fault-Injected"] = "timeout"
        return response

    secured = [Depends(require_key)]

    @app.get("/health", tags=["service"])
    def health() -> dict[str, object]:
        return {"status": "ok", "version": __version__, "tickets": store.count()}

    @app.get("/assignment-groups", tags=["tickets"], dependencies=secured)
    def assignment_groups() -> list[str]:
        return list(GROUPS)

    @app.post(
        "/tickets", tags=["tickets"], dependencies=secured, status_code=201, response_model=Ticket
    )
    def create_ticket(
        body: TicketCreate,
        response: Response,
        idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
    ):
        """Create a ticket. An Idempotency-Key header stops a retry creating a duplicate."""
        ticket, replayed = store.create(body.model_dump(), idempotency_key)
        if replayed:
            response.status_code = 200
            response.headers["Idempotent-Replay"] = "true"
        return ticket

    @app.get("/tickets", tags=["tickets"], dependencies=secured, response_model=TicketPage)
    def search_tickets(
        requester_id: str | None = None,
        status: Status | None = None,
        category: Category | None = None,
        assignment_group: Group | None = None,
        priority: Priority | None = None,
        q: Annotated[
            str | None, Query(max_length=200, description="Text to find in the descriptions")
        ] = None,
        open_only: bool = False,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        """Search tickets, newest first."""
        items, total = store.search(
            requester_id=requester_id,
            status=status,
            category=category,
            assignment_group=assignment_group,
            priority=priority,
            text=q,
            open_only=open_only,
            limit=limit,
            offset=offset,
        )
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/tickets/{ticket_id}", tags=["tickets"], dependencies=secured, response_model=Ticket)
    def get_ticket(ticket_id: str):
        return store.get(ticket_id)

    @app.patch(
        "/tickets/{ticket_id}", tags=["tickets"], dependencies=secured, response_model=Ticket
    )
    def update_ticket(ticket_id: str, body: TicketUpdate):
        """Change only the fields sent. A closed ticket cannot be changed."""
        return store.update(ticket_id, body.model_dump(exclude_unset=True))

    @app.get(
        "/tickets/{ticket_id}/comments",
        tags=["tickets"],
        dependencies=secured,
        response_model=list[Comment],
    )
    def list_comments(ticket_id: str):
        return store.comments(ticket_id)

    @app.post(
        "/tickets/{ticket_id}/comments",
        tags=["tickets"],
        dependencies=secured,
        status_code=201,
        response_model=Comment,
    )
    def add_comment(ticket_id: str, body: CommentCreate):
        return store.add_comment(ticket_id, body.author_id, body.body, body.internal)

    @app.get("/admin/faults", tags=["admin"], dependencies=secured, response_model=FaultSettings)
    def get_faults():
        return faults.settings

    @app.put("/admin/faults", tags=["admin"], dependencies=secured, response_model=FaultSettings)
    def set_faults(body: FaultSettings):
        """Replace the fault settings. Takes effect on the next request."""
        faults.configure(body)
        return faults.settings

    @app.delete("/admin/faults", tags=["admin"], dependencies=secured, response_model=FaultSettings)
    def clear_faults():
        faults.configure(FaultSettings())
        return faults.settings

    @app.post("/admin/reset", tags=["admin"], dependencies=secured)
    def reset_data() -> dict[str, object]:
        """Discard every change and reload the seed tickets. Fault settings are kept."""
        return {"status": "reset", "tickets": store.reset()}

    return app


app = create_app()
