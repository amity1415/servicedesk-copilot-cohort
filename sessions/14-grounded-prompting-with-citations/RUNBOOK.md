# 14 terminal and coding runbook

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
& $py scripts/session.py run 14
& $py scripts/session.py test 14
& $py scripts/session.py test 14 --variant starter --previous-only
& $py scripts/session.py test 14 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/14-grounded-prompting-with-citations/starter` from the
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
| [src/copilot/config.py](starter/src/copilot/config.py) | [Reference](solution/src/copilot/config.py) |
| [src/copilot/llm/client.py](starter/src/copilot/llm/client.py) | [Reference](solution/src/copilot/llm/client.py) |
| [src/copilot/rag/pipeline.py](starter/src/copilot/rag/pipeline.py) | [Reference](solution/src/copilot/rag/pipeline.py) |
| `src/copilot/rag/grounded.py` **new** | [Reference](solution/src/copilot/rag/grounded.py) |
| `src/copilot/rag/grounded_fixture.py` **new** | [Reference](solution/src/copilot/rag/grounded_fixture.py) |
| `src/copilot/rag/prompts/grounded-v2.md` **new** | [Reference](solution/src/copilot/rag/prompts/grounded-v2.md) |
| `src/copilot/rag/prompts/grounded-v3.md` **new** | [Reference](solution/src/copilot/rag/prompts/grounded-v3.md) |
| [src/copilot/cli.py](starter/src/copilot/cli.py) | [Reference](solution/src/copilot/cli.py) |
| [src/copilot/rag/cli.py](starter/src/copilot/rag/cli.py) | [Reference](solution/src/copilot/rag/cli.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 14 --variant starter
& $py scripts/session.py run 14 --variant starter
& $py -m copilot rag-grounded-verify
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check that both VPN answers have valid citations and the unknown policy results in abstention.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.

## Run the live citation lab when authorized

The instructor supplies the model ID, per-request input ceiling, spend cap,
and provider rates. Use the provider key configuration in the lesson. Run
this from the same checkout used to collect evidence:

```powershell
$model = Read-Host 'Approved model ID'
$maxTokens = Read-Host 'Maximum input tokens per request'
$budget = Read-Host 'Approved maximum spend in USD'
$inputRate = Read-Host 'Approved input USD per million'
$outputRate = Read-Host 'Approved output USD per million'
& $py scripts/verify_grounded_live.py --live --model $model --max-input-tokens $maxTokens --max-spend-usd $budget --input-usd-per-million $inputRate --output-usd-per-million $outputRate
```

Open the printed transcript and review paths. Follow the [lesson](README.md)
for the human evidence review and formal gate.
