# Actual session implementations

Sessions 01–04 now contain actual cumulative Python source. Sessions 05–40 still
have the earlier experiment/preflight launchers and are explicitly planned in
`implementation_manifest.json`; they are not claimed as finished implementations.

Each implemented folder contains `starter/src/copilot`, `solution/src/copilot`,
acceptance tests in both trees, and `BUILD_GUIDE.md`. The starter for sessions 2–4
retains the previous solution and adds the next tests and TODO interfaces. Its
inherited tests pass; its new tests intentionally fail until the learner implements
the increment. Existing problem/data guides and learner evidence are retained.

From `D:\AI-Engineering\servicedesk-copilot`:

```powershell
.\.venv\Scripts\python.exe scripts/session.py run 2
.\.venv\Scripts\python.exe scripts/session.py test 2
.\.venv\Scripts\python.exe scripts/session.py test 2 --variant starter --previous-only
.\.venv\Scripts\python.exe scripts/session.py test 2 --variant starter
.\.venv\Scripts\python.exe scripts/session.py run 3 -- token-report
.\.venv\Scripts\python.exe scripts/session.py export 2 --out .work/checkpoints/session-02
```

The fourth command is expected to fail on untouched starter work. Session 3's
tokenizer may download its public encoding cache on first use; no paid model is
called. Report prices remain unknown unless the caller explicitly supplies both
prices. The session-4 model smoke is an offline HTTP/schema fixture, not a measured
LLM accuracy result. Root `copilot session N` and the original reference files now
route sessions 1–4 through the actual source implementation.

The runner uses a fresh subprocess with imports bound to the selected source tree;
an identity test prevents accidentally executing the installed final application.
It removes known provider keys from these offline teaching subprocesses. Do not
install a session package into the running application's `.venv`. Export it and
create a separate environment for a standalone learner project.

Local course Git tags `cohort-session-01` through `cohort-session-04` now point to
complete exported projects (source, tests, package metadata and data). Clone a tag
into a fresh folder rather than checking it out over the running main application:

```powershell
git clone --branch cohort-session-02 --single-branch D:\AI-Engineering\servicedesk-copilot .work/learner-session-02
Set-Location .work/learner-session-02
git switch -c learner/my-session-02
```

Tags are created only after solution and checkpoint validation. The initial local
history is authored as automated Codex course work; no remote push or production
release tag is created. Use `git show-ref --tags` to confirm available checkpoints.

Next implementation batch: sessions 5–8 with a working baseline RAG pipeline and
trusted ingestion/chunking metadata. Provider-dependent tests, external Git hosting,
Docker deployment and Jenkins administration remain separate decisions.


## Required execution and commit gate

Source availability is separate from audited completion. Run `python scripts/complete_session.py N` in order. This executes both session and integrated application features, passes tests, saves evidence and commits before the next session is allowed. See [the completion policy](../docs/SESSION_COMPLETION_POLICY.md). A required live comparison cannot pass on a mock.


## RAG batch commands

`copilot rag-demo` runs the integrated vector/extractive pipeline. `rag-ingest`
ingests 150 sources twice to verify idempotence. `rag-chunks` inspects boundaries;
`rag-benchmark` measures fixed, recursive, neural semantic and parent-child
strategies. Use `scripts/session.py run 5` through `run 8` for the actual cumulative
session source. Prepare public model assets with `copilot rag-model-prepare` if
they are not already present. No paid OpenAI call is required for this local batch.

Session 4's live comparison remains pending. RAG answers in this batch use cited
extraction, and question labels remain draft; production answer quality is not
certified. Read `docs/RAG_SESSION_05_08.md` and each new `BUILD_GUIDE.md` for scope.
