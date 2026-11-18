# Session 09: Embeddings

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 08 is the starting point. This increment becomes part of the same application and is retained in session 10.

## Engineering objective

Embedding identity includes model revision, normalization and dimension. Cache by model identity and content; never mix vector spaces in one index. Exact codes require lexical evidence alongside semantic similarity.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Batch normalized sentence embeddings; persist a content-keyed cache; record model identity; rerun and compare cache size; compare two models on identical questions; inspect error-code misses.

## Reference implementation

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Change model name while preserving text and prove the cache cannot return the previous model's vectors. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Embedding cache and measured retrieval comparison ADR with dimension, latency and hardware. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
