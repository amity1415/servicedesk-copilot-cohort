# Session 11: Retrieval and metadata filtering

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 10 is the starting point. This increment becomes part of the same application and is retained in session 12.

## Engineering objective

Authorization and relevance are distinct filters. Apply visibility constraints before retrieval and reranking. A newer date does not automatically supersede a policy without a version register.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Normalize OS and region values; prefilter audience and current status; exclude future effective dates; resolve versions using policy register; query as employee and analyst; add cross-role retrieval tests.

## Reference implementation

- [src/copilot/rag/pipeline.py](../../src/copilot/rag/pipeline.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Place the best lexical match in an IT-only runbook; verify it never enters employee candidates. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Tests for macOS versus Windows, current versus superseded policy and employee versus IT audience. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
