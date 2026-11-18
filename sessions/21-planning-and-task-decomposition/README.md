# Session 21: Planning and task decomposition

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 20 is the starting point. This increment becomes part of the same application and is retained in session 22.

## Engineering objective

A plan is a dependency graph with explicit ownership and completion evidence. Independent steps can run concurrently only when their side effects do not conflict. Failed prerequisites block dependants.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Represent account, laptop, licences and access steps with dependencies; validate acyclicity; execute ready steps; record failures and replan within budget; show plan state in UI.

## Reference implementation

- [src/copilot/agents/planning.py](../../src/copilot/agents/planning.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Fail account creation and prove access provisioning does not run. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Stored plan, dependency-order tests and a failed-step replanning trace. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
