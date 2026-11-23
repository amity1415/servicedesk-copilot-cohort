# Project software and setup

Start with a local Python environment. Add the database and ticketing mock
when a lab requires them, then use the Compose overlay for the MCP and HR
integration. The [session setup checklist](../sessions/SETUP.md) gives the
dependencies and checks for each of the 40 lessons.

## 1. Install the software

| Software | When you need it | Check after installing |
| --- | --- | --- |
| Git and access to the private cohort repository | Before cloning | `git --version` and confirm your GitHub account can open the repository. |
| Python 3.12 or newer | Every local lab. Python 3.12 also matches the container image. | `python --version` |
| Visual Studio Code | Editing, reviewing diffs, and debugging | Open the checkout and choose its `.venv` as the Python interpreter. |
| Docker Engine with Compose v2, or Docker Desktop | Session 10 and later service labs | Start Docker, then run `docker info` and `docker compose version`. |
| Provider account, model access, and instructor-approved budget | Live model labs | Confirm the endpoint, model ID, and budget before running a paid experiment. |
| OpenTelemetry-compatible collector and trace viewer | Session 39 integration | Confirm the host can reach the collector endpoint supplied by the instructor. |

Compose supplies PostgreSQL with pgvector and the mock services. The starter
data is committed to the repository. The ONNX labs download public model
weights into a local cache when you run the preparation commands.

## 2. Clone and install the Python package

Use a short checkout path on Windows, such as `C:\work\servicedesk-copilot`.
Run the remaining commands from the repository root.

```powershell
git clone https://github.com/amity1415/servicedesk-copilot-cohort.git servicedesk-copilot
Set-Location servicedesk-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,ticketing,course]"
pre-commit install
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

On macOS/Linux, use `cd servicedesk-copilot`, `python3 -m venv .venv`,
`source .venv/bin/activate`, and `test -f .env || cp .env.example .env`.
The remaining `python` and `copilot` commands work after activation. If
PowerShell blocks activation, use `.\.venv\Scripts\python.exe` for Python
commands and `.\.venv\Scripts\copilot.exe` for Copilot commands.

```powershell
copilot tickets-stats
copilot ask "How do I set up VPN on my Mac?" --employee E1261
python scripts/session.py run 1
python scripts/session.py test 1
```

Expect 5,000 historical tickets and a local cited answer for the Mac VPN
question. This smoke check uses the bundled data and extractive answering.
For an instructor machine that will run all labs, add the optional extras and
run the integrated checks:

```powershell
python -m pip install -e ".[dev,ticketing,course,rag-local,postgres,agents,protocols,telemetry]"
python -m pip check
python -m pytest
ruff check .
ruff format --check .
```

The `neural` extra is for sentence-transformers experiments that explicitly
call for it. The pinned CPU ONNX exercises use `rag-local`. Keep exported
standalone lesson projects in their own virtual environments.

## 3. Start supporting services

```powershell
docker compose up -d --wait db ticketing
docker compose ps
docker compose exec -T db psql -U copilot -d copilot -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
Invoke-RestMethod http://127.0.0.1:8081/health
```

On macOS/Linux, use `curl -fsS http://127.0.0.1:8081/health` for the HTTP check.
PostgreSQL listens on host port `5432`. The ticketing mock listens on `8081`.
Keep the database URL and ticketing settings from `.env.example` for this local
stack. PostgreSQL runs the seed scripts when it initializes an empty volume.

## 4. Run FastAPI and Streamlit on the host

Set this synthetic classroom token map in the API shell. The same shell
variables can be used later by Compose. On macOS/Linux, use
`export NAME='value'` in place of `$env:NAME='value'`.

```powershell
$env:COPILOT_AUTH_TOKENS='{"mac-dev":"E1261","windows-dev":"E1068","slow-dev":"E1166","finance-dev":"E1237","manager-dev":"E1234","owner-dev":"E1233","analyst-dev":"E1203","admin-dev":"E1218","hiring-dev":"E1062"}'
$env:COPILOT_TICKETING_API_KEY='dev-ticketing-key'
$env:COPILOT_TRANSPORT='direct'
copilot serve
```

In a second activated terminal, check the API and launch the UI:

```powershell
Invoke-RestMethod http://127.0.0.1:8082/health
streamlit run src/copilot/ui/chat.py
```

Open the UI at `http://localhost:8501`, point it at `http://localhost:8082`,
and enter `mac-dev`. Ask how to set up VPN on a Mac and look for `KB-1017`.
The example tokens authorize fictional identities. Keep real provider keys
in local settings or your organization's secret store.

### Use persisted KB embeddings

With the database healthy and the `rag-local` and `postgres` extras installed,
run these commands in the API terminal before starting or restarting it:

```powershell
copilot rag-model-prepare
copilot rag-postgres-verify
$env:COPILOT_RETRIEVAL_BACKEND='pgvector'
copilot serve
```

The default `tfidf` backend runs in memory. `pgvector` stores dense embeddings
and searches PostgreSQL. `hybrid` combines keyword and vector retrieval.
Use `copilot rag-reranker-prepare` before selecting `reranked`. Check the
`mode` field from `/health` after a restart in direct mode.

### Enable an approved model or diagnostic graph

- **Grounded answers** use `COPILOT_ANSWER_MODE=grounded`, a valid
  `COPILOT_LLM_MODEL`, and `COPILOT_LLM_API_KEY`. Set `COPILOT_LLM_BASE_URL`
  if using a different compatible endpoint. Local extractive answering is the
  default. Use session-specific live runners when collecting formal evidence.
- **LangGraph checkpointing** requires a reachable database and the `agents`
  and `postgres` extras. Run `copilot graph-verify` for the isolated restart
  lab. For a host API exposing graph diagnostics, set
  `COPILOT_POSTGRES_DIAGNOSTICS_ENABLED=true` before startup.
- **Trace export** requires the `telemetry` extra and
  `OTEL_EXPORTER_OTLP_ENDPOINT` set before startup. The local `/metrics`
  endpoint accepts an analyst or admin token. Collector and dashboard setup
  is part of [Session 39](../sessions/39-tracing-observability-and-monitoring/README.md).

The settings object reads eligible fields from `.env`. Export switches read
directly from the process environment, including `COPILOT_AUTH_TOKENS`,
`COPILOT_TRANSPORT`, `COPILOT_RETRIEVAL_BACKEND`, and
`COPILOT_ANSWER_MODE`. Compose interpolates variables from the shell or its
environment file and passes variables declared in the service configuration.

## 5. Run the full Compose teaching stack

Stop the host API and Streamlit first to free ports `8082` and `8501`. In the
same shell as the synthetic token map, set the HR partner token and start the
overlay:

```powershell
$env:COPILOT_HR_TOKEN='dev-hr-partner-token'
docker compose -f docker-compose.yml -f docker-compose.app.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.app.yml ps
Invoke-RestMethod http://127.0.0.1:8082/health
```

The overlay uses MCP transport and starts the API, UI, documents MCP
(`8001`), assets MCP (`8002`), ticketing MCP (`8003`), and HR A2A
(`8090`), together with the base services. Open `http://localhost:8501` and
use the UI's preconfigured API URL. The overlay is the default fixture-based
teaching stack. Use the host setup in Step 4 for the pgvector RAG lab.

Run the six flows from the [training personas](../data/personas.md). For the
onboarding lab, use `hiring-dev` and the synthetic candidate `C-2041` with
the fixture date `2026-11-16`. For FinSight, submit with `finance-dev`,
approve with `manager-dev` and `owner-dev`, and fulfil with `analyst-dev`.

```powershell
docker compose -f docker-compose.yml -f docker-compose.app.yml down
```

This stops and removes the containers while retaining named volumes. Use
`docker compose down` when you started only the base services.

## 6. Troubleshoot setup

| Symptom | Check |
| --- | --- |
| `copilot` or `ruff` is missing | Activate the correct virtual environment and run the editable install from the repository root. |
| Native dependency installation fails on Windows | Use a short checkout path and retry with Python 3.12. See the [long-path helper](SETUP.md#this-workspaces-long-path-helper) for existing deep workspaces. |
| API returns 401 or 403 | Confirm the API process received the token map and that the selected identity has the required role. |
| Compose reports a missing variable | Set the token map and HR token before running the overlay command. |
| A service cannot start | Check `docker compose ps` and the affected service logs. Check for a port conflict with a host process. |
| Vector backend startup fails | Check PostgreSQL readiness, the vector extension, the database URL, both Python extras, and model preparation. |
| Session runner reports an unavailable starter or gate | Check the [implementation guide](../sessions/IMPLEMENTATION_GUIDE.md) and the [session setup checklist](../sessions/SETUP.md) for the appropriate reference path. |
