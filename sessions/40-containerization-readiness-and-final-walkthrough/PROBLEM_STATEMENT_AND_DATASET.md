# Session 40: problem statement and dataset metadata

## Containerization, readiness and final walkthrough

## Problem statement

Demonstrate the complete support lifecycle from a clean environment with reproducible data and observed release evidence.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Historical support tickets

**Size:** 5,000 records. **Origin:** datagen/tickets.py: TicketFactory.historical; topic wording from datagen/content/ and seeded population context.

- [data/tickets/historical_tickets.jsonl](../../data/tickets/historical_tickets.jsonl)

JSONL: one object per line. Labels and resolutions are generated, not independently observed real-world outcomes. Tickets cover May 2025 to November 2026 in this fixture.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `ticket_id` | string; absent 0, null 0 | Unique historical incident identifier; provenance/join key, not a predictive feature. |
| `created_at` | string; absent 0, null 0 | UTC ISO timestamp when the synthetic ticket was raised; supports temporal analysis. |
| `resolved_at` | string; absent 0, null 0 | UTC ISO timestamp when it was resolved; post-outcome information, exclude from request-time features. |
| `requester_id` | string; absent 0, null 0 | Employee ID joining employees.employee_id; use only for authorized context, not as an intent shortcut. |
| `department` | string; absent 0, null 0 | Synthetic requester department; contextual export field. |
| `region` | string; absent 0, null 0 | AMER, EMEA or APAC; requester context for regional support. |
| `office` | string; absent 0, null 0 | Synthetic office; joins offices.office. |
| `channel` | string; absent 0, null 0 | How the request arrived, such as portal or email; inspect observed values in the dictionary. |
| `device_os` | string; absent 0, null 0 | Export display label, such as Windows 11 or macOS; normalize before comparing with KB OS values. |
| `short_description` | string; absent 0, null 0 | User-supplied brief description; used with description as the ML input. |
| `description` | string; absent 0, null 0 | User-supplied issue text; may be vague, misspelled, non-IT or adversarial. |
| `category` | string; absent 0, null 0 | Classification target across eight IT categories; some generated labels are intentionally misfiled. |
| `subcategory` | string; absent 0, null 0 | More detailed topic label; exclude as an obvious category shortcut in baseline ML. |
| `priority` | string; absent 0, null 0 | Classification target P1–P4; synthetic sampling label, not an independently adjudicated impact/urgency assessment. |
| `assignment_group` | string; absent 0, null 0 | Destination support team; exclude from the baseline features because it encodes downstream handling. |
| `status` | string; absent 0, null 0 | Workflow state; historical rows are closed, open seed rows have active states. |
| `resolution_code` | string; absent 0, null 0 | Closure outcome label; post-resolution information, not a request-time feature. |
| `resolution_notes` | string; absent 0, null 0 | Synthetic analyst resolution; useful when drafting reference answers, not a classifier feature. |
| `kb_article_id` | null/string; absent 0, null 1239 | Linked resolving KB ID when available; reference label for retrieval, never an input clue to the answering model. |
| `reopened` | boolean; absent 0, null 0 | Boolean indicating a simulated reopen; post-outcome information. |

### Knowledge-base corpus

**Size:** 120 files. **Origin:** Authored Topic/TicketSpec templates in datagen/content/ expanded by datagen/kb.py per OS or region.

- [data/kb/index.csv](../../data/kb/index.csv)
- [data/kb/KB-1001.md](../../data/kb/KB-1001.md)
- [data/kb/KB-1017.html](../../data/kb/KB-1017.html)

Markdown YAML frontmatter and HTML <meta name="kb:..."> encode the same metadata. Parser normalization currently converts metadata values to strings; distinguish that representation from source-level arrays/nulls.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string | Stable article identifier, e.g. KB-1017; citation and retrieval-label join key. |
| `title` | string | Human-readable topic; filenames contain IDs rather than titles. |
| `type` | string | how-to, troubleshooting or reference. |
| `system` | string | Fictional supported product/service such as SecureTunnel VPN. |
| `category` | string | Top-level support domain. |
| `subcategory` | string | Specific support topic within the category. |
| `os` | string | windows, macos, ios, android or any; scope filter, not a display OS/version string. |
| `region` | string | global, AMER, EMEA or APAC; regional applicability. |
| `audience` | string | employee or it-staff. Restrict IT content before retrieval; this field is distinct from employee application role. |
| `version` | string | Authored/generated source version string; not safe to sort as a float. |
| `effective_date` | string | ISO date from which this document applies. |
| `last_reviewed` | string | ISO source review date in the synthetic snapshot. |
| `owner` | string | Accountable synthetic support team. |
| `status` | string | KB source status; current in the authored KB corpus. Policy status comes from its separate register. |
| `error_codes` | array | Exact identifiers, e.g. 809 or LID-MFA-102; preserve them during parsing and rewriting. |
| `related_policy` | string | Optional policy ID linking the how-to to governing policy. |

### Policy PDFs and version register

**Size:** 12 records. **Origin:** datagen/content/policies.py and datagen/docs.py; old versions are explicitly authored, not scraped.

- [data/policies/register.csv](../../data/policies/register.csv)
- [data/policies/POL-003_v4.0.pdf](../../data/policies/POL-003_v4.0.pdf)

PDF text alone may not identify a superseded version. Missing PDF audience metadata must not silently make the document visible to employees.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string; absent 0, null 0 | Policy ID, e.g. POL-003; joins KB related_policy. |
| `title` | string; absent 0, null 0 | Policy title. |
| `version` | string; absent 0, null 0 | Document version string. |
| `effective_date` | string; absent 0, null 0 | Date this version starts applying. |
| `status` | string; absent 0, null 0 | current or superseded; the register is authoritative for this distinction. |
| `superseded_by` | string; absent 0, null 0 | Successor version, blank for current records. |
| `owner` | string; absent 0, null 0 | Accountable synthetic policy owner. |
| `file` | string; absent 0, null 0 | Exact PDF filename in data/policies/. |

### IT-only runbooks

**Size:** 15 files. **Origin:** datagen/content/runbooks.py and datagen/docs.py.

- [data/runbooks/RB-001.docx](../../data/runbooks/RB-001.docx)

DOCX files contain paragraphs and tables. They are not intended for employee retrieval; current loader does not automatically enrich all metadata.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id/title/version/effective` | source document field | Runbook identity and version from authored content. |
| `group/risk/approval` | source document field | Accountable support group, read/write risk tier and approver requirement. |
| `prerequisites/steps/verification/rollback` | source document field | Procedure inputs, ordered actions, evidence and recovery instructions. |
| `audience` | source document field | All runbooks are IT-only by source contract; attach enforced it-staff metadata during ingestion. |

### SLA, catalogue and glossary references

**Size:** 4 files. **Origin:** Authored catalogue/reference definitions rendered by datagen/docs.py.

- [data/reference/glossary.md](../../data/reference/glossary.md)
- [data/reference/sla_matrix.pdf](../../data/reference/sla_matrix.pdf)
- [data/reference/software_catalogue.csv](../../data/reference/software_catalogue.csv)
- [data/reference/software_catalogue.html](../../data/reference/software_catalogue.html)

Includes sla_matrix.pdf, software_catalogue.csv, software_catalogue.html and glossary.md. Preserve table rows/columns and treat charges/SLA values as fictional training policy.

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

### Draft RAG evaluation questions

**Size:** 100 records. **Origin:** scripts/prepare_evals.py; separate from the datagen seed-pack generator.

- [evals/rag_golden.jsonl](../../evals/rag_golden.jsonl)

First 90 distinct linked KB IDs encountered in historical ticket order yield 90 provisional question/answer pairs; ten authored unanswerables are appended. Distinct IDs are not a guarantee of independent template families. Current evaluator ignores split and reports on the supplied pool, so its score is not a heldout-only result.

**Observed review status:** draft: 100.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string; absent 0, null 0 | Evaluation case ID. |
| `question` | string; absent 0, null 0 | Request text derived from a historical ticket or an authored unanswerable prompt. |
| `expected_articles` | array; absent 0, null 0 | List of relevant KB IDs; empty for ten authored unanswerable cases. Labels are provisional. |
| `reference_answer` | string; absent 0, null 0 | Draft answer based on resolution notes, or an authored abstention expectation. |
| `source_ticket` | string; absent 10, null 0 | Historical ticket provenance; absent on manually specified unanswerable cases. |
| `os` | string; absent 10, null 0 | Original ticket device display label; absent on unanswerable cases and needs normalization for filtering. |
| `review_status` | string; absent 0, null 0 | Current value draft: not approved human ground truth. |
| `split` | string; absent 0, null 0 | development for the first 60 answerable cases; heldout for the remaining 30 answerable plus ten unanswerable cases. |

### Draft agent task set

**Size:** 40 records. **Origin:** scripts/prepare_evals.py; separate from the datagen seed-pack generator.

- [evals/agent_golden.jsonl](../../evals/agent_golden.jsonl)

Six authored acceptance scenarios plus the first 34 selected historical tickets. Expected end states need manual review; the dataset is not a validated agent benchmark yet.

**Observed review status:** draft: 40.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string; absent 0, null 0 | Agent evaluation case ID. |
| `request` | string; absent 0, null 0 | User scenario text, not an implementation command. |
| `user` | string; absent 0, null 0 | Synthetic employee identity under which the task should execute. |
| `expected_tool_calls` | array; absent 0, null 0 | Draft expected tool names; do not expose these labels to the agent. |
| `expected_end_state` | string; absent 0, null 0 | Draft observable result; many ticket-derived cases explicitly say review_required. |
| `forbidden_actions` | array; absent 0, null 0 | Effects/calls the test must forbid; scoring should inspect state, not only refusal wording. |
| `source` | string; absent 0, null 0 | One of the six acceptance scenarios or a source historical ticket ID. |
| `review_status` | string; absent 0, null 0 | draft until an instructor reviews the complete task expectation. |

### Draft adversarial scenario set

**Size:** 25 records. **Origin:** scripts/prepare_evals.py; separate from the datagen seed-pack generator.

- [evals/redteam/attacks.jsonl](../../evals/redteam/attacks.jsonl)

25 authored adversarial scenarios, not naturally collected attack traffic. Some require direct tool/concurrency fixtures rather than simply passing text to a detector.

**Observed review status:** draft: 25.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string; absent 0, null 0 | Attack case ID. |
| `text` | string; absent 0, null 0 | Authored malicious/forbidden scenario text. |
| `expected` | string; absent 0, null 0 | Desired absence of forbidden effects, requiring state-based checks. |
| `review_status` | string; absent 0, null 0 | draft until reviewed; not evidence the system resists every attack. |

### Release identity and thresholds

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** Authored release configuration.

- [release/manifest.yaml](../../release/manifest.yaml)

Records model/prompt/index/policy and target metrics. Unconfigured revisions and null measurements do not certify readiness.

## How this session uses the data

Verify manifest revision/checksums, fixture identities and absolute dates, reviewed evaluation versions and clean post-action state; preserve all six acceptance scenarios.

## Outputs and evidence

Six-request demonstration, evaluation reports, security/deployment checks and readiness evidence; local references do not certify an unrun production release.

The curriculum exit criterion is: Clean-machine demo, scan outputs and measured release targets before tagging v1.0. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [Dockerfile](../../Dockerfile)
- [docker-compose.yml](../../docker-compose.yml)
- [docs/INTEGRATION_STEPS.md](../../docs/INTEGRATION_STEPS.md)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
