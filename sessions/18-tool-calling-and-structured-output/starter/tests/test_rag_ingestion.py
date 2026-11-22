import json
import os
from pathlib import Path

from copilot.rag.loaders import ingest, is_allowed, load_document

DATA = Path(os.getenv("COHORT_DATA_DIR", "data"))


def test_html_has_steps_but_no_portal_navigation():
    document = load_document(DATA / "kb/KB-1017.html")
    assert "1. Open App Hub" in document.text
    assert "Was this article helpful?" not in document.text
    assert "Suggest an article" not in document.text
    assert document.metadata["id"] == "KB-1017"
    assert isinstance(document.metadata["error_codes"], list)


def test_policy_register_and_runbook_metadata_are_enforced():
    current = load_document(DATA / "policies/POL-003_v4.0.pdf")
    old = load_document(DATA / "policies/POL-003_v3.2.pdf")
    runbook = load_document(DATA / "runbooks/RB-001.docx")
    assert is_allowed(current.metadata, "employee")
    assert not is_allowed(old.metadata, "admin")
    assert not is_allowed(runbook.metadata, "employee")
    assert is_allowed(runbook.metadata, "analyst")
    assert "14" in current.text and "12" in old.text
    assert current.id != old.id


def test_full_ingestion_is_repeatable_and_preserves_sla(tmp_path):
    output = tmp_path / "documents.json"
    first = ingest(DATA, output)
    second = ingest(DATA, output)
    assert first["documents"] == 150
    assert first["skipped"] == []
    assert second["changed"] == 0
    rows = json.loads(output.read_text())
    sla = next(row for row in rows if row["source"].endswith("sla_matrix.pdf"))
    assert all(
        value in sla["text"] for value in ("Priority 1", "Priority 2", "Priority 3", "Priority 4")
    )


def test_metadata_only_change_invalidates_and_withdrawal_removes(tmp_path):
    data = tmp_path / "data"
    (data / "kb").mkdir(parents=True)
    for folder in ("policies", "runbooks", "reference"):
        (data / folder).mkdir()
    source = data / "kb/one.md"
    source.write_text("---\nid: one\naudience: employee\n---\nVPN instructions\n")
    metadata = tmp_path / "policies/source_metadata.json"
    metadata.parent.mkdir()
    metadata.write_text('{"kb/one.md":{"audience":"employee"}}')
    output = tmp_path / "documents.json"
    assert ingest(data, output)["changed"] == 1
    digest = json.loads(output.read_text())[0]["digest"]
    metadata.write_text('{"kb/one.md":{"audience":"it-staff"}}')
    assert ingest(data, output)["changed"] == 1
    assert json.loads(output.read_text())[0]["digest"] == digest
    source.unlink()
    assert ingest(data, output)["removed"] == [str(source)]
    assert json.loads(output.read_text()) == []


def test_unreadable_source_is_reported_and_missing_audience_fails_closed(tmp_path):
    data = tmp_path / "data"
    (data / "kb").mkdir(parents=True)
    (data / "kb/bad.md").write_text("---\nunterminated: metadata\n")
    report = ingest(data, tmp_path / "documents.json")
    assert len(report["skipped"]) == 1
    assert not is_allowed({}, "admin")
