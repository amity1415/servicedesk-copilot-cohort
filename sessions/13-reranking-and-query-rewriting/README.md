# Session 13: Reranking and query rewriting

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 12 is the starting point. This increment becomes part of the same application and is retained in session 14.

## Engineering objective

Rewriting can accidentally change intent or invent facts. Preserve explicit IDs and use only authorized conversation history. Reranking improves candidate order but cannot recover an absent document.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Retrieve 30 authorized candidates; cross-encode question and passage pairs; return five; rewrite follow-ups with thread context; expand curated acronyms; compare gain against added latency.

## Reference implementation

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Use two simultaneous users discussing different VPN errors; prove histories cannot cross thread ownership. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Two-turn retrieval tests, reranking delta and p95 latency measurement. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
