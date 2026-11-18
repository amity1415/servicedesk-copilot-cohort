# Steps to follow — session 33

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 32 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Implement HR AgentExecutor with SDK.
4. Publish agent card.
5. Authenticate partner endpoint.
6. Submit joiner task.
7. Poll boundedly for completion.
8. Bind HR result to candidate ID.
9. Unblock IT plan only on success.
10. Run the reference experiment:

```bash
python sessions/33-agent-to-agent-with-the-hr-agent/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Request 5 completed through the real A2A transport plus unauthorized-call rejection`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to session 34 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
