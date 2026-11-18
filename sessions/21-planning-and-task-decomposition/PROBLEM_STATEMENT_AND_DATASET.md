# Session 21: problem statement and dataset metadata

## Planning and task decomposition

## Problem statement

Plan onboarding as dependent HR/IT work instead of falsely completing steps after a failed prerequisite.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Pending HR joiners

**Size:** 3 records. **Origin:** Fixed synthetic partner fixtures in datagen/people.py, exported by datagen/__main__.py.

- [data/hr/pending_joiners.json](../../data/hr/pending_joiners.json)

Nested JSON array. Some records are intentionally incomplete. A completed HR artifact verifies existing synthetic checklist data; it does not perform real HR work.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `candidate_id` | string; absent 0, null 0 | Stable synthetic pre-employment ID such as C-2041; distinct from employee IDs. |
| `full_name` | string; absent 0, null 0 | Fictional candidate name. |
| `department` | string; absent 0, null 0 | Destination department. |
| `job_title` | string; absent 0, null 0 | Planned role. |
| `office` | string; absent 0, null 0 | Planned work location. |
| `region` | string; absent 0, null 0 | Planned support geography. |
| `manager_id` | string; absent 0, null 0 | Hiring manager's employee ID; binds onboarding authorization. |
| `start_date` | string; absent 0, null 0 | Explicit fixture start date; Hannah Vogel's is 2026-11-16, now a historical synthetic date. |
| `cost_centre` | null/string; absent 0, null 1 | Synthetic budget unit; missing on the deliberately incomplete candidate. |
| `role_profile` | string; absent 0, null 0 | Role-profile ID joining role_profiles.profile_id. |
| `laptop_type` | string; absent 0, null 0 | Required synthetic device class. |
| `peoplehub_record` | string; absent 0, null 0 | complete or incomplete partner-record status. |
| `missing_fields` | array; absent 0, null 0 | Names of missing required HR fields. |
| `hr_checklist` | object; absent 0, null 0 | Nested contract, right-to-work, payroll and induction checks; induction includes a timezone offset. |

### Company table: role_profiles

**Size:** 10 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/role_profiles.csv](../../data/db/csv/role_profiles.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `profile_id` | string; absent 0, null 0 | Role-profile key joining role_profiles.profile_id. |
| `department` | string; absent 0, null 0 | Synthetic organizational unit. |
| `name` | string; absent 0, null 0 | Table-specific human-readable application, region or role-profile name. |
| `laptop_type` | string; absent 0, null 0 | Synthetic onboarding device class, e.g. Standard or Developer. |

### Company table: role_profile_apps

**Size:** 27 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/role_profile_apps.csv](../../data/db/csv/role_profile_apps.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `profile_id` | string; absent 0, null 0 | Role-profile key joining role_profiles.profile_id. |
| `app_id` | string; absent 0, null 0 | Application key joining software_catalogue.app_id. |

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

## How this session uses the data

Bind candidate_id, hiring manager and explicit start_date; map role_profile to recommended software and laptop type. Preserve plan dependencies and completion evidence.

## Outputs and evidence

Persisted dependency plan and failed-prerequisite blocking; do not infer next Monday from the machine clock.

The curriculum exit criterion is: Stored plan, dependency-order tests and a failed-step replanning trace. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/agents/planning.py](../../src/copilot/agents/planning.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
