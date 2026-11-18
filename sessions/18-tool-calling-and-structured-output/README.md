# Session 18: Tool calling and structured output

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 17 is the starting point. This increment becomes part of the same application and is retained in session 19.

## Engineering objective

Tool schemas constrain shape, not authority or factual correctness. Validate tool arguments and apply identity outside model-generated fields. Repair malformed drafts once and escalate after that.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Define typed TicketDraft; expose search, employee, assets, service status and ticket tools; validate all inputs; capture model tool choices on ten requests; produce 20 ticket drafts; test one repair attempt.

## Reference implementation

- [src/copilot/tools/ticketing.py](../../src/copilot/tools/ticketing.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Generate a schema-valid draft for a different employee; prove authorization rejects it despite valid JSON. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Tool-choice sample, 20 validated drafts and invalid-output escalation test. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
