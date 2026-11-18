# Steps to follow — session 16

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 15 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Expose typed ask and health routes.
4. Add restricted ingestion.
5. Authenticate bearer tokens.
6. Add request IDs.
7. Test API without network.
8. Connect Streamlit and show citations.
9. Run two-turn requests.
10. Run the reference experiment:

```bash
python sessions/16-rag-as-a-fastapi-service/reference.py
```

11. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
12. Validate `Authenticated API tests and UI walkthrough of requests 1 and 2`. The reference experiment alone is insufficient for any live-system requirement.
13. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

14. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
15. Continue to session 17 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
