# Session 05 — A small RAG baseline

Retrieve evidence from a small KB fixture and produce a cited extract. Keep this as the baseline for later retrieval comparisons.

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

**For this session.** Use the bundled `fixtures/rag-baseline` corpus. No model endpoint is needed.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 5
& $py scripts/session.py test 5
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-05/solution/rag-demo.json' -Raw | ConvertFrom-Json
Get-ChildItem 'fixtures/rag-baseline/kb' -File | Select-Object -First 5 Name
$r | Select-Object mode, chunk_strategy, document_count, answer
$r.citations | Select-Object document_id
```

Inspect the 20-document fixture, the answer, and the cited document ID.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 5 --variant starter --previous-only
& $py scripts/session.py test 5 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_baseline.py](starter/tests/test_rag_baseline.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/05-why-rag-and-a-naive-baseline/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/chunking.py](starter/src/copilot/rag/chunking.py) · [reference](solution/src/copilot/rag/chunking.py) | Implement fixed chunks and retain each chunk's source identity and metadata. |
| 2 | [rag/service.py](starter/src/copilot/rag/service.py) · [reference](solution/src/copilot/rag/service.py) | Fit the lexical representation on the baseline documents, score the query, and assemble an answer with citations from retrieved chunks. |
| 3 | `rag/cli.py` **new** · [reference](solution/src/copilot/rag/cli.py) | Wire the baseline experiment and write the structured report. |
| 4 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Register the retrieval subcommands. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 5 --variant starter
& $py scripts/session.py run 5 --variant starter
Get-Item 'reports/cohort/session-05/starter/rag-demo.json'
git status --short
```

The learner tests and run should both succeed. Open a cited article and show the passage that supports the Mac VPN answer. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-demo
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
