"""Run and record the bounded Session 19 model trajectory on synthetic data."""

import argparse
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx
from complete_session import ROOT, git
from verify_tools_live import CHAT_FRAMING_ALLOWANCE, ENDPOINT, PRICE_SOURCE, estimate

from copilot.agents.diagnostics import SLOW_REQUEST
from copilot.agents.react import DIAGNOSTIC_TOOLS, model_decider
from copilot.agents.verify_react import loop_digest, verify_react
from copilot.config import get_settings
from copilot.llm.client import LUNA_MODEL, ModelClient

MAX_CALLS = 6
MAX_INPUT = 16000
MAX_OUTPUT = 384
MAX_BUDGET = Decimal(".02")


class MeteredDiagnosis:
    def __init__(self, upstream: httpx.Client, budget: Decimal):
        self.upstream, self.budget = upstream, budget
        self.calls = []
        self.spend = Decimal(0)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        upper_input = len(request.content) + CHAT_FRAMING_ALLOWANCE
        user = json.loads(payload["messages"][1]["content"])
        if (
            str(request.url) != ENDPOINT
            or request.method != "POST"
            or len(self.calls) >= MAX_CALLS
            or upper_input > MAX_INPUT
            or self.spend + estimate(upper_input, MAX_OUTPUT) > self.budget
            or payload["model"] != LUNA_MODEL
            or payload["service_tier"] != "default"
            or payload["reasoning_effort"] != "none"
            or payload["max_completion_tokens"] != MAX_OUTPUT
            or user["request"] != SLOW_REQUEST
            or any(event["tool"] not in DIAGNOSTIC_TOOLS for event in user["observations"])
        ):
            raise ValueError("The request exceeded the Session 19 fixture or budget limits")
        event = {"input_token_bound": upper_input, "observations": len(user["observations"])}
        self.calls.append(event)
        reply = self.upstream.post(
            ENDPOINT,
            json={**payload, "store": False},
            headers={"Authorization": request.headers["Authorization"]},
        )
        event["http_status"] = reply.status_code
        if reply.is_success:
            data = reply.json()
            usage = data["usage"]
            prompt, output = usage["prompt_tokens"], usage["completion_tokens"]
            if not 0 < prompt <= upper_input or not 0 <= output <= MAX_OUTPUT:
                raise RuntimeError("Provider token usage exceeded the recorded bounds")
            self.spend += estimate(prompt, output)
            decision = data["choices"][0]["message"].get("content") or ""
            event.update(
                provider_model=data["model"],
                request_id=reply.headers.get("x-request-id"),
                prompt_tokens=prompt,
                completion_tokens=output,
                decision=decision,
            )
        return reply


def read_live_report(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("status") != "complete":
        raise RuntimeError("The live diagnostic report is incomplete")
    proof = report["http_verification"]
    trajectory = proof["trajectory"]
    calls = report["calls"]
    if (
        report["mode"] != "live-openai-diagnostics"
        or report["model"] != LUNA_MODEL
        or report["source_head"] != git("rev-parse", "HEAD")
        or proof["loop_sha256"] != loop_digest()
        or trajectory["status"] != "suggested_fixes"
        or trajectory["decision_source"] != "configured"
        or trajectory["documents"] != ["KB-1054"]
        or [row["tool"] for row in trajectory["events"]] != list(DIAGNOSTIC_TOOLS)
        or proof["tickets_written"] != 0
        or len(calls) != len(DIAGNOSTIC_TOOLS) + 1
    ):
        raise RuntimeError("The live model did not complete the expected diagnostic trajectory")
    spend = Decimal(0)
    for step, call in enumerate(calls):
        prompt, output = call["prompt_tokens"], call["completion_tokens"]
        decision = json.loads(call["decision"])
        action_matches = (
            decision.get("tool") == DIAGNOSTIC_TOOLS[step]
            and decision.get("arguments", {}) == trajectory["events"][step]["arguments"]
            if step < len(DIAGNOSTIC_TOOLS)
            else decision["answer"].strip() == trajectory["answer"]
        )
        if (
            call["observations"] != step
            or call["http_status"] != 200
            or not call["request_id"]
            or not call["provider_model"].startswith(LUNA_MODEL)
            or not 0 < prompt <= call["input_token_bound"] <= MAX_INPUT
            or not 0 <= output <= MAX_OUTPUT
            or not action_matches
        ):
            raise RuntimeError("A recorded model decision or provider request failed verification")
        spend += estimate(prompt, output)
    budget = Decimal(report["budget_usd"])
    if not 0 < spend <= budget <= MAX_BUDGET or spend != Decimal(report["estimated_usd"]):
        raise RuntimeError("The recorded model cost did not satisfy the budget")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-spend-usd", type=Decimal, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    budget = args.max_spend_usd
    reserved = MAX_CALLS * estimate(MAX_INPUT, MAX_OUTPUT)
    if not budget.is_finite() or not reserved <= budget <= MAX_BUDGET:
        parser.error(f"Budget must be between ${reserved} and ${MAX_BUDGET}")
    settings = get_settings()
    if not settings.llm_api_key:
        parser.error("Set COPILOT_LLM_API_KEY in the local environment or ignored .env file")
    report = {
        "status": "incomplete",
        "mode": "live-openai-diagnostics",
        "model": LUNA_MODEL,
        "source_head": git("rev-parse", "HEAD"),
        "run_at_utc": datetime.now(UTC).isoformat(),
        "pricing_source": PRICE_SOURCE,
        "budget_usd": str(budget),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output, httpx.Client(timeout=12) as upstream:
        meter = MeteredDiagnosis(upstream, budget)
        client = ModelClient(
            model=LUNA_MODEL,
            api_key=settings.llm_api_key.get_secret_value(),
            timeout=12,
            attempts=1,
            max_tokens=MAX_OUTPUT,
            json_response=True,
            transport=httpx.MockTransport(meter),
        )
        try:
            report["http_verification"] = verify_react(
                ROOT / "data", decision=model_decider(client)
            )
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            report["failure"] = str(exc)
            print(report["failure"], flush=True)
            return 2
        else:
            report["status"] = "complete"
            print(
                f"Model passed in {len(meter.calls)} calls. Estimated cost ${meter.spend}.",
                flush=True,
            )
            return 0
        finally:
            report.update(calls=meter.calls, estimated_usd=str(meter.spend))
            json.dump(report, output, indent=2)
            output.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
