# Session 33: Agent-to-Agent with the HR agent

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 32 is the starting point. This increment becomes part of the same application and is retained in session 34.

## Engineering objective

A2A delegates a task to another owner, whereas MCP exposes tools to the caller's orchestration. Validate the partner card and returned task state; a submitted task is not completed work.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Implement HR AgentExecutor with SDK; publish agent card; authenticate partner endpoint; submit joiner task; poll boundedly for completion; bind HR result to candidate ID; unblock IT plan only on success.

## Reference implementation

- [services/hr_agent/](../../services/hr_agent/)
- [src/copilot/agents/planning.py](../../src/copilot/agents/planning.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Return a failed or mismatched-candidate HR task and prove IT prerequisites remain blocked. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Request 5 completed through the real A2A transport plus unauthorized-call rejection. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
