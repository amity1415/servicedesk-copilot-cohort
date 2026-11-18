# Steps to follow — session 38

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 37 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Run lint, unit and API tests on pull requests.
4. Add service contract checks.
5. Gate smoke eval and red-team effects.
6. Schedule full evaluation.
7. Record release manifest.
8. Seed a bad-prompt mutation.
9. Run the reference experiment:

```bash
python sessions/38-regression-testing-in-ci/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `CI workflow, explicit thresholds and demonstrated regression rejection`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 39 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
