# 28 terminal and coding runbook

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
& $py sessions/28-guardrails-and-prompt-injection-defence/reference.py
Get-Content reports/sessions/28.json
& $py -m pytest tests/test_working_project.py::test_injection_never_grants_privileges tests/test_working_project.py::test_mask_hides_known_identifiers
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

- [src/copilot/guardrails/checks.py ](../../src/copilot/guardrails/checks.py)
- [evals/redteam ](../../evals/redteam/)
- [src/copilot/agents/engine.py ](../../src/copilot/agents/engine.py)

Work through these changes in order:

1. Add attack detection and output checks.
2. Mask logs.
3. Restrict tool dispatch per role.
4. Author 25 attacks across tickets, documents and tools.
5. Reset state before each.
6. Verify forbidden effects absent.

## 3. Check the lab result

Inspect the defensive fixture report, then verify the app's blocked outcome in the full-stack runbook. Check authorization and the durable effect separately from detector coverage.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
