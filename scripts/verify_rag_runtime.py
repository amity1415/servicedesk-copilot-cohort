"""Exercise actual CPU sentence inference and an isolated real HTTP API process."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def verify():
    import numpy as np

    from copilot.rag.semantic_encoder import OnnxEncoder

    work = ROOT / ".work/rag-runtime-validation"
    work.mkdir(parents=True, exist_ok=True)
    marker = uuid.uuid4().hex[:10]
    encoder = OnnxEncoder(ROOT / ".work/models/minilm", cache=work / f"cold-{marker}.sqlite3")
    samples = [
        "How can I connect to the company VPN?",
        "Set up the corporate virtual private network connection.",
        "The cafeteria is serving fruit salad for lunch.",
    ]
    vectors = np.asarray(encoder.encode(samples))
    assert vectors.shape == (3, 384)
    assert np.isfinite(vectors).all()
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)
    related, unrelated = float(vectors[0] @ vectors[1]), float(vectors[0] @ vectors[2])
    assert related > unrelated
    misses = encoder.encoded_misses
    assert misses == 3
    assert encoder.encode(samples) == vectors.tolist()
    assert encoder.encoded_misses == misses
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    state = work / f"api-{marker}.sqlite3"
    code = (
        "from pathlib import Path; import uvicorn; "
        "from copilot.api.app import create_app; "
        f"app=create_app(Path('data'), Path({str(state)!r}), "
        "tokens={'rag-runtime-fixture':'E1261'}); "
        f"uvicorn.run(app,host='127.0.0.1',port={port})"
    )
    with (work / f"http-{marker}.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-c", code], cwd=ROOT, env=environment, stdout=log, stderr=log
        )
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError("Temporary API exited; inspect runtime-validation log")
                try:
                    with urlopen(base + "/health", timeout=1) as response:
                        health = json.loads(response.read())
                    break
                except OSError:
                    time.sleep(0.5)
            else:
                raise RuntimeError("Temporary API readiness timeout")
            assert health["mode"] == "tfidf-vector-extractive"
            body = json.dumps(
                {
                    "question": "How do I set up VPN on my Mac?",
                    "thread_id": "isolated-rag-validation",
                }
            ).encode()
            try:
                urlopen(
                    Request(base + "/ask", data=body, headers={"Content-Type": "application/json"}),
                    timeout=10,
                )
            except HTTPError as exc:
                assert exc.code == 401
            else:
                raise AssertionError("Unauthenticated request was accepted")
            request = Request(
                base + "/ask",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer rag-runtime-fixture",
                },
            )
            with urlopen(request, timeout=15) as response:
                answer = json.loads(response.read())
            assert {c["document_id"] for c in answer["citations"]} == {"KB-1017"}
            assert "System Settings" in answer["answer"]
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    result = {
        "actual_cpu_inference": True,
        "model_revision": encoder.manifest["revision"],
        "cold_vectors_encoded": misses,
        "vector_dimension": 384,
        "related_cosine": related,
        "unrelated_cosine": unrelated,
        "cache_repeat_verified": True,
        "http_health": 200,
        "http_unauthenticated": 401,
        "http_mac_article": "KB-1017",
        "existing_api_or_ui_restarted": False,
        "paid_calls": 0,
    }
    destination = ROOT / "reports/rag-batch-validation/runtime-probes.json"
    destination.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    verify()
