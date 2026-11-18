# Session 02: problem statement and dataset metadata

## ML basics on ticket data

## Problem statement

Predict ticket category and priority from information actually available when the request arrives; discover repeated issue clusters.

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

## How this session uses the data

Use short_description plus description as X; category and priority are separate y labels. Preserve a grouped holdout by normalized short description and fit TF-IDF on training rows only.

## Outputs and evidence

Precision, recall, macro F1, confusion matrices and cluster terms in reports; inspect the weakest class instead of relying on accuracy.

The curriculum exit criterion is: Category and priority precision, recall, macro F1, support and confusion matrices; weakest-class error analysis. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/ml/train.py](../../src/copilot/ml/train.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
