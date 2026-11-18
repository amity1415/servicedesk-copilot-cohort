# Build session 04 progressively

## Source and starting point

Open `starter/src/copilot/` to implement this increment. It retains the previous
completed session's source plus explicit new TODOs/tests. `solution/src/copilot/`
is the cumulative reference implementation through this session only. It does not
import the final project's `src/copilot` to implement the lesson.

Read [the problem and data metadata](PROBLEM_STATEMENT_AND_DATASET.md) first.
Run these commands from `D:\AI-Engineering\servicedesk-copilot`.

## Before implementation

```powershell
.\.venv\Scripts\python.exe scripts/session.py test 4 --variant starter
```

The new acceptance tests are expected to fail until the work is implemented.
That expected failure is not a finished session. In sessions 2–4, verify inherited
behaviour separately:

```powershell
.\.venv\Scripts\python.exe scripts/session.py test 4 --variant starter --previous-only
```

## Implement and inspect

1. Implement `llm/client.py` transport deadlines, bounded transient retries and token/latency accounting. Never retry a permanent authentication error.
2. Implement `llm/classify.py` against its Pydantic schema, permitting at most one output repair.
3. Treat the user request as data and keep source labels out of prompts.
4. Add the `llm-smoke` command using a declared offline HTTP fixture and the offline CI workflow.
5. Run schema/repair/retry tests and keep live accuracy and cost unmeasured until the instructor selects an authorized provider, model and budget.

## Run the reference and acceptance checks

```powershell
.\.venv\Scripts\python.exe scripts/session.py run 4
.\.venv\Scripts\python.exe scripts/session.py test 4
```

To run your own changes, add `--variant starter`. The runner isolates imports to
that tree and checks source identity; it does not replace or stop the API/UI.
Run one training task at a time if sharing CPU/RAM with those services.
Reports go to `reports/cohort/session-04/<variant>/`.

## Compare and integrate

Compare your modified source with `solution/src/copilot/` after attempting the
exercise. Retain the previous contracts, run all accumulated tests and record
actual results in `evidence.md`. The completed ML/tokenization/classification
modules are also adopted in the main project's corresponding packages; the final
API continues to use its existing workflow until its later RAG/agent milestones.

## Export a complete cumulative checkpoint

```powershell
.\.venv\Scripts\python.exe scripts/session.py export 4 --out .work/checkpoints/session-04
```

The output includes cumulative source, tests, package metadata and the shared seed
data. Choose a fresh destination; existing work is never overwritten. In that
exported folder, create a **separate** virtual environment, install `.[dev]`, then
run `python -m pytest` and `python -m copilot llm-smoke`.
The exported package is the session checkpoint, not the full production release.

After local course tags are created, clone `cohort-session-04` into a new
folder to inspect that exact cumulative Git state. Do not check out a course tag
over the running main application.
