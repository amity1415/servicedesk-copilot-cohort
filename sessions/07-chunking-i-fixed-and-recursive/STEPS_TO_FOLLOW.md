# Steps to follow — session 07

[Actual cumulative Python build guide](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 06 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Implement fixed character windows.
4. Implement paragraph and numbered-step boundaries.
5. Expose strategy in experiment configuration.
6. Inspect long articles.
7. Add boundary, overlap and invalid-parameter tests.
8. Run the reference experiment:

```bash
python sessions/07-chunking-i-fixed-and-recursive/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Chunk inspection output with sizes, IDs and step-boundary checks`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 08 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
