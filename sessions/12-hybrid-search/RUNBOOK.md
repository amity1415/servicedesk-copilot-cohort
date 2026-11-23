# Session 12 — Hybrid search

Fuse PostgreSQL keyword ranks with dense vector ranks. Exact matching is useful for identifiers such as Windows error 809.

## 1. Open the project and prepare PowerShell

In VS Code, choose **File → Open Folder** and select the repository. Choose
**Terminal → New Terminal** and use PowerShell. Paste one command at a time.
Keep the terminal at the repository root, even when editing session files.

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
& $py --version
```

If the last command cannot find Python, follow the
[beginner installation walkthrough](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout).
Set `$py` again whenever you open a new terminal.

**For this session.** Reuse the PostgreSQL and encoder setup from Session 10.

```powershell
& $py -m pip install -e ".[rag-local,postgres]"
docker compose up -d --wait db
docker compose exec -T db pg_isready -U copilot -d copilot
& $py -m copilot rag-model-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 12
& $py scripts/session.py test 12
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-12/solution/rag-hybrid-compare.json' -Raw | ConvertFrom-Json
$r | Select-Object mode, label_status, question_count
$r.rankings | ConvertTo-Json -Depth 5
```

Compare vector-only, keyword-only and combined rankings on literal and paraphrased queries.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 12 --variant starter --previous-only
& $py scripts/session.py test 12 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_hybrid.py](starter/tests/test_rag_hybrid.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/12-hybrid-search/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/postgres_index.py](starter/src/copilot/rag/postgres_index.py) · [reference](solution/src/copilot/rag/postgres_index.py) | Add full-text ranking. Use the same authorized candidate set for keyword and vector queries. |
| 2 | `rag/rank_fusion.py` **new** · [reference](solution/src/copilot/rag/rank_fusion.py) | Fuse ranked lists with reciprocal rank fusion and return one result per chunk. |
| 3 | [rag/service.py](starter/src/copilot/rag/service.py) · [reference](solution/src/copilot/rag/service.py) | Add the hybrid backend and combine the two result lists. |
| 4 | `rag/hybrid_benchmark.py` **new** · [reference](solution/src/copilot/rag/hybrid_benchmark.py) | Measure the rankings on the same benchmark questions. |

For additional wiring, see [config.py](solution/src/copilot/config.py), [cli.py](solution/src/copilot/cli.py), [rag/cli.py](solution/src/copilot/rag/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 12 --variant starter
& $py scripts/session.py run 12 --variant starter
Get-Item 'reports/cohort/session-12/starter/rag-hybrid-compare.json'
git status --short
```

The learner tests and run should both succeed. Select one error-code query and one paraphrase. Explain which ranking method helped on each. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-hybrid-compare
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
