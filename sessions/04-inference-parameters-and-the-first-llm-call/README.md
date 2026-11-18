# Session 04: Inference parameters and the first LLM call

[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 03 is the starting point. This increment becomes part of the same application and is retained in session 05.

## Engineering objective

Temperature zero reduces sampling variation but is not a reproducibility guarantee. Retry only transient failures; an authorization failure is not transient. The network client owns deadlines and token accounting.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Implement the model wrapper; configure endpoint and model outside source; mock 429 then success and verify bounded retry; classify a frozen ticket sample and compare to session 2; add CI with no API key.

## Reference implementation

- [src/copilot/llm/client.py](../../src/copilot/llm/client.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Return a permanent 401 and prove only one request is made; compare output schemas rather than eyeballing prose. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

ADR with accuracy, measured latency, token usage and actual pricing; live result remains unmeasured until a provider is configured. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
