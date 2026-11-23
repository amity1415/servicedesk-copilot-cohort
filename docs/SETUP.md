# Setup for the trainer and learners

For a fresh setup, follow the [project walkthrough](PROJECT_SETUP.md). Use the
[session checklist](../sessions/SETUP.md) to prepare each lab.

Use Python 3.12 or later and VS Code. On Windows use a short checkout path such
as `C:\work\servicedesk-copilot`; compiled dependencies can fail under long paths.
All commands below run in the repository root.

```bash
python -m venv .venv
```

Activate `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` on Linux/macOS. Install the local teaching package:

```bash
python -m pip install -e ".[dev,ticketing,course]"
python -m pytest
copilot tickets-stats
copilot ask "How do I set up VPN on my Mac?" --employee E1261
python sessions/01-kickoff-and-project-setup/reference.py
```

The default answer is an explicitly labelled lexical, extractive reference. It
does not call a model, download neural weights or meet the neural RAG gate.

For the optional service, graph, neural and tracing experiments:

```bash
python -m pip install -e ".[neural,postgres,agents,protocols,telemetry]"
```

Sentence-transformer downloads require network access and disk space. Confirm
learner hardware before class. No embedding model weights are bundled.

## Identity and service configuration

Copy `.env.example` to `.env`. The settings class reads that file for its own
fields. Service factories read process environment; export their variables in the
shell or use Compose `env_file`. Never assume merely copying `.env` exports it.

For a local demonstration in PowerShell, use synthetic development tokens:

```powershell
$env:COPILOT_AUTH_TOKENS='{"mac-dev":"E1261","windows-dev":"E1068","slow-dev":"E1166","finance-dev":"E1237","manager-dev":"E1234","owner-dev":"E1233","analyst-dev":"E1203","admin-dev":"E1218","hiring-dev":"E1062"}'
$env:COPILOT_TICKETING_API_KEY='dev-ticketing-key'
copilot serve
```

These tokens are examples for the fictional environment, not production secrets.
The bearer map stays on the server; `/ask` cannot set an arbitrary employee ID.
Start the UI in another activated terminal:

```bash
streamlit run src/copilot/ui/chat.py
```

Use the appropriate bearer token in the UI. FinSight requires approvals from
Samuel Rao (`manager-dev`) and Fatima Young (`owner-dev`), followed by fulfilment
under an analyst or administrator identity.

## Infrastructure

```bash
docker compose up -d db ticketing
docker compose ps
```

For the application, UI, three MCP services and HR partner together:

```bash
docker compose -f docker-compose.yml -f docker-compose.app.yml up --build
```

Set `COPILOT_AUTH_TOKENS` and `COPILOT_HR_TOKEN` first. This overlay selects MCP
transport in the API and shares the approval store with the ticketing MCP server.
The image is a teaching build and has not been built or scanned in this workspace.

The company database is a 300-person training sample; the problem statement's
10,000 employees describe the fictional organization's production scale.

MCP uses the deliberately bounded v1 SDK dependency (`mcp<2`). See
[version notes](TECHNOLOGY_REFERENCES.md) before upgrading. The HR task store is
in memory: restarting that service loses partner task history. The local workflow
uses SQLite to demonstrate persistence; PostgreSQL graph persistence is a separate
integration check.

## This workspace's long-path helper

When working in the supplied deeply nested Windows workspace, activate its parent
virtual environment and use:

```bash
python scripts/python_longpath.py -m pytest --basetemp=.work/t
python scripts/python_longpath.py sessions/02-ml-basics-on-ticket-data/reference.py
```

Create `.work` first if you select it as pytest's base directory. The helper adds
Windows extended-length path prefixes; it accesses the same files and permissions.

## Model and budget decisions

Choose the model provider, exact model revision, per-learner spending limit and
input/output token prices before the live session 4 exercise. `ModelClient`
supports a configurable OpenAI-compatible chat endpoint. Other providers need an
adapter. Its `offline` mode returns a declared fixture, not a simulated successful
model answer. No paid call is made by CI.
