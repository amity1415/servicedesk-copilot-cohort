# Session 38: Regression testing in CI

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 37 is the starting point. This increment becomes part of the same application and is retained in session 39.

## Engineering objective

Offline contract tests and live quality evaluations answer different questions. Gate a frozen release against thresholds and preserve reports. Model, prompt, policy and index identity are release inputs.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Run lint, unit and API tests on pull requests; add service contract checks; gate smoke eval and red-team effects; schedule full evaluation; record release manifest; seed a bad-prompt mutation.

## Reference implementation

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
- [release/manifest.yaml](../../release/manifest.yaml)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Remove source-only instruction or approval gate and verify the corresponding test fails. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

CI workflow, explicit thresholds and demonstrated regression rejection. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
