"""Mixed-format ingestion with trusted metadata and repeatable content identities."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import asdict
from datetime import date
from pathlib import Path

PARSER_VERSION = "cohort-ingest-v2"
FORMATS = {".md", ".html", ".pdf", ".docx"}
SCOPE_ALIASES = {
    "os": {"mac": "macos", "mac os": "macos", "os x": "macos", "win": "windows"},
    "region": {"asia pacific": "apac", "asia-pacific": "apac", "worldwide": "global"},
}


def normalize_scope(key, value):
    normalized = " ".join(str(value).casefold().split())
    return SCOPE_ALIASES.get(key, {}).get(normalized, normalized)


def _html(path):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    metadata = {
        str(m.get("name")).split(":", 1)[-1]: str(m.get("content"))
        for m in soup.find_all("meta")
        if str(m.get("name", "")).startswith(("kb:", "doc:"))
    }
    for node in soup.select("script,style,nav,header,footer,form,.feedback,.article-feedback"):
        node.decompose()
    article = soup.find("article") or soup.find("main") or soup.body or soup
    blocks = []
    for node in article.find_all(["h1", "h2", "h3", "p", "li", "table"]):
        if node.find_parent("table") or (node.name == "p" and node.find_parent("li")):
            continue
        text = node.get_text(" ", strip=True)
        if node.name.startswith("h"):
            text = "#" * int(node.name[1]) + " " + text
        elif node.name == "li":
            siblings = node.parent.find_all("li", recursive=False)
            prefix = f"{siblings.index(node) + 1}. " if node.parent.name == "ol" else "- "
            text = prefix + text
        elif node.name == "table":
            text = "\n".join(
                " | ".join(c.get_text(" ", strip=True) for c in row.find_all(["th", "td"]))
                for row in node.find_all("tr")
            )
        if text and text != "Was this article helpful?":
            blocks.append(text)
    return "\n\n".join(blocks), metadata


def _trusted_metadata(path):
    data = path.parent.parent
    sidecar = data.parent / "policies/source_metadata.json"
    relative = path.relative_to(data).as_posix()
    trusted = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}
    metadata = dict(trusted.get(relative, {}))
    if path.parent.name == "policies":
        register = path.parent / "register.csv"
        metadata["status"] = "unregistered"
        if register.exists():
            with register.open(encoding="utf-8", newline="") as stream:
                row = next((r for r in csv.DictReader(stream) if r["file"] == path.name), None)
            if row:
                metadata.update(row)
                metadata["policy_id"] = row["id"]
                metadata["id"] = path.stem
    return metadata


def load_document(path: Path):
    from copilot.rag.pipeline import Document

    path = Path(path)
    suffix = path.suffix.lower()
    metadata = {}
    if suffix == ".md":
        import yaml

        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
            if not match:
                raise ValueError("invalid Markdown frontmatter boundary")
            metadata = yaml.safe_load(match.group(1)) or {}
            if not isinstance(metadata, dict):
                raise ValueError("metadata must be a mapping")
            text = match.group(2)
    elif suffix == ".html":
        text, metadata = _html(path)
    elif suffix == ".pdf":
        from pypdf import PdfReader

        text = "\n\n".join(
            p.extract_text(extraction_mode="layout") or "" for p in PdfReader(path).pages
        )
    elif suffix == ".docx":
        from docx import Document as WordDocument
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        doc = WordDocument(path)
        blocks = []
        for node in doc.element.body.iterchildren():
            if node.tag.endswith("}p"):
                blocks.append(Paragraph(node, doc).text)
            elif node.tag.endswith("}tbl"):
                blocks.append(
                    "\n".join(" | ".join(c.text for c in r.cells) for r in Table(node, doc).rows)
                )
        text = "\n\n".join(blocks)
    else:
        raise ValueError(f"unsupported source format {suffix}")
    metadata.update(_trusted_metadata(path))
    for key in ("effective_date", "last_reviewed"):
        if metadata.get(key) is not None:
            metadata[key] = str(metadata[key])
    for key in ("audience", "os", "region", "status"):
        if key in metadata:
            metadata[key] = normalize_scope(key, metadata[key])
    if isinstance(metadata.get("error_codes"), str):
        try:
            metadata["error_codes"] = json.loads(metadata["error_codes"])
        except json.JSONDecodeError:
            metadata["error_codes"] = [metadata["error_codes"]]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return Document(str(metadata.get("id", path.stem)), text.strip(), metadata, str(path), digest)


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
        if desired and normalize_scope(key, metadata.get(key, "any")) not in {
            normalize_scope(key, desired),
            "any",
            "global",
        }:
            return False
    return True


def fingerprint(document):
    body = {
        "content_hash": document.digest,
        "metadata": document.metadata,
        "parser_version": PARSER_VERSION,
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def ingest(data: Path, output: Path):
    from zipfile import BadZipFile

    from docx.opc.exceptions import PackageNotFoundError
    from pypdf.errors import PyPdfError
    from yaml import YAMLError

    old = {d["source"]: d for d in json.loads(output.read_text())} if output.exists() else {}
    paths = sorted(
        p
        for folder in ("kb", "policies", "runbooks", "reference")
        for p in (data / folder).glob("*")
        if p.suffix.lower() in FORMATS
    )
    documents, skipped, changed = [], [], 0
    for path in paths:
        try:
            document = load_document(path)
            if document.metadata.get("audience") not in {"employee", "it-staff"}:
                raise ValueError("missing trusted audience; quarantined")
            if not document.text:
                raise ValueError("empty extracted text")
            row = asdict(document)
            row["ingestion_fingerprint"] = fingerprint(document)
            changed += (
                old.get(str(path), {}).get("ingestion_fingerprint") != row["ingestion_fingerprint"]
            )
            documents.append(row)
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            SyntaxError,
            BadZipFile,
            PackageNotFoundError,
            PyPdfError,
            YAMLError,
        ) as exc:
            skipped.append(
                {"source": str(path), "error_type": type(exc).__name__, "error": str(exc)}
            )
    inventory = {str(p) for p in paths}
    removed = sorted(set(old) - inventory)
    report = {
        "documents": len(documents),
        "changed": changed,
        "removed": removed,
        "skipped": skipped,
        "parser_version": PARSER_VERSION,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    temporary.replace(output)
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
