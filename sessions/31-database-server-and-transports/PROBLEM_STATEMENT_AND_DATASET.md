# Session 31: problem statement and dataset metadata

## Database server and transports

## Problem statement

Expose bounded enterprise database reads through MCP rather than arbitrary SQL, then compare HTTP service behaviour.

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

### Company table: services

**Size:** 10 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/services.csv](../../data/db/csv/services.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `service` | string; absent 0, null 0 | Service key joining services.service. |
| `description` | string; absent 0, null 0 | Service description. |

### Company table: service_incidents

**Size:** 12 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/service_incidents.csv](../../data/db/csv/service_incidents.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `incident_id` | string; absent 0, null 0 | Synthetic incident primary key. |
| `service` | string; absent 0, null 0 | Service key joining services.service. |
| `region` | string; absent 0, null 0 | AMER, EMEA or APAC geography key. |
| `status` | string; absent 0, null 0 | Table-specific state: inspect SQL CHECK constraints and observed values rather than sharing one enum across tables. |
| `started_at` | string; absent 0, null 0 | Timestamp when the incident began. |
| `resolved_at` | string; absent 0, null 0 | Incident resolution timestamp; blank denotes unresolved in CSV. |
| `message` | string; absent 0, null 0 | Human-readable synthetic incident impact/evidence. |

## How this session uses the data

Use fixed query inputs and parameterized lookups with row limits; inspect key relationships and actual database grants. Current reference assets tools read CSV snapshots.

## Outputs and evidence

Three-server HTTP checks and a real SELECT-only PostgreSQL role denial test; CSV read-only behaviour is not a database-permission proof.

The curriculum exit criterion is: Three-server HTTP transcripts and database-role write denial. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/mcp_servers/servers.py](../../src/copilot/mcp_servers/servers.py)
- [src/copilot/mcp_servers/client.py](../../src/copilot/mcp_servers/client.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
