# Steps to follow — session 20

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 19 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Compile typed graph state.
4. Separate decision and tool nodes.
5. Add conditional routing.
6. Initialize PostgreSQL saver.
7. Stream updates.
8. Kill and restart after a tool observation.
9. Resume same thread.
10. Run the reference experiment:

```bash
python sessions/20-langgraph-and-state-management/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Request 3 end state plus restart-and-resume transcript against PostgreSQL`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to session 21 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
