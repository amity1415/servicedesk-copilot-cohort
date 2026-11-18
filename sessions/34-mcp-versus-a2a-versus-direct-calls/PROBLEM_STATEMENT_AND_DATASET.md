# Session 34: problem statement and dataset metadata

## MCP versus A2A versus direct calls

## Problem statement

Choose direct calls, MCP or A2A by ownership/trust boundaries and benchmark equivalent service-status work.

This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.

## How the data is obtained

All seed records come from the locally generated Larkhaven synthetic pack (snapshot 2026-11-13, seed 42). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.

Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.

## Input datasets and field metadata

### Company table: services

**Size:** 10 records. **Origin:** Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.

- [data/db/csv/services.csv](../../data/db/csv/services.csv)

CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `service` | string; absent 0, null 0 | Service key joining services.service. |
| `description` | string; absent 0, null 0 | Service description. |

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

### MCP tool schema snapshot

**Size:** runtime/configuration artifact; no fixed record count. **Origin:** scripts/snapshot_contracts.py introspects registered tool inputs.

- [tests/contracts/mcp_schemas.json](../../tests/contracts/mcp_schemas.json)

Schema metadata, not employee training examples. Compare snapshots in CI and review breaking changes; never auto-approve a changed snapshot.

## How this session uses the data

Freeze the service/region query and payload before timing; preserve canonical input schemas, sample counts, warm-up policy and actual transport configuration.

## Outputs and evidence

Measured latency/code-complexity ADR and schema-drift check; a schema snapshot is not a latency benchmark.

The curriculum exit criterion is: Measured transport ADR and version-controlled schema snapshot. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/mcp_servers/client.py](../../src/copilot/mcp_servers/client.py)
- [tests/](../../tests/)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
