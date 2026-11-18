# Steps to follow — session 02

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 01 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Read historical tickets.
4. Group the split by short description.
5. Fit TF-IDF only on training rows.
6. Train category and priority logistic regressions.
7. Export labelled confusion matrices and inspect k-means terms.
8. Run the reference experiment:

```bash
python sessions/02-ml-basics-on-ticket-data/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Category and priority precision, recall, macro F1, support and confusion matrices; weakest-class error analysis`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 03 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
