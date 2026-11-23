# Session 11 — Metadata and permission filtering

Scope retrieval by device platform, geography, audience and current effective policy before ranking.

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

**For this session.** Use the supplied KB and policy register. Prepare the CPU model for later retrieval checks.

```powershell
& $py -m pip install -e ".[rag-local]"
& $py -m copilot rag-model-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 11
& $py scripts/session.py test 11
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-11/solution/rag-metadata-verify.json' -Raw | ConvertFrom-Json
Get-Content data/policies/register.csv -TotalCount 4
$r.scopes | ConvertTo-Json -Depth 6
```

Compare allowed and excluded sources for the same question. The policy register governs which policy versions are current.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 11 --variant starter --previous-only
& $py scripts/session.py test 11 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_metadata.py](starter/tests/test_rag_metadata.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/11-retrieval-and-metadata-filtering/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/loaders.py](starter/src/copilot/rag/loaders.py) · [reference](solution/src/copilot/rag/loaders.py) | Normalize OS and region, parse audience, and check policy status and effective dates. |
| 2 | `rag/metadata_report.py` **new** · [reference](solution/src/copilot/rag/metadata_report.py) | Run scoped queries for an employee and an analyst and record the included and excluded documents. |
| 3 | [rag/cli.py](starter/src/copilot/rag/cli.py) · [reference](solution/src/copilot/rag/cli.py) | Expose the verifier and output scope details for review. |

For additional wiring, see [cli.py](solution/src/copilot/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 11 --variant starter
& $py scripts/session.py run 11 --variant starter
Get-Item 'reports/cohort/session-11/starter/rag-metadata-verify.json'
git status --short
```

The learner tests and run should both succeed. Show one correct platform-specific hit and one staff-only or superseded source that was excluded. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-metadata-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
