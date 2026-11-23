# Session-by-session engineering course

Audience: experienced engineers who know AI fundamentals. Forty 90-minute sessions build one IT Service Desk Copilot. Read [setup](../docs/SETUP.md) first.

Use the [session setup checklist](SETUP.md) to prepare dependencies and service
checks for each lab.

Each session has technical content, trainer notes, an implementation sequence, a runnable reference experiment, exercises and a verification checklist. Offline experiment completion is distinct from the syllabus integration gate. Reference source is shared with the application so fixes do not drift across forty copied repositories.

| Session | Build increment |
| --- | --- |
| 01 | [Kickoff and project setup](01-kickoff-and-project-setup/README.md) |
| 02 | [ML basics on ticket data](02-ml-basics-on-ticket-data/README.md) |
| 03 | [Neural networks, transformers and tokenization](03-neural-networks-transformers-and-tokenization/README.md) |
| 04 | [Inference parameters and the first LLM call](04-inference-parameters-and-the-first-llm-call/README.md) |
| 05 | [Why RAG and a naive baseline](05-why-rag-and-a-naive-baseline/README.md) |
| 06 | [Document ingestion and parsing](06-document-ingestion-and-parsing/README.md) |
| 07 | [Chunking I: fixed and recursive](07-chunking-i-fixed-and-recursive/README.md) |
| 08 | [Chunking II: semantic and parent-child](08-chunking-ii-semantic-and-parent-child/README.md) |
| 09 | [Embeddings](09-embeddings/README.md) |
| 10 | [Vector database and indexing](10-vector-database-and-indexing/README.md) |
| 11 | [Retrieval and metadata filtering](11-retrieval-and-metadata-filtering/README.md) |
| 12 | [Hybrid search](12-hybrid-search/README.md) |
| 13 | [Reranking and query rewriting](13-reranking-and-query-rewriting/README.md) |
| 14 | [Grounded prompting with citations](14-grounded-prompting-with-citations/README.md) |
| 15 | [RAG evaluation](15-rag-evaluation/README.md) |
| 16 | [RAG as a FastAPI service](16-rag-as-a-fastapi-service/README.md) |
| 17 | [Agents versus workflows](17-agents-versus-workflows/README.md) |
| 18 | [Tool calling and structured output](18-tool-calling-and-structured-output/README.md) |
| 19 | [The agent loop written by hand](19-the-agent-loop-written-by-hand/README.md) |
| 20 | [LangGraph and state management](20-langgraph-and-state-management/README.md) |
| 21 | [Planning and task decomposition](21-planning-and-task-decomposition/README.md) |
| 22 | [Short-term and long-term memory](22-short-term-and-long-term-memory/README.md) |
| 23 | [Agentic RAG and reflection](23-agentic-rag-and-reflection/README.md) |
| 24 | [Self-correction, error handling and retries](24-self-correction-error-handling-and-retries/README.md) |
| 25 | [Human-in-the-loop approval](25-human-in-the-loop-approval/README.md) |
| 26 | [Multi-agent I: supervisor and specialists](26-multi-agent-i-supervisor-and-specialists/README.md) |
| 27 | [Multi-agent II: hierarchical teams and handoffs](27-multi-agent-ii-hierarchical-teams-and-handoffs/README.md) |
| 28 | [Guardrails and prompt injection defence](28-guardrails-and-prompt-injection-defence/README.md) |
| 29 | [MCP architecture and the ticketing server](29-mcp-architecture-and-the-ticketing-server/README.md) |
| 30 | [Tools, resources and prompts](30-tools-resources-and-prompts/README.md) |
| 31 | [Database server and transports](31-database-server-and-transports/README.md) |
| 32 | [Authentication and permissions](32-authentication-and-permissions/README.md) |
| 33 | [Agent-to-Agent with the HR agent](33-agent-to-agent-with-the-hr-agent/README.md) |
| 34 | [MCP versus A2A versus direct calls](34-mcp-versus-a2a-versus-direct-calls/README.md) |
| 35 | [Evaluation strategy and golden datasets](35-evaluation-strategy-and-golden-datasets/README.md) |
| 36 | [LLM-as-a-judge](36-llm-as-a-judge/README.md) |
| 37 | [Agent evaluation](37-agent-evaluation/README.md) |
| 38 | [Regression testing in CI](38-regression-testing-in-ci/README.md) |
| 39 | [Tracing, observability and monitoring](39-tracing-observability-and-monitoring/README.md) |
| 40 | [Containerization, readiness and final walkthrough](40-containerization-readiness-and-final-walkthrough/README.md) |
