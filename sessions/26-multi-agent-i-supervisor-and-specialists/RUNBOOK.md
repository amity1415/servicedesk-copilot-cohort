# 26 terminal and coding runbook

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
& $py sessions/26-multi-agent-i-supervisor-and-specialists/reference.py
Get-Content reports/sessions/26.json
& $py -m pytest tests/test_working_project.py::test_loop_budget_and_read_only_specialist tests/test_react_diagnostics.py
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

- [src/copilot/agents/react.py ](../../src/copilot/agents/react.py)

Work through these changes in order:

1. Define knowledge, diagnostics and fulfilment roles.
2. Route under supervisor.
3. Restrict diagnostics to reads.
4. Pass structured results.
5. Compare against the single-agent baseline on 15 frozen tasks.

## 3. Check the lab result

For the formal comparison, run the same frozen tasks against the single-agent and specialist versions. Record model, outcome, elapsed time, and token usage.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
