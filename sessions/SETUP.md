# Session-by-session setup

Start with the [beginner terminal walkthrough](../docs/BEGINNER_RUNBOOK.md).
Use the [project setup guide](../docs/PROJECT_SETUP.md) for software requirements,
environment variables, and troubleshooting. Each row links to a runbook with
copy-and-paste commands, source files, and verification steps.

## How to start each lab

1. Open the linked lesson and read its instructor notes and setup row. Prepare
   any services or model files before class.
2. For Sessions 01–20, run `python scripts/session.py run N` for the cumulative
   solution and `python scripts/session.py test N` for its tests. Use
   `--variant starter` for the learner tree. From Session 02, add
   `--previous-only` to the starter test to check inherited behavior first.
3. For Sessions 21–40, run `python sessions/<session-folder>/reference.py`.
   Use the linked lesson for its integrated exercise and acceptance checks.
   Session 21 also has an integrated onboarding implementation. Consult the
   [implementation status](../docs/IMPLEMENTATION_STATUS.md) for verified scope.
4. Check the output or persisted state listed below, save observed evidence, and
   follow the [completion policy](../docs/SESSION_COMPLETION_POLICY.md) for any
   formal runtime or live gate. A successful local reference run demonstrates
   the scope stated in its report.

## Software and first checks for each lesson

‘Base install’ means `.[dev,ticketing,course]`. For an optional extra listed
below, install it from the root, for example
`python -m pip install -e ".[rag-local,postgres]"`. The full instructor install
in the project guide includes every extra named here.

| Session | Terminal and coding steps | Prepare before class | First run or check |
| --- | --- | --- | --- |
| [01 kickoff and project setup](01-kickoff-and-project-setup/README.md) | [Runbook](01-kickoff-and-project-setup/RUNBOOK.md) | Base Python install and the committed ticket export. | Run `python scripts/session.py run 1` and `python scripts/session.py test 1`. Use `--variant starter` for the exercise. |
| [02 ml basics on ticket data](02-ml-basics-on-ticket-data/README.md) | [Runbook](02-ml-basics-on-ticket-data/RUNBOOK.md) | Base install with the `course` extra. | Run lesson 2 and check that the classification and clustering reports use the assigned split. |
| [03 neural networks transformers and tokenization](03-neural-networks-transformers-and-tokenization/README.md) | [Runbook](03-neural-networks-transformers-and-tokenization/RUNBOOK.md) | Base install and network access for the initial tokenizer cache. | Run `python scripts/session.py run 3 -- token-report` and inspect the token count. |
| [04 inference parameters and the first llm call](04-inference-parameters-and-the-first-llm-call/README.md) | [Runbook](04-inference-parameters-and-the-first-llm-call/RUNBOOK.md) | Base install for the fixture. Approved model access, endpoint, and budget for the live exercise. | Run lesson 4 offline first. Follow its live comparison instructions when credentials and rates are available. |
| [05 why rag and a naive baseline](05-why-rag-and-a-naive-baseline/README.md) | [Runbook](05-why-rag-and-a-naive-baseline/RUNBOOK.md) | Base install and the supplied `fixtures/rag-baseline` data. | Run `copilot rag-demo` and verify the baseline result. |
| [06 document ingestion and parsing](06-document-ingestion-and-parsing/README.md) | [Runbook](06-document-ingestion-and-parsing/RUNBOOK.md) | Base install with PDF and Word parsers from `course`. | Run `copilot rag-ingest` and check the repeated ingestion result. |
| [07 chunking i fixed and recursive](07-chunking-i-fixed-and-recursive/README.md) | [Runbook](07-chunking-i-fixed-and-recursive/RUNBOOK.md) | Base install and the parsed course corpus. | Run lesson 7 and inspect fixed and recursive chunk boundaries. |
| [08 chunking ii semantic and parent child](08-chunking-ii-semantic-and-parent-child/README.md) | [Runbook](08-chunking-ii-semantic-and-parent-child/RUNBOOK.md) | `rag-local` extra and prepared MiniLM assets. | Run `copilot rag-model-prepare`, then `copilot rag-benchmark`. |
| [09 embeddings](09-embeddings/README.md) | [Runbook](09-embeddings/RUNBOOK.md) | `rag-local` extra and disk space for the embedding cache and model assets. | Run `copilot rag-model-prepare` and `copilot rag-embedding-model-prepare`, then `copilot rag-embedding-compare`. |
| [10 vector database and indexing](10-vector-database-and-indexing/README.md) | [Runbook](10-vector-database-and-indexing/RUNBOOK.md) | `rag-local,postgres` extras, prepared MiniLM, healthy Compose database, and local database URL. | Run `copilot rag-postgres-verify` and check search, replacement, and withdrawal. |
| [11 retrieval and metadata filtering](11-retrieval-and-metadata-filtering/README.md) | [Runbook](11-retrieval-and-metadata-filtering/RUNBOOK.md) | Same vector setup as 10. Keep source metadata and policy register available. | Run `copilot rag-metadata-verify` and check scoped retrieval. |
| [12 hybrid search](12-hybrid-search/README.md) | [Runbook](12-hybrid-search/RUNBOOK.md) | Same database and model setup as 10. | Run `copilot rag-hybrid-compare` and check the exact-code scenario. |
| [13 reranking and query rewriting](13-reranking-and-query-rewriting/README.md) | [Runbook](13-reranking-and-query-rewriting/RUNBOOK.md) | Hybrid stack and pinned cross-encoder. | Run `copilot rag-reranker-prepare`, then `copilot rag-rerank-compare`. |
| [14 grounded prompting with citations](14-grounded-prompting-with-citations/README.md) | [Runbook](14-grounded-prompting-with-citations/RUNBOOK.md) | Base install for offline citations. Approved live provider credentials and budget for the formal live lab. | Run `copilot rag-grounded-verify`. Follow the lesson's live instructions and save its transcript and human review. |
| [15 rag evaluation](15-rag-evaluation/README.md) | [Runbook](15-rag-evaluation/RUNBOOK.md) | Base install and the reviewed evaluation file required by the lesson. | Run `copilot rag-evaluate`. Verify the development and held-out results. |
| [16 rag as a fastapi service](16-rag-as-a-fastapi-service/README.md) | [Runbook](16-rag-as-a-fastapi-service/RUNBOOK.md) | Base install and the local API/UI settings from the project guide. | Run `copilot rag-http-verify`, then open the chat UI and check the two VPN walkthroughs. |
| [17 agents versus workflows](17-agents-versus-workflows/README.md) | [Runbook](17-agents-versus-workflows/RUNBOOK.md) | Healthy Compose database and ticketing mock. Use local development ticketing settings. | Run `copilot workflow-verify` and confirm one ticket after replay. |
| [18 tool calling and structured output](18-tool-calling-and-structured-output/README.md) | [Runbook](18-tool-calling-and-structured-output/RUNBOOK.md) | Base API dependencies and ticketing fixtures. Approved model access for the live assessment. | Run `copilot tools-verify`; use the lesson's bounded live tool evaluator for the formal report. |
| [19 the agent loop written by hand](19-the-agent-loop-written-by-hand/README.md) | [Runbook](19-the-agent-loop-written-by-hand/RUNBOOK.md) | Base API dependencies and ticketing fixtures. Approved model access for the live assessment. | Run `copilot react-verify`; use the lesson's live evaluator for the model-driven trace. |
| [20 langgraph and state management](20-langgraph-and-state-management/README.md) | [Runbook](20-langgraph-and-state-management/RUNBOOK.md) | `agents,postgres` extras and a healthy Compose database. | Run `copilot graph-verify` and check restart, ownership, and single-ticket replay. |
| [21 planning and task decomposition](21-planning-and-task-decomposition/README.md) | [Runbook](21-planning-and-task-decomposition/RUNBOOK.md) | Base install for SQLite and the reference. Full MCP/HR stack for the integrated chat walkthrough. | Run the reference and `python -m pytest tests/test_onboarding_plan.py`. With the overlay, submit the explicit candidate/date and inspect plan state. |
| [22 short term and long term memory](22-short-term-and-long-term-memory/README.md) | [Runbook](22-short-term-and-long-term-memory/RUNBOOK.md) | Base install and isolated SQLite state. Use distinct employee tokens for ownership checks. | Run the reference, then verify cross-thread recall and deletion through the lab's implementation. |
| [23 agentic rag and reflection](23-agentic-rag-and-reflection/README.md) | [Runbook](23-agentic-rag-and-reflection/RUNBOOK.md) | Base retrieval or the prepared vector backend. Approved model settings when running the live portion. | Run the reference and compare the evidence check, retry, and abstention paths. |
| [24 self correction error handling and retries](24-self-correction-error-handling-and-retries/README.md) | [Runbook](24-self-correction-error-handling-and-retries/RUNBOOK.md) | Ticketing mock with a separate lab instance for controlled faults. | Check the mock's `/health` first. Run the reference and inspect ticket state after controlled failure and replay. |
| [25 human in the loop approval](25-human-in-the-loop-approval/README.md) | [Runbook](25-human-in-the-loop-approval/RUNBOOK.md) | API and UI with finance, manager, owner, and analyst tokens. Isolate training state. | Run the FinSight workflow and inspect pending approval, fulfilment, and allocation state. |
| [26 multi agent i supervisor and specialists](26-multi-agent-i-supervisor-and-specialists/README.md) | [Runbook](26-multi-agent-i-supervisor-and-specialists/RUNBOOK.md) | Base install and an agreed frozen comparison set. Approved model access and budget for live comparison. | Run the reference, then record the single-agent and specialist comparison required by the lesson. |
| [27 multi agent ii hierarchical teams and handoffs](27-multi-agent-ii-hierarchical-teams-and-handoffs/README.md) | [Runbook](27-multi-agent-ii-hierarchical-teams-and-handoffs/RUNBOOK.md) | Base install and onboarding fixture. Use the overlay if exercising the integrated workflow. | Run the reference and verify a persisted handoff with dependency evidence. |
| [28 guardrails and prompt injection defence](28-guardrails-and-prompt-injection-defence/README.md) | [Runbook](28-guardrails-and-prompt-injection-defence/RUNBOOK.md) | Base install and isolated synthetic fixture state. Set up the reference permissions and audit path. | Run the defensive reference check and verify that unauthorized state changes are denied. |
| [29 mcp architecture and the ticketing server](29-mcp-architecture-and-the-ticketing-server/README.md) | [Runbook](29-mcp-architecture-and-the-ticketing-server/RUNBOOK.md) | `protocols` extra, ticketing mock, and MCP SDK client. | Run the lesson reference, then follow the stdio client lab to verify tool discovery and ticket readback. |
| [30 tools resources and prompts](30-tools-resources-and-prompts/README.md) | [Runbook](30-tools-resources-and-prompts/RUNBOOK.md) | `protocols` extra, documents server, and synthetic employee token. | Run the reference and exercise tool, resource, and prompt discovery with the SDK client. |
| [31 database server and transports](31-database-server-and-transports/README.md) | [Runbook](31-database-server-and-transports/RUNBOOK.md) | `protocols,postgres` extras, healthy database, and HTTP MCP services. Prepare a SELECT-only role for the lesson. | Run the reference, verify allowed reads, and verify database-enforced write denial. |
| [32 authentication and permissions](32-authentication-and-permissions/README.md) | [Runbook](32-authentication-and-permissions/RUNBOOK.md) | HTTP MCP services, distinct role tokens, and isolated state for access tests. | Check allowed and denied operations and inspect the audit records. |
| [33 agent to agent with the hr agent](33-agent-to-agent-with-the-hr-agent/README.md) | [Runbook](33-agent-to-agent-with-the-hr-agent/RUNBOOK.md) | `protocols` extra or full overlay, HR partner token, and hiring-manager token. | Use the seeded candidate/date and verify the HR task and completed IT plan. |
| [34 mcp versus a2a versus direct calls](34-mcp-versus-a2a-versus-direct-calls/README.md) | [Runbook](34-mcp-versus-a2a-versus-direct-calls/RUNBOOK.md) | Direct implementation, MCP servers, and A2A service running against equivalent fixtures. | Run the reference and capture comparable latency and contract snapshots. |
| [35 evaluation strategy and golden datasets](35-evaluation-strategy-and-golden-datasets/README.md) | [Runbook](35-evaluation-strategy-and-golden-datasets/RUNBOOK.md) | Base install, draft task fixtures, and a resettable environment. | Run the reference, review task labels, and demonstrate reset before scoring. |
| [36 llm as a judge](36-llm-as-a-judge/README.md) | [Runbook](36-llm-as-a-judge/RUNBOOK.md) | Approved judge endpoint/model and budget, plus an independently reviewed label set. | Run the reference before the live calibration. Save rubric version and human agreement results. |
| [37 agent evaluation](37-agent-evaluation/README.md) | [Runbook](37-agent-evaluation/RUNBOOK.md) | Authenticated stack, reviewed tasks, and isolated service state. | Run the reference, then score real tool calls, final state, and recorded policy decisions. |
| [38 regression testing in ci](38-regression-testing-in-ci/README.md) | [Runbook](38-regression-testing-in-ci/RUNBOOK.md) | GitHub Actions in the cohort repository and local pytest/Ruff. Use a short-lived learner branch for CI exercises. | Run local checks and use the lesson to demonstrate a rejected regression in CI. |
| [39 tracing observability and monitoring](39-tracing-observability-and-monitoring/README.md) | [Runbook](39-tracing-observability-and-monitoring/RUNBOOK.md) | `telemetry` extra, reachable OTLP collector and trace viewer, and running application services. | Run the reference, query `/metrics` with an operator token, and inspect a correlated trace in the lab's collector. |
| [40 containerization readiness and final walkthrough](40-containerization-readiness-and-final-walkthrough/README.md) | [Runbook](40-containerization-readiness-and-final-walkthrough/RUNBOOK.md) | Docker with Compose, full fixture configuration, and the image/dependency scanners selected for the class. | Build the complete stack in a clean environment, run the six acceptance flows, and retain scans and measured results. |

