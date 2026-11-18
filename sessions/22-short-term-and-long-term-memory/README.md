# Session 22: Short-term and long-term memory

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 21 is the starting point. This increment becomes part of the same application and is retained in session 23.

## Engineering objective

Conversation summaries are lossy and may preserve malicious instructions. Long-term memory needs a purpose, consent, ownership and deletion semantics. Memory must not become an authorization source.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Define allowed memory fields; summarize old turns within a token budget; store per-employee facts; read in a new thread; implement delete; verify no other employee can access the record.

## Reference implementation

- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Ask memory to remember that approval is unnecessary; reject it and retain server policy. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Budget check, cross-thread recall and deletion verification with remaining checkpoint caveat. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
