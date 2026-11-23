# 36 terminal and coding runbook

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
& $py sessions/36-llm-as-a-judge/reference.py
Get-Content reports/sessions/36.json
& $py -m pytest tests/test_scoring.py
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

- [evals/rubrics ](../../evals/rubrics/)
- [src/copilot/course/scoring.py ](../../src/copilot/course/scoring.py)

Work through these changes in order:

1. Define answer and ticket-summary rubrics.
2. Hand-label 30 examples without judge output.
3. Run judge with schema.
4. Compute agreement and confusion table.
5. Review disagreements.
6. Prefer exact checks where possible.

## 3. Check the lab result

Open the answer rubric. Hand-label the required examples before calling your approved judge. A live calibration requires the judge runner you implement in this lab and a reviewed sample.

```powershell
Get-Content evals/rubrics/answer.yaml
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
