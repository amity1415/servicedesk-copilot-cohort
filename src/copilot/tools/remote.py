"""Transport adapters used by the same workflow against actual MCP services."""

import asyncio
import json

from copilot.mcp_servers.client import call


class RemoteTools:
    def __init__(self, token: str, urls: dict[str, str]):
        self.token, self.urls = token, urls

    def call(self, server: str, tool: str, arguments: dict):
        result = asyncio.run(call(self.urls[server], self.token, tool, arguments))
        if result.isError:
            raise PermissionError("Remote tool denied or failed; review operator audit")
        structured = result.structuredContent
        if structured is not None:
            # MCP wraps list return values under result; dictionary returns stay flat.
            return structured.get("result", structured)
        return json.loads(result.content[0].text)


class RemoteRuntime:
    def __init__(self, local, remote: RemoteTools):
        self.local, self.remote = local, remote

    def __getattr__(self, name):
        return getattr(self.local, name)

    def employee(self, actor):
        employee = self.remote.call("assets_db", "get_employee", {})
        if employee["employee_id"] != actor:
            raise PermissionError("remote identity mismatch")
        return employee

    def assets(self, actor, employee_id):
        self.employee(actor)
        return self.remote.call("assets_db", "get_assets", {"employee_id": employee_id})["rows"]

    def rows(self, table):
        tools = {
            "software_catalogue": "get_software_catalogue",
            "service_incidents": "check_service_status",
        }
        if table not in tools:
            raise ValueError("no remote tool for this reference table")
        return self.remote.call("assets_db", tools[table], {})["rows"]

    def request_access(self, actor, app, key):
        self.employee(actor)
        return self.remote.call(
            "ticketing", "request_access", {"app_id": app, "idempotency_key": key}
        )


class RemoteRetriever:
    def __init__(self, remote):
        self.remote = remote

    def answer(self, query, **kwargs):
        return self.remote.call(
            "documents", "search_kb", {"query": query, "os_name": kwargs.get("os_name")}
        )


class RemoteTicketing:
    def __init__(self, remote):
        self.remote = remote

    def create(self, actor, draft, key):
        return self.remote.call(
            "ticketing", "create_ticket", {"draft": draft.model_dump(), "idempotency_key": key}
        )
