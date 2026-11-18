"""Session 5 reads the trainer-normalized Markdown corpus only."""

import hashlib
from datetime import date
from pathlib import Path

import yaml


def load_document(path: Path):
    from copilot.rag.pipeline import Document

    if path.suffix != ".md":
        raise ValueError("Mixed-format parsing is introduced in session 6")
    _, header, text = path.read_text(encoding="utf-8").split("---", 2)
    metadata = yaml.safe_load(header)
    return Document(
        metadata["id"],
        text.strip(),
        metadata,
        str(path),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def ingest(data, output):
    raise NotImplementedError("Bulk mixed-format ingestion is session 6 work")


def is_allowed(metadata, role="employee", os_name=None, region=None):
    if role not in {"employee", "analyst", "admin"}:
        return False
    audience = metadata.get("audience")
    if audience not in {"employee", "it-staff"}:
        return False
    if role == "employee" and audience != "employee":
        return False
    if metadata.get("status", "current") != "current":
        return False
    if metadata.get("effective_date"):
        try:
            if date.fromisoformat(str(metadata["effective_date"])) > date.today():
                return False
        except ValueError:
            return False
    for key, desired in (("os", os_name), ("region", region)):
        if desired and str(metadata.get(key, "any")).lower() not in {
            str(desired).lower(),
            "any",
            "global",
        }:
            return False
    return True
