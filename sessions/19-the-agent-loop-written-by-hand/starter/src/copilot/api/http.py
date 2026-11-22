"""Shared HTTP contract for the RAG lesson and the integrated workflows."""

from __future__ import annotations

import json
import logging
import os
import secrets
import time
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from copilot.logging_setup import request_id_var
from copilot.telemetry import span

log = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)
ASK_RESPONSES = {200: {"content": {"text/event-stream": {"schema": {"type": "string"}}}}}


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    thread_id: str = Field(min_length=1, max_length=128)
    stream: bool = False


class Citation(BaseModel):
    model_config = ConfigDict(extra="allow")

    chunk_id: str
    document_id: str
    source: str
    quote: str | None = None


class Answer(BaseModel):
    model_config = ConfigDict(extra="allow")

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    status: str | None = None
    abstained: bool | None = None
    mode: str | None = None


class Health(BaseModel):
    status: Literal["ok"]
    mode: str
    documents: int


class SkippedDocument(BaseModel):
    source: str
    error_type: str
    error: str


class IngestResult(BaseModel):
    documents: int
    changed: int
    removed: list[str]
    skipped: list[SkippedDocument]
    parser_version: str


def configured_tokens(tokens: dict[str, str] | None) -> dict[str, str]:
    configured = (
        tokens if tokens is not None else json.loads(os.getenv("COPILOT_AUTH_TOKENS", "{}"))
    )
    if not isinstance(configured, dict) or any(
        not isinstance(token, str)
        or not token.strip()
        or not isinstance(actor, str)
        or not actor.strip()
        for token, actor in configured.items()
    ):
        raise ValueError("COPILOT_AUTH_TOKENS must map nonempty bearer keys to employee IDs")
    return configured.copy()


def identify_with(tokens: dict[str, str]):
    def identity(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> str:
        if credentials is not None:
            supplied = credentials.credentials.encode()
            for token, actor in tokens.items():
                if secrets.compare_digest(supplied, token.encode()):
                    return actor
        raise HTTPException(401, "invalid bearer token", headers={"WWW-Authenticate": "Bearer"})

    return identity


def completed_result(result: dict, stream: bool):
    if not stream:
        return result
    payload = Answer.model_validate(result).model_dump(mode="json", exclude_unset=True)
    event = "event: result\ndata: " + json.dumps(payload) + "\n\n"
    return StreamingResponse(iter([event]), media_type="text/event-stream")


def register_http(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_metadata(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        context_token = request_id_var.set(request_id)
        started = time.monotonic()
        try:
            try:
                with span("api.request", dict(request.headers)):
                    response = await call_next(request)
            except Exception as exc:  # noqa: BLE001 - sanitize unexpected HTTP failures
                log.error("request_id=%s error_type=%s", request_id, type(exc).__name__)
                response = JSONResponse(
                    status_code=500, content={"detail": "Internal server error"}
                )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Elapsed-Seconds"] = f"{time.monotonic() - started:.4f}"
            route = request.scope.get("route")
            log.info(
                "request_id=%s method=%s route=%s status=%d",
                request_id,
                request.method,
                getattr(route, "path", "<unmatched>"),
                response.status_code,
            )
            return response
        finally:
            request_id_var.reset(context_token)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, exc: RequestValidationError):
        detail = [{key: item[key] for key in ("type", "loc", "msg")} for item in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.exception_handler(PermissionError)
    async def permission_error(_request: Request, _exc: PermissionError):
        return JSONResponse(status_code=403, content={"error": "access denied"})
