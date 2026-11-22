# Session 17: Agents versus workflows

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 16 is the starting point. This increment becomes part of the same application and is retained in session 18.

## Engineering objective

A workflow has predetermined control flow; an agent delegates decisions to a model. Start with a fixed workflow to establish action semantics and failure handling before autonomy.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Start ticketing service; inspect seeded employee data; classify read, low-risk write and approval-required actions; implement password-reset ticket workflow through HTTP; save request ID.

## Run the solution

With the Python environment activated, start the local services from the repo root.

```powershell
docker compose up -d db ticketing
docker compose ps db ticketing
python scripts/session.py test 17 --variant starter --previous-only
python scripts/session.py test 17
python scripts/session.py run 17
python -m copilot workflow-verify
```

The two runtime commands require healthy Compose services. Each starts a new
copilot API on loopback, verifies the directory seed, and creates one synthetic
ticket in the running mock. The workflow uses the authenticated employee ID.
Repeating the request in the same thread returns the original ticket. The
report includes the ticket and both copilot request IDs.

The exported learner project includes the Compose configuration and mock
service. Use the [implementation guide](../IMPLEMENTATION_GUIDE.md) to create
the standalone environment and start its services from the export directory.

- [Password-reset workflow](solution/src/copilot/tools/password_reset.py)
- [Ticketing HTTP adapter](solution/src/copilot/tools/ticketing.py)
- [Action-risk policy](solution/policies/actions.yaml)

## Deliberate failure exercise

The verifier runs a separate copy of the mock which returns `503` to ticket
requests. Check that the workflow reports the outage and leaves the ticket
count unchanged. Clear the isolated fault and retry in the same thread. The
first successful write produces one ticket.

## Evidence and exit criteria

Read the ticket back through the mock API, record its request ID, and verify
that missing actions are denied before a write. Complete
[STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md) and retain your evidence for Session 18.
