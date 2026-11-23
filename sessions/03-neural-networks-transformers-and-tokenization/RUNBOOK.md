# Session 03 — Neural networks and tokenization

Compare a multilayer perceptron with the Session 02 baseline on the same split. Measure how a named tokenizer breaks up requests and identifiers.

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

**For this session.** The `course` extra supplies the libraries. The tokenizer may download its public encoding cache on first use.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 3
& $py scripts/session.py test 3
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-03/solution/ml.json' -Raw | ConvertFrom-Json
& $py scripts/session.py run 3 -- token-report
$r | Select-Object train, test, group_overlap
$r.models.PSObject.Properties.Name
$t = Get-Content 'reports/cohort/session-03/solution/tokens.json' -Raw | ConvertFrom-Json
$t | Select-Object encoding, cost_status
$t.identifier_examples
```

Compare the logistic and MLP rows on the same split. Inspect the encoding and identifier examples. Cost requires explicit rates.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 3 --variant starter --previous-only
& $py scripts/session.py test 3 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_tokens.py](starter/tests/test_tokens.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/03-neural-networks-transformers-and-tokenization/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [ml/train.py](starter/src/copilot/ml/train.py) · [reference](solution/src/copilot/ml/train.py) | Add the MLP alongside logistic regression while preserving the split and input representation. Save macro F1 and elapsed time. |
| 2 | [ml/token_report.py](starter/src/copilot/ml/token_report.py) · [reference](solution/src/copilot/ml/token_report.py) | Use a named encoding, count tokens in tickets and articles, and show VPN error or KB identifier examples. |
| 3 | [ml/token_report.py](starter/src/copilot/ml/token_report.py) · [reference](solution/src/copilot/ml/token_report.py) | Support price inputs for input and output tokens. Preserve an unknown estimate when rates are absent. |
| 4 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Wire `compare` and `token-report` to their modules. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 3 --variant starter
& $py scripts/session.py run 3 --variant starter
& $py scripts/session.py run 3 --variant starter -- token-report
Get-Item 'reports/cohort/session-03/starter/ml.json'
git status --short
```

The learner tests and run should both succeed. Run both commands on your starter. Record the timing and macro F1 tradeoff and identify the tokenizer used. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot compare
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
