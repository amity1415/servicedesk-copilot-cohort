# 16 terminal and coding runbook

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
& $py scripts/session.py run 16
& $py scripts/session.py test 16
& $py scripts/session.py test 16 --variant starter --previous-only
& $py scripts/session.py test 16 --variant starter
```

Expect the solution checks to pass. The last command is the learner's starting
point and should fail on the new acceptance checks before implementation.

## 2. Write the code

1. In VS Code, open `sessions/16-rag-as-a-fastapi-service/starter` from the
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
| `src/copilot/api/app.py` **new** | [Reference](solution/src/copilot/api/app.py) |
| `src/copilot/api/http.py` **new** | [Reference](solution/src/copilot/api/http.py) |
| `src/copilot/api/verify.py` **new** | [Reference](solution/src/copilot/api/verify.py) |
| `src/copilot/ui/chat.py` **new** | [Reference](solution/src/copilot/ui/chat.py) |
| `src/copilot/ui/rag_chat.py` **new** | [Reference](solution/src/copilot/ui/rag_chat.py) |

## 3. Run your changes and check the integrated app

```powershell
& $py scripts/session.py test 16 --variant starter
& $py scripts/session.py run 16 --variant starter
& $py -m copilot rag-http-verify
git status --short
```

The last Copilot command uses the integrated application for comparison.
Check the API and UI report for authenticated VPN answers, citations, and the Windows follow-up.
Record the commands, observed output, and the deliberate failure exercise in
[evidence.md](evidence.md). Stage only the files you changed when committing.

## Open the browser

Follow [the local web app walkthrough](../../docs/BEGINNER_RUNBOOK.md#2-run-the-local-web-app).
For the Windows check, use `windows-dev`, ask about VPN error `809`, then send
`It still doesn't work` in the same chat. Check that both Windows replies cite
`KB-1018`.
