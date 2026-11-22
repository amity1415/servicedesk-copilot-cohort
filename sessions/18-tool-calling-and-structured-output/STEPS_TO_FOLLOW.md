# Steps to follow — session 18

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 17 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Define typed TicketDraft.
4. Expose search, employee, assets, service status and ticket tools.
5. Validate all inputs.
6. Use the bounded live runner in the README to capture model tool choices on ten synthetic requests.
7. Validate the twenty drafts from the same run against `TicketDraft`.
8. Test one repair attempt.
9. Run the standalone and integrated HTTP verification commands.

```bash
python scripts/session.py run 18
python -m copilot tools-verify
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Confirm the tool-choice scores, the twenty validated drafts, and the invalid-output escalation test.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Push and verify the completion commits before starting Session 19. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
