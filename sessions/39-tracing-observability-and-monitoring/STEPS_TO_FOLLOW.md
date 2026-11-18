# Steps to follow — session 39

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 38 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Add OpenTelemetry spans around API, retrieval, tools and model.
4. Propagate context to MCP and HR.
5. Record cost and latency.
6. Display p95 and error rate.
7. Add UI feedback.
8. Run the reference experiment:

```bash
python sessions/39-tracing-observability-and-monitoring/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Cross-service trace, dashboard and measured knowledge-answer p95; cost has no fabricated default`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 40 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
