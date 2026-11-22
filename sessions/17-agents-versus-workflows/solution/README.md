# Session 17 password-reset workflow solution

Start the seeded services with `docker compose up -d db ticketing`. Once both
are healthy, run `python -m copilot workflow-verify`. The verifier creates one
synthetic ticket and confirms that retrying its thread returns the same ticket.
