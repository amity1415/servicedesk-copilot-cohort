"""In-memory vector retrieval with authorization before scoring and cited extraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from time import monotonic

from copilot.rag.loaders import load_document

_CORPUS_CACHE = {}


def baseline_directory(data):
    own = Path(__file__).resolve().parents[3] / "fixtures/rag-baseline"
    return own if own.exists() else Path(data).parent / "fixtures/rag-baseline"


def documents_from(data, baseline=False):
    base = baseline_directory(data) if baseline else Path(data)
    folders = (
        [base / "kb"]
        if baseline
        else [base / d for d in ("kb", "policies", "runbooks", "reference")]
    )
    paths = [
        path
        for folder in folders
        for path in sorted(folder.glob("*"))
        if path.suffix.lower() in {".md", ".html", ".pdf", ".docx"}
    ]
    signature = hashlib.sha256()
    for path in paths:
        signature.update(str(path.resolve()).encode())
        signature.update(path.read_bytes())
    sidecar = Path(data).parent / "policies/source_metadata.json"
    register = Path(data) / "policies/register.csv"
    for metadata_file in (sidecar, register):
        if metadata_file.exists():
            signature.update(metadata_file.read_bytes())
    key = signature.hexdigest()
    if key not in _CORPUS_CACHE:
        _CORPUS_CACHE.clear()
        _CORPUS_CACHE[key] = tuple(load_document(path) for path in paths)
    return list(_CORPUS_CACHE[key])


class VectorRag:
    def __init__(self, documents, strategy="fixed", size=1200, overlap=120, semantic_encoder=None):
        raise NotImplementedError("TODO: implement __init__; see this session's BUILD_GUIDE.md")

    @classmethod
    def from_data(cls, data, strategy="recursive", baseline=False, semantic_encoder=None):
        return cls(documents_from(data, baseline), strategy, semantic_encoder=semantic_encoder)

    def search(self, query, role="employee", os_name=None, region=None, k=5):
        raise NotImplementedError("TODO: implement search; see this session's BUILD_GUIDE.md")

    def answer(self, query, **kwargs):
        raise NotImplementedError("TODO: implement answer; see this session's BUILD_GUIDE.md")


def benchmark(data, strategies, questions=None, baseline=False, encoder=None):
    cases = [
        json.loads(line)
        for line in (questions or baseline_directory(data) / "questions.jsonl")
        .read_text()
        .splitlines()
    ]
    documents = documents_from(data, baseline)
    results = {}
    for strategy in strategies:
        started = monotonic()
        rag = VectorRag(documents, strategy, semantic_encoder=encoder)
        rows = []
        for case in cases:
            hits = rag.search(case["question"], os_name=case.get("os"), k=5)
            expected = set(case["expected_articles"])
            actual = {c.document_id for c in hits}
            rows.append(
                {
                    "id": case["id"],
                    "retrieved": sorted(actual),
                    "recall_at_5": len(expected & actual) / len(expected) if expected else None,
                }
            )
        values = [row["recall_at_5"] for row in rows if row["recall_at_5"] is not None]
        results[strategy] = {
            "chunks": len(rag.chunks),
            "recall_at_5": sum(values) / len(values),
            "elapsed_s": monotonic() - started,
            "oversize_chunks": sum(len(c.text) > 1200 for c in rag.chunks),
            "cases": rows,
        }
    return {
        "mode": "local-vector-retrieval-benchmark",
        "retrieval_encoder": "TF-IDF cosine",
        "question_count": len(cases),
        "document_count": len(documents),
        "label_status": "draft, requires instructor review",
        "release_gate_passed": False,
        "generation": "cited extraction; no paid LLM call",
        "semantic_encoder": getattr(encoder, "manifest", None),
        "strategies": results,
    }
