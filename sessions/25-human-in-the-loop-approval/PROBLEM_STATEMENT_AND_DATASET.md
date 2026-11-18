# Session 25: problem statement and dataset metadata

## Human-in-the-loop approval

## Problem statement

Fulfil a restricted finance-access request only after matching approvals and a capacity check.

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

### Company table: software_catalogue

**Size:** 40 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/software_catalogue.csv](../../data/db/csv/software_catalogue.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `app_id` | string; absent 0, null 0 | Application key joining software_catalogue.app_id. |
| `name` | string; absent 0, null 0 | Table-specific human-readable application, region or role-profile name. |
| `vendor` | string; absent 0, null 0 | Synthetic catalogue vendor attribution, not an endorsement or pricing source. |
| `category` | string; absent 0, null 0 | Application grouping in the catalogue. |
| `licence_type` | string; absent 0, null 0 | Free, Site or Named; capacity checks matter for Named licences. |
| `annual_charge_usd` | string; absent 0, null 0 | Invented internal annual charge in USD, not a real vendor quote. |
| `approval_rule` | string; absent 0, null 0 | Required synthetic approval rule. FinSight requires manager plus data owner. |
| `platforms` | string; absent 0, null 0 | Comma-separated supported platform names. |
| `delivery` | string; absent 0, null 0 | Synthetic fulfilment channel. |
| `restricted` | string; absent 0, null 0 | Boolean indication of restricted application access; not a replacement for policy checks. |
| `seats_total` | string; absent 0, null 0 | Total Named-licence capacity; blank where a seat count does not apply. |

### Company table: entitlements

**Size:** 830 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/entitlements.csv](../../data/db/csv/entitlements.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `employee_id` | string; absent 0, null 0 | Synthetic employee primary key, also used by tickets, entitlements and runtime ownership. |
| `app_id` | string; absent 0, null 0 | Application key joining software_catalogue.app_id. |
| `granted_at` | string; absent 0, null 0 | ISO date of entitlement allocation. |
| `last_used` | string; absent 0, null 0 | ISO most recent usage date for reclaim/idle analysis. |

### Runtime records: requests

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, employee, app, status, approver, key, data_owner. Created when access is requested; key binds idempotency to arguments. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: decisions

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

request, actor, decision, created. Composite key (request, actor); manager and Finance owner decisions are distinct. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: grants

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

employee, app. Composite key prevents duplicate simulated entitlement grants. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: audit

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, actor, action, outcome, created. Records authorized/denied/failed operations and feedback events. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

## How this session uses the data

Join employee manager, FinSight APP-020, 60 seed seats/58 allocations, manager E1234 and data owner E1233; inspect decision records and post-action grants separately.

## Outputs and evidence

Pending-to-approved-to-fulfilled effect evidence; both named approvals are required and rejection is terminal.

The curriculum exit criterion is: Request 4 end state plus unauthorized, replay and seat-capacity tests. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)
- [src/copilot/api/app.py](../../src/copilot/api/app.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
