# Session 04 — First model call and inference settings

Build a bounded model client and validate its response with a typed classification schema.

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

**For this session.** Run the supplied offline HTTP fixture first. A live comparison requires approved provider access and budget.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 4
& $py scripts/session.py test 4
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-04/solution/llm-smoke.json' -Raw | ConvertFrom-Json
$r | Select-Object mode, paid_calls, accuracy, cost, live_comparison
$r.classification | ConvertTo-Json -Depth 5
```

The fixture produces structured classification with zero paid calls. Live accuracy and cost remain unmeasured.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 4 --variant starter --previous-only
& $py scripts/session.py test 4 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_inference.py](starter/tests/test_inference.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/04-inference-parameters-and-the-first-llm-call/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [llm/client.py](starter/src/copilot/llm/client.py) · [reference](solution/src/copilot/llm/client.py) | Read endpoint and model from settings. Set a timeout, retry transient responses within a limit, and record usage and elapsed time. |
| 2 | [llm/classify.py](starter/src/copilot/llm/classify.py) · [reference](solution/src/copilot/llm/classify.py) | Validate the result and permit at most one repair attempt on schema failure. |
| 3 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Connect the smoke command to the declared offline response fixture. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 4 --variant starter
& $py scripts/session.py run 4 --variant starter
Get-Item 'reports/cohort/session-04/starter/llm-smoke.json'
git status --short
```

The learner tests and run should both succeed. Compare the temporary failure fixture and the 401 test. Confirm the permanent authorization failure sends one request. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot llm-smoke
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.

## Live provider exercise

The supplied command uses an HTTP fixture. For the separate live exercise,
use the provider and model approved by the instructor, then follow the
[lesson's experiment and evidence requirements](README.md). Record the
configured model, sample, latency, usage, and pricing together.
