# Steps to follow — session 04

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

Run every command from `servicedesk-copilot/` with the environment activated. See [setup](../../docs/SETUP.md).

1. Verify session 03 is complete. Read your previous evidence and preserve its passing checks.
2. Read the session content and inspect the reference source before editing. State what result would falsify the proposed improvement.
3. Implement the model wrapper.
4. Configure endpoint and model outside source.
5. Mock 429 then success and verify bounded retry.
6. Classify a frozen ticket sample and compare to session 2.
7. Add CI with no API key.
8. Run the reference experiment:

```bash
python sessions/04-inference-parameters-and-the-first-llm-call/reference.py
```

9. Perform the deliberate failure exercise in the session README. Record the observed failure and the corrective change in `evidence.md`.
10. Validate `ADR with accuracy, measured latency, token usage and actual pricing; live result remains unmeasured until a provider is configured`. The reference experiment alone is insufficient for any live-system requirement.
11. Run regression checks:

```bash
python -m pytest --basetemp=.work/pytest
ruff check .
ruff format --check .
```

12. Complete the evidence template, review the diff and commit only this increment and its reviewed evidence. Do not commit `.env`, runtime databases or tokens.
13. Continue to session 05 without replacing the repository. Consult [integration steps](../../docs/INTEGRATION_STEPS.md) at module boundaries.
