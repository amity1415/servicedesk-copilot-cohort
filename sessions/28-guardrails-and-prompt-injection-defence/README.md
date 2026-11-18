# Session 28: Guardrails and prompt injection defence

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 27 is the starting point. This increment becomes part of the same application and is retained in session 29.

## Engineering objective

Detection patterns cannot prove injection resistance. Constrain effects with server-side role and ownership checks, source-data boundaries and approval records. Evaluate state changes as well as refusal text.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Add attack detection and output checks; mask logs; restrict tool dispatch per role; author 25 attacks across tickets, documents and tools; reset state before each; verify forbidden effects absent.

## Reference implementation

- [src/copilot/guardrails/checks.py](../../src/copilot/guardrails/checks.py)
- [evals/redteam/](../../evals/redteam/)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Rephrase an attack without known keywords and verify authorization still prevents the write. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

25-case report with state assertions, zero forbidden effects and explicit detector limitations. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
