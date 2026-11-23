# Session 20 — LangGraph checkpoint and resume

Convert the diagnostic loop into a graph with PostgreSQL checkpoints. Resume it after restart and prove safe ticket replay.

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

**For this session.** Install `agents,postgres` and start the database. The verifier starts separate API processes with isolated checkpoint state.

```powershell
& $py -m pip install -e ".[agents,postgres]"
docker compose up -d --wait db
docker compose exec -T db pg_isready -U copilot -d copilot
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 20
& $py scripts/session.py test 20
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-20/solution/graph-verify.json' -Raw | ConvertFrom-Json
$r.request_3 | ConvertTo-Json -Depth 6
$r.observed | Select-Object schema, process_ids
```

The first process pauses after `get_assets`. A different employee receives 403. The owner resumes with `check_service_status` and `search_kb`, and repeated ticket creation returns the same ticket.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 20 --variant starter --previous-only
& $py scripts/session.py test 20 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_diagnostic_graph.py](starter/tests/test_diagnostic_graph.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/20-langgraph-and-state-management/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `agents/diagnostic_graph.py` **new** · [reference](solution/src/copilot/agents/diagnostic_graph.py) | Define typed graph state, decision and tool nodes, and conditional routing. |
| 2 | `agents/checkpointed_diagnostics.py` **new** · [reference](solution/src/copilot/agents/checkpointed_diagnostics.py) | Bind the PostgreSQL checkpoint to the thread owner and resume from its saved point. |
| 3 | `api/diagnostic_graph.py` **new** · [reference](solution/src/copilot/api/diagnostic_graph.py) | Expose the authenticated streaming and resume endpoint. |
| 4 | `agents/verify_graph.py` **new** · [reference](solution/src/copilot/agents/verify_graph.py) | Verify checkpoint persistence across separate API processes, owner-only resume, and single-ticket replay. |

For additional wiring, see [agents/diagnostics.py](solution/src/copilot/agents/diagnostics.py), [api/app.py](solution/src/copilot/api/app.py), [config.py](solution/src/copilot/config.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 20 --variant starter
& $py scripts/session.py run 20 --variant starter
Get-Item 'reports/cohort/session-20/starter/graph-verify.json'
git status --short
```

The learner tests and run should both succeed. Record the process IDs and initial and resumed tool sequences. Check the persisted ticket count. The verifier steps carry out the restart. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot graph-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
