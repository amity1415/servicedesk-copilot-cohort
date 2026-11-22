"""Exercise the shared grounded API against a local HTTP provider fixture."""

import json
import os
import secrets
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx
from verify_embedding_runtime import running_api

from copilot.config import get_settings
from copilot.rag.grounded import MODE, PROMPT
from copilot.rag.query import rewrite

CASES = (
    ("How do I set up VPN on my Mac?", "KB-1017"),
    ("How do I fix Windows VPN error 809?", "KB-1018"),
    ("What does policy POL-999999999 require?", None),
)
SMOKE = "We have a new joiner next week."
REPORT_DIR = Path("reports/integrated/rag")


@contextmanager
def running_grounded_api(model, reply, *, provider_timeout=25, data=Path("data")):
    """Start a separate API and SQLite store, with a loopback provider adapter."""
    token = secrets.token_urlsafe(24)

    class LocalProvider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            if self.path != "/chat/completions":
                self.send_error(404)
                return
            if not secrets.compare_digest(self.headers.get("Authorization", ""), f"Bearer {token}"):
                self.send_error(401)
                return
            body = self.rfile.read(int(self.headers["Content-Length"]))
            result = reply(body)
            self.send_response(result.status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(result.content)))
            self.end_headers()
            self.wfile.write(result.content)

    with ThreadingHTTPServer(("127.0.0.1", 0), LocalProvider) as provider:
        worker = threading.Thread(target=provider.serve_forever, daemon=True)
        worker.start()
        config = {
            "COPILOT_ANSWER_MODE": "grounded",
            "COPILOT_LLM_MODEL": model,
            "COPILOT_LLM_API_KEY": token,
            "COPILOT_LLM_BASE_URL": f"http://127.0.0.1:{provider.server_port}",
            "COPILOT_REQUEST_TIMEOUT_S": str(provider_timeout + 5),
        }
        try:
            with patch.dict(os.environ, config), TemporaryDirectory() as directory:
                get_settings.cache_clear()
                root = Path(directory)
                with running_api(
                    "tfidf", root / "cache.sqlite3", root / "state.sqlite3", data=data
                ) as client:
                    yield client
        finally:
            provider.shutdown()
            worker.join(timeout=5)
            get_settings.cache_clear()


def exercise(client, *, timeout=35):
    health = client.get("/health").raise_for_status().json()
    if health["status"] != "ok" or health["mode"] != MODE:
        raise RuntimeError(f"Grounded API did not start: {health}")
    headers = {"Authorization": "Bearer runtime-test"}
    observed = []
    for index, (question, _) in enumerate(CASES):
        response = client.post(
            "/ask",
            headers=headers,
            json={"question": question, "thread_id": f"grounded-{index}"},
            timeout=timeout,
        ).raise_for_status()
        observed.append(
            {
                "question": question,
                "request_id": response.headers["X-Request-ID"],
                "elapsed_s": float(response.headers["X-Elapsed-Seconds"]),
                "result": response.json(),
            }
        )
    smoke = client.post(
        "/ask",
        headers=headers,
        json={"question": SMOKE, "thread_id": "workflow-smoke"},
    ).raise_for_status()
    return {
        "health": health,
        "retrieval_backend": "tfidf",
        "transport": "direct",
        "cases": observed,
        "workflow_smoke": {"question": SMOKE, "status": smoke.json()["status"]},
    }


def check_cases(report):
    cases = report["cases"]
    if (
        report["health"]["status"] != "ok"
        or report["health"]["mode"] != MODE
        or len(cases) != len(CASES)
        or len({case["request_id"] for case in cases}) != len(CASES)
        or report["workflow_smoke"]["status"] != "needs_details"
    ):
        raise RuntimeError("Required API cases or the existing workflow smoke check failed")
    for case, (question, expected) in zip(cases, CASES, strict=True):
        result = case["result"]
        citations = {item["document_id"] for item in result["citations"]}
        if (
            case["question"] != question
            or result["mode"] != MODE
            or result["prompt_version"] != PROMPT.stem
            or citations != ({expected} if expected else set())
            or result["abstained"] is not (expected is None)
            or not result["answer"].strip()
            or any(not item["quote"].strip() for item in result["citations"])
            or (expected is None and result.get("reason") != "no_supporting_source")
        ):
            raise RuntimeError(f"Unexpected grounding result for {question}")


def write_report(name, report):
    target = REPORT_DIR / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return target


def fixture_completion(request):
    expected = "KB-1018" if "809" in request["question"] else "KB-1017"
    target = "App Hub" if expected == "KB-1017" else "try the VPN"
    source, quote = next(
        (item, line)
        for item in request["sources"]
        if item["chunk_id"].startswith(expected)
        for line in item["content"].splitlines()
        if target in line
    )
    result = {
        "abstained": False,
        "citations": [{"chunk_id": source["chunk_id"], "quote": quote}],
    }
    return {"choices": [{"message": {"content": json.dumps(result)}}]}


def verify():
    provider_calls = []

    def fixture(body):
        request = json.loads(json.loads(body)["messages"][1]["content"])
        provider_calls.append({"question": request["question"], "request_bytes": len(body)})
        return httpx.Response(200, json=fixture_completion(request))

    with running_grounded_api("local-http-fixture", fixture) as client:
        report = exercise(client)
    check_cases(report)
    expected_calls = [rewrite(question) for question, expected in CASES if expected]
    if [call["question"] for call in provider_calls] != expected_calls:
        raise RuntimeError("Only answerable grounding cases may call the provider")
    return {
        **report,
        "provider": "local-http-fixture",
        "live_generation_verified": False,
        "provider_calls": len(provider_calls),
        "fixture_request_sizes": provider_calls,
    }


if __name__ == "__main__":
    result = verify()
    write_report("grounded-runtime.json", result)
    print(json.dumps(result))
