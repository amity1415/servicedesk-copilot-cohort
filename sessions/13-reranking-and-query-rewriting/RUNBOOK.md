# Session 13 — Query rewriting and reranking

Use a thread's recent context to rewrite short follow-ups and rerank authorized passages with a cross-encoder.

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

**For this session.** Reuse the hybrid setup and prepare the pinned CPU reranker.

```powershell
& $py -m pip install -e ".[rag-local,postgres]"
docker compose up -d --wait db
docker compose exec -T db pg_isready -U copilot -d copilot
& $py -m copilot rag-model-prepare
& $py -m copilot rag-reranker-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 13
& $py scripts/session.py test 13
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-13/solution/rag-rerank-compare.json' -Raw | ConvertFrom-Json
$r | Select-Object model, question_count, label_status
$r.rankings | ConvertTo-Json -Depth 5
```

Look at both measured retrieval quality and p95 latency before choosing whether to enable the reranker.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 13 --variant starter --previous-only
& $py scripts/session.py test 13 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_reranking.py](starter/tests/test_rag_reranking.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/13-reranking-and-query-rewriting/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `rag/query.py` **new** · [reference](solution/src/copilot/rag/query.py) | Rewrite incomplete follow-ups with thread context and curated acronym expansions. |
| 2 | `rag/reranker.py` **new** · [reference](solution/src/copilot/rag/reranker.py) | Score query-and-passage pairs with the pinned cross-encoder. |
| 3 | [rag/service.py](starter/src/copilot/rag/service.py) · [reference](solution/src/copilot/rag/service.py) | Apply scope before candidate selection, rerank the candidate set, and apply the final limit. |
| 4 | `rag/reranker_benchmark.py` **new** · [reference](solution/src/copilot/rag/reranker_benchmark.py) | Compare hybrid and reranked hybrid on identical cases. |

For additional wiring, see [rag/semantic_encoder.py](solution/src/copilot/rag/semantic_encoder.py), [cli.py](solution/src/copilot/cli.py), [rag/cli.py](solution/src/copilot/rag/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 13 --variant starter
& $py scripts/session.py run 13 --variant starter
Get-Item 'reports/cohort/session-13/starter/rag-rerank-compare.json'
git status --short
```

The learner tests and run should both succeed. Verify the Windows follow-up in the learner tests and record whether quality improved enough to justify added latency. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-rerank-compare
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
