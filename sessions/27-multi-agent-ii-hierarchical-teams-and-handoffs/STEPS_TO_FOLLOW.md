# Steps to follow — session 27

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 26 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Add onboarding lead and IT steps.
4. Use planner dependencies.
5. Create typed case summary with evidence and unresolved issues.
6. Hand unresolved work to analyst queue.
7. Preserve correlation ID.
8. Run the reference experiment:

```bash
python sessions/27-multi-agent-ii-hierarchical-teams-and-handoffs/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `IT onboarding trace and analyst queue case with full evidence summary`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 28 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
