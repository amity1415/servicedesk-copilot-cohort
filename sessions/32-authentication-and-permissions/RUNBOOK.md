# 32 terminal and coding runbook

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
& $py sessions/32-authentication-and-permissions/reference.py
Get-Content reports/sessions/32.json
& $py -m pytest tests/test_working_project.py::test_ownership_enforced_on_assets_and_threads tests/test_cumulative_flow.py
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

- [src/copilot/api/app.py ](../../src/copilot/api/app.py)
- [src/copilot/tools/runtime.py ](../../src/copilot/tools/runtime.py)

Work through these changes in order:

1. Validate token server-side.
2. Map identity to employee role.
3. Apply tool and row permissions.
4. Audit allowed and denied calls.
5. Test employee, analyst and admin.
6. Reject unknown tokens.

## 3. Check the lab result

Use two synthetic employee identities and an operator identity. Record each permitted call and denied cross-user attempt in your permission matrix.

```powershell
& $py -m pytest
& $py -m ruff check .
& $py -m ruff format --check .
git status --short
```

Record actual outputs and any required verification still pending in
[evidence.md](evidence.md). The formal project gate is described in the
[completion policy](../../docs/SESSION_COMPLETION_POLICY.md).
