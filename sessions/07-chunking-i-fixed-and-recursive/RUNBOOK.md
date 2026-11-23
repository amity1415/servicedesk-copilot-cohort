# 07 terminal and coding runbook

Open the [lesson](README.md) and [build guide](BUILD_GUIDE.md). Start from the repository root
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
& $py scripts/session.py run 7
& $py scripts/session.py test 7
& $py scripts/session.py test 7 --variant starter --previous-only
& $py scripts/session.py test 7 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/07-chunking-i-fixed-and-recursive/starter` from the
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
| [src/copilot/rag/chunking.py](starter/src/copilot/rag/chunking.py) | [Reference](solution/src/copilot/rag/chunking.py) |
| [src/copilot/cli.py](starter/src/copilot/cli.py) | [Reference](solution/src/copilot/cli.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 7 --variant starter
& $py scripts/session.py run 7 --variant starter
& $py -m copilot rag-chunks
git status --short
```

The last Copilot command uses the integrated application for comparison.
Inspect the recursive chunk output for complete troubleshooting steps and retained section context.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.
