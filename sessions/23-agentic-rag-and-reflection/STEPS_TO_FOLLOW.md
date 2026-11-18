# Steps to follow — session 23

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 22 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Make search optional by intent.
4. Grade evidence sufficiency.
5. Combine policy and how-to context.
6. Generate a draft.
7. Verify support.
8. Retry once or abstain.
9. Retain both attempts for scoring.
10. Run the reference experiment:

```bash
python sessions/23-agentic-rag-and-reflection/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Two-source answer, caught unsupported draft and measured reflection overhead`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to session 24 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
