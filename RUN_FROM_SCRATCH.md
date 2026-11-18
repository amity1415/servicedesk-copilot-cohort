# Run from scratch on Windows

Project folder: `D:\AI-Engineering\servicedesk-copilot`.
Use PowerShell. Install Python 3.12 or later first (`python --version`).

## 1. Create and install the environment

```powershell
Set-Location D:\AI-Engineering\servicedesk-copilot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ticketing,course,protocols,agents,postgres,telemetry]"
Copy-Item .env.example .env
```

Copy `.env.example` only when `.env` does not already exist; preserve your local
configuration on subsequent runs. Commands below use the virtual environment
directly, so PowerShell activation and execution-policy changes are unnecessary.
Neural model downloads and paid model calls are not required for this local demo.

## 2. Verify the installation

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts/check_course.py
.\.venv\Scripts\copilot.exe tickets-stats
.\.venv\Scripts\copilot.exe ask "How do I set up VPN on my Mac?" --employee E1261
```

The final command prints a labelled extractive answer with KB citations.

## 3. Run a session

```powershell
.\.venv\Scripts\python.exe sessions/01-kickoff-and-project-setup/reference.py
.\.venv\Scripts\python.exe sessions/02-ml-basics-on-ticket-data/reference.py
```

Follow the session's `STEPS_TO_FOLLOW.md` and complete its `evidence.md`. The
[session index](sessions/README.md) lists all 40 folders. Reports are written to
`reports/sessions/`. Later references include preflights, not completed live gates.

## 4. Start the local API

In the first terminal:

```powershell
Set-Location D:\AI-Engineering\servicedesk-copilot
$env:COPILOT_AUTH_TOKENS='{"mac-dev":"E1261","windows-dev":"E1068","slow-dev":"E1166","finance-dev":"E1237","manager-dev":"E1234","owner-dev":"E1233","analyst-dev":"E1203","admin-dev":"E1218","hiring-dev":"E1062"}'
$env:COPILOT_TICKETING_API_KEY='dev-ticketing-key'
.\.venv\Scripts\copilot.exe serve
```

Open [API health](http://localhost:8082/health) or
[interactive API documentation](http://localhost:8082/docs). For `/ask`, send
`Authorization: Bearer mac-dev` with a body such as:

```json
{"question":"How do I set up VPN on my Mac?","thread_id":"first-chat"}
```

Without the ticket service, knowledge questions work; ticket creation needs step 6.

## 5. Start the chat UI

In a second terminal:

```powershell
Set-Location D:\AI-Engineering\servicedesk-copilot
.\.venv\Scripts\streamlit.exe run src/copilot/ui/chat.py
```

Open [the chat UI](http://localhost:8501). Set API URL to
`http://localhost:8082` and access token to `mac-dev`. Ask the VPN question.
Stop either server with Ctrl+C in its terminal.

## 6. Optional enterprise services and MCP/A2A application

Install and start Docker Desktop with Linux containers. For the direct API's
ticket service and PostgreSQL:

```powershell
docker compose up -d db ticketing
docker compose ps
```

For the full teaching service topology, stop the host API and UI first to free
their ports. In the terminal with the bearer map set:

```powershell
$env:COPILOT_HR_TOKEN='local-hr-demo-token'
docker compose -f docker-compose.yml -f docker-compose.app.yml up --build
```

The overlay runs API, UI, three MCP services and the HR A2A partner. Use
`mac-dev` in the UI as above. The overlay sets API-to-MCP URLs internally.
Docker execution has not been validated on this machine because its CLI failed
engine inspection; see [implementation status](docs/IMPLEMENTATION_STATUS.md).

The local demo is a deterministic reference with lexical retrieval. Consult
[setup](docs/SETUP.md) for optional neural/model configuration and
[integration steps](docs/INTEGRATION_STEPS.md) for the remaining course gates.
