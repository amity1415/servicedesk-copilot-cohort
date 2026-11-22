"""Expose the cumulative RAG pipeline over authenticated HTTP."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException

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
from copilot.config import get_settings
from copilot.rag.grounded import MODE as GROUNDED_MODE
from copilot.rag.grounded import configured_rag
from copilot.rag.pipeline import ingest
from copilot.rag.query import rewrite


@dataclass
class Conversation:
    actor: str
    previous: str = ""
    lock: Lock = field(default_factory=Lock)


def create_app(
    data: Path = Path("data"),
    state: Path = Path(".work/runtime.sqlite3"),
    tokens: dict[str, str] | None = None,
) -> FastAPI:
    configured = configured_tokens(tokens)
    reference = data / "db/csv"
    with (reference / "employees.csv").open(encoding="utf-8", newline="") as stream:
        employees = {row["employee_id"]: row for row in csv.DictReader(stream)}
    if not employees.keys() >= set(configured.values()):
        raise ValueError("COPILOT_AUTH_TOKENS contains an unknown employee ID")
    primary_os = {}
    with (reference / "devices.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            primary_os.setdefault(row["assigned_to"], row["os"])

    rag = configured_rag(data)
    threads: dict[str, Conversation] = {}
    threads_lock = Lock()
    ingestion_lock = Lock()
    app = FastAPI(title="Larkhaven Copilot", version="0.2.0")
    identify = identify_with(configured)
    register_http(app)

    @app.get("/health", response_model=Health)
    def health():
        return {"status": "ok", "mode": rag.mode, "documents": len(rag.chunks)}

    @app.post(
        "/ask", response_model=Answer, response_model_exclude_unset=True, responses=ASK_RESPONSES
    )
    def ask(body: Ask, actor: str = Depends(identify)):
        with threads_lock:
            if body.thread_id not in threads:
                threads[body.thread_id] = Conversation(actor)
            thread = threads[body.thread_id]
        if thread.actor != actor:
            raise PermissionError("thread belongs to another employee")

        employee = employees[actor]
        with thread.lock:
            query = rewrite(body.question, thread.previous)
            scope = body.question.lower()
            if "mac" not in scope and "windows" not in scope:
                scope = query.lower()
            os_name = (
                "macos"
                if "mac" in scope
                else "windows"
                if "windows" in scope
                else primary_os.get(actor)
            )
            result = rag.answer(
                query, role=employee["role"], os_name=os_name, region=employee["region"]
            )
            thread.previous = body.question
        status = (
            "abstained"
            if result.get("mode") == GROUNDED_MODE and result.get("abstained")
            else "answered"
        )
        result.update(status=status, steps=["search_kb"])
        return completed_result(result, body.stream)

    @app.post("/ingest", response_model=IngestResult)
    def ingest_documents(actor: str = Depends(identify)):
        if employees[actor]["role"] != "admin":
            raise HTTPException(403, "ingestion requires admin")
        with ingestion_lock:
            return ingest(data, state.parent / "documents.json")

    return app


def production_app() -> FastAPI:
    return create_app(data=get_settings().data_dir)
