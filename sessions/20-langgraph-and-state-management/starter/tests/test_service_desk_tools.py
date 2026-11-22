import json
import os
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient


def test_typed_service_desk_tools_authorize_before_writing(tmp_path, monkeypatch):
    from copilot.api.app import create_app
    from copilot.tools.ticketing import TicketingClient
    from copilot.tools.verify_tools import ANALYST, DRAFT, EMPLOYEE, KEY, exercise_tools
    from copilot.tools.verify_workflow import seeded_ticketing

    monkeypatch.setenv("COPILOT_ANSWER_MODE", "extractive")
    monkeypatch.setenv("COPILOT_RETRIEVAL_BACKEND", "tfidf")
    monkeypatch.setenv("COPILOT_TRANSPORT", "direct")
    data = Path(os.environ.get("COHORT_DATA_DIR", "data"))
    with TestClient(seeded_ticketing(data, KEY), headers={"X-API-Key": KEY}) as tickets:

        def bridge(request):
            response = tickets.request(
                request.method,
                str(request.url),
                headers=dict(request.headers),
                content=request.content,
            )
            return httpx.Response(
                response.status_code, headers=dict(response.headers), content=response.content
            )

        app = create_app(
            data,
            tmp_path / "tools.sqlite3",
            {"employee-fixture": EMPLOYEE, "analyst-fixture": ANALYST},
            ticketing=TicketingClient("http://testserver", KEY, httpx.MockTransport(bridge)),
        )
        with TestClient(app) as api:
            proof = exercise_tools(api, tickets)
            assert proof["ticket"]["status"] == "Awaiting User"
            assert proof["search_documents"] == ["KB-1017"]
            assert len(proof["analyst_tools"]) == 6
            headers = {"Authorization": "Bearer employee-fixture", "Idempotency-Key": "foreign-id"}
            bad = api.post(
                "/tools/create_ticket",
                headers=headers,
                json={"draft": {**DRAFT, "requester_id": "E1166"}},
            )
            assert bad.status_code == 422
            assert "E1166" not in bad.text
            assert (
                api.post(
                    "/tools/get_assets", headers=headers, json={"employee_id": "E1166"}
                ).status_code
                == 403
            )
            unapproved_close = api.post(
                "/tools/update_ticket",
                headers={"Authorization": "Bearer analyst-fixture"},
                json={"ticket_id": proof["ticket"]["ticket_id"], "changes": {"status": "Closed"}},
            )
            assert unapproved_close.status_code == 422
            assert tickets.get("/health").json()["tickets"] == 62


def test_model_tool_choice_and_single_draft_repair():
    from copilot.llm.client import ModelClient
    from copilot.llm.service_desk import (
        DraftEscalation,
        InvalidToolChoice,
        choose_tool,
        generate_ticket_draft,
    )
    from copilot.tools.verify_tools import DRAFT

    def call(name, arguments):
        return {"type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}

    responses = iter(
        [
            {"tool_calls": [call("get_assets", {"employee_id": None})]},
            {"tool_calls": [call("get_employee", {"employee_id": "E1166"})]},
            {"content": "{}"},
            {"content": json.dumps(DRAFT)},
            {"content": "{}"},
            {"content": "{}"},
            {"refusal": "fixture refusal"},
        ]
    )
    requests = []

    def answer(request):
        requests.append(json.loads(request.content))
        message = next(responses)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": message, "finish_reason": "stop"}],
                "usage": {"total_tokens": 8},
            },
        )

    model = ModelClient(
        "fixture", api_key="fixture", transport=httpx.MockTransport(answer), attempts=1
    )
    selected = choose_tool(model, "Which devices are assigned to me?")
    assert selected.name == "get_assets" and selected.arguments == {}
    assert requests[0]["tool_choice"] == "required" and requests[0]["parallel_tool_calls"] is False
    assert len(requests[0]["tools"]) == 6
    assert all(tool["function"]["strict"] for tool in requests[0]["tools"])
    with pytest.raises(InvalidToolChoice):
        choose_tool(model, "Read my directory profile")

    draft = generate_ticket_draft(model, "The VPN disconnects on my Mac")
    assert draft.model_dump() == DRAFT
    assert requests[2]["response_format"]["json_schema"]["strict"] is True
    assert len(requests[2]["messages"]) == 2 and len(requests[3]["messages"]) == 3
    with pytest.raises(DraftEscalation, match="after one repair"):
        generate_ticket_draft(model, "The printer has stopped working")
    with pytest.raises(DraftEscalation, match="analyst review"):
        generate_ticket_draft(model, "The browser stopped working")
    assert len(requests) == 7
