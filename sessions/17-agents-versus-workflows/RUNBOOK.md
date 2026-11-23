# Session 17 — Fixed password-reset workflow

Create and read back a help-desk ticket through a deterministic workflow, with a stable retry key and explicit risk rules.

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

**For this session.** Start Docker, the PostgreSQL directory seed, and the ticketing mock. The verifier uses separate fault-test state.

```powershell
& $py -m pip install -e ".[postgres]"
docker compose up -d --wait db ticketing
docker compose exec -T db pg_isready -U copilot -d copilot
Invoke-RestMethod http://127.0.0.1:8081/health
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 17
& $py scripts/session.py test 17
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-17/solution/workflow-verify.json' -Raw | ConvertFrom-Json
$r.directory | ConvertTo-Json -Depth 4
$r.workflow | ConvertTo-Json -Depth 5
$r.outage | ConvertTo-Json -Depth 5
```

The verified path reads back the ticket, repeats the same request, and recovers after a temporary 503.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 17 --variant starter --previous-only
& $py scripts/session.py test 17 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_password_reset_workflow.py](starter/tests/test_password_reset_workflow.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/17-agents-versus-workflows/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `tools/ticketing.py` **new** · [reference](solution/src/copilot/tools/ticketing.py) | Send the validated draft over HTTP using a stable idempotency key. |
| 2 | `tools/password_reset.py` **new** · [reference](solution/src/copilot/tools/password_reset.py) | Build the fixed password-reset intake and route the draft under the documented risk rules. |
| 3 | [api/app.py](starter/src/copilot/api/app.py) · [reference](solution/src/copilot/api/app.py) | Route authenticated reset requests to the workflow and retain the thread context. |
| 4 | `tools/verify_workflow.py` **new** · [reference](solution/src/copilot/tools/verify_workflow.py) | Read back the ticket and test replay and a temporary service failure using isolated state. |

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 17 --variant starter
& $py scripts/session.py run 17 --variant starter
Get-Item 'reports/cohort/session-17/starter/workflow-verify.json'
git status --short
```

The learner tests and run should both succeed. Record the ticket ID before and after replay. Verify both refer to the same persisted ticket. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot workflow-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
