# Session 35: problem statement and dataset metadata

## Evaluation strategy and golden datasets

## Problem statement

Create a defensible agent benchmark from historical support cases with measurable end states and forbidden actions.

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

The supplied 40 drafts start with six acceptance scenarios plus 34 ticket-derived cases; review each expected end state, reset policy and provenance before approving labels.

## Outputs and evidence

Reviewed task schema and isolated reset evidence; existing draft cases are not certified ground truth.

The curriculum exit criterion is: 40 reviewed tasks and reset proof for tickets, database and checkpoint state. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [evals/](../../evals/)
- [src/copilot/course/experiments.py](../../src/copilot/course/experiments.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
