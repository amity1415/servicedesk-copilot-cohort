"""Explicit contract snapshot authoring; never auto-update in CI."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from copilot.mcp_servers.servers import make_server  # noqa: E402


async def schemas(data: Path, state: Path):
    snapshots = {}
    for name in ("documents", "assets_db", "ticketing"):
        server = make_server(name, "E1261", data, state)
        snapshots[name] = {tool.name: tool.inputSchema for tool in await server.list_tools()}
    return snapshots


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("COPILOT_TICKETING_API_KEY", "dev-ticketing-key")
    actual = asyncio.run(schemas(ROOT / "data", ROOT / ".work/contracts.sqlite3"))
    path = ROOT / "tests/contracts/mcp_schemas.json"
    if args.update:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(actual, sort_keys=True, indent=2) + "\n")
        print("Updated schema contract; review the diff before committing")
    else:
        assert actual == json.loads(path.read_text()), "MCP schema drift; review the change"
        print("MCP tool schemas match the reviewed snapshot")


if __name__ == "__main__":
    main()
