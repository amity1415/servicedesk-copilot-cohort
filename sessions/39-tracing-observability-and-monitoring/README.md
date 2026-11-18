# Session 39: Tracing, observability and monitoring

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 38 is the starting point. This increment becomes part of the same application and is retained in session 40.

## Engineering objective

A useful trace connects services through propagated context. Tokens and cost require provider usage and a price version; missing values must remain unknown. Mask PII before export.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Add OpenTelemetry spans around API, retrieval, tools and model; propagate context to MCP and HR; record cost and latency; display p95 and error rate; add UI feedback.

## Reference implementation

- [telemetry/](../../telemetry/)
- [src/copilot/ui/chat.py](../../src/copilot/ui/chat.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Send email and employee IDs through a failure path and inspect exported attributes for leakage. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Cross-service trace, dashboard and measured knowledge-answer p95; cost has no fabricated default. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
