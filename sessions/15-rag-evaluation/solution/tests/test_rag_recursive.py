import pytest

from copilot.rag.chunking import make_chunks
from copilot.rag.pipeline import Document


def doc(text):
    return Document("steps", text, {"audience": "employee"}, "fixture", "hash")


def test_fixed_windows_reconstruct_original_and_validate_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = make_chunks(doc(text), "fixed", size=10, overlap=3)
    assert chunks[0].text + "".join(c.text[3:] for c in chunks[1:]) == text
    with pytest.raises(ValueError):
        make_chunks(doc(text), size=10, overlap=10)


def test_recursive_keeps_troubleshooting_steps_atomic():
    first = "1. " + "x" * 1500
    chunks = make_chunks(doc(first + "\n\n2. Restart the laptop."), "recursive")
    assert chunks[0].text == first
    assert chunks[1].text == "2. Restart the laptop."


def test_chunk_identity_is_repeatable_and_changes_with_metadata():
    document = doc("VPN instructions\n\n1. Install app\n\n2. Connect")
    before = make_chunks(document, "recursive", size=140, overlap=20)
    assert [c.id for c in before] == [c.id for c in make_chunks(document, "recursive", 140, 20)]
    document.metadata["audience"] = "it-staff"
    assert before[0].id != make_chunks(document, "recursive", 140, 20)[0].id


def test_recursive_does_not_orphan_a_section_heading():
    document = doc("x" * 40 + "\n\n## Network\n\n1. Restart the VPN client.")
    chunks = make_chunks(document, "recursive", size=60, overlap=10)
    section = next(c for c in chunks if "## Network" in c.text)
    assert "Restart the VPN client" in section.text
