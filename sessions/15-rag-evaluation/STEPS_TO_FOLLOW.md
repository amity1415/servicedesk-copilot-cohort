# Steps to follow — session 15

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 14 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Expand to 100 reviewed questions including ten unanswerables.
4. Record expected source IDs and reference answers.
5. Calculate Recall@5.
6. Evaluate precision and answer metrics.
7. Compare saved baseline.
8. Tag ten failures by cause.
9. Run the reference experiment:

```bash
python sessions/15-rag-evaluation/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Four-metric report with judge configuration, baseline, uncertainty and ten attributed failures`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 16 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
