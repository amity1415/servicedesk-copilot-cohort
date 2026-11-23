# Session 01 — Kickoff and setup

Read a JSONL export (one JSON object per line), count tickets, and configure structured logging.

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

**For this session.** A Git checkout and the base course Python install. The ticket export is supplied.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 1
& $py scripts/session.py test 1
```

Inspect the output:

```powershell
Get-Content data/tickets/historical_tickets.jsonl -TotalCount 2
& $py scripts/session.py run 1 -- tickets-stats --by priority
```

The completed solution prints 5,000 tickets, including 850 Network & VPN tickets, and passes 17 tests. The priority command groups the same records by a different field.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 1 --variant starter
```

The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_config.py](starter/tests/test_config.py), [test_logging_setup.py](starter/tests/test_logging_setup.py), [test_tickets.py](starter/tests/test_tickets.py), [test_source_identity.py](starter/tests/test_source_identity.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/01-kickoff-and-project-setup/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [tickets.py](starter/src/copilot/tickets.py) · [reference](solution/src/copilot/tickets.py) | Implement `iter_tickets`. Open UTF-8, skip blank lines, validate each record, and attach the filename and line number to malformed-record errors. |
| 2 | [tickets.py](starter/src/copilot/tickets.py) · [reference](solution/src/copilot/tickets.py) | Implement `count_by`. Check the field against `COUNTABLE_FIELDS`, then count each value. |
| 3 | [logging_setup.py](starter/src/copilot/logging_setup.py) · [reference](solution/src/copilot/logging_setup.py) | Implement `configure_logging`. Apply the selected format and level, retain request IDs, and avoid duplicate handlers. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 1 --variant starter
& $py scripts/session.py run 1 --variant starter
git status --short
```

The learner tests and run should both succeed. Confirm your starter prints the same total. Open the malformed-record test and explain the error that it expects. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot tickets-stats
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
