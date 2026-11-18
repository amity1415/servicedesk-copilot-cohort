# Steps to follow — session 18

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 17 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Define typed TicketDraft.
4. Expose search, employee, assets, service status and ticket tools.
5. Validate all inputs.
6. Capture model tool choices on ten requests.
7. Produce 20 ticket drafts.
8. Test one repair attempt.
9. Run the reference experiment:

```bash
python sessions/18-tool-calling-and-structured-output/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Tool-choice sample, 20 validated drafts and invalid-output escalation test`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 19 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
