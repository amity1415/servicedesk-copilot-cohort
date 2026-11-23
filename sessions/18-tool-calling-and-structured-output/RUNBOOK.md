# Session 18 — Typed tool calling

Expose narrow tool contracts for knowledge, employee, assets, incidents and ticket operations. Validate requests before making a change.

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

**For this session.** Use the local HTTP verifier first. Its fixtures distinguish employee and analyst permissions.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 18
& $py scripts/session.py test 18
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-18/solution/tools-verify.json' -Raw | ConvertFrom-Json
$r | Select-Object search_documents, incident_ids, paid_calls
$r.rejected_calls | ConvertTo-Json -Depth 5
$r.ticket | ConvertTo-Json -Depth 5
```

Inspect which inputs passed and which were rejected, then check the persisted ticket and replay outcome.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 18 --variant starter --previous-only
& $py scripts/session.py test 18 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_service_desk_tools.py](starter/tests/test_service_desk_tools.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/18-tool-calling-and-structured-output/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [tools/ticketing.py](starter/src/copilot/tools/ticketing.py) · [reference](solution/src/copilot/tools/ticketing.py) | Define `TicketDraft` with required fields and allowed values. |
| 2 | `tools/service_desk.py` **new** · [reference](solution/src/copilot/tools/service_desk.py) | Enforce caller and asset scope before returning records or writing a ticket. |
| 3 | `api/tools.py` **new** · [reference](solution/src/copilot/api/tools.py) | Expose tool endpoints with typed request and response structures. |
| 4 | `llm/service_desk.py` **new** · [reference](solution/src/copilot/llm/service_desk.py) | Validate the proposed structured result and constrain schema repair to the lesson's allowed attempt. |

For additional wiring, see [api/app.py](solution/src/copilot/api/app.py), [llm/client.py](solution/src/copilot/llm/client.py), [tools/password_reset.py](solution/src/copilot/tools/password_reset.py), [tools/verify_workflow.py](solution/src/copilot/tools/verify_workflow.py), [tools/directory.py](solution/src/copilot/tools/directory.py), [tools/verify_tools.py](solution/src/copilot/tools/verify_tools.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 18 --variant starter
& $py scripts/session.py run 18 --variant starter
Get-Item 'reports/cohort/session-18/starter/tools-verify.json'
git status --short
```

The learner tests and run should both succeed. Verify that an otherwise valid draft naming someone else's device fails, and that a replay does not duplicate the ticket. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot tools-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.

## Run the live exercise when authorized

Set up the provider credential as described in the [lesson](README.md).
Use a fresh report path for each run:

```powershell
$budget = Read-Host 'Instructor-approved maximum spend in USD'
$run = [guid]::NewGuid().ToString('N')
& $py scripts/verify_tools_live.py --max-spend-usd $budget --out "reports/session18-live/$run.json"
```
