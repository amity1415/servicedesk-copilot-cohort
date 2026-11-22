import json
import logging
import os
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient


def test_typed_rag_api_scopes_threads_and_cleans_errors(tmp_path, monkeypatch, caplog):
    from copilot.api.app import create_app

    monkeypatch.setenv("COPILOT_ANSWER_MODE", "extractive")
    monkeypatch.setenv("COPILOT_RETRIEVAL_BACKEND", "tfidf")
    monkeypatch.setenv("COPILOT_TRANSPORT", "direct")
    data = Path(os.environ.get("COHORT_DATA_DIR", "data"))
    app = create_app(data, tmp_path / "runtime.sqlite3", {"sample-a": "E1261", "sample-b": "E1068"})
    caplog.set_level(logging.INFO, logger="copilot.api.http")

    @app.get("/test-error")
    def service_failure():
        raise RuntimeError("private fixture exception")

    mac = {"Authorization": "bearer sample-a"}
    windows = {"Authorization": "Bearer sample-b"}
    question = {"question": "How do I set up VPN on my Mac?", "thread_id": "acceptance"}

    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        assert {"Ask", "Answer", "Health", "IngestResult"} <= schema["components"]["schemas"].keys()
        ask_contract = schema["paths"]["/ask"]["post"]
        assert ask_contract["security"] == [{"HTTPBearer": []}]
        assert "text/event-stream" in ask_contract["responses"]["200"]["content"]
        assert client.get("/health").json()["status"] == "ok"

        denied = client.post("/ask", json=question)
        assert denied.status_code == 401 and denied.headers["WWW-Authenticate"] == "Bearer"
        assert (
            client.post(
                "/ask", headers={"Authorization": "Bearer bogus"}, json=question
            ).status_code
            == 401
        )
        private_text = "private input " * 800
        invalid = client.post("/ask", headers=mac, json={**question, "question": private_text})
        assert invalid.status_code == 422 and "private input" not in invalid.text
        assert set(invalid.json()["detail"][0]) == {"type", "loc", "msg"}

        result = client.post("/ask", headers=mac, json=question)
        assert result.status_code == 200
        request_id = result.headers["X-Request-ID"]
        assert UUID(request_id).version == 4
        assert any(f"request_id={request_id}" in line for line in caplog.messages)
        assert {citation["document_id"] for citation in result.json()["citations"]} == {"KB-1017"}

        forbidden = client.post("/ask", headers=windows, json=question)
        assert forbidden.status_code == 403 and forbidden.json() == {"error": "access denied"}
        assert client.post("/ingest", headers=mac).status_code == 403

        stream = client.post("/ask", headers=mac, json={**question, "stream": True})
        assert stream.headers["content-type"].startswith("text/event-stream")
        event, data = stream.text.strip().splitlines()
        assert event == "event: result" and json.loads(data.removeprefix("data: ")) == result.json()

        failure = client.get("/test-error")
        assert failure.status_code == 500 and failure.json() == {"detail": "Internal server error"}
        assert "private fixture exception" not in caplog.text
        assert "sample-a" not in caplog.text and "private input" not in caplog.text
