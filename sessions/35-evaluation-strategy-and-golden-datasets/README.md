# Session 35: Evaluation strategy and golden datasets

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 34 is the starting point. This increment becomes part of the same application and is retained in session 36.

## Engineering objective

A task success label needs an observable end state and forbidden effects. Generated cases are drafts until reviewed. Keep task families separate across development and held-out sets.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Author 40 tasks from historical tickets; include user, expected calls and final state; add forbidden actions; validate schema; review difficulty and coverage; implement isolated environment reset.

## Reference implementation

- [evals/](../../evals/)
- [src/copilot/course/experiments.py](../../src/copilot/course/experiments.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Create a task whose expected result leaks the answer to the model and remove the leakage. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

40 reviewed tasks and reset proof for tickets, database and checkpoint state. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
