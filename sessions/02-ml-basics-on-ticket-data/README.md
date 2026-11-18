# Session 02: ML basics on ticket data

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 01 is the starting point. This increment becomes part of the same application and is retained in session 03.

## Engineering objective

Synthetic ticket templates create leakage. Split by template family before fitting TF-IDF, keep resolution and linked KB out of features, and compare macro F1 with accuracy. Clustering reveals vocabulary structure rather than ground-truth intent.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Read historical tickets; group the split by short description; fit TF-IDF only on training rows; train category and priority logistic regressions; export labelled confusion matrices and inspect k-means terms.

## Reference implementation

- [src/copilot/ml/train.py](../../src/copilot/ml/train.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Compare a random split with grouped holdout; inspect ten errors in the weakest class before assigning a cause. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Category and priority precision, recall, macro F1, support and confusion matrices; weakest-class error analysis. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
