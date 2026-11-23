# Session 14 — Grounded answering and citations

Use a structured prompt to select evidence, validate citations and passages, and abstain when evidence is missing.

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

**For this session.** Use the offline verifier first. The separate live run requires an approved model and spending limit.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 14
& $py scripts/session.py test 14
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-14/solution/rag-grounded-verify.json' -Raw | ConvertFrom-Json
$r | Select-Object mode, live_generation_verified, human_review_completed
$r.cases | ConvertTo-Json -Depth 5
```

Inspect both VPN citation outcomes and the unknown-policy abstention. Record whether the report covers a fixture or live generation.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 14 --variant starter --previous-only
& $py scripts/session.py test 14 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_grounded.py](starter/tests/test_rag_grounded.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/14-grounded-prompting-with-citations/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `rag/prompts/grounded-v3.md` **new** · [reference](solution/src/copilot/rag/prompts/grounded-v3.md) | Version the prompt, delimit retrieved source content, and ask for a structured evidence response. |
| 2 | `rag/grounded.py` **new** · [reference](solution/src/copilot/rag/grounded.py) | Validate the output shape, retrieved IDs and supported excerpts. Abstain when validation fails or evidence is insufficient. |
| 3 | `rag/grounded_fixture.py` **new** · [reference](solution/src/copilot/rag/grounded_fixture.py) | Cover Mac VPN, Windows 809 and an unknown policy with controlled responses. |
| 4 | [llm/client.py](starter/src/copilot/llm/client.py) · [reference](solution/src/copilot/llm/client.py) | Apply the approved request settings and bounded model behavior. |

For additional wiring, see [config.py](solution/src/copilot/config.py), [rag/pipeline.py](solution/src/copilot/rag/pipeline.py), [rag/prompts/grounded-v2.md](solution/src/copilot/rag/prompts/grounded-v2.md), [cli.py](solution/src/copilot/cli.py), [rag/cli.py](solution/src/copilot/rag/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 14 --variant starter
& $py scripts/session.py run 14 --variant starter
Get-Item 'reports/cohort/session-14/starter/rag-grounded-verify.json'
git status --short
```

The learner tests and run should both succeed. Open each cited passage and check that it supports the answer. A valid citation ID alone does not prove support. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-grounded-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.

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
