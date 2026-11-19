"""Exercise the shared grounded API against a local HTTP provider fixture."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from verify_embedding_runtime import running_api

from copilot.config import get_settings

CASES = [
    ("How do I set up VPN on my Mac?", "KB-1017"),
    ("How do I fix Windows VPN error 809?", "KB-1018"),
    ("What does policy POL-999999999 require?", None),
]


def verify():
    provider_calls = []

    class FixtureProvider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            request = json.loads(body["messages"][1]["content"])
            provider_calls.append(request["question"])
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
                "answer": quote,
                "abstained": False,
                "citations": [{"chunk_id": source["chunk_id"], "quote": quote}],
            }
            payload = json.dumps({"choices": [{"message": {"content": json.dumps(result)}}]})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload.encode())

    with ThreadingHTTPServer(("127.0.0.1", 0), FixtureProvider) as provider:
        worker = threading.Thread(target=provider.serve_forever, daemon=True)
        worker.start()
        try:
            os.environ.update(
                COPILOT_ANSWER_MODE="grounded",
                COPILOT_LLM_MODEL="local-http-fixture",
                COPILOT_LLM_API_KEY="fixture-only",
                COPILOT_LLM_BASE_URL=f"http://127.0.0.1:{provider.server_port}",
            )
            get_settings.cache_clear()
            observed = []
            with TemporaryDirectory() as directory:
                root = Path(directory)
                with running_api("tfidf", root / "cache.sqlite3", root / "state.sqlite3") as client:
                    health = client.get("/health").raise_for_status().json()
                    if health["mode"] != "grounded-source-selection":
                        raise RuntimeError(f"Grounded API did not start: {health}")
                    for index, (question, expected) in enumerate(CASES):
                        response = (
                            client.post(
                                "/ask",
                                headers={"Authorization": "Bearer runtime-test"},
                                json={"question": question, "thread_id": f"grounded-{index}"},
                            )
                            .raise_for_status()
                            .json()
                        )
                        citations = [item["document_id"] for item in response["citations"]]
                        if citations != ([expected] if expected else []):
                            raise RuntimeError(f"Unexpected citations for {question}: {citations}")
                        if response["abstained"] != (expected is None):
                            raise RuntimeError(f"Unexpected abstention for {question}")
                        observed.append({"question": question, "result": response})
            if len(provider_calls) != 2:
                raise RuntimeError("Unknown policy must abstain before calling the provider")
            return {
                "health": health,
                "provider": "local-http-fixture",
                "live_generation_verified": False,
                "provider_calls": len(provider_calls),
                "cases": observed,
            }
        finally:
            provider.shutdown()
            worker.join(timeout=5)


if __name__ == "__main__":
    result = verify()
    target = Path("reports/integrated/rag/grounded-runtime.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
