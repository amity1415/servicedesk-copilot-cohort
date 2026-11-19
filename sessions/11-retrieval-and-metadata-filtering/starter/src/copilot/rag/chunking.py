"""Four chunking strategies with deterministic IDs and section-level parents."""

from __future__ import annotations

import hashlib
import json
import re


def units(text):
    """Keep headings with their first atomic paragraph or numbered step."""
    parts = [part.strip() for part in re.split(r"\n\s*\n|(?=\n\d+\. )", text) if part.strip()]
    output = []
    index = 0
    while index < len(parts):
        part = parts[index]
        if re.match(r"^#{1,3} ", part) and index + 1 < len(parts):
            part += "\n\n" + parts[index + 1]
            index += 1
        output.append(part)
        index += 1
    return output


def pack(parts, size):
    output, current = [], ""
    for part in parts:
        if current and len(current) + len(part) + 2 > size:
            output.append(current)
            current = ""
        current = (current + "\n\n" + part).strip()
    if current:
        output.append(current)
    return output


def sections(text):
    """A parent is a heading section, not an entire long policy."""
    return [s.strip() for s in re.split(r"(?m)(?=^#{1,3} )", text) if s.strip()]


def semantic_parts(parts, encoder, size, threshold):
    if encoder is None:
        raise ValueError("semantic chunking requires an explicit neural encoder")
    if not parts:
        return []
    vectors = encoder.encode(parts)
    groups, current = [], []
    for i, part in enumerate(parts):
        similarity = sum(a * b for a, b in zip(vectors[i - 1], vectors[i], strict=True)) if i else 1
        if current and similarity < threshold:
            groups.extend(pack(current, size))
            current = []
        current.append(part)
    groups.extend(pack(current, size))
    return groups


def make_chunks(
    document, strategy="recursive", size=1200, overlap=120, encoder=None, threshold=0.55
):
    from copilot.rag.pipeline import Chunk

    if not 0 <= overlap < size:
        raise ValueError("require 0 <= overlap < size")
    if not -1 <= threshold <= 1:
        raise ValueError("similarity threshold must be between -1 and 1")
    if strategy == "fixed":
        parts = [
            (document.text[i : i + size], "") for i in range(0, len(document.text), size - overlap)
        ]
    elif strategy == "recursive":
        parts = [(text, "") for text in pack(units(document.text), size)]
    elif strategy == "semantic":
        parts = [
            (text, "") for text in semantic_parts(units(document.text), encoder, size, threshold)
        ]
    elif strategy == "parent-child":
        parts = [
            (child, parent)
            for parent in sections(document.text)
            for child in pack(units(parent), max(1, size // 3))
        ]
    else:
        raise ValueError(f"unknown chunk strategy: {strategy}")
    identity = {
        "source": document.id,
        "digest": document.digest,
        "metadata": document.metadata,
        "strategy": strategy,
        "size": size,
        "overlap": overlap if strategy == "fixed" else 0,
        "threshold": threshold if strategy == "semantic" else None,
        "encoder": getattr(encoder, "identity", None) if strategy == "semantic" else None,
        "chunker_version": "cohort-chunks-v2",
    }
    revision = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    return [
        Chunk(
            f"{document.id}:{strategy}:{revision}:{i}",
            document.id,
            text,
            dict(document.metadata),
            document.source,
            parent,
        )
        for i, (text, parent) in enumerate(parts)
    ]
