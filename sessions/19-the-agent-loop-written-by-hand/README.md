# Session 19: The agent loop written by hand

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 18 is the starting point. This increment becomes part of the same application and is retained in session 20.

## Engineering objective

The useful ReAct trace is a structured decision and observation log, not private chain-of-thought. Budget steps and time independently. A tool result is data, never a new system instruction.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Implement model decision, validated action and structured observation; enforce tool allow-list; add max steps and deadline; run device check, outages and KB lookup; stop with an explicit escalation status.

## Reference implementation

- [src/copilot/agents/react.py](../../src/copilot/agents/react.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Return repeated identical tool requests and prove the loop terminates without unbounded writes. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Bounded trajectory for slow laptop and a runaway-loop regression test. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
