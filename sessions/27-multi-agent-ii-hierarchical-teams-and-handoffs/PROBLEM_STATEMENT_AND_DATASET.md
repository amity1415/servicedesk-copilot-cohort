# Session 27: problem statement and dataset metadata

## Multi-agent II: hierarchical teams and handoffs

## Problem statement

Coordinate the onboarding subteam and hand unresolved work to an analyst with complete evidence.

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

### Runtime records: threads

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, employee, state. Ownership is checked; state is JSON, including the frozen retry draft. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: onboarding_steps

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

candidate, step, evidence. Composite key (candidate, step); includes verified HR evidence and simulated IT work items. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

## How this session uses the data

Carry candidate/manager IDs, dependency state, evidence, steps tried and the suggested next action across handoffs without transferring arbitrary executable instructions.

## Outputs and evidence

IT work-item evidence and an analyst case summary; a summary alone is not evidence that provisioning ran.

The curriculum exit criterion is: IT onboarding trace and analyst queue case with full evidence summary. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/agents/planning.py](../../src/copilot/agents/planning.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
