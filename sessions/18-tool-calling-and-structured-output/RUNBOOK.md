# 18 terminal and coding runbook

Open the [lesson](README.md) and [numbered build steps](STEPS_TO_FOLLOW.md). Start from the repository root
with the [course environment](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout)
installed. In PowerShell, run these three lines to confirm the folder and
use its Python interpreter:

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
```

## 1. Run the instructor solution and inspect the starter

```powershell
& $py scripts/session.py run 18
& $py scripts/session.py test 18
& $py scripts/session.py test 18 --variant starter --previous-only
& $py scripts/session.py test 18 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/18-tool-calling-and-structured-output/starter` from the
   Explorer. Open its `tests` folder and read the first failing test named by
   PowerShell. The test gives the input and expected output.
2. Use the [numbered build steps](STEPS_TO_FOLLOW.md) for the implementation sequence. Start with the
   first relevant file below. Create paths marked **new** in the starter tree
   if the feature needs them.
3. Save each change with **Ctrl+S**. Rerun the learner test command after each
   change. When stuck, open the corresponding reference beside your file and
   compare one function at a time.

| File in the starter | Completed example |
| --- | --- |
| [src/copilot/api/app.py](starter/src/copilot/api/app.py) | [Reference](solution/src/copilot/api/app.py) |
| [src/copilot/llm/client.py](starter/src/copilot/llm/client.py) | [Reference](solution/src/copilot/llm/client.py) |
| [src/copilot/tools/password_reset.py](starter/src/copilot/tools/password_reset.py) | [Reference](solution/src/copilot/tools/password_reset.py) |
| [src/copilot/tools/ticketing.py](starter/src/copilot/tools/ticketing.py) | [Reference](solution/src/copilot/tools/ticketing.py) |
| [src/copilot/tools/verify_workflow.py](starter/src/copilot/tools/verify_workflow.py) | [Reference](solution/src/copilot/tools/verify_workflow.py) |
| `src/copilot/api/tools.py` **new** | [Reference](solution/src/copilot/api/tools.py) |
| `src/copilot/llm/service_desk.py` **new** | [Reference](solution/src/copilot/llm/service_desk.py) |
| `src/copilot/tools/directory.py` **new** | [Reference](solution/src/copilot/tools/directory.py) |
| `src/copilot/tools/service_desk.py` **new** | [Reference](solution/src/copilot/tools/service_desk.py) |
| `src/copilot/tools/verify_tools.py` **new** | [Reference](solution/src/copilot/tools/verify_tools.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 18 --variant starter
& $py scripts/session.py run 18 --variant starter
& $py -m copilot tools-verify
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check the typed tool verifier for scoped reads, validated writes, and idempotent ticket creation.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.

## Run the live exercise when authorized

Set up the provider credential as described in the [lesson](README.md).
Use a fresh report path for each run:

```powershell
$budget = Read-Host 'Instructor-approved maximum spend in USD'
$run = [guid]::NewGuid().ToString('N')
& $py scripts/verify_tools_live.py --max-spend-usd $budget --out "reports/session18-live/$run.json"
```
