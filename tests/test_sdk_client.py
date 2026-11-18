import asyncio
import json
from pathlib import Path

import httpx
import pytest

pytest.importorskip("mcp")

from copilot.mcp_servers.client import http_session  # noqa: E402
from copilot.mcp_servers.http import create_app  # noqa: E402
from copilot.mcp_servers.servers import make_server  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_real_mcp_client_and_server_over_asgi_http(tmp_path):
    async def run():
        app = create_app(
            "assets_db", {"fixture": "E1261"}, ROOT / "data", tmp_path / "client.sqlite3"
        )

        def factory(headers=None, timeout=None, auth=None):
            return httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                headers=headers,
                timeout=timeout,
                auth=auth,
                follow_redirects=True,
            )

        async with (
            app.router.lifespan_context(app),
            http_session("http://testserver/mcp", "fixture", factory) as client,
        ):
            listed = await client.list_tools()
            assert "get_assets" in {tool.name for tool in listed.tools}
            own = await client.call_tool("get_assets", {"employee_id": "E1261"})
            assert not own.isError
            payload = own.structuredContent or json.loads(own.content[0].text)
            assert payload["rows"][0]["assigned_to"] == "E1261"
            denied = await client.call_tool("get_assets", {"employee_id": "E1166"})
            assert denied.isError

    asyncio.run(run())


def test_every_mcp_tool_schema_matches_snapshot(tmp_path, monkeypatch):
    monkeypatch.setenv("COPILOT_TICKETING_API_KEY", "fixture")
    expected = json.loads((ROOT / "tests/contracts/mcp_schemas.json").read_text())

    async def collect():
        actual = {}
        for name in ("documents", "assets_db", "ticketing"):
            server = make_server(name, "E1261", ROOT / "data", tmp_path / "schemas.sqlite3")
            actual[name] = {tool.name: tool.inputSchema for tool in await server.list_tools()}
        return actual

    assert asyncio.run(collect()) == expected


def test_langgraph_tool_loop_and_budget():
    pytest.importorskip("langgraph")
    from langgraph.checkpoint.memory import InMemorySaver

    from copilot.agents.graph import build_tool_graph, invoke_for_identity

    graph = build_tool_graph(
        lambda query, events: {"tool": "get_assets"},
        {"get_assets": lambda: []},
        {"get_assets"},
        InMemorySaver(),
        max_steps=2,
    )
    result = invoke_for_identity(graph, "E1261", "bounded", "slow")
    assert result["result"]["reason"] == "step_limit"
    assert len(result["result"]["events"]) == 2
