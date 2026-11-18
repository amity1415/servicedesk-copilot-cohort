# Steps to follow — session 40

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 39 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Build images.
4. Scan dependencies and images.
5. Configure secrets and resource limits.
6. Start Compose.
7. Run all six requests with traces.
8. Rerun evaluation and red-team checks.
9. Record remaining risks.
10. Run the reference experiment:

```bash
python sessions/40-containerization-readiness-and-final-walkthrough/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Clean-machine demo, scan outputs and measured release targets before tagging v1.0`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to the final release review without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
