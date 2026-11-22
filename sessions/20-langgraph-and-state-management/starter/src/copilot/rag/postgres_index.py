"""Persistent pgvector index for the active local corpus."""

import hashlib
import json
import re


class PersistentIndex:
    def __init__(self, url, model_identity, dimension, *, options=None):
        if not isinstance(dimension, int) or not 1 <= dimension <= 2000:
            raise ValueError("HNSW vector dimension must be between 1 and 2000")
        self.url = url
        self.model_identity = model_identity
        self.dimension = dimension
        self.options = options

    def connect(self):
        import psycopg

        return psycopg.connect(self.url, connect_timeout=5, options=self.options)

    def publish(self, chunks, texts, encoder):
        generation = hashlib.sha256(
            json.dumps(
                [
                    "fts-v1",
                    self.model_identity,
                    self.dimension,
                    [(c.id, t, c.metadata) for c, t in zip(chunks, texts, strict=True)],
                ],
                sort_keys=True,
            ).encode()
        ).hexdigest()
        with self.connect() as db:
            db.execute("SELECT pg_advisory_xact_lock(1526719595)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS copilot_rag_generation "
                "(active boolean PRIMARY KEY CHECK (active), generation text NOT NULL, "
                "dimension integer NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS copilot_rag_vectors "
                "(id text PRIMARY KEY, generation text NOT NULL, "
                f"embedding vector({self.dimension}) NOT NULL)"
            )
            db.execute(
                "ALTER TABLE copilot_rag_vectors ADD COLUMN IF NOT EXISTS "
                "content text NOT NULL DEFAULT ''"
            )
            db.execute(
                "ALTER TABLE copilot_rag_vectors ADD COLUMN IF NOT EXISTS "
                "terms tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED"
            )
            current = db.execute(
                "SELECT generation, dimension FROM copilot_rag_generation WHERE active"
            ).fetchone()
            if current == (generation, self.dimension):
                return generation
            if current and current[1] != self.dimension:
                raise ValueError("embedding dimension changed; migrate the vector index first")
            vectors = encoder.encode(texts)
            db.execute("DELETE FROM copilot_rag_vectors")
            with db.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO copilot_rag_vectors (id, generation, embedding, content) "
                    "VALUES (%s, %s, %s::vector, %s)",
                    [
                        (chunk.id, generation, str(vector), content)
                        for chunk, vector, content in zip(chunks, vectors, texts, strict=True)
                    ],
                )
            db.execute(
                "CREATE INDEX IF NOT EXISTS copilot_rag_vectors_hnsw ON copilot_rag_vectors "
                "USING hnsw (embedding vector_cosine_ops)"
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS copilot_rag_terms_gin ON copilot_rag_vectors "
                "USING gin (terms)"
            )
            db.execute(
                "INSERT INTO copilot_rag_generation VALUES (true, %s, %s) "
                "ON CONFLICT (active) DO UPDATE SET generation = EXCLUDED.generation, "
                "dimension = EXCLUDED.dimension",
                (generation, self.dimension),
            )
        return generation

    def search(
        self,
        generation,
        allowed_ids,
        vector,
        limit,
        *,
        exact=False,
        force_hnsw=False,
        explain=False,
    ):
        if not allowed_ids:
            return []
        with self.connect() as db:
            if exact:
                db.execute("SET LOCAL enable_indexscan = off")
                db.execute("SET LOCAL enable_bitmapscan = off")
            else:
                db.execute("SET LOCAL hnsw.iterative_scan = 'strict_order'")
                if force_hnsw:
                    db.execute("SET LOCAL enable_seqscan = off")
                    db.execute("SET LOCAL enable_bitmapscan = off")
                    db.execute("SET LOCAL enable_sort = off")
            statement = (
                "SELECT id, 1 - (embedding <=> %s::vector) AS score "
                "FROM copilot_rag_vectors WHERE generation=%s AND id=ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s"
            )
            return db.execute(
                ("EXPLAIN (ANALYZE, FORMAT JSON) " if explain else "") + statement,
                (str(vector), generation, allowed_ids, str(vector), limit),
            ).fetchall()

    def keyword(self, generation, allowed_ids, query, limit):
        tokens = re.findall(r"[a-z0-9]+", query.casefold())
        if not tokens or not allowed_ids:
            return []
        terms = "|".join(dict.fromkeys(tokens))
        with self.connect() as db:
            return db.execute(
                "WITH q AS (SELECT to_tsquery('english', %s) AS query) "
                "SELECT id, ts_rank_cd(terms, query) FROM copilot_rag_vectors, q "
                "WHERE generation=%s AND id=ANY(%s) AND terms @@ query "
                "ORDER BY ts_rank_cd(terms, query) DESC, id LIMIT %s",
                (terms, generation, allowed_ids, limit),
            ).fetchall()
