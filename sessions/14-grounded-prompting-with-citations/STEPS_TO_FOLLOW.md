# Steps to follow — session 14

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 13 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Version the grounded prompt.
4. Delimit source data.
5. Require answer and citation JSON.
6. Validate each citation against retrieved IDs.
7. Reject malformed or unsupported output.
8. Test Mac VPN, Windows 809 and unknown policy.
9. Run the reference experiment:

```bash
python sessions/14-grounded-prompting-with-citations/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Validate `Requests 1 and 2 transcripts plus citation-membership tests and human entailment review`. The reference experiment alone is insufficient for any live-system requirement.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
14. Continue to session 15 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
