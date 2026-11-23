# IT Service Desk Copilot

Teaching materials, executable reference code and synthetic data for the 60-hour AI Engineering and Agentic AI program. Forty sessions build one IT Service Desk Copilot cumulatively. The audience is experienced engineers who already understand AI fundamentals.

## Start here

- [Beginner terminal walkthrough](docs/BEGINNER_RUNBOOK.md)
- [Project software and step-by-step setup](docs/PROJECT_SETUP.md)
- [Session-by-session software and setup checklist](sessions/SETUP.md)
- [Actual cumulative session implementations](sessions/IMPLEMENTATION_GUIDE.md)

- [Dataset provenance and generation](docs/DATASET_PROVENANCE.md)
- [Session problem statements and dataset metadata](sessions/DATASET_GUIDES.md)

- [Setup and runnable commands](docs/SETUP.md)
- [All 40 session folders](sessions/README.md): content, instructor notes, build steps, runnable reference experiments and evidence templates
- [Cumulative project integration steps](docs/INTEGRATION_STEPS.md)
- [Implementation and validation status](docs/IMPLEMENTATION_STATUS.md)
- [Original supplied build plan](docs/BUILD_PLAN.txt)

The local reference supports the six acceptance control flows, including MCP and HR A2A components. Default answers use a labelled lexical/extractive baseline. Neural retrieval, live-model quality, human-reviewed datasets and production release targets need their own measured gates; successful local experiments do not certify those targets.

Everything here is fictional. Larkhaven Group, its people, systems, prices and incidents were generated for training; see [data/README.md](data/README.md).

## What is in the repository

| Part | Where | First used |
| --- | --- | --- |
| Project scaffold: settings, logging, command line, tests | `src/copilot/`, `tests/` | Session 1 |
| Synthetic data pack: 120 articles, 12 policy PDFs, 15 runbooks, 5,000 tickets, a 300-person database | `data/` | Session 1 |
| Ticketing mock with fault injection | `services/ticketing_mock/` | Session 17 |
| PostgreSQL with pgvector, seeded with the company data | `docker-compose.yml`, `data/db/` | Session 10 |
| Data generator (trainer tool) | `datagen/` | Before session 1 |
| ML, retrieval, tools, workflow, graph, API, UI and protocol references | `src/copilot/`, `services/hr_agent/` | Sessions 2 to 39 |
| Session teaching content and cumulative steps | `sessions/`, `docs/INTEGRATION_STEPS.md` | All 40 sessions |

## Quick start

Python 3.12 or later. On Windows, keep the repository in a short path such as `C:\work\servicedesk-copilot`; compiled Python packages fail to load from paths longer than 260 characters.

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS and Linux, then:

```bash
pip install -e ".[dev,ticketing,course]"
pytest
copilot tickets-stats
```

`copilot tickets-stats` prints the historical tickets by category. Try `--by priority` or `--by assignment_group`.

Set up Git and the commit hooks once:

```bash
git init
pre-commit install
cp .env.example .env
```

`.env` holds local settings and, from session 4, the model API key. It is ignored by Git, and the gitleaks hook blocks commits that contain keys.

## Enterprise systems

The copilot talks to three systems. All three are simulated.

| System | How it is simulated | Start it |
| --- | --- | --- |
| Documents | Files in `data/kb/`, `data/policies/`, `data/runbooks/`, `data/reference/` | Nothing to start |
| Company database | PostgreSQL with pgvector, loaded from `data/db/` | `docker compose up -d db` |
| Ticketing | The mock in `services/ticketing_mock/`, seeded with 60 open tickets | `docker compose up -d ticketing` |

The mock's API documentation is at http://localhost:8081/docs and its rules are in [services/ticketing_mock/README.md](services/ticketing_mock/README.md). The database connection string is in `.env.example`.

## Regenerating the data

The data pack is committed, so learners never need to generate it. To change its size or seed:

```bash
pip install -e ".[datagen]"
python -m datagen --seed 42 --tickets 5000
```

The same seed always writes identical files; `data/manifest.json` records a checksum for each. The authored content, including every article, policy and runbook, is in `datagen/content/`.

## Layout

```text
src/copilot/            the application
  config.py             settings from environment variables and .env
  logging_setup.py      console and JSON logging with request IDs
  tickets.py            reads the historical ticket export
  cli.py                the `copilot` command
  llm/ ml/ rag/ api/ ui/ tools/ agents/ guardrails/ mcp_servers/   shared teaching implementations
services/ticketing_mock/   trainer-provided ticketing API
datagen/                trainer tool that writes data/
data/                   the synthetic data pack
policies/               tool permissions, approval rules, guardrail settings (session 17 onward)
evals/                  golden sets, rubrics and evaluation runners (session 5 onward)
telemetry/              tracing configuration (session 39)
release/                pinned versions for a release (session 38)
docs/adr/               decision records
tests/                  tests for the scaffold and the data pack
sessions/               forty separate learning increments and their build instructions
scripts/                course authoring, dataset preparation, verification and schema snapshots
docker-compose.app.yml  optional API, UI, MCP and HR service overlay
```

## Working agreements

- Settings come from environment variables with the `COPILOT_` prefix. Nothing is hard-coded and no secret is committed.
- `ruff check .` and `ruff format .` must pass; the pre-commit hooks run both.
- Every session ends with its "done when" check passing and a commit.
- A choice between alternatives, such as a model or a chunking strategy, is recorded in `docs/adr/` with the numbers that justified it.
- VS Code only: no notebooks. Experiments are scripts under `src/copilot/` or `scripts/`.
