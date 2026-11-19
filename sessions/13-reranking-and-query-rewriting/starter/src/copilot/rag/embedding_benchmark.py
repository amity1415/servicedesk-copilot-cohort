"""Compare pinned retrieval models on the same draft questions."""

import json
import platform
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from copilot.rag.semantic_encoder import OnnxEncoder, model_directory
from copilot.rag.service import VectorRag, baseline_directory, documents_from


def compare_embeddings(data, second_model=None):
    first_model = model_directory()
    second_model = Path(second_model or first_model.with_name("minilm-l12"))
    questions = baseline_directory(data) / "questions.jsonl"
    cases = [json.loads(line) for line in questions.read_text(encoding="utf-8").splitlines()]
    documents = documents_from(data)
    results = []
    with TemporaryDirectory() as directory:
        cache = Path(directory) / "vectors.sqlite3"
        for model in (first_model, second_model):
            encoder = OnnxEncoder(model, cache=cache)
            if results and encoder.identity == results[0]["identity"]:
                raise ValueError("embedding comparison requires two distinct model identities")
            started = perf_counter()
            rag = VectorRag(documents, "recursive", retrieval_encoder=encoder)
            indexing_seconds = perf_counter() - started
            rows = []
            for case in cases:
                started = perf_counter()
                hits = rag.search(case["question"], os_name=case.get("os"))
                latency = perf_counter() - started
                expected = set(case["expected_articles"])
                actual = {hit.document_id for hit in hits}
                rows.append(
                    {
                        "id": case["id"],
                        "retrieved": sorted(actual),
                        "missed": sorted(expected - actual),
                        "error_code_query": bool(re.search(r"\b\d{3,}\b", case["question"])),
                        "recall_at_5": len(expected & actual) / len(expected) if expected else None,
                        "latency_seconds": latency,
                    }
                )
            with closing(sqlite3.connect(cache)) as db:
                before = db.execute("SELECT count(*) FROM vectors").fetchone()[0]
                misses = encoder.encoded_misses
                if not misses:
                    raise RuntimeError("fresh model identity unexpectedly reused cached vectors")
                repeat = OnnxEncoder(model, cache=cache)
                repeated_rag = VectorRag(documents, "recursive", retrieval_encoder=repeat)
                for case, row in zip(cases, rows, strict=True):
                    hits = repeated_rag.search(case["question"], os_name=case.get("os"))
                    if sorted({hit.document_id for hit in hits}) != row["retrieved"]:
                        raise RuntimeError("cached retrieval changed the result")
                after = db.execute("SELECT count(*) FROM vectors").fetchone()[0]
            if repeat.encoded_misses or before != after:
                raise RuntimeError("repeat retrieval did not reuse the persistent cache")
            measured = [row["recall_at_5"] for row in rows if row["recall_at_5"] is not None]
            results.append(
                {
                    "model": encoder.manifest,
                    "identity": encoder.identity,
                    "indexing_seconds": indexing_seconds,
                    "recall_at_5": sum(measured) / len(measured),
                    "cold_vector_misses": misses,
                    "repeat_vector_misses": repeat.encoded_misses,
                    "cache_rows_before_repeat": before,
                    "cache_rows_after_repeat": after,
                    "cases": rows,
                }
            )
    return {
        "mode": "local-neural-retrieval-comparison",
        "hardware": {"machine": platform.machine(), "processor": platform.processor()},
        "question_count": len(cases),
        "label_status": "draft, requires instructor review",
        "models": results,
    }
