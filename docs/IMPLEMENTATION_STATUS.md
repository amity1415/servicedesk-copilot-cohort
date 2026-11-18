# Implementation and validation ledger

The supplied 40-session plan is the curriculum contract. Offline teaching checks,
live integration checks and release gates are separate. A successful offline run
does not certify production readiness, model quality, protocol interoperability or
the numerical release targets.

## Validated cumulative RAG batch, sessions 05–08

Implemented in both the integrated application and independent cumulative session
source trees, following the instructor-authorized batch exception. All four
session solutions and their commands passed; starters preserve inherited tests
and intentionally fail the new work. Main regression: 111 passed. Fresh session-08
Git checkout: 45 passed and its four-strategy benchmark completed. Real CPU ONNX
inference and an isolated authenticated HTTP request passed. No paid calls occurred.

Ingestion: 150 documents, no skips, no changes on repeated unchanged ingestion.
All 177 protected original seed/evaluation files retain their recorded hashes.
TF-IDF cosine retrieval and cited extraction are integrated into API/MCP; semantic
chunk boundaries use pinned MiniLM ONNX. Recursive remains the default after a
20-question draft comparison (0.80 Recall@5 versus semantic/parent-child 0.75).
These are draft-label development results, not reviewed release scores.

Local tags cohort-session-05 through cohort-session-08 contain standalone projects.
Evidence: reports/baselines/rag-batch-verification.json and
sessions/implementation_manifest.json. Session 04 remains pending live validation.
GitHub publishing, PostgreSQL indexing, live generation, Jenkins and Docker runtime
validation remain unfinished. Existing API/UI processes need restart to load code.

## Delivered teaching material

- Forty numbered session folders, each with technical content, numbered build
  steps, instructor timing/notes, a runnable reference and an evidence template.
- Original supplied plan preserved in `docs/BUILD_PLAN.txt`.
- Environment setup and cumulative project integration instructions.
- Draft datasets: 100 RAG questions, 40 agent tasks and 25 attack scenarios.
  They retain provenance and review status; generated expectations are not
  represented as human-reviewed ground truth.

## Implemented reference software

| Area | Implementation | Validation scope |
| --- | --- | --- |
| Foundations | Grouped ticket holdout, TF-IDF logistic/MLP classifiers, clustering | Actual fits on the 5,000-ticket corpus |
| Model client | Configurable compatible chat endpoint, bounded retry, tokens/latency | Mock transport; no paid calls |
| Retrieval | Mixed-format parsers, trusted metadata, four chunking strategies, TF-IDF cosine with pre-scoring authorization | Full-corpus parsing and repeatability; source/OS/error-code tests |
| Neural/database adapters | Sentence embeddings, cache, semantic chunks, RRF, cross-encoder, pgvector schema/search | Pinned CPU ONNX semantic chunking exercised; PostgreSQL, dense retrieval and reranking runtime not exercised |
| API/UI | Authenticated ask, completed-result SSE, ingestion restriction, approvals, feedback, Streamlit | API exercised; UI source compiled, no visual browser review |
| Actions/state | Durable local threads, memory deletion, stable ticket draft/key, dual approval, licence allocation | Ownership, duplicate/rejection, approval and effect tests |
| Agent references | Bounded hand-written loop, specialist allow-lists, dependency executor, typed LangGraph decision/tool loop | Scripted decisions and in-memory checkpoints; PostgreSQL saver not exercised |
| MCP | Three stdio/HTTP server references, actual SDK client, server-derived identity and per-tool audit | SDK client/server over ASGI HTTP, permission denial, resource/prompt access, schema snapshots |
| HR/A2A | Agent card, authenticated task execution, candidate/date binding, onboarding dependency | Actual A2A SDK task over in-process HTTP |
| Evaluation | Draft retrieval runner, exact trajectory rules, end-state scoring adapters, judge rubric, agreement interval, fail-closed release gate | Deterministic scoring tests; judge calibration and release scores unmeasured |
| Operations | Named spans, safe token attributes, W3C outbound headers, basic metrics, CI, non-root image and Compose overlay | Local tests/lint; no clean Docker startup, image scan or full cross-service trace dashboard |

## Actual cumulative acceptance test

`tests/test_cumulative_flow.py` drives the API through three actual MCP server
applications and an HR A2A application using in-process HTTP bridges. It checks:

1. Mac VPN answer cites `KB-1017` only.
2. Windows error 809 and the follow-up cite `KB-1018`.
3. Slow-laptop diagnosis reads assets/incidents and creates one idempotent ticket.
4. FinSight cannot fulfil before both manager and Finance owner approve; after
   approval the simulated entitlement persists.
5. Explicit candidate/date onboarding verifies HR over A2A, then persists five
   simulated HR/IT work items. Vague requests ask for candidate and absolute date.
6. The injection request changes no privilege and records a blocked attempt.

The bridge replaces network transport only. The default orchestration is a
deterministic teaching workflow, not a claimed autonomous-model benchmark. The
separate SDK-client test exercises real MCP initialization, listing and invocation
over ASGI transport. Docker networking remains untested.

## Current limitations and remaining syllabus gates

- Configure a provider, model revision and per-learner budget before paid calls.
  Tokenization/cost reports, model comparisons and live structured-output samples
  still need their session experiments completed.
- Wire the chosen neural/PostgreSQL retriever into the API/documents server;
  complete policy-register metadata enrichment, withdrawals and database
  SELECT-only role checks. The current assets server reads fixed CSV snapshots.
- Run the actual model-driven graph and specialist comparisons; finish consented
  token-budgeted memory, reflection, approval editing/reapproval and PostgreSQL
  restart/recovery checks. Graph and loop references are not the default API path.
- Complete ticket search/update/comment MCP tools, generalized role configuration,
  HR long-running task polling/durable partner store and production token verifier.
- Review all draft eval labels, author 30 independent human labels, run Ragas or
  equivalent claim-based metrics, and measure all release targets. The 25-case
  detector experiment is not a claim that all attacks are safely handled.
- Complete Presidio masking, cross-service trace propagation, durable dashboards,
  rate limits, graceful shutdown and full-stack/nightly quality CI gates.
- Pin and scan container image digests, resolve and test dependencies on the target
  OS, then run the clean-machine Compose walkthrough. `constraints-tested.txt`
  records this Windows/Python authoring environment; it is not a multi-platform lock.

Docker CLI engine inspection failed in this environment, including an internal
Docker CLI panic. No Docker build, deployment, CI-hosted run, paid model call or
production release tag is claimed. See `reports/session_validation.json` for local
experiment results; the later-session preflights explicitly preserve their gaps.

## Verification recorded on 17 November 2026

- Test suite: **72 passed**, with 14 third-party deprecation warnings.
  JUnit evidence: `reports/tests.xml`.
- Ruff lint and format checks passed.
- All 40 local reference experiments ran successfully. Later preflights remain
  preflights; see `reports/session_validation.json` and per-session JSON reports.
- All 40 folders contain required material and their session links resolve.
- MCP tool schemas match the stored contract snapshot.
- Retrieval baseline: **Recall@5 0.7667 on draft relevance labels**, below the
  starting 0.85 target. Other RAG release metrics remain null.
- ML results and interpretation are recorded in ADR 0002 and `reports/ml.json`.


## Foundation source checkpoint update on 18 November 2026

Sessions 01–04 now have cumulative starter/solution Python packages, inherited and
new acceptance tests, build guides and a safe standalone exporter. Their source
identity is tested independently of the installed main application. The completed
ML, token-report and classification helpers are integrated into the main source.
Session 4's paid-provider comparison remains unmeasured; no paid calls are made by
the offline checks. Sessions 05–40 remain explicitly planned as cumulative source
implementations, even though their original documentation/experiments exist.

See `sessions/IMPLEMENTATION_GUIDE.md` and `sessions/implementation_manifest.json`.

Foundation batch verification: 88 integrated tests passed; session solutions passed 17, 21, 24 and 28 checks respectively. Starters preserve the preceding tests and intentionally fail the new acceptance checks. A fresh clone of cohort-session-04 passed all 28 checkpoint checks. Local tags identify real complete cumulative projects. No GitHub repository or paid-provider call is claimed.
