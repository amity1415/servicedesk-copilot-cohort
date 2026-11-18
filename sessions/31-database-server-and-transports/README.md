# Session 31: Database server and transports

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 30 is the starting point. This increment becomes part of the same application and is retained in session 32.

## Engineering objective

A read-only database role is a stronger boundary than telling an agent not to write. Streamable HTTP adds connection, session and authentication semantics. Arbitrary SQL is not a tool.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Expose fixed parameterized employee, assets, licence and service queries; enforce row limits; create database SELECT-only role; move servers to HTTP; run real client contract tests.

## Reference implementation

- [src/copilot/mcp_servers/servers.py](../../src/copilot/mcp_servers/servers.py)
- [src/copilot/mcp_servers/client.py](../../src/copilot/mcp_servers/client.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Attempt INSERT with the server database credentials and require PostgreSQL denial. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Three-server HTTP transcripts and database-role write denial. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
