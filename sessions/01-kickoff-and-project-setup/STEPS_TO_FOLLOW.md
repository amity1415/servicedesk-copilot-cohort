# Steps to follow — session 01

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify the trainer-provided starter and synthetic corpus is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Inspect the six requests and personas.
4. Install the editable package in a clean environment.
5. Load settings from environment without printing secrets.
6. Propagate request IDs into structured logs.
7. Run ticket counts and the scaffold tests.
8. Run the reference experiment:

```bash
python sessions/01-kickoff-and-project-setup/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Clean-install transcript, ticket counts and a decision record naming the three enterprise boundaries`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 02 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
