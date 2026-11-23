# 25 terminal and coding runbook

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
& $py sessions/25-human-in-the-loop-approval/reference.py
Get-Content reports/sessions/25.json
& $py -m pytest tests/test_working_project.py::test_finsight_requires_manager_and_data_owner tests/test_working_project.py::test_rejection_and_idempotency
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

- [src/copilot/tools/runtime.py ](../../src/copilot/tools/runtime.py)
- [src/copilot/api/app.py ](../../src/copilot/api/app.py)

Work through these changes in order:

1. Create pending access request.
2. Derive Sofia's manager from employee data.
3. Persist approve or reject decision.
4. Gate fulfilment on matching record.
5. Allocate licence in a transaction.
6. Audit all decisions.

## 3. Check the lab result

Run the FinSight terminal sequence in the overall runbook. Verify the pending result, both decisions, and that the analyst receives the fulfilled result.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
