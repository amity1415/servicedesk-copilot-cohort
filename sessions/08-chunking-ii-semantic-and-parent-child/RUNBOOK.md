# Session 08 — Semantic and parent-child chunking

Find topic changes from paragraph similarity. Compare child chunks optimized for search with larger parent sections used as answer context.

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

**For this session.** Install the `rag-local` extra and prepare the pinned CPU model.

```powershell
& $py -m pip install -e ".[rag-local]"
& $py -m copilot rag-model-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 8
& $py scripts/session.py test 8
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-08/solution/rag-benchmark.json' -Raw | ConvertFrom-Json
$r | Select-Object question_count, label_status, mode
$r.strategies | ConvertTo-Json -Depth 5
```

The report contains fixed, recursive, semantic, and parent-child results. Interpret Recall@5 with the recorded label status.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 8 --variant starter --previous-only
& $py scripts/session.py test 8 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_semantic.py](starter/tests/test_rag_semantic.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/08-chunking-ii-semantic-and-parent-child/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `rag/semantic_encoder.py` **new** · [reference](solution/src/copilot/rag/semantic_encoder.py) | Load the pinned encoder and encode paragraph units. |
| 2 | [rag/chunking.py](starter/src/copilot/rag/chunking.py) · [reference](solution/src/copilot/rag/chunking.py) | Split across topic changes using adjacent paragraph similarity. Retain parent references in child chunks. |
| 3 | [rag/chunking.py](starter/src/copilot/rag/chunking.py) · [reference](solution/src/copilot/rag/chunking.py) | Check that multiple children from one source can map back to the same parent. |
| 4 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Compare the four strategies against the same questions and avoid double-counting a source. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 8 --variant starter
& $py scripts/session.py run 8 --variant starter
Get-Item 'reports/cohort/session-08/starter/rag-benchmark.json'
git status --short
```

The learner tests and run should both succeed. Pick one retrieval hit. Follow its child-to-parent link and assess whether the extra context is useful. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-benchmark
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
