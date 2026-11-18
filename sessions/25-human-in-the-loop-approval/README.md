# Session 25: Human-in-the-loop approval

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 24 is the starting point. This increment becomes part of the same application and is retained in session 26.

## Engineering objective

Approval is a durable state transition bound to exact arguments and the authorized approver. Editing an approved action invalidates approval. Licence allocation and final status must commit atomically.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Create pending access request; derive Sofia's manager from employee data; persist approve or reject decision; gate fulfilment on matching record; allocate licence in a transaction; audit all decisions.

## Reference implementation

- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)
- [src/copilot/api/app.py](../../src/copilot/api/app.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Approve as analyst instead of the named manager, replay a decision and race two claims for the final seat. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Request 4 end state plus unauthorized, replay and seat-capacity tests. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
