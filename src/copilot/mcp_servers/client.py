"""Real MCP session setup; no home-grown JSON envelope pretending to be MCP."""

from contextlib import asynccontextmanager


@asynccontextmanager
async def http_session(url: str, bearer: str, httpx_client_factory=None):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    options = {"httpx_client_factory": httpx_client_factory} if httpx_client_factory else {}
    async with (
        streamablehttp_client(url, headers={"Authorization": f"Bearer {bearer}"}, **options) as (
            read,
            write,
            _,
        ),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        yield session


async def call(url: str, bearer: str, tool: str, arguments: dict):
    async with http_session(url, bearer) as session:
        return await session.call_tool(tool, arguments)
