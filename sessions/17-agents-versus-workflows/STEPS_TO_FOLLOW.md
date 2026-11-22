# Steps to follow — session 17

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 16 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Start PostgreSQL and ticketing with `docker compose up -d db ticketing`.
4. Confirm the services are healthy and inspect the seeded employee and device tables.
5. Classify read, low-risk write and approval-required actions.
6. Implement password-reset ticket workflow through HTTP.
7. Save request ID.
8. Run the standalone and integrated workflow checks.

```bash
python scripts/session.py run 17
python -m copilot workflow-verify
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Confirm a ticket is visible in the mock API and every workflow action has a risk tier. Verify that an unlisted action is denied.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Push the completion commits, verify CI on GitHub and then continue to Session 18. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
