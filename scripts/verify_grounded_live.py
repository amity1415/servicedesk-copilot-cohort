"""Run the two authorized Session 14 OpenAI requests and save review evidence."""

import argparse
import hashlib
import json
import re
import threading
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import httpx
from complete_session import ROOT, git
from verify_grounded_runtime import CASES, check_cases, exercise, running_grounded_api, write_report

from copilot.config import get_settings
from copilot.llm.client import LUNA_MODEL
from copilot.rag.grounded import MAX_OUTPUT_TOKENS
from copilot.rag.query import rewrite

OPENAI_URL = "https://api.openai.com/v1"
ANSWERABLE = tuple((question, doc) for question, doc in CASES if doc)
CASE_SOURCES = {
    "KB-1017": frozenset({"KB-1017", "KB-1061", "KB-1094", "REF-003"}),
    "KB-1018": frozenset({"KB-1018"}),
}
# UTF-8 request bytes conservatively count text tokens for OpenAI's byte-level
# tokenizer. Reserve additional framing tokens and check reported usage afterwards.
CHAT_FRAMING_ALLOWANCE = 256


@dataclass(frozen=True)
class Limits:
    max_input_tokens: int
    max_spend_usd: Decimal
    input_usd_per_million: Decimal
    output_usd_per_million: Decimal

    def __post_init__(self):
        prices = (self.max_spend_usd, self.input_usd_per_million, self.output_usd_per_million)
        if self.max_input_tokens <= 0 or any(
            not value.is_finite() or value <= 0 for value in prices
        ):
            raise ValueError(
                "Token and USD limits and both unit prices must be finite and positive"
            )
        if self.reserved_usd > self.max_spend_usd:
            raise ValueError(
                f"Both requests reserve ${self.reserved_usd}, above the approved limit"
            )

    def cost(self, input_tokens, output_tokens):
        return (
            input_tokens * self.input_usd_per_million + output_tokens * self.output_usd_per_million
        ) / 1_000_000

    @property
    def reserved_usd(self):
        return self.cost(self.max_input_tokens, MAX_OUTPUT_TOKENS) * len(ANSWERABLE)

    def report(self):
        return {
            key: str(value) if isinstance(value, Decimal) else value
            for key, value in asdict(self).items()
        } | {
            "max_requests": len(ANSWERABLE),
            "max_output_tokens_per_request": MAX_OUTPUT_TOKENS,
            "reserved_usd": str(self.reserved_usd),
        }


class BoundedProvider:
    """Forward each allowed question once, even when the upstream request fails."""

    def __init__(self, client, model, key, limits):
        self.client = client
        self.model = model
        self.key = key
        self.limits = limits
        self.options = {"model": model, "temperature": 0}
        self.output_field = "max_tokens"
        if model == LUNA_MODEL:
            self.options.update(
                reasoning_effort="none",
                service_tier="default",
                response_format={"type": "json_object"},
            )
            self.output_field = "max_completion_tokens"
        self.calls = []
        self.refusals = []
        self.lock = threading.Lock()

    def reject(self, reason):
        self.refusals.append(reason)
        return httpx.Response(400, json={"error": reason})

    def reply(self, body):
        upper_input = len(body) + CHAT_FRAMING_ALLOWANCE
        with self.lock:
            index = len(self.calls)
            if index >= len(ANSWERABLE) or (self.calls and not self.calls[-1]["accepted"]):
                return self.reject("request_limit_or_previous_failure")
            if upper_input > self.limits.max_input_tokens:
                return self.reject("input_limit")
            question, document = ANSWERABLE[index]
            try:
                payload = json.loads(body)
                messages = payload["messages"]
                user = json.loads(messages[1]["content"])
                source_ids = {chunk["chunk_id"].partition(":")[0] for chunk in user["sources"]}
                output_limit = payload[self.output_field]
                valid = (
                    payload.keys() == self.options.keys() | {"messages", self.output_field}
                    and all(payload[key] == value for key, value in self.options.items())
                    and type(output_limit) is int
                    and 0 < output_limit <= MAX_OUTPUT_TOKENS
                    and [message["role"] for message in messages] == ["system", "user"]
                    and user.keys() == {"question", "sources"}
                    and user["question"] == rewrite(question)
                    and document in source_ids
                    and source_ids <= CASE_SOURCES[document]
                )
            except (AttributeError, IndexError, KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                return self.reject("unexpected_request")
            event = {
                "question": question,
                "input_token_bound": upper_input,
                "output_token_limit": output_limit,
                "accepted": False,
            }
            self.calls.append(event)
            return self.forward(body, event)

    def forward(self, body, event):
        try:
            response = self.client.post(
                OPENAI_URL + "/chat/completions",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                content=body,
            )
            event["http_status"] = response.status_code
            response.raise_for_status()
            data = response.json()
            usage = data["usage"]
            prompt, completion = usage["prompt_tokens"], usage["completion_tokens"]
            choices = data.get("choices") or []
            event.update(
                model=data["model"],
                prompt_tokens=prompt,
                completion_tokens=completion,
                service_tier=data.get("service_tier"),
                finish_reason=choices[0].get("finish_reason") if choices else None,
            )
        except (httpx.HTTPError, AttributeError, KeyError, TypeError, ValueError) as error:
            event["failure"] = type(error).__name__
            return httpx.Response(502, json={"error": "provider_error"})
        event["accepted"] = (
            matches_model(self.model, event["model"])
            and (self.model != LUNA_MODEL or event["service_tier"] == "default")
            and type(prompt) is int
            and 0 < prompt <= event["input_token_bound"]
            and type(completion) is int
            and 0 < completion <= event["output_token_limit"]
        )
        if not event["accepted"]:
            event["failure"] = "model_or_usage_differed_from_plan"
            return httpx.Response(502, json={"error": event["failure"]})
        event["estimated_usd"] = str(self.limits.cost(prompt, completion))
        return httpx.Response(200, json=data)


def matches_model(requested, served):
    # Luna is published under an undated ID. Preserve a dated serving ID when returned.
    return requested == served or (
        requested == LUNA_MODEL
        and isinstance(served, str)
        and re.fullmatch(r"gpt-6-luna-\d{4}-\d{2}-\d{2}", served) is not None
    )


def source_fingerprint(root):
    paths = [
        *root.glob("src/copilot/**/*.py"),
        *root.glob("src/copilot/rag/prompts/*.md"),
        *root.glob("data/**/*"),
        root / "policies/source_metadata.json",
        root / "scripts/verify_grounded_live.py",
        root / "scripts/verify_grounded_runtime.py",
        root / "scripts/verify_embedding_runtime.py",
    ]
    digest = hashlib.sha256()
    for path in sorted(path for path in paths if path.is_file()):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def check_provider_calls(report):
    calls = report["provider_calls"]
    if (
        report["provider_refusals"]
        or [call["question"] for call in calls] != [question for question, _ in ANSWERABLE]
        or not all(
            call["accepted"] is True and matches_model(report["model"], call.get("model"))
            for call in calls
        )
    ):
        raise RuntimeError("The provider did not complete exactly the two authorized requests")


def run(model, limits):
    settings = get_settings()
    if not settings.llm_api_key:
        raise ValueError("Configure the scoped COPILOT_LLM_API_KEY locally before using --live")
    if settings.llm_base_url.rstrip("/") != OPENAI_URL or (
        settings.llm_provider and settings.llm_provider.lower() != "openai"
    ):
        raise ValueError("Session 14's live runner uses the approved OpenAI endpoint")
    if model != settings.llm_model:
        raise ValueError("--model must match the model ID configured in COPILOT_LLM_MODEL")
    report = {
        "mode": "live-grounded-runtime",
        "provider": "openai",
        "model": model,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "source_revision": git("rev-parse", "HEAD"),
        "source_fingerprint": source_fingerprint(ROOT),
        "limits": limits.report(),
        "live_generation_verified": False,
    }
    timeout = settings.request_timeout_s
    with httpx.Client(timeout=timeout, follow_redirects=False) as upstream:
        provider = BoundedProvider(upstream, model, settings.llm_api_key.get_secret_value(), limits)
        report.update(
            request_options=provider.options,
            provider_calls=provider.calls,
            provider_refusals=provider.refusals,
        )
        try:
            with running_grounded_api(
                model, provider.reply, provider_timeout=timeout, data=ROOT / "data"
            ) as client:
                report.update(exercise(client, timeout=timeout + 10))
            check_cases(report)
            check_provider_calls(report)
        except RuntimeError as error:
            report["failure"] = str(error)
        except httpx.HTTPError as error:
            report["failure"] = f"Local API request failed ({type(error).__name__})"
        else:
            report["live_generation_verified"] = True
    return report


def read_review(transcript_path, review_path, root):
    raw = transcript_path.read_bytes()
    transcript = json.loads(raw)
    review = json.loads(review_path.read_bytes())
    if (
        transcript.get("mode") != "live-grounded-runtime"
        or transcript.get("provider") != "openai"
        or transcript.get("live_generation_verified") is not True
        or transcript.get("source_fingerprint") != source_fingerprint(root)
    ):
        raise RuntimeError("A passing live transcript for the current app and data is required")
    check_cases(transcript)
    check_provider_calls(transcript)
    if review.get("transcript_sha256") != hashlib.sha256(raw).hexdigest():
        raise RuntimeError("The review must refer to the exact live transcript")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise RuntimeError("The review must name the human reviewer")
    expected_ids = [case["request_id"] for case in transcript["cases"][: len(ANSWERABLE)]]
    reviewed = review.get("verdicts", [])
    if [verdict.get("request_id") for verdict in reviewed] != expected_ids or not all(
        verdict.get("supported") is True
        and isinstance(verdict.get("notes"), str)
        and verdict["notes"].strip()
        for verdict in reviewed
    ):
        raise RuntimeError("Both answerable responses need a passing human citation review")
    return transcript, review


def decimal_argument(value):
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise argparse.ArgumentTypeError("expected a USD amount") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-input-tokens", type=int, required=True, help="per request")
    parser.add_argument("--max-spend-usd", type=decimal_argument, required=True)
    parser.add_argument("--input-usd-per-million", type=decimal_argument, required=True)
    parser.add_argument("--output-usd-per-million", type=decimal_argument, required=True)
    args = parser.parse_args()
    if not args.model.strip() or args.model == "offline":
        parser.error("select an explicit live model ID")
    try:
        limits = Limits(
            args.max_input_tokens,
            args.max_spend_usd,
            args.input_usd_per_million,
            args.output_usd_per_million,
        )
        report = run(args.model, limits)
    except ValueError as error:
        parser.error(str(error))
    name = f"grounded-live-{uuid4().hex}"
    target = write_report(name + ".json", report)
    print(f"Live transcript: {target}")
    if not report["live_generation_verified"]:
        print(report["failure"])
        return 1
    template = {
        "transcript_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "reviewer": "",
        "verdicts": [
            {"request_id": case["request_id"], "supported": None, "notes": ""}
            for case in report["cases"][: len(ANSWERABLE)]
        ],
    }
    review_path = write_report(name + "-review.json", template)
    print(f"Human review template: {review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
