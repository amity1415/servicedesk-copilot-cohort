# Session 40: Containerization, readiness and final walkthrough

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 39 is the starting point. This increment becomes part of the same application and is retained in the final release review.

## Engineering objective

Production readiness is evidence, not a label. Pin images and dependencies, run as non-root, verify health and termination, and demonstrate recovery from a clean environment.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Build images; scan dependencies and images; configure secrets and resource limits; start Compose; run all six requests with traces; rerun evaluation and red-team checks; record remaining risks.

## Reference implementation

- [Dockerfile](../../Dockerfile)
- [docker-compose.yml](../../docker-compose.yml)
- [docs/INTEGRATION_STEPS.md](../../docs/INTEGRATION_STEPS.md)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Restart during pending approval and demonstrate safe recovery with one final side effect. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Clean-machine demo, scan outputs and measured release targets before tagging v1.0. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
