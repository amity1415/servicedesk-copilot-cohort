"""Exercise both retrieval backends over authenticated HTTP."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sqlite3
import threading
import time
from contextlib import closing, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
import uvicorn

from copilot.api.app import create_app

QUESTION = "How do I set up VPN on my Mac?"


@contextmanager
def running_api(mode, cache, state, *, data=Path("data"), tokens=None):
    os.environ["COPILOT_RETRIEVAL_BACKEND"] = mode
    os.environ["COPILOT_EMBEDDING_CACHE"] = str(cache)
    os.environ["COPILOT_TRANSPORT"] = "direct"
    app = create_app(data=data, state=state, tokens=tokens or {"runtime-test": "E1261"})
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        worker = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        worker.start()
        try:
            deadline = time.monotonic() + 15
            while not server.started:
                if not worker.is_alive() or time.monotonic() >= deadline:
                    raise RuntimeError("API did not start")
                time.sleep(0.05)
            url = f"http://127.0.0.1:{listener.getsockname()[1]}"
            with httpx.Client(base_url=url, trust_env=False, timeout=30.0) as client:
                yield client
        finally:
            server.should_exit = True
            worker.join(timeout=15)


def cache_count(cache):
    with closing(sqlite3.connect(cache)) as db:
        return db.execute("SELECT count(*) FROM vectors").fetchone()[0]


def verify(include_pgvector=False, include_hybrid=False):
    results = {}
    with TemporaryDirectory() as directory:
        cache = Path(directory) / "vectors.sqlite3"
        backends = [
            ("tfidf", "tfidf-vector-extractive"),
            ("neural", "neural-vector-extractive"),
        ]
        if include_pgvector or include_hybrid:
            backends.append(("pgvector", "pgvector-extractive"))
        if include_hybrid:
            backends.append(("hybrid", "hybrid-extractive"))
        for mode, expected in backends:
            with running_api(mode, cache, Path(directory) / f"{mode}.sqlite3") as client:
                health = client.get("/health").raise_for_status().json()
                if health["status"] != "ok" or health["mode"] != expected:
                    raise RuntimeError(f"Unexpected readiness response: {health}")
                counts = [cache_count(cache)] if mode == "neural" else []
                for attempt in range(2 if counts else 1):
                    answer = (
                        client.post(
                            "/ask",
                            json={"question": QUESTION, "thread_id": f"runtime-{attempt}"},
                            headers={"Authorization": "Bearer runtime-test"},
                        )
                        .raise_for_status()
                        .json()
                    )
                    citations = sorted({row["document_id"] for row in answer["citations"]})
                    if answer["abstained"] or "KB-1017" not in citations:
                        raise RuntimeError(f"Unexpected citations: {citations}")
                    if counts:
                        counts.append(cache_count(cache))
                if counts and not (counts[0] + 1 == counts[1] == counts[2]):
                    raise RuntimeError(f"Unexpected cache sizes: {counts}")
                results[mode] = {"health": health, "citations": citations, "cache_rows": counts}
    return {"question": QUESTION, "backends": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pgvector", action="store_true")
    parser.add_argument("--hybrid", action="store_true")
    args = parser.parse_args()
    result = verify(include_pgvector=args.pgvector, include_hybrid=args.hybrid)
    name = (
        "hybrid-runtime.json"
        if args.hybrid
        else "postgres-runtime.json"
        if args.pgvector
        else "embedding-runtime.json"
    )
    target = Path("reports/integrated/rag") / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
