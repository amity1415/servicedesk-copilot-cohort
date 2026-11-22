# Session 16: RAG as a FastAPI service

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 15 is the starting point. This increment becomes part of the same application and is retained in session 17.

## Engineering objective

The service boundary adds authentication, validation, and safe error responses.
The server derives employee identity and retrieval scope. An ask with `stream`
enabled returns one SSE `result` event after the answer and citations are ready.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Expose typed ask and health routes; add restricted ingestion; authenticate bearer tokens; add request IDs; test API without network; connect Streamlit and show citations; run two-turn requests.

## Run the solution

From the repository root with the Python environment activated:

```powershell
python scripts/session.py test 16 --variant starter --previous-only
python scripts/session.py test 16
python scripts/session.py run 16
python -m copilot rag-http-verify
```

The last two commands start a fresh API on loopback, test its routes, and run
the real Streamlit page with Streamlit's test harness. They use local extractive
answers from the synthetic corpus and make zero paid calls.

To try the learner solution interactively, export and install it in its own
environment as described in the [implementation guide](../IMPLEMENTATION_GUIDE.md).
From the exported learner directory, start the API with these example keys:

```powershell
$env:COPILOT_AUTH_TOKENS = '{"course-mac":"E1261","course-windows":"E1068","course-admin":"E1218"}'
python -m copilot serve --host 127.0.0.1 --port 8082
```

In a second terminal with the same learner environment active, run
`python -m streamlit run src/copilot/ui/chat.py`. Use `course-mac` for “How do I
set up VPN on my Mac?” and `course-windows` for “How do I fix Windows VPN error
809?” Follow the second question with “It still doesn't work.”

The service exposes `/docs` for the API schema. `/health` reports the number of
indexed chunks. `/ingest` writes the parsed document manifest and its report
under `.work/`. The learner solution keeps conversations in memory for the
lifetime of its API process.

- [Learner API](solution/src/copilot/api/app.py)
- [Integrated API](../../src/copilot/api/app.py)
- [Streamlit page](solution/src/copilot/ui/chat.py)

## Deliberate failure exercise

Send an oversized request, a missing token and another user's thread ID; check errors disclose no private state. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Pass the authenticated API tests and the UI walkthrough of requests 1 and 2.
Record observed results in [evidence.md](evidence.md), publish the completion
commit, and verify CI before creating the `v0.2-rag` tag.
