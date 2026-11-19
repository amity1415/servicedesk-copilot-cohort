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
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ["-c", "user.name=Codex Course Builder", "-c", "user.email=codex-course@local.invalid"]


def git(*arguments):
    result = subprocess.run(
        [
            "git",
            "--git-dir=.git",
            "--work-tree=.",
            "-c",
            "core.fsmonitor=false",
            *IDENTITY,
            *arguments,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
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
    if number not in {1, 2, 3, 9, 10, 11, 12, 13}:
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
        (
            "main-tests",
            ["-m", "pytest", "--tb=short", f"--basetemp=.work/pytest-gate-{uuid4().hex}"],
        ),
        ("lint", ["-m", "ruff", "check", "."]),
        ("format", ["-m", "ruff", "format", "--check", "."]),
        ("session-run", ["scripts/session.py", "run", str(number)]),
    ]
    runtime_command = {
        1: "tickets-stats",
        2: "train",
        3: "compare",
        9: "rag-embedding-compare",
        10: "rag-postgres-verify",
        11: "rag-metadata-verify",
        12: "rag-hybrid-compare",
        13: "rag-rerank-compare",
    }[number]
    commands.append(("main-run", ["-m", "copilot", runtime_command]))
    if number in {9, 10, 11, 12, 13}:
        starter = ["scripts/session.py", "test", str(number), "--variant", "starter"]
        runtime = ["scripts/verify_embedding_runtime.py"]
        if number == 10:
            runtime.append("--pgvector")
        if number == 11:
            runtime = ["scripts/verify_metadata_runtime.py"]
        if number == 12:
            runtime.append("--hybrid")
        if number == 13:
            runtime.append("--reranked")
            commands.append(("followup-http-runtime", ["scripts/verify_followup_runtime.py"]))
        commands.extend(
            [
                ("starter-inherited", [*starter, "--previous-only"]),
                ("starter-new", starter),
                ("main-http-runtime", runtime),
            ]
        )
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
        expected_failure = label == "starter-new"
        passed = (
            result.returncode == 1 and "1 failed" in output and item["new_tests"][0] in output
            if expected_failure
            else result.returncode == 0
        )
        results.append(
            {
                "name": label,
                "command": arguments,
                "exit_code": result.returncode,
                "expected_failure": expected_failure,
                "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
            }
        )
        if not passed:
            item["completion_state"] = "verification_failed"
            item["completion_blocker"] = f"{label} failed; inspect {logs.relative_to(ROOT)}"
            path.write_text(json.dumps(manifest, indent=2) + "\n")
            raise RuntimeError(item["completion_blocker"])
    # Validate outputs exist and reflect full corpus execution, not just a zero exit.
    if number in {2, 3}:
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
    if number == 9:
        main_rag = ROOT / "reports/integrated/rag"
        report = json.loads((main_rag / "rag-embedding-compare.json").read_text())
        cohort = json.loads(
            (ROOT / "reports/cohort/session-09/solution/rag-embedding-compare.json").read_text()
        )
        for integrated, standalone in zip(report["models"], cohort["models"], strict=True):
            if integrated["identity"] != standalone["identity"] or [
                row["retrieved"] for row in integrated["cases"]
            ] != [row["retrieved"] for row in standalone["cases"]]:
                raise RuntimeError("Integrated and standalone embedding results differ")
        evidence["comparison"] = report
        evidence["http_runtime"] = json.loads((main_rag / "embedding-runtime.json").read_text())
    if number == 10:
        main_rag = ROOT / "reports/integrated/rag"
        report = json.loads((main_rag / "rag-postgres-verify.json").read_text())
        checkpoint = ROOT / "reports/cohort/session-10/solution/rag-postgres-verify.json"
        cohort = json.loads(checkpoint.read_text())
        for field in (
            "published_chunks",
            "search_document_ids",
            "top5_overlap",
            "replaced_old_chunks",
            "withdrawn_chunks",
            "failed_replace_rolled_back",
        ):
            if report[field] != cohort[field]:
                raise RuntimeError(f"Integrated and standalone database results differ for {field}")
        evidence["postgres"] = report
        evidence["http_runtime"] = json.loads((main_rag / "postgres-runtime.json").read_text())
    if number == 11:
        main_rag = ROOT / "reports/integrated/rag"
        report = json.loads((main_rag / "rag-metadata-verify.json").read_text())
        checkpoint = ROOT / "reports/cohort/session-11/solution/rag-metadata-verify.json"
        if report != json.loads(checkpoint.read_text()):
            raise RuntimeError("Integrated and standalone metadata results differ")
        evidence["metadata"] = report
        evidence["http_runtime"] = json.loads((main_rag / "metadata-runtime.json").read_text())
    if number == 12:
        main_rag = ROOT / "reports/integrated/rag"
        report = json.loads((main_rag / "rag-hybrid-compare.json").read_text())
        checkpoint = ROOT / "reports/cohort/session-12/solution/rag-hybrid-compare.json"
        cohort = json.loads(checkpoint.read_text())
        for ranking in ("vector", "keyword", "hybrid"):
            if report["rankings"][ranking]["subsets"] != cohort["rankings"][ranking]["subsets"]:
                raise RuntimeError(f"Integrated and standalone results differ for {ranking}")
        evidence["hybrid"] = report
        evidence["http_runtime"] = json.loads((main_rag / "hybrid-runtime.json").read_text())
    if number == 13:
        main_rag = ROOT / "reports/integrated/rag"
        report = json.loads((main_rag / "rag-rerank-compare.json").read_text())
        checkpoint = ROOT / "reports/cohort/session-13/solution/rag-rerank-compare.json"
        cohort = json.loads(checkpoint.read_text())
        for ranking in ("hybrid", "reranked"):
            if (
                report["rankings"][ranking]["recall_at_5"]
                != cohort["rankings"][ranking]["recall_at_5"]
            ):
                raise RuntimeError(f"Integrated and standalone results differ for {ranking}")
        evidence["reranking"] = report
        evidence["http_runtime"] = json.loads((main_rag / "reranked-runtime.json").read_text())
        evidence["followups"] = json.loads((main_rag / "followup-runtime.json").read_text())
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
    if number == 9:
        paths = [
            "docs/SESSION_COMPLETION_POLICY.md",
            "docs/adr/0003-local-embedding-retrieval.md",
            "docs/engineering-design/DESIGN.md",
            "sessions/IMPLEMENTATION_GUIDE.md",
            "sessions/implementation_manifest.json",
            "sessions/09-embeddings",
            "policies/embedding_model_l12.json",
            "scripts/complete_session.py",
            "scripts/session.py",
            "scripts/verify_embedding_runtime.py",
            "src/copilot/api/app.py",
            "src/copilot/cli.py",
            "src/copilot/mcp_servers/servers.py",
            "src/copilot/rag/cli.py",
            "src/copilot/rag/embedding_benchmark.py",
            "src/copilot/rag/semantic_encoder.py",
            "src/copilot/rag/service.py",
            "tests/test_rag_embeddings.py",
        ]
    if number == 10:
        paths = [
            "docs/IMPLEMENTATION_STATUS.md",
            "docker-compose.yml",
            "sessions/10-vector-database-and-indexing",
            "sessions/implementation_manifest.json",
            "scripts/complete_session.py",
            "scripts/verify_embedding_runtime.py",
            "src/copilot/cli.py",
            "src/copilot/rag/cli.py",
            "src/copilot/rag/postgres_benchmark.py",
            "src/copilot/rag/postgres_index.py",
            "src/copilot/rag/service.py",
            "tests/test_rag_postgres.py",
        ]
    if number == 11:
        paths = [
            "sessions/11-retrieval-and-metadata-filtering",
            "sessions/implementation_manifest.json",
            "scripts/complete_session.py",
            "scripts/verify_embedding_runtime.py",
            "scripts/verify_metadata_runtime.py",
            "src/copilot/agents/engine.py",
            "src/copilot/cli.py",
            "src/copilot/mcp_servers/servers.py",
            "src/copilot/rag/cli.py",
            "src/copilot/rag/loaders.py",
            "src/copilot/rag/metadata_report.py",
            "tests/test_rag_metadata.py",
        ]
    if number == 12:
        paths = [
            ".env.example",
            "sessions/12-hybrid-search",
            "sessions/implementation_manifest.json",
            "scripts/complete_session.py",
            "scripts/verify_embedding_runtime.py",
            "src/copilot/cli.py",
            "src/copilot/config.py",
            "src/copilot/rag/advanced.py",
            "src/copilot/rag/cli.py",
            "src/copilot/rag/hybrid_benchmark.py",
            "src/copilot/rag/postgres_index.py",
            "src/copilot/rag/rank_fusion.py",
            "src/copilot/rag/service.py",
            "tests/test_rag_hybrid.py",
        ]
    if number == 13:
        paths = [
            "policies/reranker_model.json",
            "sessions/13-reranking-and-query-rewriting",
            "sessions/implementation_manifest.json",
            "scripts/complete_session.py",
            "scripts/session.py",
            "scripts/verify_embedding_runtime.py",
            "scripts/verify_followup_runtime.py",
            "src/copilot/agents/engine.py",
            "src/copilot/cli.py",
            "src/copilot/rag/advanced.py",
            "src/copilot/rag/cli.py",
            "src/copilot/rag/query.py",
            "src/copilot/rag/reranker.py",
            "src/copilot/rag/reranker_benchmark.py",
            "src/copilot/rag/semantic_encoder.py",
            "src/copilot/rag/service.py",
            "tests/test_rag_reranking.py",
        ]
    if number in {9, 10, 11, 12, 13} and git("diff", "--cached", "--name-only"):
        raise RuntimeError("The Git index has staged changes. Preserve them before completion.")
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
