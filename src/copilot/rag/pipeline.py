"""Inspectable retrieval reference; lexical mode is deliberately labelled, not embeddings."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
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
    return re.findall(r"[\w]+(?:-[\w]+)*", text.lower())


def load_document(path: Path) -> Document:
    suffix = path.suffix.lower()
    metadata = {}
    if suffix == ".pdf":
        from pypdf import PdfReader

        text = "\n".join(
            page.extract_text(extraction_mode="layout") or "" for page in PdfReader(path).pages
        )
    elif suffix == ".docx":
        from docx import Document as WordDocument

        doc = WordDocument(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        text += "\n" + "\n".join(
            " | ".join(c.text for c in r.cells) for t in doc.tables for r in t.rows
        )
    else:
        text = path.read_text(encoding="utf-8")
        if suffix == ".html":
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(text, "html.parser")
            metadata = {
                str(m.get("name")).removeprefix("kb:"): str(m.get("content"))
                for m in soup.find_all("meta")
                if m.get("name")
            }
            text = soup.get_text("\n", strip=True)
        elif text.startswith("---"):
            import yaml

            _, header, text = text.split("---", 2)
            metadata = {k: str(v) for k, v in yaml.safe_load(header).items()}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return Document(metadata.get("id", path.stem), text.strip(), metadata, str(path), digest)


def ingest(data: Path, output: Path) -> dict:
    paths = sorted(
        p
        for directory in ("kb", "policies", "runbooks", "reference")
        for p in (data / directory).glob("*")
        if p.suffix.lower() in {".md", ".html", ".pdf", ".docx"}
    )
    old = {d["source"]: d for d in json.loads(output.read_text())} if output.exists() else {}
    documents, skipped, changed = [], [], 0
    for path in paths:
        try:
            doc = load_document(path)
            changed += old.get(str(path), {}).get("digest") != doc.digest
            documents.append(asdict(doc))
        except Exception as exc:
            skipped.append({"source": str(path), "error": str(exc)})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    report = {"documents": len(documents), "changed": changed, "skipped": skipped}
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def chunk(
    document: Document, strategy: str = "recursive", size: int = 1200, overlap: int = 120
) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("require 0 <= overlap < size")
    if strategy == "fixed":
        parts = [document.text[i : i + size] for i in range(0, len(document.text), size - overlap)]
    elif strategy in {"recursive", "parent-child"}:
        # Paragraphs and numbered steps are atomic. An oversize atomic unit is
        # retained intact rather than silently breaking a troubleshooting step.
        units = re.split(r"\n\s*\n|(?=\n\d+\. )", document.text)
        parts, current = [], ""
        for unit in units:
            if current and len(current) + len(unit) > size:
                parts.append(current)
                current = ""
            current = (current + "\n\n" + unit).strip()
        if current:
            parts.append(current)
    else:
        raise ValueError(f"unknown chunk strategy: {strategy}")
    return [
        Chunk(
            f"{document.id}:{i}",
            document.id,
            part,
            document.metadata,
            document.source,
            document.text if strategy == "parent-child" else "",
        )
        for i, part in enumerate(parts)
    ]


def allowed(metadata: dict, role: str, os_name: str | None, region: str | None) -> bool:
    # Missing audience is denied for employees: PDFs/DOCX require curated metadata.
    if role == "employee" and metadata.get("audience") != "employee":
        return False
    if metadata.get("status", "current") != "current":
        return False
    effective = metadata.get("effective_date", "")
    if effective and effective > date.today().isoformat():
        return False
    return not any(
        wanted and metadata.get(key, "any").lower() not in {wanted.lower(), "any", "global"}
        for key, wanted in (("os", os_name), ("region", region))
    )


class Retriever:
    def __init__(self, documents: list[Document], strategy: str = "recursive"):
        self.chunks = [c for d in documents for c in chunk(d, strategy)]

    @classmethod
    def from_data(cls, data: Path):
        # KB baseline needs no parser dependencies beyond YAML/BeautifulSoup.
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
        exact = re.findall(r"\b(?:KB-\d+|\d{3,})\b", query, re.I)
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
        # This extractive baseline cannot establish semantic answerability.
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
