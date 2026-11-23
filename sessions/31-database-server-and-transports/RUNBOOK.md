# 31 terminal and coding runbook

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
& $py sessions/31-database-server-and-transports/reference.py
Get-Content reports/sessions/31.json
& $py -m pytest tests/test_protocols.py::test_mcp_http_initialization_and_real_tool_call
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

1. Expose fixed parameterized employee, assets, licence and service queries.
2. Enforce row limits.
3. Create database SELECT-only role.
4. Move servers to HTTP.
5. Run real client contract tests.

## 3. Check the lab result

Start the full MCP stack and make an authenticated request to the assets
server. Complete fixed PostgreSQL reads and the read-only role exercise in
your lab branch. The shipped assets adapter uses fixture data.

After starting the [Compose overlay](../../docs/BEGINNER_RUNBOOK.md#4-switch-to-the-full-mcp-and-hr-stack):

```powershell
docker compose -f docker-compose.yml -f docker-compose.app.yml ps
& $py -c "import asyncio; from copilot.mcp_servers.client import call; result = asyncio.run(call('http://localhost:8002/mcp', 'mac-dev', 'get_employee', {})); assert not result.isError; print(result.structuredContent or result.content)"
```

The output should identify the synthetic employee `E1261`.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
