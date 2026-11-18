# Steps to follow — session 29

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 28 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Pin MCP v1 SDK.
4. Create stdio ticketing server.
5. Register typed create tool.
6. Inspect tool schema.
7. Connect actual SDK client.
8. Compare direct and MCP ticket outcomes.
9. Run the reference experiment:

```bash
python sessions/29-mcp-architecture-and-the-ticketing-server/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Actual initialize, list_tools and create-ticket transcript plus session 28 regressions`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 30 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
