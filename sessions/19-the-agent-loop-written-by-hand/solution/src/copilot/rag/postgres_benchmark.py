"""Exercise Session 10 in an isolated schema on a real pgvector server."""

import hashlib
import json
from dataclasses import replace
from time import perf_counter
from uuid import uuid4

from copilot.rag.postgres_index import PersistentIndex
from copilot.rag.semantic_encoder import OnnxEncoder
from copilot.rag.service import VectorRag, documents_from


def verify_postgres(data, url):
    from psycopg import DataError, sql

    encoder = OnnxEncoder()
    dimension = encoder.manifest["dimension"]
    schema = f"copilot_s10_{uuid4().hex}"
    base = PersistentIndex(url, encoder.identity, dimension)
    with base.connect() as db:
        version = db.execute(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        ).fetchone()
        if not version:
            raise RuntimeError("Enable the pgvector extension before running Session 10")
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    index = PersistentIndex(
        url, encoder.identity, dimension, options=f"-c search_path={schema},public"
    )
    try:
        documents = documents_from(data)
        started = perf_counter()
        rag = VectorRag(documents, "recursive", retrieval_encoder=encoder, persistent_index=index)
        publish_ms = (perf_counter() - started) * 1000
        question = "How do I set up VPN on my Mac?"
        timings, results = [], []
        for _ in range(6):
            started = perf_counter()
            hits = rag.search(question, os_name="macos")
            timings.append((perf_counter() - started) * 1000)
            results.append([hit.document_id for hit in hits])
        if (
            not results[0]
            or results[0][0] != "KB-1017"
            or any(row != results[0] for row in results)
        ):
            raise RuntimeError(f"Unexpected database search results: {results}")
        query_vector = encoder.encode([question])[0]
        chunk_ids = [item.id for item in rag.chunks]
        plan = index.search(
            rag.generation, chunk_ids, query_vector, 5, force_hnsw=True, explain=True
        )[0][0]
        if "copilot_rag_vectors_hnsw" not in json.dumps(plan):
            raise RuntimeError("Expected to observe the HNSW index in EXPLAIN ANALYZE")
        exact = index.search(rag.generation, chunk_ids, query_vector, 5, exact=True)
        approximate = index.search(rag.generation, chunk_ids, query_vector, 5, force_hnsw=True)
        overlap = len({row[0] for row in exact} & {row[0] for row in approximate}) / len(exact)
        old_ids = {item.id for item in rag.chunks if item.document_id == "KB-1017"}
        revised_text = "Revised VPN setup for macOS."
        changed = [
            replace(
                doc, text=revised_text, digest=hashlib.sha256(revised_text.encode()).hexdigest()
            )
            if doc.id == "KB-1017"
            else doc
            for doc in documents
        ]

        class WrongDimensionEncoder:
            def encode(self, texts):
                return [[0.0] for _ in texts]

        try:
            VectorRag(
                changed,
                "recursive",
                retrieval_encoder=WrongDimensionEncoder(),
                persistent_index=index,
            )
        except DataError as error:
            retained = index.search(rag.generation, chunk_ids, query_vector, 5, exact=True)
            if retained != exact:
                raise RuntimeError(
                    "Failed replacement changed the previously published index"
                ) from error
        else:
            raise RuntimeError("Expected replacement with a wrong vector dimension to fail")
        replaced = VectorRag(
            changed, "recursive", retrieval_encoder=encoder, persistent_index=index
        )
        with index.connect() as db:
            old_rows = db.execute(
                "SELECT id FROM copilot_rag_vectors WHERE id=ANY(%s)", (list(old_ids),)
            ).fetchall()
        replacement_ids = {item.id for item in replaced.chunks if item.document_id == "KB-1017"}
        if not old_ids or not replacement_ids or old_rows:
            raise RuntimeError("Replacement retained old chunks or failed to publish new chunks")
        withdrawn = [doc for doc in changed if doc.id != "KB-1017"]
        VectorRag(withdrawn, "recursive", retrieval_encoder=encoder, persistent_index=index)
        with index.connect() as db:
            remaining = db.execute(
                "SELECT id FROM copilot_rag_vectors WHERE id=ANY(%s)", (list(replacement_ids),)
            ).fetchall()
        if remaining:
            raise RuntimeError("Withdrawal retained chunks")
        return {
            "mode": "pgvector-extractive",
            "pgvector_version": version[0],
            "dimension": dimension,
            "published_chunks": len(rag.chunks),
            "publish_ms": publish_ms,
            "query": question,
            "search_document_ids": results[0],
            "first_query_ms": timings[0],
            "repeat_query_ms": timings[1:],
            "exact_top5_chunk_ids": [row[0] for row in exact],
            "approximate_top5_chunk_ids": [row[0] for row in approximate],
            "top5_overlap": overlap,
            "hnsw_plan": plan,
            "replaced_old_chunks": len(old_ids),
            "failed_replace_rolled_back": True,
            "withdrawn_chunks": len(replacement_ids),
        }
    finally:
        with base.connect() as db:
            db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
