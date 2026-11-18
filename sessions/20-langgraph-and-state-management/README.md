# Session 20: LangGraph and state management

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 19 is the starting point. This increment becomes part of the same application and is retained in session 21.

## Engineering objective

A checkpoint persists control state but does not grant identity. Bind authenticated identity to thread ownership. Resumption must survive a fresh process and preserve idempotency keys.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Compile typed graph state; separate decision and tool nodes; add conditional routing; initialize PostgreSQL saver; stream updates; kill and restart after a tool observation; resume same thread.

## Reference implementation

- [src/copilot/agents/graph.py](../../src/copilot/agents/graph.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Resume a thread under another employee and require denial before state is read. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Request 3 end state plus restart-and-resume transcript against PostgreSQL. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
