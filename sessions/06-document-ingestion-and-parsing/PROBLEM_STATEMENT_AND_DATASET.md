# Session 06: problem statement and dataset metadata

## Document ingestion and parsing

## Problem statement

Turn mixed-format source documents into a repeatable and auditable corpus without losing tables or access metadata.

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

### Policy PDFs and version register

**Size:** 12 records. **Origin:** datagen/content/policies.py and datagen/docs.py; old versions are explicitly authored, not scraped.

- [data/policies/register.csv](../../data/policies/register.csv)
- [data/policies/POL-003_v4.0.pdf](../../data/policies/POL-003_v4.0.pdf)

PDF text alone may not identify a superseded version. Missing PDF audience metadata must not silently make the document visible to employees.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id` | string; absent 0, null 0 | Policy ID, e.g. POL-003; joins KB related_policy. |
| `title` | string; absent 0, null 0 | Policy title. |
| `version` | string; absent 0, null 0 | Document version string. |
| `effective_date` | string; absent 0, null 0 | Date this version starts applying. |
| `status` | string; absent 0, null 0 | current or superseded; the register is authoritative for this distinction. |
| `superseded_by` | string; absent 0, null 0 | Successor version, blank for current records. |
| `owner` | string; absent 0, null 0 | Accountable synthetic policy owner. |
| `file` | string; absent 0, null 0 | Exact PDF filename in data/policies/. |

### IT-only runbooks

**Size:** 15 files. **Origin:** datagen/content/runbooks.py and datagen/docs.py.

- [data/runbooks/RB-001.docx](../../data/runbooks/RB-001.docx)

DOCX files contain paragraphs and tables. They are not intended for employee retrieval; current loader does not automatically enrich all metadata.

| Field | Representation / missingness | Meaning |
| --- | --- | --- |
| `id/title/version/effective` | source document field | Runbook identity and version from authored content. |
| `group/risk/approval` | source document field | Accountable support group, read/write risk tier and approver requirement. |
| `prerequisites/steps/verification/rollback` | source document field | Procedure inputs, ordered actions, evidence and recovery instructions. |
| `audience` | source document field | All runbooks are IT-only by source contract; attach enforced it-staff metadata during ingestion. |

### SLA, catalogue and glossary references

**Size:** 4 files. **Origin:** Authored catalogue/reference definitions rendered by datagen/docs.py.

- [data/reference/glossary.md](../../data/reference/glossary.md)
- [data/reference/sla_matrix.pdf](../../data/reference/sla_matrix.pdf)
- [data/reference/software_catalogue.csv](../../data/reference/software_catalogue.csv)
- [data/reference/software_catalogue.html](../../data/reference/software_catalogue.html)

Includes sla_matrix.pdf, software_catalogue.csv, software_catalogue.html and glossary.md. Preserve table rows/columns and treat charges/SLA values as fictional training policy.

## How this session uses the data

Read Markdown frontmatter, kb:-prefixed HTML tags, the policy register and runbook restrictions. Preserve source path, content digest and skip reasons; PDFs/DOCX require metadata enrichment rather than guessing visibility.

## Outputs and evidence

Normalized Document records and ingestion reports; the second unchanged run reports zero changes and no unexpected skipped files.

The curriculum exit criterion is: Full-corpus parse count, zero unexpected skips, second-run changed count zero and inspected SLA text. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.

## Before running

1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.
2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.
3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.
4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.
5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.

## Reference implementation and scope

- [src/copilot/rag/pipeline.py](../../src/copilot/rag/pipeline.py)

The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).
