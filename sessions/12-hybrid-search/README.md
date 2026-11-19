# Session 12: Hybrid search

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 11 is the starting point. This increment becomes part of the same application and is retained in session 13.

## Engineering objective

Sparse and dense rank scores have incompatible scales. Reciprocal rank fusion uses order rather than raw magnitude. Exact code matching and semantic paraphrases should both be represented in the evaluation set.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Add PostgreSQL full-text search; run the same authorization predicate in sparse and dense queries; fuse ranked lists; deduplicate chunk IDs; compare vector, keyword and hybrid on code and paraphrase subsets.

## Reference implementation

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)

Run `scripts/session.py run 12` for the standalone comparison or
`copilot rag-hybrid-compare` for the shared application comparison. Both
use PostgreSQL and report vector, keyword, and hybrid Recall@5 and
latency on the same draft questions. Use `COPILOT_RETRIEVAL_BACKEND=hybrid`
to enable the fused rankings in the API and documents server.

## Deliberate failure exercise

Add a rare code to an irrelevant article and inspect whether fusion overpromotes it. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Per-subset Recall@5, candidate IDs and a latency comparison. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
