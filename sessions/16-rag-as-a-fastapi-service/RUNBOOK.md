# Session 16 — FastAPI and Streamlit

Put the retrieval pipeline behind authenticated HTTP and display answers and citations in a browser.

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

**For this session.** Use the base install with FastAPI, Uvicorn, and Streamlit. The verifier starts its own loopback API.

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 16
& $py scripts/session.py test 16
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-16/solution/rag-http-verify.json' -Raw | ConvertFrom-Json
$r.health | Format-List
$r.requests | ConvertTo-Json -Depth 4
$r.ui | ConvertTo-Json -Depth 5
```

Check basic readiness, permissions and the UI walkthrough for Mac VPN and Windows 809 with its follow-up.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 16 --variant starter --previous-only
& $py scripts/session.py test 16 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_http.py](starter/tests/test_rag_http.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/16-rag-as-a-fastapi-service/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `api/http.py` **new** · [reference](solution/src/copilot/api/http.py) | Define input and response schemas, enforce bearer identity and capture request IDs. |
| 2 | `api/app.py` **new** · [reference](solution/src/copilot/api/app.py) | Expose health, ask and restricted ingestion. Apply thread ownership and employee scope. |
| 3 | `ui/rag_chat.py` **new** · [reference](solution/src/copilot/ui/rag_chat.py) | Send an authenticated question and preserve citations across Streamlit reruns. |
| 4 | `api/verify.py` **new** · [reference](solution/src/copilot/api/verify.py) | Exercise the loopback requests and the browser test harness using the seeded personas. |

For additional wiring, see [ui/chat.py](solution/src/copilot/ui/chat.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 16 --variant starter
& $py scripts/session.py run 16 --variant starter
Get-Item 'reports/cohort/session-16/starter/rag-http-verify.json'
git status --short
```

The learner tests and run should both succeed. In the browser, confirm Mac results cite `KB-1017` and the Windows follow-up keeps `KB-1018`. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-http-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.

## Open the learner app in the browser

Use two terminals. Close any existing learner API or Streamlit process with
**Ctrl+C** first so ports 8082 and 8501 are available. In **Terminal A**, from
the repository root, export your completed starter to a fresh folder and
give it its own Python environment:

```powershell
$repo = (Get-Location).Path
$name = 'session-16-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$learner = Join-Path $repo ".work\$name"
& $py scripts/session.py export 16 --variant starter --out $learner
Set-Location $learner
Get-Location
python -m venv .venv
$appPy = '.\.venv\Scripts\python.exe'
& $appPy -m pip install -e ".[dev]"
$env:COPILOT_AUTH_TOKENS = '{"course-mac":"E1261","course-windows":"E1068"}'
& $appPy -m copilot serve --host 127.0.0.1 --port 8082
```

Leave Terminal A running. In **Terminal B**, change to the folder printed by
`Get-Location` in Terminal A. Paste that exact path in place of
`YOUR_EXPORTED_PATH`.

```powershell
Set-Location 'YOUR_EXPORTED_PATH'
Invoke-RestMethod http://127.0.0.1:8082/health
.\.venv\Scripts\python.exe -m streamlit run src/copilot/ui/chat.py
```

1. Open `http://localhost:8501`. Set **API URL** to
   `http://localhost:8082` and enter `course-mac` as your access token.
2. Ask **How do I set up VPN on my Mac?** Check for `KB-1017`.
3. Change the token to `course-windows`. Ask **How do I fix Windows VPN
   error 809?** Then ask **It still doesn't work.** in the same chat.
   Check for `KB-1018` in both Windows replies.
4. Press **Ctrl+C** in both terminals when finished. Return your terminal to the
   original repository before beginning Session 17.
