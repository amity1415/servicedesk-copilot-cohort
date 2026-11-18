# Steps to follow — session 24

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 23 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Return typed tool errors.
4. Add bounded backoff and deadlines.
5. Persist ticket idempotency key in state.
6. Apply step and cost budgets.
7. Enable ticketing faults.
8. Inspect final state.
9. Run the reference experiment:

```bash
python sessions/24-self-correction-error-handling-and-retries/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Fault matrix with success or clean escalation and duplicate count zero`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 25 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
