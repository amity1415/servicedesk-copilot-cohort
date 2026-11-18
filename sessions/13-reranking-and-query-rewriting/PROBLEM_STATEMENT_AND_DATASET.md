# Session 13: problem statement and dataset metadata

## Reranking and query rewriting

## Problem statement

Resolve follow-up questions in the right conversation and rerank only authorized candidates.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

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

### Runtime records: threads

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, employee, state. Ownership is checked; state is JSON, including the frozen retry draft. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

## How this session uses the data

Bind thread ownership to identity; preserve explicit error codes during rewriting and separate 30-candidate recall from five-result reranking quality.

## Outputs and evidence

Two-turn article IDs, reranking quality change and added latency; scripted rewriting is not a measured model rewrite.

The curriculum exit criterion is: Two-turn retrieval tests, reranking delta and p95 latency measurement. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/rag/advanced.py](../../src/copilot/rag/advanced.py)
- [src/copilot/tools/runtime.py](../../src/copilot/tools/runtime.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
