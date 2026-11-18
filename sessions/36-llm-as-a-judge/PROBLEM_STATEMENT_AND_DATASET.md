# Session 36: problem statement and dataset metadata

## LLM-as-a-judge

## Problem statement

Calibrate an answer-quality judge against independent human labels rather than assuming the judge is authoritative.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

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

### Required human calibration examples (not supplied)

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** Instructor/learner annotation required in session 36.

Expected schema: example_id, question, sources, candidate_answer, rubric_version, human_score, annotator/review metadata. Store judge_score and judge_model/revision separately. This describes the required future artifact, not an existing file or a completed set of 30 labels.

## How this session uses the data

Keep question, sources, candidate answer, rubric/model version, human score and judge score separate; 30 independent human-labelled examples are required but not supplied.

## Outputs and evidence

Agreement/confusion/uncertainty report; never relabel generated or self-judged scores as human annotations.

The curriculum exit criterion is: Agreement report against 85 percent starting target, with model, rubric version and uncertainty. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [evals/rubrics/](../../evals/rubrics/)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
