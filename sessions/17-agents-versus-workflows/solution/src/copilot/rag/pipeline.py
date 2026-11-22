from __future__ import annotations

import re
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
    return re.findall(r"[\w]+(?:-[\w]+)*", text.lower())


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
