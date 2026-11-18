# Session 10: Vector database and indexing

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 09 is the starting point. This increment becomes part of the same application and is retained in session 11.

## Engineering objective

HNSW is approximate nearest-neighbour search. Index parameters trade memory, build cost and recall. Replacing source chunks must be atomic so readers do not see a partially updated article.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Start pgvector; initialize chunk table and HNSW index; insert embeddings; perform top-k search; replace one changed document in a transaction; remove withdrawn source rows; benchmark warm and cold query latency.

## Reference implementation

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)
- [docker-compose.yml](../../docker-compose.yml)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Change one source and assert old chunk IDs disappear; compare approximate search with an exact scan. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Database search transcript, replacement and withdrawal checks, measured latency distribution. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
