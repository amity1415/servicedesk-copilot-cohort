# Session 05: Why RAG and a naive baseline

[Actual cumulative Python build guide](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 04 is the starting point. This increment becomes part of the same application and is retained in session 06.

## Engineering objective

Retrieval supplies private evidence but cannot make an answer truthful by itself. Establish retrieval and answer baselines separately. Keep an invented bare-model answer as an observed failure only if a real call produces it.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Select 20 Markdown documents; construct fixed chunks; implement lexical baseline and then vector baseline; create 20 reviewed questions from resolved tickets; run Mac VPN query and save retrieved IDs.

## Reference implementation

- [src/copilot/rag/pipeline.py](../../src/copilot/rag/pipeline.py)

Run the adjacent `reference.py` from the project root. It executes this session's own cumulative solution source. The matching feature also runs through the main application. This RAG batch is validated with real local retrieval/semantic inference; live LLM quality remains a separate gate.

## Deliberate failure exercise

Ask an unanswerable company-policy question and compare unsupported confidence with explicit abstention. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Frozen 20-question dataset, retrieved IDs and a clearly labelled baseline report. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
