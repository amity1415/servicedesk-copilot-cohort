# Session 02 — Ticket classification and clustering

Train category and priority classifiers and inspect groups of similar tickets. TF-IDF turns words into numbers, logistic regression predicts labels, and k-means groups examples.

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

**For this session.** Use the `course` extra and the supplied historical ticket data.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 2
& $py scripts/session.py test 2
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-02/solution/ml.json' -Raw | ConvertFrom-Json
$r | Select-Object train, test, group_overlap, feature_fields
$r.models.'category:logistic'.weakest_class
$r.models.'priority:logistic'.weakest_class
$r.models.'category:logistic'.metrics.'macro avg'
```

The verified split has 3,894 training and 1,106 held-out tickets with zero group overlap. The reference passes 21 tests. Security and P1 were the weakest classes in the training run.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 2 --variant starter --previous-only
& $py scripts/session.py test 2 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_ml.py](starter/tests/test_ml.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/02-ml-basics-on-ticket-data/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [ml/train.py](starter/src/copilot/ml/train.py) · [reference](solution/src/copilot/ml/train.py) | Implement `read_examples` and `request_text`. Use only short description and description as input text. Category and priority are output labels. |
| 2 | [ml/train.py](starter/src/copilot/ml/train.py) · [reference](solution/src/copilot/ml/train.py) | Implement `split_examples`. Keep each normalized short-description group entirely in training or entirely in the test set. |
| 3 | [ml/train.py](starter/src/copilot/ml/train.py) · [reference](solution/src/copilot/ml/train.py) | Implement `features`. Fit TF-IDF on the training text, then use the fitted object to transform the held-out text. |
| 4 | [ml/train.py](starter/src/copilot/ml/train.py) · [reference](solution/src/copilot/ml/train.py) | Train both models, save metrics and labelled confusion matrices, and add training cluster terms. |
| 5 | [cli.py](starter/src/copilot/cli.py) · [reference](solution/src/copilot/cli.py) | Connect `train` to the training function and print its report path. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 2 --variant starter
& $py scripts/session.py run 2 --variant starter
Get-Item 'reports/cohort/session-02/starter/ml.json'
git status --short
```

The learner tests and run should both succeed. Find one misclassification in the confusion matrix. Explain why the rare-class result matters even when overall accuracy looks good. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot train
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
