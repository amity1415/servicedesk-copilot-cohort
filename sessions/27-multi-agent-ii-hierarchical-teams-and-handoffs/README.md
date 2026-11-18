# Session 27: Multi-agent II: hierarchical teams and handoffs

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 26 is the starting point. This increment becomes part of the same application and is retained in session 28.

## Engineering objective

Handoffs transfer responsibility and evidence, not arbitrary executable instructions. Hierarchy adds value when subteams have distinct tools, owners or failure domains.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Add onboarding lead and IT steps; use planner dependencies; create typed case summary with evidence and unresolved issues; hand unresolved work to analyst queue; preserve correlation ID.

## Reference implementation

- [src/copilot/agents/planning.py](../../src/copilot/agents/planning.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Drop a prerequisite from a handoff and verify the recipient asks for evidence rather than inventing completion. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

IT onboarding trace and analyst queue case with full evidence summary. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
