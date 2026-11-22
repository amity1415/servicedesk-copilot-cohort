# Steps to follow — session 19

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 18 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Implement model decision, validated action and structured observation.
4. Enforce tool allow-list.
5. Add max steps and deadline.
6. Run device check, outages and KB lookup.
7. Stop with an explicit escalation status.
8. Run the standalone solution and integrated HTTP check.

```bash
python scripts/session.py run 19
python -m copilot react-verify
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Run the bounded live evaluation from the README. Compare the observed device, incidents and article with the two local runs.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Push the verified checkpoint and confirm CI before continuing to Session 20. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
