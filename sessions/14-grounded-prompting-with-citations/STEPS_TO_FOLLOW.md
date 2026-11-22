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
11. Run [live acceptance](README.md#live-acceptance) with an approved model and
    spend. Review the Mac VPN and Windows VPN 809 excerpts against their cited
    sources. Verify that the unknown policy abstains without a provider call.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Complete the evidence template, review the diff, and run the completion
    command with the live transcript and human review.
14. Continue to session 15 after the Session 14 completion commit is recorded.
    Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
