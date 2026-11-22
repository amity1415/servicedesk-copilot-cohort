# Session 20: LangGraph and state management

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 19 is the starting point. This increment becomes part of the same application and is retained in session 21.

## Engineering objective

Authorize each turn using the authenticated employee and the saved thread
owner. Persist decisions, observations, and the frozen ticket draft and key in
PostgreSQL so another application process can continue the same thread.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Compile typed graph state; separate decision and tool nodes; add conditional routing; initialize PostgreSQL saver; stream updates; kill and restart after a tool observation; resume same thread.

## Run the solution

Use the course Python environment with LangGraph and PostgreSQL support installed.
Start the seeded database, then run both source trees against it.

```powershell
docker compose up -d db
python scripts/session.py test 20 --variant starter --previous-only
python scripts/session.py test 20
python scripts/session.py run 20
python -m copilot graph-verify
```

Each runtime check creates its own PostgreSQL schema and starts a seeded
ticketing mock on loopback. It stops the first API process after the laptop
observation, resumes the thread in a fresh process, and reads back the ticket
created after the employee reports that the fixes failed. Another restart
checks the saved ticket and its replay. The checker removes its own schema
after collecting the results.

Set `COPILOT_POSTGRES_DIAGNOSTICS_ENABLED=true` when serving the application
to expose `POST /diagnostics/graph`. Send `thread_id`, `operation`, and a
`question` for `diagnose` or `create_ticket`. To continue a paused run, send
`operation` set to `resume` with the same thread and bearer token. Set `stream`
to `true` for SSE updates. The graph carries its decision count across restarts
and checks a 30-second elapsed budget during each active execution.

- [Typed LangGraph workflow](solution/src/copilot/agents/diagnostic_graph.py)
- [PostgreSQL checkpoint and ownership handling](solution/src/copilot/agents/checkpointed_diagnostics.py)
- [Streamed API route](solution/src/copilot/api/diagnostic_graph.py)
- [LangGraph persistence documentation](https://docs.langchain.com/oss/python/langgraph/add-memory#use-in-production)

## Deliberate failure exercise

After stopping the first process, resume the paused thread with another
employee's bearer token. Confirm a `403` response, then use the owner's token
to resume at the next node.

## Evidence and exit criteria

Request 3 end state plus restart-and-resume transcript against PostgreSQL. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
