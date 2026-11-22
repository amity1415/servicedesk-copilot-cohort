"""Exercise the teaching API and chat UI against a temporary loopback server."""

from __future__ import annotations

import json
import os
import socket
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from unittest.mock import patch
from uuid import UUID

import httpx
import uvicorn
from streamlit.testing.v1 import AppTest

from copilot.api.app import create_app

MAC_QUESTION = "How do I set up VPN on my Mac?"
WINDOWS_QUESTION = "How do I fix Windows VPN error 809?"
FOLLOWUP = "It still doesn't work."


@contextmanager
def running_server(app):
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        worker = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        worker.start()
        try:
            deadline = time.monotonic() + 15
            while not server.started:
                if not worker.is_alive() or time.monotonic() >= deadline:
                    raise RuntimeError("The RAG server did not start")
                time.sleep(0.05)
            yield f"http://127.0.0.1:{listener.getsockname()[1]}"
        finally:
            server.should_exit = True
            worker.join(timeout=15)


def walkthrough(token: str, question: str, expected: str, *, followup: bool = False) -> dict:
    page = Path(__file__).resolve().parents[1] / "ui/chat.py"
    ui = AppTest.from_file(str(page), default_timeout=20).run()
    ui.sidebar.text_input[1].set_value(token).run()

    def submit(text):
        ui.chat_input[0].set_value(text).run()
        if ui.exception or ui.error:
            raise RuntimeError("The Streamlit request failed")
        answer = ui.session_state.messages[-1]
        if answer["role"] != "assistant" or not answer["content"].strip():
            raise RuntimeError("The Streamlit view did not receive an answer")
        sources = sorted({citation["document_id"] for citation in answer["citations"]})
        if sources != [expected] or not any(expected in item.value for item in ui.caption):
            raise RuntimeError(f"The expected citation {expected} is missing from the UI")
        return sources

    result = {"question": question, "documents": submit(question)}
    ui.run()
    if not any(expected in item.value for item in ui.caption):
        raise RuntimeError("A Streamlit rerun dropped the previous citation")
    result["citation_survived_rerun"] = True
    if followup:
        result["followup"] = FOLLOWUP
        result["followup_documents"] = submit(FOLLOWUP)
    return result


def verify_http_service(data: Path) -> dict:
    config = {
        "COPILOT_ANSWER_MODE": "extractive",
        "COPILOT_RETRIEVAL_BACKEND": "tfidf",
        "COPILOT_TRANSPORT": "direct",
    }
    with TemporaryDirectory() as folder, patch.dict(os.environ, config):
        app = create_app(
            data=data,
            state=Path(folder) / "runtime.sqlite3",
            tokens={"mac-fixture": "E1261", "windows-fixture": "E1068", "admin-fixture": "E1218"},
        )
        with running_server(app) as base, patch.dict(os.environ, {"COPILOT_UI_API_URL": base}):
            with httpx.Client(base_url=base, timeout=15, trust_env=False) as client:
                health = client.get("/health").raise_for_status().json()
                if health["status"] != "ok" or health["documents"] <= 0:
                    raise RuntimeError("The API readiness response did not include indexed data")
                report = verify_requests(client)
            ui = {
                "mac": walkthrough("mac-fixture", MAC_QUESTION, "KB-1017"),
                "windows": walkthrough(
                    "windows-fixture", WINDOWS_QUESTION, "KB-1018", followup=True
                ),
            }
    return {
        "mode": "live-loopback-rag-service",
        "backend": "tfidf",
        "answer_mode": "extractive",
        "health": health,
        "requests": report,
        "ui": ui,
        "paid_calls": 0,
    }


def verify_requests(client: httpx.Client) -> dict:
    mac = {"Authorization": "Bearer mac-fixture"}
    windows = {"Authorization": "Bearer windows-fixture"}
    admin = {"Authorization": "Bearer admin-fixture"}
    ask = {"question": MAC_QUESTION, "thread_id": "verify-api", "stream": True}
    unauthorized = client.post("/ask", json=ask)
    if unauthorized.status_code != 401:
        raise RuntimeError("The API accepted an unauthenticated request")
    too_long = client.post("/ask", headers=mac, json={**ask, "question": "x" * 8001})
    if too_long.status_code != 422 or "input" in too_long.json()["detail"][0]:
        raise RuntimeError("The validation error returned the rejected request text")
    stream = client.post("/ask", headers=mac, json=ask).raise_for_status()
    UUID(stream.headers["X-Request-ID"])
    event, data = stream.text.strip().splitlines()
    result = json.loads(data.removeprefix("data: "))
    documents = sorted({citation["document_id"] for citation in result["citations"]})
    if not (
        stream.headers["content-type"].startswith("text/event-stream")
        and event == "event: result"
        and documents == ["KB-1017"]
    ):
        raise RuntimeError("The SSE result missed the expected citation")
    forbidden = client.post("/ask", headers=windows, json=ask)
    member_ingest = client.post("/ingest", headers=mac)
    if forbidden.status_code != 403 or member_ingest.status_code != 403:
        raise RuntimeError("The API did not enforce the thread or ingestion authorization")
    ingestion = client.post("/ingest", headers=admin).raise_for_status().json()
    if ingestion["documents"] <= 0 or ingestion["skipped"]:
        raise RuntimeError("The administrator did not ingest the complete synthetic corpus")
    return {
        "missing_token": unauthorized.status_code,
        "oversize": too_long.status_code,
        "cross_employee_thread": forbidden.status_code,
        "employee_ingest": member_ingest.status_code,
        "admin_ingest_documents": ingestion["documents"],
        "sse_documents": documents,
        "request_id_observed": True,
    }
