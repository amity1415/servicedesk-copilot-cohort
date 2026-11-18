# Build session 03 progressively

## Source and starting point

Open `starter/src/copilot/` to implement this increment. It retains the previous
completed session's source plus explicit new TODOs/tests. `solution/src/copilot/`
is the cumulative reference implementation through this session only. It does not
import the final project's `src/copilot` to implement the lesson.

Read [the problem and data metadata](PROBLEM_STATEMENT_AND_DATASET.md) first.
Run these commands from `D:\AI-Engineering\servicedesk-copilot`.

## Before implementation

```powershell
.\.venv\Scripts\python.exe scripts/session.py test 3 --variant starter
```

The new acceptance tests are expected to fail until the work is implemented.
That expected failure is not a finished session. In sessions 2–4, verify inherited
behaviour separately:

```powershell
.\.venv\Scripts\python.exe scripts/session.py test 3 --variant starter --previous-only
```

## Implement and inspect

1. Extend the previous `train` function with an explicit `neural` option and the small MLP comparator while retaining the same holdout and vocabulary.
2. Implement `ml/token_report.py` with a named tokenizer, real token IDs and separate source/request distributions.
3. Keep cost unknown unless both input/output prices are explicitly provided; distinguish forecast from provider billing.
4. Add `compare` and `token-report` CLI commands.
5. Run `scripts/session.py run 3 -- token-report` separately. First use of the tokenizer may download its public encoding cache; no paid model is called. Raw export token counts include metadata/HTML markup and are not a cleaned RAG context budget.

## Run the reference and acceptance checks

```powershell
.\.venv\Scripts\python.exe scripts/session.py run 3
.\.venv\Scripts\python.exe scripts/session.py test 3
```

To run your own changes, add `--variant starter`. The runner isolates imports to
that tree and checks source identity; it does not replace or stop the API/UI.
Run one training task at a time if sharing CPU/RAM with those services.
Reports go to `reports/cohort/session-03/<variant>/`.

## Compare and integrate

Compare your modified source with `solution/src/copilot/` after attempting the
exercise. Retain the previous contracts, run all accumulated tests and record
actual results in `evidence.md`. The completed ML/tokenization/classification
modules are also adopted in the main project's corresponding packages; the final
API continues to use its existing workflow until its later RAG/agent milestones.

## Export a complete cumulative checkpoint

```powershell
.\.venv\Scripts\python.exe scripts/session.py export 3 --out .work/checkpoints/session-03
```

The output includes cumulative source, tests, package metadata and the shared seed
data. Choose a fresh destination; existing work is never overwritten. In that
exported folder, create a **separate** virtual environment, install `.[dev]`, then
run `python -m pytest` and `python -m copilot compare`.
The exported package is the session checkpoint, not the full production release.

After local course tags are created, clone `cohort-session-03` into a new
folder to inspect that exact cumulative Git state. Do not check out a course tag
over the running main application.
