# ruff: noqa: E501
"""Actual runtime validation of the instructor-authorized RAG session batch."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run():
    manifest = json.loads((ROOT / "sessions/implementation_manifest.json").read_text())
    batch = next(b for b in manifest.get("validation_batches", []) if b["sessions"] == [5, 6, 7, 8])
    if not batch.get("authorization"):
        raise RuntimeError("No instructor authorization for this batch")
    output = ROOT / "reports/rag-batch-validation"
    output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        COPILOT_LOCAL_MODEL_DIR=str(ROOT / ".work/models/minilm"),
        PYTHONPATH=str(ROOT / "src"),
    )
    for key in ("OPENAI_API_KEY", "COPILOT_LLM_API_KEY", "COPILOT_AUTH_TOKENS"):
        environment.pop(key, None)
    checks = []

    def execute(label, arguments, expected=0):
        print(label, flush=True)
        result = subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=600,
        )
        text = (result.stdout or "") + (result.stderr or "")
        (output / f"{label}.log").write_text(text, encoding="utf-8")
        valid = (
            result.returncode == expected
            if expected == 0
            else result.returncode != 0 and "ERROR collecting" not in text
        )
        checks.append(
            {
                "name": label,
                "command": arguments,
                "exit_code": result.returncode,
                "expected": "success" if expected == 0 else "starter new work fails",
                "passed": valid,
                "output_sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
        )
        if not valid:
            raise RuntimeError(f"{label} failed; inspect {output / (label + '.log')}")

    for number in range(5, 9):
        execute(f"session-{number:02d}-solution-tests", ["scripts/session.py", "test", str(number)])
        execute(
            f"session-{number:02d}-starter-inherited",
            ["scripts/session.py", "test", str(number), "--variant", "starter", "--previous-only"],
        )
        execute(
            f"session-{number:02d}-starter-new",
            ["scripts/session.py", "test", str(number), "--variant", "starter"],
            expected=1,
        )
        execute(f"session-{number:02d}-runtime", ["scripts/session.py", "run", str(number)])
    execute(
        "main-regression", ["-m", "pytest", "--junitxml=reports/rag-batch-tests.xml", "--tb=short"]
    )
    for label, arguments in [
        ("main-baseline", ["rag-demo"]),
        ("main-ingestion", ["rag-ingest"]),
        ("main-recursive", ["rag-chunks", "--strategy", "recursive"]),
        ("main-four-strategies", ["rag-benchmark"]),
        (
            "main-mac-workflow",
            [
                "ask",
                "How do I set up VPN on my Mac?",
                "--employee",
                "E1261",
                "--thread",
                "rag-batch-check",
            ],
        ),
    ]:
        execute(label, ["-m", "copilot", *arguments])
    execute("lint", ["-m", "ruff", "check", "."])
    execute("format", ["-m", "ruff", "format", "--check", "."])
    execute("course-links", ["scripts/check_course.py"])
    scorecard = json.loads((ROOT / "reports/integrated/rag/rag-benchmark.json").read_text())
    session_scorecard = json.loads(
        (ROOT / "reports/cohort/session-08/solution/rag-benchmark.json").read_text()
    )
    assert set(scorecard["strategies"]) == {"fixed", "recursive", "semantic", "parent-child"}
    assert scorecard["document_count"] == session_scorecard["document_count"] == 150
    assert scorecard["question_count"] == session_scorecard["question_count"] == 20
    assert (
        scorecard["semantic_encoder"]["revision"]
        == session_scorecard["semantic_encoder"]["revision"]
    )
    assert all(
        scorecard["strategies"][name]["recall_at_5"]
        == session_scorecard["strategies"][name]["recall_at_5"]
        for name in scorecard["strategies"]
    )
    # Protect original seed data and the pre-existing evaluation labels from changes.
    baseline = json.loads((ROOT / "docs/dataset_metadata.json").read_text())
    for relative, expected in baseline["protected_file_hashes"].items():
        path = ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, (
            f"Protected data changed: {relative}"
        )
    report = {
        "scope": "sessions 5–8 actual source plus integrated local RAG validation",
        "verified_at": datetime.now(UTC).isoformat(),
        "checks": checks,
        "all_passed": True,
        "paid_calls": 0,
        "semantic_encoder": scorecard["semantic_encoder"],
        "retrieval_encoder": scorecard["retrieval_encoder"],
        "scorecard": {
            name: {k: value for k, value in row.items() if k != "cases"}
            for name, row in scorecard["strategies"].items()
        },
        "label_status": "draft; no production-quality certification",
        "session_4_live_gate": "still pending",
    }
    (output / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        "RAG batch runtime validation passed; completion commits and checkpoint validation are next",
        flush=True,
    )
    return report


if __name__ == "__main__":
    run()
