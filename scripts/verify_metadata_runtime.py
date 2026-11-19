"""Verify cross-role and cross-region retrieval over the shared HTTP API."""

import json
import shutil
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
        for article, audience, region in (
            ("KB-9990", "it-staff", "Asia-Pacific"),
            ("KB-9991", "employee", "Asia-Pacific"),
        ):
            (kb / f"{article}.md").write_text(
                f"---\naudience: {audience}\nregion: {region}\nos: Mac OS\n---\n"
                f"Catalog entry {article} for macOS.\n",
                encoding="utf-8",
            )
        tokens = {"employee-emea": "E1261", "employee-apac": "E1001", "analyst-apac": "E1203"}
        cases = [
            ("employee-apac", "KB-9990", []),
            ("analyst-apac", "KB-9990", ["KB-9990"]),
            ("employee-emea", "KB-9991", []),
            ("employee-apac", "KB-9991", ["KB-9991"]),
        ]
        evidence = []
        with running_api(
            "tfidf", root / "cache.sqlite3", root / "state.sqlite3", data=data, tokens=tokens
        ) as client:
            health = client.get("/health").raise_for_status().json()
            for number, (token, article, expected) in enumerate(cases):
                response = (
                    client.post(
                        "/ask",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "question": f"Find {article} for macOS",
                            "thread_id": f"scope-{number}",
                        },
                    )
                    .raise_for_status()
                    .json()
                )
                ids = sorted({citation["document_id"] for citation in response["citations"]})
                if ids != expected or response["abstained"] != (not expected):
                    raise RuntimeError(f"Unexpected visibility for {token} and {article}: {ids}")
                evidence.append({"identity_scope": token, "requested": article, "citations": ids})
        return {"health": health, "cases": evidence}


if __name__ == "__main__":
    result = verify()
    target = Path("reports/integrated/rag/metadata-runtime.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
