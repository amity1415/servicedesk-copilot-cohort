"""In-memory vector retrieval with authorization before scoring and cited extraction."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from time import monotonic

from copilot.rag.loaders import is_allowed, load_document

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
    def __init__(
        self,
        documents,
        strategy="fixed",
        size=1200,
        overlap=120,
        semantic_encoder=None,
        retrieval_encoder=None,
        persistent_index=None,
        hybrid=False,
        reranker=None,
    ):
        from sklearn.feature_extraction.text import TfidfVectorizer

        from copilot.rag.chunking import make_chunks

        self.documents = documents
        self.strategy = strategy
        self.chunks = [
            c
            for doc in documents
            for c in make_chunks(doc, strategy, size, overlap, encoder=semantic_encoder)
        ]
        self.retrieval_encoder = retrieval_encoder
        self.persistent_index = persistent_index
        self.hybrid = hybrid
        self.reranker = reranker
        self.mode = "neural-vector-extractive" if retrieval_encoder else "tfidf-vector-extractive"
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        texts = [str(c.metadata.get("title", "")) + "\n" + c.text for c in self.chunks]
        self.matrix = None
        if persistent_index:
            self.generation = persistent_index.publish(self.chunks, texts, retrieval_encoder)
            self.mode = "hybrid-extractive" if hybrid else "pgvector-extractive"
            if reranker:
                self.mode = "reranked-hybrid-extractive"
        elif texts and retrieval_encoder:
            import numpy as np

            self.matrix = np.asarray(retrieval_encoder.encode(texts), dtype=np.float32)
        elif texts:
            self.matrix = self.vectorizer.fit_transform(texts)

    @classmethod
    def from_data(
        cls,
        data,
        strategy="recursive",
        baseline=False,
        semantic_encoder=None,
        retrieval_encoder=None,
    ):
        return cls(
            documents_from(data, baseline),
            strategy,
            semantic_encoder=semantic_encoder,
            retrieval_encoder=retrieval_encoder,
        )

    @classmethod
    def configured(cls, data):
        backend = os.getenv("COPILOT_RETRIEVAL_BACKEND", "tfidf")
        if backend == "tfidf":
            return cls.from_data(data)
        if backend == "reranked":
            from copilot.rag.reranker import OnnxReranker

            return cls.with_postgres(data, hybrid=True, reranker=OnnxReranker())
        if backend in {"pgvector", "hybrid"}:
            return cls.with_postgres(data, hybrid=backend == "hybrid")
        if backend == "neural":
            from copilot.rag.semantic_encoder import OnnxEncoder

            return cls.from_data(
                data, retrieval_encoder=OnnxEncoder(cache=os.getenv("COPILOT_EMBEDDING_CACHE"))
            )
        raise ValueError(
            "COPILOT_RETRIEVAL_BACKEND must be tfidf, neural, pgvector, hybrid, or reranked"
        )

    @classmethod
    def with_postgres(cls, data, *, hybrid=False, reranker=None):
        from copilot.config import get_settings
        from copilot.rag.postgres_index import PersistentIndex
        from copilot.rag.semantic_encoder import OnnxEncoder

        encoder = OnnxEncoder(cache=os.getenv("COPILOT_EMBEDDING_CACHE"))
        index = PersistentIndex(
            get_settings().database_url.get_secret_value(),
            encoder.identity,
            encoder.manifest["dimension"],
        )
        return cls(
            documents_from(data),
            "recursive",
            retrieval_encoder=encoder,
            persistent_index=index,
            hybrid=hybrid,
            reranker=reranker,
        )

    def search(self, query, role="employee", os_name=None, region=None, k=5, *, ranking=None):
        if k < 1:
            raise ValueError("k must be positive")
        candidates = [
            i for i, c in enumerate(self.chunks) if is_allowed(c.metadata, role, os_name, region)
        ]
        exact = re.findall(r"\b(?:KB-\d+|\d{3,})\b", query, re.IGNORECASE)
        if exact:
            candidates = [
                i
                for i in candidates
                if all(
                    code.lower()
                    in (
                        self.chunks[i].text
                        + " "
                        + self.chunks[i].document_id
                        + " "
                        + str(self.chunks[i].metadata.get("title", ""))
                    ).lower()
                    for code in exact
                )
            ]
        if not candidates:
            return []
        if self.persistent_index:
            authorized = {self.chunks[i].id: self.chunks[i] for i in candidates}
            return self._search_postgres(query, authorized, k, ranking)
        if self.matrix is None:
            return []
        if self.retrieval_encoder:
            vector = self.retrieval_encoder.encode([query])[0]
            scores = self.matrix[candidates] @ vector
        else:
            vector = self.vectorizer.transform([query])
            scores = (self.matrix[candidates] @ vector.T).toarray().ravel()
        ranked = sorted(zip(candidates, scores, strict=True), key=lambda row: row[1], reverse=True)
        return [self.chunks[index] for index, score in ranked if score > 0.02][:k]

    def _search_postgres(self, query, authorized, k, ranking):
        from copilot.rag.rank_fusion import reciprocal_rank_fusion

        default = "reranked" if self.reranker else "hybrid" if self.hybrid else "vector"
        ranking = ranking or default
        if ranking not in {"vector", "keyword", "hybrid", "reranked"}:
            raise ValueError("Unknown PostgreSQL ranking")
        ids = list(authorized)
        limit = max(k, 30) if ranking in {"hybrid", "reranked"} else k
        dense, sparse = [], []
        if ranking != "keyword":
            vector = self.retrieval_encoder.encode([query])[0]
            hits = self.persistent_index.search(self.generation, ids, vector, limit)
            dense = [authorized[chunk_id] for chunk_id, score in hits if score > 0.02]
        if ranking != "vector":
            hits = self.persistent_index.keyword(self.generation, ids, query, limit)
            sparse = [authorized[chunk_id] for chunk_id, _ in hits]
        if ranking == "hybrid":
            return reciprocal_rank_fusion([dense, sparse], k=k)
        if ranking == "reranked":
            if not self.reranker:
                raise ValueError("reranked search requires a reranker")
            candidates = reciprocal_rank_fusion([dense, sparse], k=limit)
            return self.reranker.rank(query, candidates)[:k]
        return dense if ranking == "vector" else sparse

    def answer(self, query, **kwargs):
        hits = self.search(query, **kwargs)
        if not hits:
            return {
                "answer": "No supporting source found. I can raise a ticket.",
                "citations": [],
                "abstained": True,
                "mode": self.mode,
            }
        best = hits[0].document_id
        chosen_ids = {h.id for h in hits if h.document_id == best}
        chosen = [c for c in self.chunks if c.id in chosen_ids]
        context = list(dict.fromkeys(c.parent or c.text for c in chosen))
        return {
            "answer": "\n\n".join(context),
            "abstained": False,
            "citations": [
                {"chunk_id": c.id, "document_id": c.document_id, "source": c.source} for c in chosen
            ],
            "mode": self.mode,
            "chunk_strategy": self.strategy,
        }


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
