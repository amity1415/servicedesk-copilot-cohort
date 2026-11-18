# Steps to follow — session 12

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 11 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Add PostgreSQL full-text search.
4. Run the same authorization predicate in sparse and dense queries.
5. Fuse ranked lists.
6. Deduplicate chunk IDs.
7. Compare vector, keyword and hybrid on code and paraphrase subsets.
8. Run the reference experiment:

```bash
python sessions/12-hybrid-search/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `Per-subset Recall@5, candidate IDs and a latency comparison`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 13 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
