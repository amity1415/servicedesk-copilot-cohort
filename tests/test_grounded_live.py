import hashlib
import importlib
import json
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from copilot.llm.client import LUNA_MODEL
from copilot.rag.query import rewrite


@pytest.fixture
def live(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("verify_grounded_live")


def request_body(live, index=0):
    question, document = live.ANSWERABLE[index]
    return json.dumps(
        {
            "model": "approved-revision",
            "max_tokens": live.MAX_OUTPUT_TOKENS,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Use the supplied source."},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"question": rewrite(question), "sources": [{"chunk_id": f"{document}:1"}]}
                    ),
                },
            ],
        }
    ).encode()


def limits(live, *, max_input_tokens=2000, max_spend="0.02"):
    return live.Limits(max_input_tokens, Decimal(max_spend), Decimal("1"), Decimal("5"))


def test_budget_and_input_checks_stop_requests_before_contacting_provider(live):
    with pytest.raises(ValueError, match="above the approved limit"):
        limits(live, max_spend="0.001")

    def unexpected(request):
        pytest.fail("The input cap must prevent any upstream request")

    with httpx.Client(transport=httpx.MockTransport(unexpected)) as client:
        provider = live.BoundedProvider(
            client, "approved-revision", "test", limits(live, max_input_tokens=200)
        )
        assert provider.reply(request_body(live)).status_code == 400
        assert provider.refusals == ["input_limit"]
        assert provider.calls == []


def test_only_the_two_distinct_approved_questions_and_sources_can_reach_the_provider(live):
    attempts = []

    def reply(request):
        assert request.url == live.OPENAI_URL + "/chat/completions"
        attempts.append(request.content)
        return httpx.Response(
            200,
            json={
                "model": "approved-revision",
                "usage": {"prompt_tokens": 80, "completion_tokens": 40},
            },
        )

    first, second = (request_body(live, index) for index in range(2))
    unexpected = json.loads(first)
    user = json.loads(unexpected["messages"][1]["content"])
    user["sources"].append({"chunk_id": "KB-9999:1"})
    unexpected["messages"][1]["content"] = json.dumps(user)
    with httpx.Client(transport=httpx.MockTransport(reply)) as client:
        provider = live.BoundedProvider(client, "approved-revision", "test", limits(live))
        assert provider.reply(json.dumps(unexpected).encode()).status_code == 400
        assert provider.reply(first).status_code == 200
        assert provider.reply(first).status_code == 400
        assert provider.reply(second).status_code == 200
        assert provider.reply(second).status_code == 400
    assert attempts == [first, second]
    assert len(provider.calls) == 2
    assert provider.calls[0]["estimated_usd"] == "0.00028"


def test_a_provider_failure_does_not_retry_or_forward_the_next_question(live):
    def unavailable(request):
        raise httpx.ReadTimeout("no upstream response")

    with httpx.Client(transport=httpx.MockTransport(unavailable)) as client:
        provider = live.BoundedProvider(client, "approved-revision", "test", limits(live))
        assert provider.reply(request_body(live)).status_code == 502
        assert provider.reply(request_body(live, 1)).status_code == 400
    assert len(provider.calls) == 1
    assert provider.calls[0]["failure"] == "ReadTimeout"


@pytest.mark.parametrize("model", ["approved-revision", LUNA_MODEL])
def test_authenticated_api_runs_all_cases_with_a_bounded_upstream_fixture(live, model):
    runtime = importlib.import_module("verify_grounded_runtime")

    def reply(request):
        payload = json.loads(request.content)
        result = runtime.fixture_completion(json.loads(payload["messages"][1]["content"]))
        result["choices"][0]["finish_reason"] = "stop"
        served = model
        if model == LUNA_MODEL:
            assert payload["reasoning_effort"] == "none"
            assert payload["service_tier"] == "default"
            assert payload["response_format"] == {"type": "json_object"}
            assert payload["max_completion_tokens"] == 550
            assert "max_tokens" not in payload
            served = f"{model}-2026-01-01"
        return httpx.Response(
            200,
            json={
                **result,
                "model": served,
                "service_tier": "default",
                "usage": {"prompt_tokens": 400, "completion_tokens": 125},
            },
        )

    chosen_limits = live.Limits(7000, Decimal("0.003"), Decimal("0.125"), Decimal("0.50"))
    with httpx.Client(transport=httpx.MockTransport(reply)) as upstream:
        provider = live.BoundedProvider(upstream, model, "test", chosen_limits)
        with runtime.running_grounded_api(model, provider.reply) as client:
            report = runtime.exercise(client)
    runtime.check_cases(report)
    live.check_provider_calls(
        {"provider_calls": provider.calls, "provider_refusals": provider.refusals, "model": model}
    )
    assert chosen_limits.reserved_usd == Decimal("0.00230")
    assert [call["finish_reason"] for call in provider.calls] == ["stop", "stop"]


def test_completion_evidence_requires_review_of_the_exact_passing_transcript(
    live, tmp_path, monkeypatch
):
    monkeypatch.setattr(live, "source_fingerprint", lambda root: "sha")
    runtime = importlib.import_module("verify_grounded_runtime")
    transcript = {
        "provider": "openai",
        "mode": "live-grounded-runtime",
        "live_generation_verified": True,
        "source_fingerprint": "sha",
        "model": "approved-revision",
        "health": {"status": "ok", "mode": runtime.MODE},
        "provider_refusals": [],
        "provider_calls": [
            {"question": question, "accepted": True, "model": "approved-revision"}
            for question, _ in live.ANSWERABLE
        ],
        "workflow_smoke": {"status": "needs_details"},
        "cases": [
            {
                "question": question,
                "request_id": str(index),
                "result": {
                    "mode": runtime.MODE,
                    "prompt_version": runtime.PROMPT.stem,
                    "answer": "Excerpt." if doc else "I can help you raise a support ticket.",
                    "citations": [{"document_id": doc, "quote": "Excerpt."}] if doc else [],
                    "abstained": not doc,
                    "reason": "no_supporting_source" if not doc else None,
                },
            }
            for index, (question, doc) in enumerate(live.CASES)
        ],
    }
    transcript_path = tmp_path / "transcript.json"
    transcript_path.write_text(json.dumps(transcript), encoding="utf-8")
    review = {
        "transcript_sha256": hashlib.sha256(transcript_path.read_bytes()).hexdigest(),
        "reviewer": "Test reviewer",
        "verdicts": [
            {"request_id": str(index), "supported": True, "notes": "Checked the cited text"}
            for index in range(2)
        ],
    }
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    assert live.read_review(transcript_path, review_path, tmp_path) == (transcript, review)

    review["verdicts"][1]["supported"] = False
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(RuntimeError, match="passing human citation review"):
        live.read_review(transcript_path, review_path, tmp_path)
    transcript_path.write_text(json.dumps(transcript) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="exact live transcript"):
        live.read_review(transcript_path, review_path, tmp_path)
