from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("mcp")
pytest.importorskip("a2a")

from fastapi.testclient import TestClient  # noqa: E402

from copilot.mcp_servers.http import create_app as mcp_app  # noqa: E402
from services.hr_agent.app import create_app as hr_app  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def test_mcp_http_initialization_and_real_tool_call(tmp_path):
    app = mcp_app("assets_db", {"fixture": "E1261"}, DATA, tmp_path / "mcp.sqlite3")
    with TestClient(app) as client:
        assert client.post("/mcp", json={}).status_code == 401
        headers = {
            "Authorization": "Bearer fixture",
            "Accept": "application/json, text/event-stream",
        }
        initialized = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "1"},
                },
            },
        )
        assert initialized.status_code == 200
        assert "serverInfo" in initialized.json()["result"]
        listed = client.post(
            "/mcp",
            headers=headers,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert "get_assets" in {t["name"] for t in listed.json()["result"]["tools"]}
        own = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "get_assets", "arguments": {"employee_id": "E1261"}},
            },
        )
        assert not own.json()["result"].get("isError", False)
        denied = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "get_assets", "arguments": {"employee_id": "E1166"}},
            },
        )
        assert denied.json()["result"]["isError"] is True


def test_mcp_documents_resources_prompts_and_schema(tmp_path):
    app = mcp_app("documents", {"fixture": "E1261"}, DATA, tmp_path / "docs.sqlite3")
    headers = {"Authorization": "Bearer fixture", "Accept": "application/json, text/event-stream"}
    with TestClient(app) as client:

        def rpc(method, params):
            response = client.post(
                "/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            )
            assert response.status_code == 200
            return response.json()

        tools = rpc("tools/list", {})["result"]["tools"]
        assert tools[0]["inputSchema"]["required"] == ["query"]
        article = rpc("resources/read", {"uri": "kb://articles/KB-1001"})
        assert "password" in article["result"]["contents"][0]["text"].lower()
        prompt = rpc(
            "prompts/get", {"name": "triage_ticket", "arguments": {"description": "VPN fails"}}
        )
        assert "untrusted" in prompt["result"]["messages"][0]["content"]["text"]


def test_hr_a2a_real_task_completion_and_authentication():
    pytest.importorskip("a2a")
    app = hr_app(DATA, "fixture")
    with TestClient(app) as client:
        card = client.get("/.well-known/agent-card.json")
        assert card.status_code == 200
        assert client.post("/", json={}).status_code == 401
        request = {
            "jsonrpc": "2.0",
            "id": "task-one",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "message-one",
                    "role": "user",
                    "parts": [
                        {
                            "kind": "text",
                            "text": json.dumps(
                                {
                                    "candidate_id": "C-2041",
                                    "manager_id": "E1062",
                                    "start_date": "2026-11-16",
                                }
                            ),
                        }
                    ],
                }
            },
        }
        response = client.post("/", headers={"Authorization": "Bearer fixture"}, json=request)
        assert response.status_code == 200
        assert response.json()["result"]["status"]["state"] == "completed"
        artifact = response.json()["result"]["artifacts"][0]["parts"][0]["text"]
        assert json.loads(artifact)["candidate_id"] == "C-2041"


def test_langgraph_checkpoint_restores_state(tmp_path):
    pytest.importorskip("langgraph")
    from langgraph.checkpoint.memory import InMemorySaver

    from copilot.agents.graph import build

    class FakeEngine:
        def run(self, actor, question, thread):
            return {"answer": question, "actor": actor}

    graph = build(FakeEngine(), InMemorySaver())
    config = {"configurable": {"thread_id": "graph-test"}}
    state = {"actor": "E1261", "question": "VPN", "thread": "graph-test"}
    result = graph.invoke(state, config)
    assert result["result"]["answer"] == "VPN"
    assert graph.get_state(config).values["actor"] == "E1261"
