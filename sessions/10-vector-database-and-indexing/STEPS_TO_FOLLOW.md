# Steps to follow — session 10

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 09 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Start pgvector.
4. Initialize chunk table and HNSW index.
5. Insert embeddings.
6. Perform top-k search.
7. Replace one changed document in a transaction.
8. Remove withdrawn source rows.
9. Benchmark warm and cold query latency.
10. Run the reference experiment:

```bash
python sessions/10-vector-database-and-indexing/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Database search transcript, replacement and withdrawal checks, measured latency distribution`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to session 11 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
