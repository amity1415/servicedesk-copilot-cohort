# Session 01: Kickoff and project setup

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

The trainer-provided starter and synthetic corpus is the starting point. This increment becomes part of the same application and is retained in session 02.

## Engineering objective

Configuration is a dependency boundary. Reproducibility includes data, identity, secrets and the command used to measure behaviour. Define acceptance outcomes before choosing an agent framework.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Inspect the six requests and personas; install the editable package in a clean environment; load settings from environment without printing secrets; propagate request IDs into structured logs; run ticket counts and the scaffold tests.

## Reference implementation

- [src/copilot/config.py](../../src/copilot/config.py)
- [src/copilot/logging_setup.py](../../src/copilot/logging_setup.py)
- [src/copilot/tickets.py](../../src/copilot/tickets.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Set an invalid timeout and verify startup fails; introduce a fake secret in an untracked scratch file and explain how the commit hook would catch it. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Clean-install transcript, ticket counts and a decision record naming the three enterprise boundaries. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
