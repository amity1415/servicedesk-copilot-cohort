# 04 terminal and coding runbook

Open the [lesson](README.md) and [build guide](BUILD_GUIDE.md). Start from the repository root
with the [course environment](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout)
installed. In PowerShell, run these three lines to confirm the folder and
use its Python interpreter:

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
```

## Prepare this lab

```powershell
& $py -m copilot llm-smoke --help
```

## 1. Run the instructor solution and inspect the starter

```powershell
& $py scripts/session.py run 4
& $py scripts/session.py test 4
& $py scripts/session.py test 4 --variant starter --previous-only
& $py scripts/session.py test 4 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/04-inference-parameters-and-the-first-llm-call/starter` from the
   Explorer. Open its `tests` folder and read the first failing test named by
   PowerShell. The test gives the input and expected output.
2. Use the [build guide](BUILD_GUIDE.md) for the implementation sequence. Start with the
   first relevant file below. Create paths marked **new** in the starter tree
   if the feature needs them.
3. Save each change with **Ctrl+S**. Rerun the learner test command after each
   change. When stuck, open the corresponding reference beside your file and
   compare one function at a time.

| File in the starter | Completed example |
| --- | --- |
| [src/copilot/llm/classify.py](starter/src/copilot/llm/classify.py) | [Reference](solution/src/copilot/llm/classify.py) |
| [src/copilot/llm/client.py](starter/src/copilot/llm/client.py) | [Reference](solution/src/copilot/llm/client.py) |
| [src/copilot/cli.py](starter/src/copilot/cli.py) | [Reference](solution/src/copilot/cli.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 4 --variant starter
& $py scripts/session.py run 4 --variant starter
& $py -m copilot llm-smoke
git status --short
```

The last Copilot command uses the integrated application for comparison.
Look for the offline fixture output and schema-valid classification. Live accuracy remains unmeasured.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.

For the paid provider exercise, follow the model configuration and sample
requirements in the [lesson](README.md). The commands above use the local
fixture.
