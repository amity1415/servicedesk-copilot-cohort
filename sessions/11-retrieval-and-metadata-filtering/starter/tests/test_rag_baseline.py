import os
from pathlib import Path

import pytest

from copilot.rag.pipeline import Document
from copilot.rag.service import VectorRag, baseline_directory, benchmark

DATA = Path(os.getenv("COHORT_DATA_DIR", "data"))


def test_baseline_is_twenty_normalized_markdown_sources():
    folder = baseline_directory(DATA)
    assert len(list((folder / "kb").glob("*.md"))) == 20
    rag = VectorRag.from_data(DATA, strategy="fixed", baseline=True)
    assert len(rag.documents) == 20
    assert rag.matrix.shape[0] == len(rag.chunks)


def test_baseline_mac_answer_is_cited_and_has_no_windows_steps():
    rag = VectorRag.from_data(DATA, strategy="fixed", baseline=True)
    result = rag.answer("How do I set up VPN on my Mac?", os_name="macos")
    assert not result["abstained"]
    assert {c["document_id"] for c in result["citations"]} == {"KB-1017"}
    assert "System Settings" in result["answer"]
    assert "Control Panel" not in result["answer"]


def test_authorization_is_applied_before_vector_top_k():
    documents = [
        Document("private", "unicornvpn configuration", {"audience": "it-staff"}, "private", "1"),
        Document("public", "VPN help", {"audience": "employee"}, "public", "2"),
    ]
    rag = VectorRag(documents)
    assert rag.search("unicornvpn", role="employee", k=1) == []
    assert rag.search("unicornvpn", role="analyst", k=1)[0].document_id == "private"


def test_unknown_vocabulary_abstains_and_invalid_k_is_rejected():
    rag = VectorRag.from_data(DATA, strategy="fixed", baseline=True)
    assert rag.answer("quasarbananas supernovapotatoes")["abstained"]
    with pytest.raises(ValueError):
        rag.search("VPN", k=0)


def test_question_benchmark_is_measured_and_not_human_reviewed():
    report = benchmark(DATA, ["fixed"], baseline=True)
    assert report["question_count"] == 20
    assert report["document_count"] == 20
    assert 0 <= report["strategies"]["fixed"]["recall_at_5"] <= 1
    assert not report["release_gate_passed"]
