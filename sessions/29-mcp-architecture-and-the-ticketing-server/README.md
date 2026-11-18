# Session 29: MCP architecture and the ticketing server

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 28 is the starting point. This increment becomes part of the same application and is retained in session 30.

## Engineering objective

MCP defines a host, client and server contract for tool access. Stdio inherits a process trust boundary. Preserve existing idempotency and authorization when moving a tool out of process.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Pin MCP v1 SDK; create stdio ticketing server; register typed create tool; inspect tool schema; connect actual SDK client; compare direct and MCP ticket outcomes.

## Reference implementation

- [src/copilot/mcp_servers/servers.py](../../src/copilot/mcp_servers/servers.py)
- [src/copilot/mcp_servers/client.py](../../src/copilot/mcp_servers/client.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Print debug output to stdout and observe protocol corruption; move logs to stderr. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Actual initialize, list_tools and create-ticket transcript plus session 28 regressions. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
