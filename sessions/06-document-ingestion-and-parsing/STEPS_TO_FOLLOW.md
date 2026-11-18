# Steps to follow — session 06

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 05 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Load Markdown frontmatter and HTML metadata.
4. Extract PDF layout text and DOCX tables.
5. Normalize one Document schema.
6. Write a content-hash manifest.
7. Rerun ingestion.
8. Review skipped-file log and SLA rows.
9. Run the reference experiment:

```bash
python sessions/06-document-ingestion-and-parsing/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Full-corpus parse count, zero unexpected skips, second-run changed count zero and inspected SLA text`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 07 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
