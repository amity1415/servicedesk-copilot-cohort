# RAG sessions 5 through 8

The instructor authorized implementation of sessions 5–8 as one batch, then actual
validation. Session 4's live-model gate remains pending and is not falsely marked
complete. The exception is explicit; it does not waive this batch's validation.

Implemented scope: twenty-source vector/extractive baseline and draft questions;
full mixed-format ingestion with trusted policy/runbook metadata and invalidation;
fixed/recursive inspection; true local neural semantic boundaries and section-level
parent-child context. TF-IDF cosine is the retrieval baseline, not neural embeddings.
The local sentence encoder is a separate pinned CPU ONNX model used in semantic
chunking. Its weights live under ignored .work/models, never in normal Git history.

The normalized twenty-source fixture is derived from original Markdown/HTML with
source hashes, avoiding an invented Markdown-only origin for the HTML Mac article.
All original data files and existing evaluation labels are retained unchanged.
Additional questions remain draft labels requiring instructor review.

Main CLI: rag-demo, rag-ask, rag-ingest, rag-chunks, rag-benchmark and
rag-model-prepare. The API and documents MCP factory select the same VectorRag
service implementation. Existing role/OS/region/version constraints still apply.
The running service must be restarted to load changed Python modules; a temporary
isolated API smoke test will be used during validation before any restart.

This file describes implementation scope. Validation and completion/commit status
are recorded separately in sessions/implementation_manifest.json and batch evidence.


## Observed initial results

The integrated regression suite passed 111 tests. Ingestion produced 150 documents,
zero skips and zero changes on its second unchanged run. On 20 draft questions,
fixed/recursive document Recall@5 was 0.80; semantic/parent-child was 0.75. These
are local draft-label comparisons, not reviewed release metrics. Runtime totals
include index construction/import/cache effects and are not a production p95.
Recursive remains the application default. The fixed strategy created 237 chunks,
recursive 209, semantic 1770 and parent-child 764. Two atomic units exceed the soft
size target under structure-preserving strategies; they are retained, not truncated.

The model repository is sentence-transformers/all-MiniLM-L6-v2, pinned in
policies/semantic_model.json. All weights stay outside Git in .work/models. The
running pre-existing API/UI processes are not automatically replaced by changing
Python files. Restart the API on 8082 (and MCP services when used) to load the new
pipeline in those processes; isolated real HTTP validation uses the same factory.
