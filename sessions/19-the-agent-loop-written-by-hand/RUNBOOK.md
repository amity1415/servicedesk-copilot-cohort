# Session 19 — Hand-written diagnostic loop

Implement decision, allowed action, and observation. Stop on an answer or an explicit escalation when the budget is exhausted.

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

**For this session.** The loopback verifier uses scripted decisions. The paid comparison is a separate exercise.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 19
& $py scripts/session.py test 19
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-19/solution/react-verify.json' -Raw | ConvertFrom-Json
$r.trajectory | ConvertTo-Json -Depth 6
$r.runaway | ConvertTo-Json -Depth 6
$r | Select-Object tickets_written, paid_calls
```

The normal path reads the device, incident and KB, then cites `KB-1054`. The repeated-decision fixture stops at the step limit.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 19 --variant starter --previous-only
& $py scripts/session.py test 19 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_react_diagnostics.py](starter/tests/test_react_diagnostics.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/19-the-agent-loop-written-by-hand/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `agents/react.py` **new** · [reference](solution/src/copilot/agents/react.py) | Implement the loop, tool allow-list, argument validation and step budget. |
| 2 | `agents/diagnostics.py` **new** · [reference](solution/src/copilot/agents/diagnostics.py) | Wire asset, incident and KB lookups, and preserve observations in the result. |
| 3 | [api/app.py](starter/src/copilot/api/app.py) · [reference](solution/src/copilot/api/app.py) | Invoke the diagnostic loop from the authenticated slow-laptop route. |
| 4 | `agents/verify_react.py` **new** · [reference](solution/src/copilot/agents/verify_react.py) | Exercise the expected trajectory and the repeated-decision escalation. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 19 --variant starter
& $py scripts/session.py run 19 --variant starter
Get-Item 'reports/cohort/session-19/starter/react-verify.json'
git status --short
```

The learner tests and run should both succeed. Read the tool trace in order and check that the runaway case writes zero tickets. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot react-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.

## Run the live exercise when authorized

Set up the provider credential as described in the [lesson](README.md).
Use a fresh report path for each run:

```powershell
$budget = Read-Host 'Instructor-approved maximum spend in USD'
$run = [guid]::NewGuid().ToString('N')
& $py scripts/verify_react_live.py --max-spend-usd $budget --out "reports/session19-live/$run.json"
```
