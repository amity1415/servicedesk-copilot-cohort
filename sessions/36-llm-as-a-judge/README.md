# Session 36: LLM-as-a-judge

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 35 is the starting point. This increment becomes part of the same application and is retained in session 37.

## Engineering objective

A judge is a measurement instrument with bias and uncertainty. Agreement on 30 examples has a wide interval. Freeze rubric, judge model and human labels before reporting agreement.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Define answer and ticket-summary rubrics; hand-label 30 examples without judge output; run judge with schema; compute agreement and confusion table; review disagreements; prefer exact checks where possible.

## Reference implementation

- [evals/rubrics/](../../evals/rubrics/)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Swap answer order or inject judge instructions into answer text and measure rubric stability. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Agreement report against 85 percent starting target, with model, rubric version and uncertainty. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
