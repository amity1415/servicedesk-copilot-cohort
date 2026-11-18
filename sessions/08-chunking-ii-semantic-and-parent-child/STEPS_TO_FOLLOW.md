# Steps to follow — session 08

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 07 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Embed paragraph units.
4. Split on adjacent-similarity changes.
5. Retain parent sections for child hits.
6. Run fixed, recursive, semantic and parent-child variants.
7. Compute document-level Recall@5 with duplicate parents collapsed.
8. Run the reference experiment:

```bash
python sessions/08-chunking-ii-semantic-and-parent-child/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Four-strategy scorecard on the same 20 reviewed questions, with context token counts`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 09 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
