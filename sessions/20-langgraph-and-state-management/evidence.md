# Evidence — session 20

- The first API process streamed `get_assets` and paused. The verifier stopped
  that process and read the saved checkpoint from PostgreSQL.
- The replacement process denied resume under a different employee with
  `403`. The owner resumed at `check_service_status` and `search_kb` and
  received the Windows troubleshooting article `KB-1054`.
- An explicit ticket request created one P3 Hardware & Devices ticket for
  employee `E1166`, routed to Workplace Engineering. The description included
  laptop `LH-L-00166` and the reported failed fixes.
- A third API process replayed the same ticket and checkpoint. The mock
  ticket count increased from 60 to 61. The retry fixture also checked that the
  draft and idempotency key were preserved through a ticketing outage.
- `verification/runtime-gate.json` records the test results, independent
  PostgreSQL schemas, process IDs, and checkpoint IDs. The runs used local
  decisions and made zero paid model calls.
