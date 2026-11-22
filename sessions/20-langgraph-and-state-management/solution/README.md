# Session 20 LangGraph diagnostics solution

Start local PostgreSQL with `docker compose up -d db`, then run
`python -m copilot graph-verify` with the course data available. The verifier
streams the diagnosis, restarts the service, and checks the saved ticket.
