# Session 37: problem statement and dataset metadata

## Agent evaluation

## Problem statement

Score actual task completion, tool arguments and action ordering instead of plausible success text.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

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

### Runtime records: onboarding_steps

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

candidate, step, evidence. Composite key (candidate, step); includes verified HR evidence and simulated IT work items. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

## How this session uses the data

Inspect persisted end state for each task; evaluate policy-before-request, approval-before-fulfilment and forbidden calls against the recorded trajectory.

## Outputs and evidence

Task success, tool accuracy and zero-violation report on reviewed tasks; missing measurements cannot pass a release threshold.

The curriculum exit criterion is: Task success, tool accuracy and trajectory report; no target is claimed without measured run. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

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
