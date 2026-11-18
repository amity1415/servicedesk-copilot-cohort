# Steps to follow — session 03

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 02 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Reuse the session 2 split.
4. Add the MLP without changing features.
5. Compare fit time and macro F1.
6. Tokenize tickets and articles with an explicitly named encoding.
7. Inspect VPN error codes and KB identifiers.
8. Price input and output separately.
9. Run the reference experiment:

```bash
python sessions/03-neural-networks-transformers-and-tokenization/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Comparison report plus token distribution and a cost estimate with explicit model, encoding, prices and output-length assumption`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 04 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
