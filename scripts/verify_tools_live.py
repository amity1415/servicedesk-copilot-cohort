"""Measure Session 18 against the frozen synthetic prompts with a capped OpenAI run."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx
from complete_session import ROOT, git

from copilot.config import get_settings
from copilot.llm.client import LUNA_MODEL, ModelClient
from copilot.llm.service_desk import (
    DraftEscalation,
    InvalidToolChoice,
    choose_tool,
    contract_digest,
    generate_ticket_draft,
)
from copilot.tools.service_desk import TOOLS
from copilot.tools.ticketing import TicketDraft

DATASET = ROOT / "evals/session18_tools.json"
ENDPOINT = "https://api.openai.com/v1/chat/completions"
PRICE_SOURCE = "https://developers.openai.com/api/docs/models/gpt-6-luna"
INPUT_RATE = Decimal("0.125")  # Use the cache-write rate as an upper estimate for all input.
OUTPUT_RATE = Decimal("0.50")
MAX_BUDGET = Decimal("0.08")
MAX_INPUT_TOKENS = 10000
MAX_OUTPUT_TOKENS = 384
MAX_REQUESTS = 50
CHAT_FRAMING_ALLOWANCE = 256


def estimate(input_tokens: int, output_tokens: int) -> Decimal:
    return (input_tokens * INPUT_RATE + output_tokens * OUTPUT_RATE) / 1_000_000


def fixture() -> tuple[dict, str]:
    raw = DATASET.read_bytes()
    data = json.loads(raw)
    choices, drafts = data["tool_choices"], data["drafts"]
    if (
        data["version"] != 1
        or len(choices) != 10
        or len(drafts) != 20
        or len({row["id"] for row in choices + drafts}) != 30
        or {row["expected"] for row in choices} != TOOLS.keys()
        or any(not row["request"].strip() or len(row["request"]) > 250 for row in choices + drafts)
    ):
        raise ValueError(
            "The evaluation needs ten labeled tool requests and twenty distinct synthetic drafts"
        )
    return data, hashlib.sha256(raw).hexdigest()


class MeteredProvider:
    def __init__(self, upstream: httpx.Client, budget: Decimal):
        self.upstream = upstream
        self.budget = budget
        self.calls = []
        self.spend = Decimal(0)
        self.case = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if str(request.url) != ENDPOINT or request.method != "POST" or self.case is None:
            raise ValueError("Unexpected live evaluation request")
        payload = json.loads(request.content)
        upper_input = len(request.content) + CHAT_FRAMING_ALLOWANCE
        if (
            len(self.calls) >= MAX_REQUESTS
            or upper_input > MAX_INPUT_TOKENS
            or self.spend + estimate(upper_input, MAX_OUTPUT_TOKENS) > self.budget
            or payload.get("model") != LUNA_MODEL
            or payload.get("service_tier") != "default"
            or payload.get("reasoning_effort") != "none"
            or payload.get("max_completion_tokens") != MAX_OUTPUT_TOKENS
            or payload["messages"][1] != {"role": "user", "content": self.case["request"]}
        ):
            raise ValueError(
                "The live request exceeded its approved model, fixture or budget limits"
            )
        event = {"case_id": self.case["id"], "input_token_bound": upper_input}
        self.calls.append(event)
        response = self.upstream.post(
            ENDPOINT,
            json={**payload, "store": False},
            headers={"Authorization": request.headers["Authorization"]},
        )
        event["http_status"] = response.status_code
        if response.is_success:
            data = response.json()
            usage = data["usage"]
            prompt, completion = usage["prompt_tokens"], usage["completion_tokens"]
            if not (0 < prompt <= upper_input and 0 <= completion <= MAX_OUTPUT_TOKENS):
                raise RuntimeError("OpenAI usage exceeded the recorded token bounds")
            self.spend += estimate(prompt, completion)
            event.update(
                provider_model=data["model"],
                request_id=response.headers.get("x-request-id"),
                prompt_tokens=prompt,
                completion_tokens=completion,
            )
        elif response.status_code == 400:
            error = response.json().get("error", {})
            event["provider_error"] = {key: error.get(key) for key in ("type", "code", "param")}
        return response


def evaluate(client: ModelClient, meter: MeteredProvider, fixtures: dict, report: dict) -> None:
    for case in fixtures["tool_choices"]:
        meter.case = case
        choice = choose_tool(client, case["request"])
        report["tool_choices"].append(
            {
                "id": case["id"],
                "expected": case["expected"],
                "selected": choice.name,
                "arguments": choice.arguments,
            }
        )
        print(f"{case['id']} selected {choice.name}", flush=True)
    if any(row["expected"] != row["selected"] for row in report["tool_choices"]):
        raise InvalidToolChoice("At least one live tool choice differed from the frozen label")

    for case in fixtures["drafts"]:
        meter.case = case
        start = len(meter.calls)
        draft = generate_ticket_draft(client, case["request"])
        report["drafts"].append(
            {"id": case["id"], "attempts": len(meter.calls) - start, "draft": draft.model_dump()}
        )
        print(f"{case['id']} validated", flush=True)


def read_live_report(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    dataset, digest = fixture()
    if (
        report["status"] != "complete"
        or report["mode"] != "live-openai-tool-evaluation"
        or report["model"] != LUNA_MODEL
        or report["dataset_sha256"] != digest
        or report["contract_sha256"] != contract_digest()
        or report["source_head"] != git("rev-parse", "HEAD")
    ):
        raise RuntimeError(
            "The live evaluation does not match the Session 18 model, source and fixture"
        )

    sequence = []
    for row, case in zip(report["tool_choices"], dataset["tool_choices"], strict=True):
        if (
            row["id"] != case["id"]
            or row["expected"] != case["expected"]
            or row["selected"] != case["expected"]
        ):
            raise RuntimeError("All ten live tool choices must match the frozen labels")
        TOOLS[row["selected"]].input.model_validate(row["arguments"])
        sequence.append(row["id"])
    for row, case in zip(report["drafts"], dataset["drafts"], strict=True):
        if row["id"] != case["id"] or row["attempts"] not in {1, 2}:
            raise RuntimeError("Every ticket sample needs a valid draft and at most one repair")
        TicketDraft.model_validate(row["draft"])
        sequence.extend([row["id"]] * row["attempts"])

    spend = Decimal(0)
    calls = report["calls"]
    budget = Decimal(report["budget_usd"])
    if not 0 < budget <= MAX_BUDGET or len(calls) > MAX_REQUESTS:
        raise RuntimeError("The observed live request or budget limit was invalid")
    for call, case_id in zip(calls, sequence, strict=True):
        prompt, completion = call["prompt_tokens"], call["completion_tokens"]
        if (
            call["case_id"] != case_id
            or call["http_status"] != 200
            or not call["provider_model"].startswith(LUNA_MODEL)
            or not call["request_id"]
            or not 0 < prompt <= call["input_token_bound"] <= MAX_INPUT_TOKENS
            or not 0 <= completion <= MAX_OUTPUT_TOKENS
        ):
            raise RuntimeError("The recorded OpenAI call failed the evidence checks")
        spend += estimate(prompt, completion)
    if spend != Decimal(report["estimated_usd"]) or spend > budget:
        raise RuntimeError("OpenAI usage does not match the recorded cost")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-spend-usd", type=Decimal, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    budget = args.max_spend_usd
    reserve = MAX_REQUESTS * estimate(MAX_INPUT_TOKENS, MAX_OUTPUT_TOKENS)
    if not budget.is_finite() or not reserve <= budget <= MAX_BUDGET:
        parser.error(
            f"The live plan requires at least ${reserve} and caps spending at ${MAX_BUDGET}"
        )
    settings = get_settings()
    if not settings.llm_api_key:
        parser.error("Set COPILOT_LLM_API_KEY in the local environment or ignored .env file")
    fixtures, digest = fixture()
    report = {
        "mode": "live-openai-tool-evaluation",
        "status": "incomplete",
        "source_head": git("rev-parse", "HEAD"),
        "run_at_utc": datetime.now(UTC).isoformat(),
        "model": LUNA_MODEL,
        "dataset_sha256": digest,
        "contract_sha256": contract_digest(),
        "pricing_source": PRICE_SOURCE,
        "input_usd_per_million_upper_estimate": str(INPUT_RATE),
        "output_usd_per_million": str(OUTPUT_RATE),
        "budget_usd": str(budget),
        "tool_choices": [],
        "drafts": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output, httpx.Client(timeout=30) as upstream:
        meter = MeteredProvider(upstream, budget)
        client = ModelClient(
            model=LUNA_MODEL,
            api_key=settings.llm_api_key.get_secret_value(),
            attempts=1,
            max_tokens=MAX_OUTPUT_TOKENS,
            transport=httpx.MockTransport(meter),
        )
        try:
            evaluate(client, meter, fixtures, report)
        except (
            DraftEscalation,
            InvalidToolChoice,
            httpx.HTTPError,
            RuntimeError,
            ValueError,
        ) as exc:
            report["failure"] = str(exc)
            print(report["failure"], flush=True)
            return 2
        else:
            report["status"] = "complete"
            print(f"Session 18 live checks complete. Estimated cost ${meter.spend}.", flush=True)
            return 0
        finally:
            report.update(calls=meter.calls, estimated_usd=str(meter.spend))
            json.dump(report, output, indent=2)
            output.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
