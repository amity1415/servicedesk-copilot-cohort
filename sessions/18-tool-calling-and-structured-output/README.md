# Session 18: Tool calling and structured output

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 17 is the starting point. This increment becomes part of the same application and is retained in session 19.

## Engineering objective

Validate tool arguments against the declared schema. Use the authenticated
employee and risk policy to authorize actions. Repair a malformed draft once,
then escalate for analyst review if it still fails validation.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Define typed TicketDraft; expose search, employee, assets, service status and ticket tools; validate all inputs; capture model tool choices on ten requests; produce 20 ticket drafts; test one repair attempt.

## Run the solution

From the repository root with the Python environment activated, run the local checks.

```powershell
python scripts/session.py test 18 --variant starter --previous-only
python scripts/session.py test 18
python scripts/session.py run 18
python -m copilot tools-verify
```

Each verification starts an authenticated copilot API and a fresh seeded
ticketing mock on loopback. `GET /tools` lists schemas for the caller's role.
Send validated arguments as JSON to `POST /tools/{name}` and include an
`Idempotency-Key` header for `create_ticket`. Ticket updates require an
analyst or admin. These checks use local retrieval and report zero paid calls.

- [Tool definitions and dispatch](solution/src/copilot/tools/service_desk.py)
- [Ticket schema and HTTP adapter](solution/src/copilot/tools/ticketing.py)
- [Model tool selection and draft repair](solution/src/copilot/llm/service_desk.py)

## Live evaluation

The live runner uses the configured OpenAI key and GPT-6 Luna with a spending
cap of $0.08. It evaluates the ten tool labels and twenty draft prompts in the
frozen synthetic fixture. [Evaluation fixture](../../evals/session18_tools.json)

```powershell
python scripts/verify_tools_live.py --max-spend-usd 0.08 --out reports/session18-live/run.json
python scripts/complete_session.py 18 --tool-evaluation reports/session18-live/run.json
```

## Deliberate failure exercise

Supply an otherwise valid draft that names another employee's asset. Verify
that the request returns `403` and the ticket count stays unchanged. Use the
local fixture to exercise both successful repair and analyst escalation.

## Evidence and exit criteria

Tool-choice sample, 20 validated drafts and invalid-output escalation test. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
