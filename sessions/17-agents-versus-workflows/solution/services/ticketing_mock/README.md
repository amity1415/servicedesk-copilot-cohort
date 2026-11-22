# Ticketing mock

A stand-in for HelpHub, the company ticketing system. It is provided by the trainer and treated as an external system: learners call it, they do not change it. First used in session 17.

## Run it

With Docker, from the repository root:

```bash
docker compose up ticketing
```

Without Docker, from the repository root:

```bash
pip install -e ".[ticketing]"
```

```bash
uvicorn mockapi.main:app --app-dir services/ticketing_mock --port 8081
```

Interactive API documentation is at http://localhost:8081/docs. Every request except `/health` needs the header `X-API-Key: dev-ticketing-key`.

## Endpoints

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Liveness and ticket count. No key needed, never faulted. |
| `POST /tickets` | Create a ticket. Send `Idempotency-Key` so a retry cannot create a duplicate. |
| `GET /tickets` | Search, newest first. Filters: `requester_id`, `status`, `category`, `assignment_group`, `priority`, `q`, `open_only`, `limit`, `offset`. |
| `GET /tickets/{id}` | One ticket with its comments. |
| `PATCH /tickets/{id}` | Change only the fields sent. |
| `GET` and `POST /tickets/{id}/comments` | Read and add comments. |
| `GET /assignment-groups` | The eight groups a ticket can be routed to. |
| `GET`, `PUT`, `DELETE /admin/faults` | Read, set and clear fault injection. |
| `POST /admin/reset` | Discard all changes and reload the seed tickets. |

## Rules a client has to handle

- A ticket needs a requester that exists, a category from the fixed list and a description. Anything else returns `422` with the fields at fault.
- Setting status to `Resolved` or `Closed` needs `resolution_notes`.
- A `Closed` ticket cannot be changed (`409 ticket_closed`).
- The same `Idempotency-Key` with the same body returns the first ticket again (`200`, header `Idempotent-Replay: true`). With a different body it returns `409 idempotency_key_reused`.

Every error has the same shape:

```json
{"error": {"code": "ticket_not_found", "message": "No ticket with ID INC0099999.", "details": {"ticket_id": "INC0099999"}}}
```

## Fault injection

Faults apply to `/tickets` and `/assignment-groups`. Set them at start-up with environment variables or at any time through `PUT /admin/faults`.

| Setting | Environment variable | Effect |
| --- | --- | --- |
| `error_rate` | `FAULT_ERROR_RATE` | Share of requests answered `503` before any work is done. Safe to retry. |
| `rate_limit_per_minute` | `FAULT_RATE_LIMIT_PER_MINUTE` | Requests allowed per API key per minute, then `429` with `Retry-After`. |
| `timeout_rate` | `FAULT_TIMEOUT_RATE` | Share of requests that are processed and then answered late. |
| `timeout_seconds` | `FAULT_TIMEOUT_SECONDS` | How late (default 30 seconds). |
| `latency_ms` | `FAULT_LATENCY_MS` | Delay added to every request. |
| `seed` | `FAULT_SEED` | Makes the random faults repeatable. |

The timeout fault is the one that matters most: the ticket is created, but a client with a shorter timeout never sees the answer. If it retries without an idempotency key, it creates a duplicate.

```bash
curl -X PUT http://localhost:8081/admin/faults -H "X-API-Key: dev-ticketing-key" -H "Content-Type: application/json" -d "{\"error_rate\": 0.2, \"timeout_rate\": 0.1, \"timeout_seconds\": 20, \"seed\": 7}"
```

## Data

The mock starts with the 60 open tickets in `data/tickets/open_tickets.json` and validates requesters against `data/db/csv/employees.csv`. Storage is an in-memory SQLite database, so a restart or `POST /admin/reset` returns it to the seed. Set `TICKETING_DB` to a file path to keep changes across restarts.

## Tests

```bash
pytest services/ticketing_mock/tests
```
