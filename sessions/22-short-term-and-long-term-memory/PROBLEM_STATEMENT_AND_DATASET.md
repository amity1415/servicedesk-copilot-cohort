# Session 22: problem statement and dataset metadata

## Short-term and long-term memory

## Problem statement

Retain useful employee context within a conversation budget and support deliberate deletion without using memory as authorization.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Runtime records: threads

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, employee, state. Ownership is checked; state is JSON, including the frozen retry draft. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: memory

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

employee, value. Local per-employee memory with a deletion operation; not a training dataset. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

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

## How this session uses the data

Separate short-term thread state from long-term per-employee memory and system-of-record facts; document which fields have consent to persist.

## Outputs and evidence

Scoped recall, budget and deletion checks; deleting memory does not automatically erase old checkpoints or audit records.

The curriculum exit criterion is: Budget check, cross-thread recall and deletion verification with remaining checkpoint caveat. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
