# Session 15: RAG evaluation

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 14 is the starting point. This increment becomes part of the same application and is retained in session 16.

## Engineering objective

Recall needs relevance labels; context precision needs labelled retrieved units; faithfulness needs claim support; relevance needs an answer rubric. Do not relabel lexical overlap as faithfulness. Freeze splits before tuning.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Expand to 100 reviewed questions including ten unanswerables; record expected source IDs and reference answers; calculate Recall@5; evaluate precision and answer metrics; compare saved baseline; tag ten failures by cause.

## Reference implementation

- [evals/](../../evals/)
- [src/copilot/course/experiments.py](../../src/copilot/course/experiments.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Tune on one subset and report held-out performance; bootstrap uncertainty when comparing small gains. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Four-metric report with judge configuration, baseline, uncertainty and ten attributed failures. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
