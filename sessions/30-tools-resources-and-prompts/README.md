# Session 30: Tools, resources and prompts

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 29 is the starting point. This increment becomes part of the same application and is retained in session 31.

## Engineering objective

Tools perform operations, resources expose addressable content and prompts offer reusable message templates. Resource access needs the same visibility rules as search to avoid direct-URI bypass.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Create documents server; expose search tool; register article URI resource; register triage and incident prompts; exercise all primitives from client; preserve role filters.

## Reference implementation

- [src/copilot/mcp_servers/servers.py](../../src/copilot/mcp_servers/servers.py)

Run the adjacent `reference.py` from the project root. It executes the session experiment through the shared application code. Its JSON report declares whether it is an offline experiment or an integration preflight. A preflight does not satisfy the integration gate.

## Deliberate failure exercise

Read a restricted or malformed article URI directly and require denial. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Client transcripts for list_tools, read_resource and get_prompt with visibility tests. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
