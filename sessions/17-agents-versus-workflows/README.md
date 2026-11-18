# Session 17: Agents versus workflows

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 16 is the starting point. This increment becomes part of the same application and is retained in session 18.

## Engineering objective

A workflow has predetermined control flow; an agent delegates decisions to a model. Start with a fixed workflow to establish action semantics and failure handling before autonomy.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Start ticketing service; inspect seeded employee data; classify read, low-risk write and approval-required actions; implement password-reset ticket workflow through HTTP; save request ID.

## Reference implementation

- [src/copilot/tools/ticketing.py](../../src/copilot/tools/ticketing.py)
- [policies/actions.yaml](../../policies/actions.yaml)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Inject a ticket API 503 and determine which steps may safely retry. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Ticket visible in mock API and an action-risk inventory with default-deny handling. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
