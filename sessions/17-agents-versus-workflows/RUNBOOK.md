# 17 terminal and coding runbook

Open the [lesson](README.md) and [numbered build steps](STEPS_TO_FOLLOW.md). Start from the repository root
with the [course environment](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout)
installed. In PowerShell, run these three lines to confirm the folder and
use its Python interpreter:

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
```

## Prepare this lab

Wait for each preparation command to finish before going on.

```powershell
docker compose up -d --wait db ticketing
docker compose exec -T db pg_isready -U copilot -d copilot
Invoke-RestMethod http://127.0.0.1:8081/health
```

## 1. Run the instructor solution and inspect the starter

```powershell
& $py scripts/session.py run 17
& $py scripts/session.py test 17
& $py scripts/session.py test 17 --variant starter --previous-only
& $py scripts/session.py test 17 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/17-agents-versus-workflows/starter` from the
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
| `src/copilot/tools/password_reset.py` **new** | [Reference](solution/src/copilot/tools/password_reset.py) |
| `src/copilot/tools/ticketing.py` **new** | [Reference](solution/src/copilot/tools/ticketing.py) |
| `src/copilot/tools/verify_workflow.py` **new** | [Reference](solution/src/copilot/tools/verify_workflow.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 17 --variant starter
& $py scripts/session.py run 17 --variant starter
& $py -m copilot workflow-verify
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check the verifier for a ticket read back through HTTP and the same ticket on replay.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.
