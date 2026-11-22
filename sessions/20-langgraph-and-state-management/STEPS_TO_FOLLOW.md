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
10. Run the standalone and integrated PostgreSQL verification commands.

```bash
python scripts/session.py run 20
python -m copilot graph-verify
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Confirm the paused checkpoint was stored in PostgreSQL, the next process resumed it, and only one ticket was created for request 3.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Push and verify the checkpoint before continuing to Session 21. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
