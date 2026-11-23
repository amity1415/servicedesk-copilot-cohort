# Session 07 — Fixed and recursive chunking

Compare fixed-size windows with text-aware splitting at paragraphs and procedural steps.

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

**For this session.** Use the local teaching corpus prepared in the ingestion lesson.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 7
& $py scripts/session.py test 7
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-07/solution/rag-chunks.json' -Raw | ConvertFrom-Json
$r | Select-Object documents, chunks, strategy
& $py scripts/session.py run 7 -- rag-chunks --strategy fixed
Get-Content 'reports/cohort/session-07/solution/chunks.jsonl' -TotalCount 1
& $py scripts/session.py run 7 -- rag-chunks --strategy recursive
Get-Content 'reports/cohort/session-07/solution/chunks.jsonl' -TotalCount 1
```

Each strategy rewrites the same chunks inspection file. Read or save the first output before running the second strategy.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 7 --variant starter --previous-only
& $py scripts/session.py test 7 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_recursive.py](starter/tests/test_rag_recursive.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/07-chunking-i-fixed-and-recursive/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/chunking.py](starter/src/copilot/rag/chunking.py) · [reference](solution/src/copilot/rag/chunking.py) | Implement fixed windows, validate size and overlap, and retain stable source IDs. |
| 2 | [rag/chunking.py](starter/src/copilot/rag/chunking.py) · [reference](solution/src/copilot/rag/chunking.py) | Prefer text boundaries for the recursive strategy. Keep an oversized numbered step intact. |
| 3 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Expose the strategy switch and write the chunk inspection records. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 7 --variant starter
& $py scripts/session.py run 7 --variant starter
Get-Item 'reports/cohort/session-07/starter/rag-chunks.json'
git status --short
```

The learner tests and run should both succeed. Compare a long troubleshooting article under both strategies. Record how the boundaries change the context a reader receives. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-chunks
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
