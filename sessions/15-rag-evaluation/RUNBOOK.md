# Session 15 — RAG evaluation

Compare the baseline and expanded pipeline on fixed development and held-out questions using reviewed evidence labels.

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

**For this session.** Use the reviewed evaluation file shipped in the checkout. Keep case IDs and splits stable.

```powershell
Get-Item evals/rag_session15_reviewed.jsonl
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 15
& $py scripts/session.py test 15
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-15/solution/rag-evaluate.json' -Raw | ConvertFrom-Json
$r.dataset | ConvertTo-Json -Depth 4
$r.splits | ConvertTo-Json -Depth 5
$r.failure_examples | Select-Object -First 2 | ConvertTo-Json -Depth 5
```

Look for Recall@5, context precision, faithfulness and relevance for both splits. Check source coverage when interpreting a difference.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 15 --variant starter --previous-only
& $py scripts/session.py test 15 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_evaluation.py](starter/tests/test_rag_evaluation.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/15-rag-evaluation/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/loaders.py](starter/src/copilot/rag/loaders.py) · [reference](solution/src/copilot/rag/loaders.py) | Preserve permission and platform metadata consistently across pipelines. |
| 2 | `rag/evaluation.py` **new** · [reference](solution/src/copilot/rag/evaluation.py) | Load and validate cases with their split, relevant sources and reference evidence. Distinguish answerable cases from abstention cases. |
| 3 | `rag/evaluation.py` **new** · [reference](solution/src/copilot/rag/evaluation.py) | Score cases, aggregate by split, calculate paired uncertainty, and save failure examples. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 15 --variant starter
& $py scripts/session.py run 15 --variant starter
Get-Item 'reports/cohort/session-15/starter/rag-evaluate.json'
git status --short
```

The learner tests and run should both succeed. Explain one observed failure using its expected source and retrieved output. Use the lesson's reviewed-copy workflow for formal label changes. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-evaluate
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
