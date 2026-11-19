import pytest

from copilot.rag.chunking import make_chunks
from copilot.rag.pipeline import Document


class BoundaryEncoder:
    identity = "controlled-boundary-fixture"

    def encode(self, paragraphs):
        return [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]][: len(paragraphs)]


def test_semantic_boundaries_use_encoder_similarity_and_preserve_text():
    text = "VPN setup\n\nVPN connection\n\nPrinter setup\n\nPrinter queue"
    document = Document("topics", text, {"audience": "employee"}, "fixture", "hash")
    chunks = make_chunks(document, "semantic", encoder=BoundaryEncoder())
    assert len(chunks) == 2
    assert chunks[0].text == "VPN setup\n\nVPN connection"
    assert chunks[1].text == "Printer setup\n\nPrinter queue"
    with pytest.raises(ValueError):
        make_chunks(document, "semantic")


def test_parent_child_returns_only_the_matching_section_as_parent():
    text = "# Policy\n\n## VPN\n\n1. Install VPN.\n\n## Printers\n\n1. Add printer."
    document = Document("policy", text, {"audience": "employee"}, "fixture", "hash")
    chunks = make_chunks(document, "parent-child", size=180, overlap=20)
    vpn = next(c for c in chunks if "Install VPN" in c.text)
    assert "VPN" in vpn.parent
    assert "Add printer" not in vpn.parent
    assert len({c.id for c in chunks}) == len(chunks)


def test_threshold_is_validated():
    document = Document("one", "hello", {}, "fixture", "hash")
    with pytest.raises(ValueError):
        make_chunks(document, "semantic", encoder=BoundaryEncoder(), threshold=2)
