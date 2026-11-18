# Session 39: problem statement and dataset metadata

## Tracing, observability and monitoring

## Problem statement

Observe request cost, latency, tool failures and feedback without leaking personal-data-shaped inputs into telemetry.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Runtime records: audit

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, actor, action, outcome, created. Records authorized/denied/failed operations and feedback events. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Runtime records: threads

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.

id, employee, state. Ownership is checked; state is JSON, including the frozen retry draft. Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.

### Operational observations

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** Emitted while running the API/tools/model; optional OTLP export and bounded in-memory samples.

- [src/copilot/telemetry.py](../../src/copilot/telemetry.py)

Current measurement rows: operation, seconds, error. Dashboard fields: sample_count, request_p95_s, operation_error_rate, cost_per_resolved_request and cost_status. Provider tokens and trace/span IDs are operational metadata, not training labels. No durable collector dataset is bundled.

## How this session uses the data

Use request/trace/span correlation, safe role and operation names, provider token usage and an explicit price version. Process-local p95 samples are not durable fleet metrics.

## Outputs and evidence

Cross-service traces and dashboards with measured cost/latency; absent prices/usage remain unknown rather than zero.

The curriculum exit criterion is: Cross-service trace, dashboard and measured knowledge-answer p95; cost has no fabricated default. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [telemetry/](../../telemetry/)
- [src/copilot/ui/chat.py](../../src/copilot/ui/chat.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
