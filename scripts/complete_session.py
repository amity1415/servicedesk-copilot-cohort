"""Verify runtime in both source trees, test, commit, then permit the next session.

Does not certify a live-model session using a mocked call. Existing code-ready
checkpoints are retained as history; verified completion is tracked separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ["-c", "user.name=Codex Course Builder", "-c", "user.email=codex-course@local.invalid"]


def git(*arguments):
    result = subprocess.run(
        ["git", *IDENTITY, *arguments], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def complete(number):
    path = ROOT / "sessions/implementation_manifest.json"
    manifest = json.loads(path.read_text())
    item = next(row for row in manifest["sessions"] if row["session"] == number)
    if number > 1:
        previous = next(row for row in manifest["sessions"] if row["session"] == number - 1)
        if previous.get("completion_state") != "verified_committed":
            raise RuntimeError("Previous session is not verified and committed; cannot advance")
        git("cat-file", "-e", previous["completion_commit"] + "^{commit}")
    if item.get("completion_state") == "verified_committed":
        raise RuntimeError("This session already has a completion commit; do not rewrite it")
    if number == 4:
        # Offline source and tests exist, but the required live comparison is absent.
        item["completion_state"] = "pending_live_validation"
        item["completion_blocker"] = (
            "Live-model classification/summarization and measured comparison are not verified. "
            "A rotated local key, bounded live runner and explicit model/pricing are required."
        )
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        git("add", "sessions/implementation_manifest.json")
        git("commit", "-m", "Keep session 04 pending until live acceptance is verified")
        print(item["completion_blocker"], flush=True)
        return 2
    if number not in {1, 2, 3}:
        raise RuntimeError("No complete runtime-gate definition exists for this session yet")
    evidence_dir = ROOT / "sessions" / Path(item["solution"]).parts[1] / "verification"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    logs = ROOT / "reports/completion" / f"session-{number:02d}"
    logs.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
    )
    for name in ("OPENAI_API_KEY", "COPILOT_LLM_API_KEY", "COPILOT_AUTH_TOKENS"):
        environment.pop(name, None)
    commands = [
        ("session-tests", ["scripts/session.py", "test", str(number)]),
        ("main-tests", ["-m", "pytest", "--tb=short"]),
        ("lint", ["-m", "ruff", "check", "."]),
        ("format", ["-m", "ruff", "format", "--check", "."]),
        ("session-run", ["scripts/session.py", "run", str(number)]),
    ]
    runtime_command = {1: "tickets-stats", 2: "train", 3: "compare"}[number]
    commands.append(("main-run", ["-m", "copilot", runtime_command]))
    if number == 3:
        pricing = [
            "token-report",
            "--encoding",
            "o200k_base",
            "--input-price-per-million",
            "0.4",
            "--output-price-per-million",
            "1.6",
        ]
        commands.extend(
            [
                ("session-token-run", ["scripts/session.py", "run", "3", "--", *pricing]),
                ("main-token-run", ["-m", "copilot", *pricing]),
            ]
        )
    results = []
    for label, arguments in commands:
        print(f"Session {number:02d}: {label}", flush=True)
        result = subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = (result.stdout or "") + (result.stderr or "")
        (logs / f"{label}.log").write_text(output, encoding="utf-8")
        results.append(
            {
                "name": label,
                "command": arguments,
                "exit_code": result.returncode,
                "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
            }
        )
        if result.returncode:
            item["completion_state"] = "verification_failed"
            item["completion_blocker"] = f"{label} failed; inspect {logs.relative_to(ROOT)}"
            path.write_text(json.dumps(manifest, indent=2) + "\n")
            raise RuntimeError(item["completion_blocker"])
    # Validate outputs exist and reflect full corpus execution, not just a zero exit.
    if number >= 2:
        main_report = json.loads((ROOT / "reports/integrated/ml.json").read_text())
        session_report = json.loads(
            (ROOT / f"reports/cohort/session-{number:02d}/solution/ml.json").read_text()
        )
        assert main_report["train"] + main_report["test"] == 5000
        assert session_report["train"] == main_report["train"]
        assert session_report["test"] == main_report["test"]
        assert set(session_report["models"]) == set(main_report["models"])
        assert main_report["group_overlap"] == session_report["group_overlap"] == 0
    evidence = {
        "session": number,
        "verified_at_utc": datetime.now(UTC).isoformat(),
        "source_state": git("rev-parse", "HEAD"),
        "checks": results,
        "runtime_scope": "actual session source and integrated main application",
        "paid_calls": 0,
    }
    if number == 3:
        main_tokens = json.loads((ROOT / "reports/integrated/tokens.json").read_text())
        session_tokens = json.loads(
            (ROOT / "reports/cohort/session-03/solution/tokens.json").read_text()
        )
        assert main_tokens["tickets"]["count"] == session_tokens["tickets"]["count"] == 5000
        assert main_tokens["identifier_examples"] == session_tokens["identifier_examples"]
        assert main_tokens["cost_estimate"] is not None
        evidence["forecast_pricing"] = {
            "scenario": "GPT-4.1-mini published unit-rate forecast, not model deployment selection",
            "input_usd_per_million": 0.4,
            "output_usd_per_million": 1.6,
            "encoding": "o200k_base",
            "output_tokens_assumed": 128,
            "source": "https://developers.openai.com/api/docs/models/gpt-4.1-mini",
            "checked_date": "2026-11-18",
            "actual_provider_cost": None,
            "limitations": "Request-text estimate excludes prompts, context and chat framing.",
        }
    record = evidence_dir / "runtime-gate.json"
    record.write_text(json.dumps(evidence, indent=2) + "\n")
    item["completion_state"] = "verified_awaiting_commit"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    # Scope staging to this gate's reviewed code, policy, tests and evidence.
    paths = [
        "src/copilot/cli.py",
        "src/copilot/foundation_cli.py",
        "scripts/complete_session.py",
        "tests/test_foundation_cli.py",
        "tests/test_completion_policy.py",
        "sessions/implementation_manifest.json",
        "docs/SESSION_COMPLETION_POLICY.md",
        "sessions/IMPLEMENTATION_GUIDE.md",
        str(record.relative_to(ROOT)),
    ]
    git("add", "--", *paths)
    git("diff", "--cached", "--check")
    git("commit", "-m", f"Verify session {number:02d} runtime in cohort and main application")
    commit = git("rev-parse", "HEAD")
    item.update(
        completion_state="verified_committed",
        completion_commit=commit,
        completion_evidence=str(record.relative_to(ROOT).as_posix()),
    )
    item.pop("completion_blocker", None)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    git("add", "sessions/implementation_manifest.json")
    git("commit", "-m", f"Record session {number:02d} completion commit before advancing")
    print(f"Session {number:02d} verified and committed: {commit[:12]}", flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", type=int, choices=range(1, 41))
    raise SystemExit(complete(parser.parse_args().number))
