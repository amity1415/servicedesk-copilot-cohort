# Steps to follow — session 35

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 34 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Author 40 tasks from historical tickets.
4. Include user, expected calls and final state.
5. Add forbidden actions.
6. Validate schema.
7. Review difficulty and coverage.
8. Implement isolated environment reset.
9. Run the reference experiment:

```bash
python sessions/35-evaluation-strategy-and-golden-datasets/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `40 reviewed tasks and reset proof for tickets, database and checkpoint state`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 36 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
