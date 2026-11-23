# 09 terminal and coding runbook

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
& $py -m copilot rag-model-prepare
& $py -m copilot rag-embedding-model-prepare
```

## 1. Run the instructor solution and inspect the starter

```powershell
& $py scripts/session.py run 9
& $py scripts/session.py test 9
& $py scripts/session.py test 9 --variant starter --previous-only
& $py scripts/session.py test 9 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/09-embeddings/starter` from the
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
| [src/copilot/rag/semantic_encoder.py](starter/src/copilot/rag/semantic_encoder.py) | [Reference](solution/src/copilot/rag/semantic_encoder.py) |
| [src/copilot/rag/service.py](starter/src/copilot/rag/service.py) | [Reference](solution/src/copilot/rag/service.py) |
| `src/copilot/rag/embedding_benchmark.py` **new** | [Reference](solution/src/copilot/rag/embedding_benchmark.py) |
| [src/copilot/cli.py](starter/src/copilot/cli.py) | [Reference](solution/src/copilot/cli.py) |
| [src/copilot/rag/cli.py](starter/src/copilot/rag/cli.py) | [Reference](solution/src/copilot/rag/cli.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 9 --variant starter
& $py scripts/session.py run 9 --variant starter
& $py -m copilot rag-embedding-compare
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check that the comparison identifies both models and records cache behavior and retrieval measurements.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.
