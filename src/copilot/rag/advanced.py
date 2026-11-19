"""Local neural embeddings and reranking, cached separately from lexical baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from copilot.rag.pipeline import Chunk, Document, Retriever, allowed, chunk
from copilot.rag.rank_fusion import reciprocal_rank_fusion


class Embeddings:
    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache: Path = Path(".work/embeddings.json"),
    ):
        from sentence_transformers import SentenceTransformer

        self.name, self.cache = model, cache
        self.model = SentenceTransformer(model)
        self.values = json.loads(cache.read_text()) if cache.exists() else {}

    def encode(self, texts: list[str]) -> list[list[float]]:
        keys = [hashlib.sha256((self.name + "\0" + t).encode()).hexdigest() for t in texts]
        missing = {k: t for k, t in zip(keys, texts, strict=True) if k not in self.values}
        if missing:
            vectors = self.model.encode(
                list(missing.values()), batch_size=32, normalize_embeddings=True
            )
            self.values.update({k: v.tolist() for k, v in zip(missing, vectors, strict=True)})
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            self.cache.write_text(json.dumps(self.values), encoding="utf-8")
        return [self.values[k] for k in keys]


def semantic_chunks(
    document: Document, embeddings: Embeddings, threshold: float = 0.55
) -> list[Chunk]:
    import numpy as np

    paragraphs = [p.strip() for p in document.text.split("\n\n") if p.strip()]
    vectors = embeddings.encode(paragraphs)
    sections, current = [], ""
    for i, paragraph in enumerate(paragraphs):
        if i and float(np.dot(vectors[i - 1], vectors[i])) < threshold:
            sections.append(current)
            current = ""
        current = (current + "\n\n" + paragraph).strip()
    if current:
        sections.append(current)
    return [
        Chunk(f"{document.id}:semantic:{i}", document.id, text, document.metadata, document.source)
        for i, text in enumerate(sections)
    ]


class NeuralRetriever(Retriever):
    def __init__(self, documents: list[Document], embeddings: Embeddings, rerank: bool = False):
        super().__init__(documents)
        self.embeddings = embeddings
        self.vectors = embeddings.encode([c.text for c in self.chunks])
        self.reranker = None
        if rerank:
            from sentence_transformers import CrossEncoder

            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def search(self, query: str, role="employee", os_name=None, region=None, k=5) -> list[Chunk]:
        import numpy as np

        vector = self.embeddings.encode([query])[0]
        permitted = [
            (c, v)
            for c, v in zip(self.chunks, self.vectors, strict=True)
            if allowed(c.metadata, role, os_name, region)
        ]
        dense = [
            c
            for c, _ in sorted(
                permitted, key=lambda pair: float(np.dot(pair[1], vector)), reverse=True
            )[:30]
        ]
        lexical = super().search(query, role, os_name, region, k=30)
        fused = reciprocal_rank_fusion([dense, lexical], k=30)
        if self.reranker and fused:
            scores = self.reranker.predict([(query, c.text) for c in fused])
            fused = [
                c
                for c, _ in sorted(
                    zip(fused, scores, strict=True), key=lambda pair: pair[1], reverse=True
                )
            ]
        return fused[:k]


def rewrite(query: str, previous: str = "") -> str:
    if previous and any(
        part in query.lower() for part in ("still", "doesn't work", "same problem")
    ):
        return previous + " " + query
    return query.replace("MFA", "multi-factor authentication MFA")


def grounded_answer(query: str, hits: list[Chunk], client) -> dict:
    from copilot.guardrails.checks import valid_citations

    if not hits:
        return {"answer": "No supporting source found. Offer a ticket.", "citations": []}
    context = [{"chunk_id": c.id, "content": c.parent or c.text} for c in hits]
    result = client.complete(
        [
            {
                "role": "system",
                "content": (Path(__file__).parent / "prompts/grounded-v1.md").read_text(
                    encoding="utf-8"
                ),
            },
            {"role": "user", "content": json.dumps({"question": query, "sources": context})},
        ]
    )
    parsed = json.loads(result.text)
    if parsed.get("abstained") is True:
        if parsed.get("citations") or not isinstance(parsed.get("answer"), str):
            raise ValueError("invalid abstention")
        return parsed
    if (
        not isinstance(parsed.get("answer"), str)
        or not parsed.get("citations")
        or not valid_citations(parsed["citations"], hits)
    ):
        raise ValueError("invalid answer or ungrounded citation; escalate")
    return parsed


class PostgresIndex:
    def __init__(self, url: str, dimension: int = 384):
        if not 1 <= dimension <= 2000:
            raise ValueError("invalid embedding dimension")
        self.url, self.dimension = url, dimension

    def connect(self):
        import psycopg

        return psycopg.connect(self.url)

    def setup(self):
        with self.connect() as db:
            db.execute("CREATE EXTENSION IF NOT EXISTS vector")
            db.execute(
                "CREATE TABLE IF NOT EXISTS rag_chunks (id TEXT PRIMARY KEY, "
                "document TEXT NOT NULL, content TEXT NOT NULL, metadata JSONB NOT NULL, "
                f"embedding vector({self.dimension}), terms tsvector GENERATED ALWAYS AS "
                "(to_tsvector('english', content)) STORED)"
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS rag_vectors ON rag_chunks "
                "USING hnsw (embedding vector_cosine_ops)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS rag_terms ON rag_chunks USING gin (terms)")

    def replace(self, document: Document, embeddings: Embeddings):
        parts = chunk(document)
        vectors = embeddings.encode([c.text for c in parts])
        with self.connect() as db:
            db.execute("DELETE FROM rag_chunks WHERE document=%s", (document.id,))
            for part, vector in zip(parts, vectors, strict=True):
                db.execute(
                    "INSERT INTO rag_chunks(id,document,content,metadata,embedding) "
                    "VALUES (%s,%s,%s,%s::jsonb,%s::vector)",
                    (part.id, document.id, part.text, json.dumps(part.metadata), str(vector)),
                )

    def search(self, query: str, vector: list[float], audience: str, os_name: str, k: int = 5):
        # Filter authorization in SQL before either ranking.
        filters = (
            "metadata->>'audience' = %s AND metadata->>'os' IN (%s,'any') "
            "AND metadata->>'status'='current'"
        )
        with self.connect() as db:
            dense = db.execute(
                f"SELECT id,content FROM rag_chunks WHERE {filters} "
                "ORDER BY embedding <=> %s::vector LIMIT %s",
                (audience, os_name, str(vector), k),
            ).fetchall()
            keyword = db.execute(
                f"SELECT id,content FROM rag_chunks WHERE {filters} "
                "AND terms @@ plainto_tsquery('english',%s) "
                "ORDER BY ts_rank(terms,plainto_tsquery('english',%s)) DESC LIMIT %s",
                (audience, os_name, query, query, k),
            ).fetchall()
        return {"vector": dense, "keyword": keyword}
