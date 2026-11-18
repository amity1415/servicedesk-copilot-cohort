# Steps to follow — session 11

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 10 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Normalize OS and region values.
4. Prefilter audience and current status.
5. Exclude future effective dates.
6. Resolve versions using policy register.
7. Query as employee and analyst.
8. Add cross-role retrieval tests.
9. Run the reference experiment:

```bash
python sessions/11-retrieval-and-metadata-filtering/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Tests for macOS versus Windows, current versus superseded policy and employee versus IT audience`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 12 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
