# Steps to follow — session 09

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 08 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Batch normalized sentence embeddings.
4. Persist a content-keyed cache.
5. Record model identity.
6. Rerun and compare cache size.
7. Compare two models on identical questions.
8. Inspect error-code misses.
9. Run the reference experiment:

```bash
python sessions/09-embeddings/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Embedding cache and measured retrieval comparison ADR with dimension, latency and hardware`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 10 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
