"""Verify follow-up rewriting and thread ownership through the HTTP API."""

import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from verify_embedding_runtime import running_api


def verify():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        data = root / "data"
        shutil.copytree(Path("data/db/csv"), data / "db/csv")
        kb = data / "kb"
        kb.mkdir()
        for code in ("809", "806"):
            (kb / f"KB-9{code}.md").write_text(
                f"---\naudience: employee\nos: windows\n---\n"
                f"VPN error {code} troubleshooting on Windows.\n",
                encoding="utf-8",
            )
        tokens = {"first-actor": "E1261", "second-actor": "E1001"}
        with running_api(
            "tfidf", root / "cache.sqlite3", root / "state.sqlite3", data=data, tokens=tokens
        ) as client:

            def ask(actor, thread, question):
                return client.post(
                    "/ask",
                    headers={"Authorization": f"Bearer {actor}"},
                    json={"question": question, "thread_id": thread},
                )

            def conversation(actor, code):
                thread = f"thread-{actor}"
                for question in (f"VPN error {code} on Windows", "It still doesn't work."):
                    answer = ask(actor, thread, question).raise_for_status().json()
                    ids = sorted({item["document_id"] for item in answer["citations"]})
                    if ids != [f"KB-9{code}"]:
                        raise RuntimeError(f"Wrong follow-up context for {actor}: {ids}")
                return {"actor": actor, "error_code": code, "citations": ids}

            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(conversation, "first-actor", "809")
                second = pool.submit(conversation, "second-actor", "806")
                conversations = [first.result(), second.result()]
            forbidden = ask("second-actor", "thread-first-actor", "Same problem")
            if forbidden.status_code != 403:
                raise RuntimeError("A different actor could read the original thread")
        return {"conversations": conversations, "cross_actor_http": forbidden.status_code}


if __name__ == "__main__":
    result = verify()
    target = Path("reports/integrated/rag/followup-runtime.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
