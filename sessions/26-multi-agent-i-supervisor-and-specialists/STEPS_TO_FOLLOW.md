# Steps to follow — session 26

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 25 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Define knowledge, diagnostics and fulfilment roles.
4. Route under supervisor.
5. Restrict diagnostics to reads.
6. Pass structured results.
7. Compare against the single-agent baseline on 15 frozen tasks.
8. Run the reference experiment:

```bash
python sessions/26-multi-agent-i-supervisor-and-specialists/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Requests 3 and 4 trajectories plus quality, token and latency comparison ADR`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 27 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
