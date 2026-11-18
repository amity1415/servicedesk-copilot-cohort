# Session 23: Agentic RAG and reflection

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 22 is the starting point. This increment becomes part of the same application and is retained in session 24.

## Engineering objective

Reflection adds another fallible model call. Grade retrieved evidence, retry with a bounded rewrite and validate supported claims. Measure the gain and the extra cost rather than assuming reflection helps.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Make search optional by intent; grade evidence sufficiency; combine policy and how-to context; generate a draft; verify support; retry once or abstain; retain both attempts for scoring.

## Reference implementation

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)
- [src/copilot/agents/react.py](../../src/copilot/agents/react.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Return an authoritative-looking document with no relevant evidence and require abstention. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Two-source answer, caught unsupported draft and measured reflection overhead. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
