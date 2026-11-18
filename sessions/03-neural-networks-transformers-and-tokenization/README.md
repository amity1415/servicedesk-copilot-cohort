# Session 03: Neural networks, transformers and tokenization

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 02 is the starting point. This increment becomes part of the same application and is retained in session 04.

## Engineering objective

An MLP over TF-IDF is a useful nonlinear comparator but is not a transformer. Attention contextualizes tokens; token boundaries do not preserve error-code identity. Token counts and prices must be tied to the deployed model.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Reuse the session 2 split; add the MLP without changing features; compare fit time and macro F1; tokenize tickets and articles with an explicitly named encoding; inspect VPN error codes and KB identifiers; price input and output separately.

## Reference implementation

- [src/copilot/ml/train.py](../../src/copilot/ml/train.py)
- [src/copilot/course/experiments.py](../../src/copilot/course/experiments.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Change the random seed and compare stability; explain why better training accuracy can worsen the grouped holdout. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Comparison report plus token distribution and a cost estimate with explicit model, encoding, prices and output-length assumption. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
