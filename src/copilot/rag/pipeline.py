"""Inspectable retrieval reference; lexical mode is deliberately labelled, not embeddings."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    id: str
    text: str
    metadata: dict[str, str]
    source: str
    digest: str


@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    metadata: dict[str, str]
    source: str
    parent: str = ""


def tokens(text: str) -> list[str]:
    return re.findall("[\\w]+(?:-[\\w]+)*", text.lower())


def load_document(path: Path) -> Document:
    from copilot.rag.loaders import load_document as parse

    return parse(path)


def ingest(data: Path, output: Path) -> dict:
    from copilot.rag.loaders import ingest as run

    return run(data, output)


def chunk(
    document: Document, strategy="recursive", size=1200, overlap=120, encoder=None, threshold=0.55
):
    from copilot.rag.chunking import make_chunks

    return make_chunks(document, strategy, size, overlap, encoder, threshold)


def allowed(metadata, role, os_name, region):
    from copilot.rag.loaders import is_allowed

    return is_allowed(metadata, role, os_name, region)


class Retriever:
    def __init__(self, documents: list[Document], strategy: str = "recursive"):
        self.chunks = [c for d in documents for c in chunk(d, strategy)]

    @classmethod
    def from_data(cls, data: Path):
        return cls(
            [
                load_document(p)
                for p in sorted((data / "kb").glob("*"))
                if p.suffix in {".md", ".html"}
            ]
        )

    def search(
        self,
        query: str,
        role: str = "employee",
        os_name: str | None = None,
        region: str | None = None,
        k: int = 5,
    ) -> list[Chunk]:
        candidates = [c for c in self.chunks if allowed(c.metadata, role, os_name, region)]
        stopwords = {
            "i",
            "my",
            "me",
            "the",
            "a",
            "an",
            "to",
            "on",
            "how",
            "do",
            "is",
            "it",
            "and",
            "of",
            "what",
            "for",
        }
        q = Counter(t for t in tokens(query) if t not in stopwords)
        exact = re.findall("\\b(?:KB-\\d+|\\d{3,})\\b", query, re.I)
        if exact:
            candidates = [
                c
                for c in candidates
                if all(
                    code.lower()
                    in (c.text + " " + c.document_id + " " + c.metadata.get("title", "")).lower()
                    for code in exact
                )
            ]
        dfs = Counter(t for c in candidates for t in set(tokens(c.text)))
        average = sum(len(tokens(c.text)) for c in candidates) / max(1, len(candidates))

        def score(c):
            words = Counter(tokens(c.text))
            length = sum(words.values())
            bm25 = sum(
                math.log(1 + (len(candidates) - dfs[t] + 0.5) / (dfs[t] + 0.5))
                * words[t]
                * 2.2
                / (words[t] + 1.2 * (0.25 + 0.75 * length / max(1, average)))
                for t in q
                if words[t]
            )
            title = set(tokens(c.metadata.get("title", "")))
            return bm25 + 2 * len(title & set(q)) if bm25 else 0

        return [c for c in sorted(candidates, key=score, reverse=True) if score(c) > 0][:k]

    def answer(self, query: str, **kwargs) -> dict:
        hits = self.search(query, **kwargs)
        if not hits:
            return {
                "answer": "No supporting source found. I can raise a ticket.",
                "citations": [],
                "mode": "lexical-extractive",
            }
        best = hits[0]
        selected = [c for c in self.chunks if c.document_id == best.document_id]
        return {
            "answer": best.parent or "\n\n".join(c.text for c in selected),
            "citations": [
                {"chunk_id": c.id, "source": c.source, "document_id": c.document_id}
                for c in selected
            ],
            "mode": "lexical-extractive",
        }
