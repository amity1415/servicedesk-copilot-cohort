"""Authenticated Streamable HTTP with a server-bound identity per token.

For a teaching environment the opaque bearer map replaces an identity provider.
Use an OAuth verifier and managed identity in a real deployment.
"""

import json
import os
import secrets
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount

from copilot.mcp_servers.servers import make_server


def create_app(
    name: str,
    tokens: dict[str, str],
    data: Path = Path("data"),
    state: Path = Path(".work/runtime.sqlite3"),
):
    if any(not token for token in tokens):
        raise ValueError("empty bearer tokens are forbidden")
    servers = {actor: make_server(name, actor, data, state) for actor in set(tokens.values())}
    applications = {}
    for actor, server in servers.items():
        server.settings.stateless_http = True
        server.settings.json_response = True
        applications[actor] = server.streamable_http_app()

    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for server in servers.values():
                await stack.enter_async_context(server.session_manager.run())
            yield

    async def dispatch(scope, receive, send):
        if scope["type"] != "http":
            return
        headers = dict(scope.get("headers", []))
        supplied = headers.get(b"authorization", b"").decode().removeprefix("Bearer ")
        actor = next(
            (actor for token, actor in tokens.items() if secrets.compare_digest(supplied, token)),
            None,
        )
        if actor is None:
            await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
            return
        await applications[actor](scope, receive, send)

    return Starlette(routes=[Mount("/", app=dispatch)], lifespan=lifespan)


def configured_app():
    return create_app(
        os.environ["COPILOT_MCP_SERVER"], json.loads(os.environ["COPILOT_AUTH_TOKENS"])
    )
