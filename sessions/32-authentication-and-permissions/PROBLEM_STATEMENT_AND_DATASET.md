# Session 32: problem statement and dataset metadata

## Authentication and permissions

## Problem statement

Enforce authenticated role and record ownership at each tool boundary, including denied calls.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Company table: employees

**Size:** 300 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/employees.csv](../../data/db/csv/employees.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `employee_id` | string; absent 0, null 0 | Synthetic employee primary key, also used by tickets, entitlements and runtime ownership. |
| `full_name` | string; absent 0, null 0 | Fictional person name; personal-data-shaped text for privacy exercises. |
| `email` | string; absent 0, null 0 | Fictional address under larkhaven.example; do not treat it as a real contact. |
| `department` | string; absent 0, null 0 | Synthetic organizational unit. |
| `job_title` | string; absent 0, null 0 | Synthetic role title; the Finance owner is identified by Chief Financial Officer. |
| `role` | string; absent 0, null 0 | Application role: employee, analyst or admin. This is not the KB audience field. |
| `is_manager` | string; absent 0, null 0 | Boolean manager flag; CSV stores text, so parse true/false explicitly. |
| `manager_id` | string; absent 0, null 0 | Self-referencing foreign key to employees.employee_id; root manager may be blank. |
| `office` | string; absent 0, null 0 | Office name; joins offices.office. |
| `region` | string; absent 0, null 0 | AMER, EMEA or APAC geography key. |
| `start_date` | string; absent 0, null 0 | ISO calendar date of employee or candidate start; use explicit dates, not the machine's next Monday. |
| `status` | string; absent 0, null 0 | Table-specific state: inspect SQL CHECK constraints and observed values rather than sharing one enum across tables. |

### Company table: devices

**Size:** 450 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/devices.csv](../../data/db/csv/devices.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `asset_tag` | string; absent 0, null 0 | Unique device key, e.g. LH-L-00166. |
| `device_type` | string; absent 0, null 0 | laptop or phone. |
| `model` | string; absent 0, null 0 | Synthetic hardware model label. |
| `os` | string; absent 0, null 0 | Normalized OS family such as windows or macos. |
| `os_version` | string; absent 0, null 0 | Human-readable OS release/version. |
| `serial_number` | string; absent 0, null 0 | Fictional unique serial; personal-data-shaped asset identifier. |
| `purchase_date` | string; absent 0, null 0 | ISO device purchase date; supports age-based diagnostics. |
| `ram_gb` | string; absent 0, null 0 | Device RAM in GB; may be blank for some phone rows. |
| `storage_gb` | string; absent 0, null 0 | Device storage capacity in GB. |
| `assigned_to` | string; absent 0, null 0 | Employee ID currently assigned to the device; join employees.employee_id. |
| `status` | string; absent 0, null 0 | Table-specific state: inspect SQL CHECK constraints and observed values rather than sharing one enum across tables. |
| `encrypted` | string; absent 0, null 0 | Boolean disk/device encryption flag; CSV stores text. |
| `compliant` | string; absent 0, null 0 | Boolean synthetic compliance flag; CSV stores text. |
| `last_patch_date` | string; absent 0, null 0 | ISO date of most recent patch; can be blank. |
| `pending_updates` | string; absent 0, null 0 | Count of outstanding synthetic updates. |

### Open ticket seed

**Size:** 60 records. **Origin:** datagen/tickets.py: TicketFactory.open_tickets; consumed by services/ticketing_mock/.

- [data/tickets/open_tickets.json](../../data/tickets/open_tickets.json)

JSON array seed, not the live mutable API database. One seeded request contains an injection attempt.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `ticket_id` | string; absent 0, null 0 | Unique historical incident identifier; provenance/join key, not a predictive feature. |
| `created_at` | string; absent 0, null 0 | UTC ISO timestamp when the synthetic ticket was raised; supports temporal analysis. |
| `updated_at` | string; absent 0, null 0 | UTC timestamp of the latest mock ticket update. |
| `requester_id` | string; absent 0, null 0 | Employee ID joining employees.employee_id; use only for authorized context, not as an intent shortcut. |
| `short_description` | string; absent 0, null 0 | User-supplied brief description; used with description as the ML input. |
| `description` | string; absent 0, null 0 | User-supplied issue text; may be vague, misspelled, non-IT or adversarial. |
| `category` | string; absent 0, null 0 | Classification target across eight IT categories; some generated labels are intentionally misfiled. |
| `subcategory` | string; absent 0, null 0 | More detailed topic label; exclude as an obvious category shortcut in baseline ML. |
| `priority` | string; absent 0, null 0 | Classification target P1–P4; synthetic sampling label, not an independently adjudicated impact/urgency assessment. |
| `assignment_group` | string; absent 0, null 0 | Destination support team; exclude from the baseline features because it encodes downstream handling. |
| `status` | string; absent 0, null 0 | Workflow state; historical rows are closed, open seed rows have active states. |
| `comments` | array; absent 0, null 0 | Comment records on live mock tickets; their content remains untrusted data. |

### Runtime records: audit

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, actor, action, outcome, created. Records authorized/denied/failed operations and feedback events. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### MCP tool schema snapshot

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** scripts/snapshot_contracts.py introspects registered tool inputs.

- [tests/contracts/mcp_schemas.json](../../tests/contracts/mcp_schemas.json)

Schema metadata, not employee training examples. Compare snapshots in CI and review breaking changes; never auto-approve a changed snapshot.

## How this session uses the data

Map bearer tokens to employee IDs server-side, distinguish analyst/admin from named approvers, and audit tool name/outcome without source text or secrets.

## Outputs and evidence

Employee/analyst/admin permission matrix and cross-user denial evidence; supplied YAML inventories are not a replacement for enforcement tests.

The curriculum exit criterion is: Role-by-tool permission matrix, denied-call audit and ownership tests. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/api/app.py](../../src/copilot/api/app.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
