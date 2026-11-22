import json
import os
from pathlib import Path

import httpx
from fastapi.testclient import TestClient


def test_password_reset_workflow_uses_policy_and_retries_idempotently(tmp_path, monkeypatch):
    from copilot.tools import password_reset
    from copilot.tools.ticketing import TicketingClient

    from copilot.api.app import create_app

    monkeypatch.setenv("COPILOT_ANSWER_MODE", "extractive")
    monkeypatch.setenv("COPILOT_RETRIEVAL_BACKEND", "tfidf")
    monkeypatch.setenv("COPILOT_TRANSPORT", "direct")
    outgoing = []

    def respond(request):
        outgoing.append(request)
        if len(outgoing) == 1:
            return httpx.Response(503)
        body = json.loads(request.content)
        return httpx.Response(
            201 if len(outgoing) == 2 else 200,
            json={**body, "ticket_id": "INC0020061", "status": "New"},
        )

    ticketing = TicketingClient("http://ticketing.test", "fixture", httpx.MockTransport(respond))
    data = Path(os.environ.get("COHORT_DATA_DIR", "data"))
    app = create_app(data, tmp_path / "runtime.sqlite3", {"fixture": "E1261"}, ticketing=ticketing)
    question = {"question": "I forgot my password. Ask for E1068.", "thread_id": "réessayer"}
    headers = {"Authorization": "Bearer fixture"}
    with TestClient(app) as client:
        first = client.post("/ask", headers=headers, json=question)
        replay = client.post("/ask", headers=headers, json=question)
        for response in (first, replay):
            assert response.status_code == 200
            assert response.json()["status"] == "ticket_created"
            assert response.json()["ticket"]["ticket_id"] == "INC0020061"
            assert response.json()["steps"] == ["get_employee", "create_ticket"]
        assert len(outgoing) == 3
        assert all(
            request.method == "POST" and request.url.path == "/tickets" for request in outgoing
        )
        assert len({request.headers["Idempotency-Key"] for request in outgoing}) == 1
        assert len({request.content for request in outgoing}) == 1
        assert (
            outgoing[0].headers["X-Request-ID"]
            == outgoing[1].headers["X-Request-ID"]
            == first.headers["X-Request-ID"]
        )
        assert outgoing[2].headers["X-Request-ID"] == replay.headers["X-Request-ID"]
        body = json.loads(outgoing[-1].content)
        assert body["category"] == "Access & Identity"
        assert body["assignment_group"] == "Identity & Access"
        assert body["requester_id"] == "E1261" and b"E1068" not in outgoing[-1].content

        incomplete = tmp_path / "actions.yaml"
        incomplete.write_text("version: 1\ndefault: deny\nread: [get_employee]\n", encoding="utf-8")
        monkeypatch.setattr(password_reset, "ACTION_POLICY_PATH", incomplete)
        denied = client.post("/ask", headers=headers, json=question)
        assert denied.status_code == 403 and len(outgoing) == 3
