# Session 01: problem statement and dataset metadata

## Kickoff and project setup

## Problem statement

Establish a reproducible engineering baseline for Larkhaven's fragmented IT support records before choosing a model.

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

### Fixed acceptance identities and source manifest

**Size:** 2 files. **Origin:** datagen/people.py: PERSONAS and datagen/__main__.py: build_manifest/personas_markdown.

- [data/personas.md](../../data/personas.md)
- [data/manifest.json](../../data/manifest.json)

Eight fixed personas make acceptance checks reproducible. manifest.json records company/as_of/seed/counts and byte length/SHA-256 for seed files; it does not cover later evals or runtime outputs.

## How this session uses the data

Inspect category frequencies, source timestamps and the snapshot boundary; distinguish the 300-person sample from the fictional 10,000-person company.

## Outputs and evidence

Ticket counts, verified source manifest and a working environment; no model training is needed.

The curriculum exit criterion is: Clean-install transcript, ticket counts and a decision record naming the three enterprise boundaries. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/config.py](../../src/copilot/config.py)
- [src/copilot/logging_setup.py](../../src/copilot/logging_setup.py)
- [src/copilot/tickets.py](../../src/copilot/tickets.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
