# 29 terminal and coding runbook

Open the [lesson](README.md) and [numbered build steps](STEPS_TO_FOLLOW.md). Start from the repository root
with the [course environment](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout)
installed. In PowerShell, run these three lines to confirm the folder and
use its Python interpreter:

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
```

## 1. Run the supplied reference and check the existing behavior

```powershell
& $py sessions/29-mcp-architecture-and-the-ticketing-server/reference.py
Get-Content reports/sessions/29.json
& $py -m pytest tests/test_sdk_client.py::test_real_mcp_client_and_server_over_asgi_http
```

The JSON report describes the scope of the reference. The test command checks
the existing behaviors shown above. The later lessons use the shared source
tree for coding. Use a learner branch and keep the preceding work in that
branch.

## 2. Implement the lab

1. Open the repository root in VS Code. Open the source entry points below
   and read the existing behavior.
2. Read [the numbered steps](STEPS_TO_FOLLOW.md) and the
   [deliberate failure exercise](README.md#deliberate-failure-exercise).
   Add the expected outcome as a focused test before changing the feature.
3. Edit one operation at a time, save with **Ctrl+S**, and rerun the targeted
   test command from Step 1. Run your new test as well. Keep the checks from
   earlier sessions passing.

- [src/copilot/mcp_servers/servers.py ](../../src/copilot/mcp_servers/servers.py)
- [src/copilot/mcp_servers/client.py ](../../src/copilot/mcp_servers/client.py)

Work through these changes in order:

1. Pin MCP v1 SDK.
2. Create stdio ticketing server.
3. Register typed create tool.
4. Inspect tool schema.
5. Connect actual SDK client.
6. Compare direct and MCP ticket outcomes.

## 3. Check the lab result

The SDK test exercises HTTP in process. For the lesson's stdio exercise, use the terminal and client instructions below.

Start the ticketing mock and use the SDK to launch the stdio process,
initialize a session, and list the tools:

```powershell
docker compose up -d --wait ticketing
Invoke-RestMethod http://127.0.0.1:8081/health
@'
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "copilot.mcp_servers.servers", "ticketing"],
        env={
            "COPILOT_ACTOR": "E1261",
            "COPILOT_TICKETING_API_KEY": "dev-ticketing-key",
        },
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([tool.name for tool in tools.tools])


asyncio.run(main())
'@ | & $py -
```

Expect a tool list containing `create_ticket`. The Python client shuts down
the stdio child process when the session closes.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
