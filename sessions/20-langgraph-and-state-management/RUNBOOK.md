# 20 terminal and coding runbook

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
docker compose up -d --wait db
docker compose exec -T db pg_isready -U copilot -d copilot
```

## 1. Run the instructor solution and inspect the starter

```powershell
& $py scripts/session.py run 20
& $py scripts/session.py test 20
& $py scripts/session.py test 20 --variant starter --previous-only
& $py scripts/session.py test 20 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/20-langgraph-and-state-management/starter` from the
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
| [src/copilot/agents/diagnostics.py](starter/src/copilot/agents/diagnostics.py) | [Reference](solution/src/copilot/agents/diagnostics.py) |
| [src/copilot/api/app.py](starter/src/copilot/api/app.py) | [Reference](solution/src/copilot/api/app.py) |
| [src/copilot/config.py](starter/src/copilot/config.py) | [Reference](solution/src/copilot/config.py) |
| `src/copilot/agents/checkpointed_diagnostics.py` **new** | [Reference](solution/src/copilot/agents/checkpointed_diagnostics.py) |
| `src/copilot/agents/diagnostic_graph.py` **new** | [Reference](solution/src/copilot/agents/diagnostic_graph.py) |
| `src/copilot/agents/verify_graph.py` **new** | [Reference](solution/src/copilot/agents/verify_graph.py) |
| `src/copilot/api/diagnostic_graph.py` **new** | [Reference](solution/src/copilot/api/diagnostic_graph.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 20 --variant starter
& $py scripts/session.py run 20 --variant starter
& $py -m copilot graph-verify
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check the PostgreSQL verifier for an owner resume across processes and a single ticket after replay.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.
