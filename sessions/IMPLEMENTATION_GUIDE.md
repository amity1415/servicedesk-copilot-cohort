# Actual session implementations

Sessions 01–18 contain cumulative Python source. The
[implementation manifest](implementation_manifest.json) records verified
completion separately and tracks the pending live gate for Session 04.
Sessions 19–40 have lesson material and reference launchers.

Each implemented folder contains `starter/src/copilot`, `solution/src/copilot`,
acceptance tests in both trees, and build instructions. The starter retains the
previous solution and adds the next tests and exercise interfaces. Its inherited
tests pass. Its new tests fail until the learner implements the increment.

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

Session 14 records [reviewed live acceptance](14-grounded-prompting-with-citations/README.md#live-acceptance).
Session 15 uses the reviewed RAG evaluation set. Session 16 verifies the
[FastAPI service and Streamlit UI](16-rag-as-a-fastapi-service/README.md).
Session 17 adds the [fixed ticket workflow](17-agents-versus-workflows/README.md)
and verifies it with the local Compose services.
Session 18 adds [typed service desk tools and ticket drafting](18-tool-calling-and-structured-output/README.md).


## Required execution and commit gate

Source availability is separate from audited completion. Run `python scripts/complete_session.py N` in order. This executes both session and integrated application features, passes tests, saves evidence and commits before the next session is allowed. See [the completion policy](../docs/SESSION_COMPLETION_POLICY.md). A required live comparison cannot pass on a mock.


Before recording completion, start or restart the affected shared application
services and verify readiness, the new capability, and an existing workflow
through the running app. Record the observed results in the session evidence.
Follow the [session completion policy](../docs/SESSION_COMPLETION_POLICY.md).

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
