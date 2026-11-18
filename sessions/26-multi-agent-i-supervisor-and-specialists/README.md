# Session 26: Multi-agent I: supervisor and specialists

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 25 is the starting point. This increment becomes part of the same application and is retained in session 27.

## Engineering objective

Splitting agents can improve policy boundaries while increasing coordination cost. A specialist prompt is not a permission boundary. Enforce distinct tool allow-lists in the dispatcher.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Define knowledge, diagnostics and fulfilment roles; route under supervisor; restrict diagnostics to reads; pass structured results; compare against the single-agent baseline on 15 frozen tasks.

## Reference implementation

- [src/copilot/agents/react.py](../../src/copilot/agents/react.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Have diagnostics request create_ticket and prove the dispatcher refuses. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Requests 3 and 4 trajectories plus quality, token and latency comparison ADR. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
