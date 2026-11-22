# Evidence — session 17

- Compose reported PostgreSQL and ticketing healthy. PostgreSQL returned 300
  employees and 450 devices. The ticketing service loaded 60 seed tickets.
- Each solution created a password-reset ticket in `Identity & Access` for
  synthetic employee `E1261`. Calling the same thread again returned the same
  ticket ID. `GET /tickets/{id}` found the ticket, and the total increased by one.
- The previous Mac VPN request returned `KB-1017` with no ticket write.
- An isolated mock returned `503` on three attempts. The workflow reported
  `ticket_unavailable` and added zero tickets. After clearing the isolated
  fault, retrying the same thread added one ticket.
- The workflow reads the employee and creates the ticket under default-deny
  policy. The test removes `create_ticket` from the policy and observes `403`
  with no new outbound call. It also checks the same idempotency key and
  request ID on the HTTP retry.
- Both commands used the synthetic pack, extractive TF-IDF and genuine local
  HTTP, with zero paid calls. The gate records actual ticket IDs, request IDs,
  and check results in `verification/runtime-gate.json`.
