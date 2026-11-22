"""Compare reranking with the same authorized hybrid candidate pipeline."""

import json
from statistics import mean, quantiles
from time import perf_counter

from copilot.rag.reranker import OnnxReranker
from copilot.rag.service import VectorRag, baseline_directory


def compare_reranker(data):
    path = baseline_directory(data) / "questions.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    reranker = OnnxReranker()
    rag = VectorRag.with_postgres(data, hybrid=True, reranker=reranker)
    results = {}
    for ranking in ("hybrid", "reranked"):
        rows = []
        for case in cases:
            start = perf_counter()
            hits = rag.search(case["question"], os_name=case.get("os"), ranking=ranking)
            elapsed_ms = (perf_counter() - start) * 1000
            actual = {item.document_id for item in hits}
            expected = set(case["expected_articles"])
            rows.append(
                {
                    "id": case["id"],
                    "retrieved": sorted(actual),
                    "recall_at_5": len(expected & actual) / len(expected) if expected else None,
                    "latency_ms": elapsed_ms,
                }
            )
        results[ranking] = {
            "recall_at_5": mean(
                row["recall_at_5"] for row in rows if row["recall_at_5"] is not None
            ),
            "p95_latency_ms": quantiles(
                [row["latency_ms"] for row in rows], n=100, method="inclusive"
            )[94],
            "cases": rows,
        }
    return {
        "mode": "local-reranking-comparison",
        "question_count": len(cases),
        "label_status": "draft, requires instructor review",
        "model": reranker.manifest,
        "rankings": results,
    }
