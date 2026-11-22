# Steps to follow — session 15

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 14 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Review the 100-case candidate, including ten unanswerables. Preserve case
   IDs, provenance and the development and heldout splits.
4. Verify the expected source IDs, platform and verbatim reference excerpts.
5. Calculate document Recall@5.
6. Calculate context precision from exact evidence spans and score answer
   faithfulness and relevance using the extractive rubric.
7. Compare the Session 5 fixture and the current local pipeline. Inspect
   baseline corpus coverage before interpreting the paired intervals.
8. Tag ten observed failures by cause.
9. Run the reference experiment:

```bash
python sessions/15-rag-evaluation/reference.py
```

10. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
11. Verify that both split reports contain all four metrics, a judge
    configuration, paired uncertainty and ten attributed failures.
12. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

13. Save the reviewed dataset and run the [completion gate](README.md#evidence-and-exit-criteria).
    Push the verified session commits and confirm their remote location.
14. Continue to session 16 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
