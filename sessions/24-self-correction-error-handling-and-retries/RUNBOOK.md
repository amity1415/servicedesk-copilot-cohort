# 24 terminal and coding runbook

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
& $py sessions/24-self-correction-error-handling-and-retries/reference.py
Get-Content reports/sessions/24.json
& $py -m pytest tests/test_password_reset_workflow.py
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

- [src/copilot/tools/ticketing.py ](../../src/copilot/tools/ticketing.py)
- [src/copilot/tools/password_reset.py ](../../src/copilot/tools/password_reset.py)

Work through these changes in order:

1. Return typed tool errors.
2. Add bounded backoff and deadlines.
3. Persist ticket idempotency key in state.
4. Apply step and cost budgets.
5. Enable ticketing faults.
6. Inspect final state.

## 3. Check the lab result

For live fault recovery, start the isolated verifier with `python -m copilot workflow-verify` after starting the database and ticketing mock as in Session 17. Inspect the resulting ticket ID and replay evidence.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
