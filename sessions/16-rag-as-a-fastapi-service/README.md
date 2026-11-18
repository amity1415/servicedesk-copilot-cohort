# Session 16: RAG as a FastAPI service

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 15 is the starting point. This increment becomes part of the same application and is retained in session 17.

## Engineering objective

The service boundary adds authentication, validation, cancellation and error semantics. A completed-result SSE event is different from model token streaming. Keep identity server-derived.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Expose typed ask and health routes; add restricted ingestion; authenticate bearer tokens; add request IDs; test API without network; connect Streamlit and show citations; run two-turn requests.

## Reference implementation

- [src/copilot/api/app.py](../../src/copilot/api/app.py)
- [src/copilot/ui/chat.py](../../src/copilot/ui/chat.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Send an oversized request, a missing token and another user's thread ID; check errors disclose no private state. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Authenticated API tests and UI walkthrough of requests 1 and 2. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
