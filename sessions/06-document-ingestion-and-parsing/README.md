# Session 06: Document ingestion and parsing

[Actual cumulative Python build guide](BUILD_GUIDE.md)

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 05 is the starting point. This increment becomes part of the same application and is retained in session 07.

## Engineering objective

Parsing is a data engineering stage. A content hash detects changed bytes but metadata changes also affect access control. Missing audience must fail closed. Tables need structural inspection rather than a nonempty-text assertion.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Load Markdown frontmatter and HTML metadata; extract PDF layout text and DOCX tables; normalize one Document schema; write a content-hash manifest; rerun ingestion; review skipped-file log and SLA rows.

## Reference implementation

- [src/copilot/rag/pipeline.py](../../src/copilot/rag/pipeline.py)

Run the adjacent `reference.py` from the project root. It executes this session's own cumulative solution source. The matching feature also runs through the main application. This RAG batch is validated with real local retrieval/semantic inference; live LLM quality remains a separate gate.

## Deliberate failure exercise

Remove an audience field and prove the document is invisible to employees; withdraw a source and compare manifests. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Full-corpus parse count, zero unexpected skips, second-run changed count zero and inspected SLA text. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
