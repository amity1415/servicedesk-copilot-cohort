# 40 terminal and coding runbook

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
& $py sessions/40-containerization-readiness-and-final-walkthrough/reference.py
Get-Content reports/sessions/40.json
& $py -m pytest tests/test_cumulative_flow.py
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

- [Dockerfile ](../../Dockerfile)
- [docker-compose.yml ](../../docker-compose.yml)
- [docker-compose.app.yml ](../../docker-compose.app.yml)

Work through these changes in order:

1. Build images.
2. Scan dependencies and images.
3. Configure secrets and resource limits.
4. Start Compose.
5. Run all six requests with traces.
6. Rerun evaluation and red-team checks.

## 3. Check the lab result

Follow the full-stack instructions and run all six scenarios. Run the class-approved scanners and retain outputs before assessing release readiness.

The [full-stack walkthrough](../../docs/BEGINNER_RUNBOOK.md#4-switch-to-the-full-mcp-and-hr-stack)
has the exact Compose startup, six terminal requests, and operator metrics
commands. While it is running, collect the container status and image list:

```powershell
docker compose -f docker-compose.yml -f docker-compose.app.yml ps
docker compose -f docker-compose.yml -f docker-compose.app.yml images
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
