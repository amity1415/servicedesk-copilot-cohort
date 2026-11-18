"""Honest retrieval baseline; answer and task metrics require separate labels."""

import json
from pathlib import Path

from copilot.rag.pipeline import Retriever


def retrieval_report(root: Path) -> dict:
    dataset = [
        json.loads(line)
        for line in (root / "evals/rag_golden.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    retriever = Retriever.from_data(root / "data")
    rows = []
    for item in dataset:
        expected = set(item["expected_articles"])
        actual = {c.document_id for c in retriever.search(item["question"])}
        rows.append(
            {
                "id": item["id"],
                "recall_at_5": len(expected & actual) / len(expected) if expected else None,
                "retrieved": sorted(actual),
                "review_status": item["review_status"],
            }
        )
    answerable = [row["recall_at_5"] for row in rows if row["recall_at_5"] is not None]
    report = {
        "mode": "lexical-baseline-on-draft-labels",
        "recall_at_5": sum(answerable) / len(answerable),
        "context_precision": None,
        "faithfulness": None,
        "answer_relevance": None,
        "release_gate_passed": False,
        "reason": "Review labels and run answer metrics before assessing release targets",
        "cases": rows,
    }
    path = root / "reports/retrieval.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = retrieval_report(Path.cwd())
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))
