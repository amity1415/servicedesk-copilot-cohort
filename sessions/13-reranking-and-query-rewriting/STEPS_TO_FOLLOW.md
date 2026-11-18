# Steps to follow — session 13

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 12 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Retrieve 30 authorized candidates.
4. Cross-encode question and passage pairs.
5. Return five.
6. Rewrite follow-ups with thread context.
7. Expand curated acronyms.
8. Compare gain against added latency.
9. Run the reference experiment:

```bash
python sessions/13-reranking-and-query-rewriting/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Two-turn retrieval tests, reranking delta and p95 latency measurement`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 14 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
