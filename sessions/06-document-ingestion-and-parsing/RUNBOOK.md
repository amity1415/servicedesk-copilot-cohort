# Session 06 — Ingestion and parsing

Convert Markdown, HTML, PDF and Word content into one document schema with text and source metadata.

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

**For this session.** Use the `course` extra for the PDF and Word parsers. The source documents are in `data`.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 6
& $py scripts/session.py test 6
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-06/solution/rag-ingest.json' -Raw | ConvertFrom-Json
$r.first | Format-List
$r.repeat | Format-List
Get-ChildItem 'reports/cohort/session-06/solution' -File | Select-Object Name
```

The first pass parses sources. The repeat pass should report zero changes when the inputs are unchanged.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 6 --variant starter --previous-only
& $py scripts/session.py test 6 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_ingestion.py](starter/tests/test_rag_ingestion.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/06-document-ingestion-and-parsing/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/loaders.py](starter/src/copilot/rag/loaders.py) · [reference](solution/src/copilot/rag/loaders.py) | Read Markdown frontmatter and HTML metadata. Strip navigation and rendered portal chrome. |
| 2 | [rag/loaders.py](starter/src/copilot/rag/loaders.py) · [reference](solution/src/copilot/rag/loaders.py) | Read PDF layout and Word paragraphs and tables. Normalize the outputs to the shared document shape. |
| 3 | [rag/loaders.py](starter/src/copilot/rag/loaders.py) · [reference](solution/src/copilot/rag/loaders.py) | Use content hashes to distinguish unchanged, changed, removed, and skipped inputs. |
| 4 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Expose the ingestion experiment and write the manifest and report. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 6 --variant starter
& $py scripts/session.py run 6 --variant starter
Get-Item 'reports/cohort/session-06/starter/rag-ingest.json'
git status --short
```

The learner tests and run should both succeed. Compare first and repeated ingestion. Inspect a parsed policy table to see whether the value stayed with the correct label. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-ingest
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
