# Steps to follow — session 05

[Actual cumulative Python build guide](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 04 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Select 20 Markdown documents.
4. Construct fixed chunks.
5. Implement lexical baseline and then vector baseline.
6. Create 20 reviewed questions from resolved tickets.
7. Run Mac VPN query and save retrieved IDs.
8. Run the reference experiment:

```bash
python sessions/05-why-rag-and-a-naive-baseline/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Frozen 20-question dataset, retrieved IDs and a clearly labelled baseline report`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 06 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
