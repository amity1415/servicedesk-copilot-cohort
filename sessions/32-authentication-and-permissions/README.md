# Session 32: Authentication and permissions

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 31 is the starting point. This increment becomes part of the same application and is retained in session 33.

## Engineering objective

Authentication establishes the principal; authorization constrains each operation and object. A bearer token must never allow the caller to choose a different actor through tool arguments.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Validate token server-side; map identity to employee role; apply tool and row permissions; audit allowed and denied calls; test employee, analyst and admin; reject unknown tokens.

## Reference implementation

- [src/copilot/api/app.py](../../src/copilot/api/app.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Replay an employee token with another employee ID and verify no cross-user device or ticket data returns. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Role-by-tool permission matrix, denied-call audit and ownership tests. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
