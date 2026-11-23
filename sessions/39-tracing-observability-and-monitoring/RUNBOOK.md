# 39 terminal and coding runbook

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
& $py sessions/39-tracing-observability-and-monitoring/reference.py
Get-Content reports/sessions/39.json
& $py -m pytest tests/test_working_project.py::test_mask_hides_known_identifiers
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

- [telemetry ](../../telemetry/)
- [src/copilot/ui/chat.py ](../../src/copilot/ui/chat.py)
- [src/copilot/telemetry.py ](../../src/copilot/telemetry.py)

Work through these changes in order:

1. Add OpenTelemetry spans around API, retrieval, tools and model.
2. Propagate context to MCP and HR.
3. Record cost and latency.
4. Display p95 and error rate.
5. Add UI feedback.

## 3. Check the lab result

Start the host API with the instructor's collector endpoint as shown below. Find a trace in the collector and record which spans share its trace ID.

Reuse [Terminal A's API setup](../../docs/BEGINNER_RUNBOOK.md#2-run-the-local-web-app).
Before starting the API, install the telemetry extra if needed and enter the
collector URL supplied for your class:

```powershell
python -m pip install -e ".[telemetry]"
$env:OTEL_EXPORTER_OTLP_ENDPOINT = Read-Host 'Collector OTLP endpoint'
python -m copilot serve --host 127.0.0.1 --port 8082
```

In a second terminal, run the Mac request from the overall runbook, then query
metrics with the synthetic operator token:

```powershell
Invoke-RestMethod http://127.0.0.1:8082/metrics -Headers @{ Authorization = 'Bearer analyst-dev' }
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
