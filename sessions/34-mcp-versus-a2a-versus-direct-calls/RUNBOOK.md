# 34 terminal and coding runbook

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
& $py sessions/34-mcp-versus-a2a-versus-direct-calls/reference.py
Get-Content reports/sessions/34.json
& $py -m pytest tests/test_sdk_client.py::test_every_mcp_tool_schema_matches_snapshot
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

- [src/copilot/mcp_servers/client.py ](../../src/copilot/mcp_servers/client.py)
- [tests ](../../tests/)

Work through these changes in order:

1. Implement service status by direct call, MCP and A2A.
2. Run repeated samples.
3. Record median and p95.
4. Snapshot canonical MCP schemas.
5. Fail a changed required argument.

## 3. Check the lab result

Run each transport against equivalent fixture state in your benchmark code. Collect repeated samples and report median and p95. The schema check is separate from the benchmark.

Generate and inspect the contract report:

```powershell
python scripts/snapshot_contracts.py
Get-Content tests/contracts/mcp_schemas.json -TotalCount 25
```

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
