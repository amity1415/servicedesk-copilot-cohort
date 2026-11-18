# Session 34: MCP versus A2A versus direct calls

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 33 is the starting point. This increment becomes part of the same application and is retained in session 35.

## Engineering objective

Choose a boundary by ownership and consumers before optimizing transport overhead. Benchmark identical work; warm-up, serialization and network distance otherwise dominate comparisons.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Implement service status by direct call, MCP and A2A; run repeated samples; record median and p95; snapshot canonical MCP schemas; fail a changed required argument.

## Reference implementation

- [src/copilot/mcp_servers/client.py](../../src/copilot/mcp_servers/client.py)
- [tests/](../../tests/)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Add a required field to a tool and verify contract comparison fails before deployment. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Measured transport ADR and version-controlled schema snapshot. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
