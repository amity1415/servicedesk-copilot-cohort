from types import SimpleNamespace

import pytest

from copilot.rag.loaders import is_allowed
from copilot.rag.pipeline import Chunk


def test_rag_evaluation_contract():
    from copilot.rag.evaluation import Case, bootstrap_delta, case_evidence, score_case, summarize

    windows = {"audience": "employee", "os": "windows"}
    assert is_allowed(windows, os_name="Windows 11")
    assert not is_allowed(windows, os_name="iOS")

    case = Case(
        id="demo-1",
        question="How do I connect the VPN?",
        expected_articles=["KB-1017"],
        reference_answer="Install the VPN through App Hub.",
        review_status="reviewed",
        reviewer="test-reviewer",
        split="development",
        reference_excerpts={"KB-1017": ["Install the VPN through App Hub."]},
    )
    text = "## Steps\n1. Install the VPN through App Hub."
    documents = {"KB-1017": SimpleNamespace(text=text, metadata={"audience": "employee"})}
    excerpts, excluded = case_evidence(case, documents)
    assert excluded == []
    good = Chunk("a", "KB-1017", text, {}, "kb.md")
    irrelevant = Chunk("b", "KB-1061", "Clean the trackpad.", {}, "other.md")
    hit_citations = [{"chunk_id": "a", "document_id": "KB-1017"}]
    answer = {
        "answer": "1. Install the VPN through App Hub.",
        "abstained": False,
        "citations": hit_citations,
    }
    scored = score_case(case, excerpts, [good, irrelevant], answer)
    assert scored["recall_at_5"] == scored["faithfulness"] == scored["answer_relevance"] == 1
    assert scored["context_precision"] == 0.5
    assert scored["failure"] is None

    unsupported = score_case(case, excerpts, [good], answer | {"answer": "Use the app store."})
    assert unsupported["faithfulness"] == 0 and unsupported["failure"] == "generation"
    short = Chunk("a", "KB-1017", "VPN setup.", {}, "kb.md")
    incomplete = score_case(case, excerpts, [short], answer | {"answer": short.text})
    assert incomplete["recall_at_5"] == 1 and incomplete["failure"] == "bad_chunk"
    missed = score_case(case, excerpts, [irrelevant], answer)
    assert missed["recall_at_5"] == 0 and missed["failure"] == "retrieval_miss"

    unknown = case.model_copy(update={"expected_articles": [], "reference_excerpts": {}})
    abstained = {"answer": "No evidence.", "abstained": True, "citations": []}
    negative = score_case(unknown, {}, [], abstained)
    assert negative["recall_at_5"] is None and negative["faithfulness"] is None
    assert negative["answer_relevance"] == 1
    report = summarize(
        [
            {
                "expected_articles": case.expected_articles,
                "baseline": missed | {"contains_expected": False},
                "current": scored | {"contains_expected": True},
            }
        ]
    )
    assert report["corpus_coverage"] == {"baseline": 0, "current": 1}
    assert report["recall_at_5"]["paired_delta"] == bootstrap_delta([(0, 1)])
    assert report["recall_at_5"]["paired_delta"]["ci95"] == [1, 1]

    bad_review = case.model_copy(update={"reference_excerpts": {"KB-1017": ["Copy a password."]}})
    with pytest.raises(ValueError, match="absent from KB-1017"):
        case_evidence(bad_review, documents)
