# Session 06 actual RAG implementation

This session has cumulative `starter/src/copilot` and `solution/src/copilot` trees.
It inherits the preceding solution and adds mixed-format ingestion and trusted metadata.

Run from `D:\AI-Engineering\servicedesk-copilot`:

```powershell
.\.venv\Scripts\python.exe scripts/session.py test 6 --variant starter --previous-only
.\.venv\Scripts\python.exe scripts/session.py test 6 --variant starter
.\.venv\Scripts\python.exe scripts/session.py run 6
.\.venv\Scripts\python.exe scripts/session.py test 6
```

The untouched starter must retain old behaviour and fail the new acceptance work.
Implement the functions used by `tests/test_rag_ingestion.py`, then compare with the solution. Read the adjacent problem/data guide; record actual evidence rather than desired metrics.

1. Inspect `rag/pipeline.py` contracts and the current loaders/chunker/service code.
2. Follow the named new acceptance tests from inputs to the missing behaviour.
3. Preserve authorization before scoring and provenance in every result.
4. Run the actual session command and the corresponding root `copilot rag-*` command.
5. Save report paths, run the accumulated tests and participate in the approved 5–8 batch validation.

Session 5 uses twenty trainer-normalized Markdown sources. Some originate from HTML,
including the Mac article; original_source/original_sha256 preserve that lineage.
The twenty questions are drafts, not reviewed golden truth. Session 6 ingests all
150 supported files and reports changes/skips/removals. Session 7 retains atomic
steps even when an atomic unit exceeds the target size. Session 8 uses the pinned
local MiniLM ONNX encoder for semantic boundaries and compares all four strategies
on the same full corpus and questions. Retrieval scoring remains TF-IDF cosine so
the chunking comparison does not also change the retrieval model.

For semantic model preparation (public download, no paid inference):

```powershell
.\.venv\Scripts\copilot.exe rag-model-prepare
```

Use `scripts/session.py run 6 -- rag-benchmark` for its available strategy
comparison. Session 8's default already runs all four strategies. Reports are under
`reports/cohort/session-06/solution/`; root runs write under
`reports/integrated/rag/`. The answer mode is explicitly extractive. Live LLM
generation, later hybrid/reranking modules and reviewed release quality are not
claimed by this local batch.

Export with `scripts/session.py export 6 --out .work/checkpoints/session-06`.
Create a separate environment there and install `.[dev]`, plus `[rag-local]` for
session 8's actual neural run. Prepare the pinned model before the semantic command.
Do not install the checkpoint into the running application's environment.
