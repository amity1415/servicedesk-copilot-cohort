# 38 terminal and coding runbook

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
& $py sessions/38-regression-testing-in-ci/reference.py
Get-Content reports/sessions/38.json
& $py -m pytest tests/test_completion_policy.py
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

- [.github/workflows/ci.yml ](../../.github/workflows/ci.yml)
- [release/manifest.yaml ](../../release/manifest.yaml)

Work through these changes in order:

1. Run lint, unit and API tests on pull requests.
2. Add service contract checks.
3. Gate smoke eval and red-team effects.
4. Schedule full evaluation.
5. Record release manifest.
6. Seed a bad-prompt mutation.

## 3. Check the lab result

Run the offline workflow commands below locally. After reviewing and committing your learner changes, push to an authorized learner branch to see CI run on GitHub.

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python scripts/check_course.py
python scripts/snapshot_contracts.py
git status --short
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
