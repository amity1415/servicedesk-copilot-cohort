# Session 28: problem statement and dataset metadata

## Guardrails and prompt injection defence

## Problem statement

Resist instructions hidden in source text and prevent forbidden effects even when an attack evades pattern detection.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

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

## How this session uses the data

Attack records carry id/text/expected/review_status; open ticket INC0020058 is a separate seeded injection. Audit outcomes and authoritative state matter more than refusal prose.

## Outputs and evidence

25-case effect-oriented red-team results; the supplied detector coverage report alone is not an attack-success measurement.

The curriculum exit criterion is: 25-case report with state assertions, zero forbidden effects and explicit detector limitations. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/guardrails/checks.py](../../src/copilot/guardrails/checks.py)
- [evals/redteam/](../../evals/redteam/)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
