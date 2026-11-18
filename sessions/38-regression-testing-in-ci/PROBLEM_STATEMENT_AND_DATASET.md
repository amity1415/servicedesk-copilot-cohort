# Session 38: problem statement and dataset metadata

## Regression testing in CI

## Problem statement

Block regressions by freezing data, prompts, policy and index identity and separating offline checks from live quality gates.

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

### MCP tool schema snapshot

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** scripts/snapshot_contracts.py introspects registered tool inputs.

- [tests/contracts/mcp_schemas.json](../../tests/contracts/mcp_schemas.json)

Schema metadata, not employee training examples. Compare snapshots in CI and review breaking changes; never auto-approve a changed snapshot.

### Release identity and thresholds

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** Authored release configuration.

- [release/manifest.yaml](../../release/manifest.yaml)

Records model/prompt/index/policy and target metrics. Unconfigured revisions and null measurements do not certify readiness.

## How this session uses the data

Track dataset split/review status and hashes alongside release model/index/prompt/policy versions. Seeded data checksums do not automatically cover evaluation files.

## Outputs and evidence

CI artifacts and intentional-regression rejection; included CI runs offline checks and still needs full-stack/nightly quality gates.

The curriculum exit criterion is: CI workflow, explicit thresholds and demonstrated regression rejection. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
- [release/manifest.yaml](../../release/manifest.yaml)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
