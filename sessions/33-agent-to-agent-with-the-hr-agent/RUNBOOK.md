# 33 terminal and coding runbook

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
& $py sessions/33-agent-to-agent-with-the-hr-agent/reference.py
Get-Content reports/sessions/33.json
& $py -m pytest tests/test_protocols.py::test_hr_a2a_real_task_completion_and_authentication tests/test_cumulative_flow.py
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

- [services/hr_agent ](../../services/hr_agent/)
- [src/copilot/agents/planning.py ](../../src/copilot/agents/planning.py)

Work through these changes in order:

1. Implement HR AgentExecutor with SDK.
2. Publish agent card.
3. Authenticate partner endpoint.
4. Submit joiner task.
5. Poll boundedly for completion.
6. Bind HR result to candidate ID.

## 3. Check the lab result

Use the full-stack terminal walkthrough to run the incomplete request and then the request with candidate C-2041 and date 2026-11-16.

After starting the [Compose overlay](../../docs/BEGINNER_RUNBOOK.md#4-switch-to-the-full-mcp-and-hr-stack):

```powershell
Invoke-RestMethod http://localhost:8090/.well-known/agent-card.json
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
