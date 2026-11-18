# Steps to follow — session 22

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 21 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Define allowed memory fields.
4. Summarize old turns within a token budget.
5. Store per-employee facts.
6. Read in a new thread.
7. Implement delete.
8. Verify no other employee can access the record.
9. Run the reference experiment:

```bash
python sessions/22-short-term-and-long-term-memory/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Budget check, cross-thread recall and deletion verification with remaining checkpoint caveat`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 23 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
