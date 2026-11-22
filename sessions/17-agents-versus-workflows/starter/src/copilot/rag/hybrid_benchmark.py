"""Measure PostgreSQL keyword, vector and hybrid rankings on the same draft labels."""

import json
import re
from statistics import mean
from time import perf_counter

from copilot.rag.service import VectorRag, baseline_directory


def compare_hybrid(data):
    path = baseline_directory(data) / "questions.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rag = VectorRag.with_postgres(data, hybrid=True)
    results = {}
    for ranking in ("vector", "keyword", "hybrid"):
        rows = []
        for case in cases:
            started = perf_counter()
            hits = rag.search(case["question"], os_name=case.get("os"), ranking=ranking)
            elapsed = (perf_counter() - started) * 1000
            expected = set(case["expected_articles"])
            actual = {item.document_id for item in hits}
            rows.append(
                {
                    "id": case["id"],
                    "subset": "code"
                    if re.search(r"\b\d{3,}\b", case["question"])
                    else "paraphrase",
                    "retrieved": sorted(actual),
                    "recall_at_5": len(expected & actual) / len(expected) if expected else None,
                    "query_ms": elapsed,
                }
            )
        results[ranking] = {
            "subsets": {
                subset: {
                    "cases": len(values),
                    "recall_at_5": mean(values),
                }
                for subset in ("code", "paraphrase")
                if (
                    values := [
                        row["recall_at_5"]
                        for row in rows
                        if row["subset"] == subset and row["recall_at_5"] is not None
                    ]
                )
            },
            "mean_query_ms": mean(row["query_ms"] for row in rows),
            "cases": rows,
        }
    return {
        "mode": "postgres-hybrid-comparison",
        "label_status": "draft, requires instructor review",
        "question_count": len(cases),
        "rankings": results,
    }
