"""Run, test or export real cumulative session source without replacing the main app."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def implementation(number: int, variant: str):
    manifest = json.loads((ROOT / "sessions/implementation_manifest.json").read_text())
    item = next((s for s in manifest["sessions"] if s["session"] == number), None)
    if item is None or item["status"] != "implemented":
        raise ValueError(f"Session {number:02d} has no cumulative implementation yet")
    return item, ROOT / item[variant]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "test", "export"])
    parser.add_argument("number", type=int, choices=range(1, 41))
    parser.add_argument("--variant", choices=["starter", "solution"], default="solution")
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--previous-only",
        action="store_true",
        help="test only behaviour inherited from the previous completed session",
    )
    args, extra = parser.parse_known_args(argv)
    item, snapshot = implementation(args.number, args.variant)
    if args.action == "export":
        if extra:
            parser.error("unexpected arguments for export")
        destination = (
            args.out or ROOT / ".work/checkpoints" / f"session-{args.number:02d}"
        ).resolve()
        if destination.exists():
            parser.error(f"destination already exists; choose a fresh directory: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            snapshot,
            destination,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "reports"
            ),
        )
        shutil.copytree(ROOT / "data", destination / "data")
        (destination / "CHECKPOINT.json").write_text(
            json.dumps(
                {
                    "session": args.number,
                    "variant": args.variant,
                    "source": str(snapshot.relative_to(ROOT)),
                    "includes_shared_seed_data": True,
                    "scope": (
                        "completed course state at this "
                        "session, not the final production application"
                    ),
                },
                indent=2,
            )
        )
        (destination / "README.md").write_text(
            f"# Cumulative course checkpoint session {args.number:02d}\n\n"
            f"Variant: {args.variant}. "
            "This folder includes actual source, tests and synthetic seed data.\n\n"
            "Create a separate environment here using `python -m venv .venv`, "
            'then install with `.venv\\Scripts\\python.exe -m pip install -e ".[dev]"`.\n\n'
            "Run `.venv\\Scripts\\python.exe -m pytest` and "
            f"`.venv\\Scripts\\python.exe -m copilot {' '.join(item['default_command'])}`.\n\n"
            "A starter intentionally fails its new acceptance checks until implemented. "
            "A solution is the completed state for this session only, "
            "not the final production release.\n",
            encoding="utf-8",
        )
        print(f"Standalone checkpoint exported to {destination}")
        return 0
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(snapshot / "src")
    environment["COHORT_DATA_DIR"] = str(ROOT / "data")
    environment["COPILOT_DATA_DIR"] = str(ROOT / "data")
    environment["COHORT_REPORT_DIR"] = str(
        ROOT / "reports/cohort" / f"session-{args.number:02d}" / args.variant
    )
    # Do not pass application bearer maps or paid-provider secrets to offline teaching checks.
    for key in ("COPILOT_AUTH_TOKENS", "COPILOT_LLM_API_KEY", "OPENAI_API_KEY"):
        environment.pop(key, None)
    if args.action == "test":
        if extra:
            parser.error("unexpected arguments for test")
        tests = [str(snapshot / "tests")]
        if args.previous_only:
            if args.number == 1:
                parser.error("session 1 has no previous-session tests")
            tests = [str(snapshot / "tests" / name) for name in item["previous_tests"]]
        command = [
            sys.executable,
            "-m",
            "pytest",
            *tests,
            "--confcutdir",
            str(snapshot),
            "--basetemp",
            str(ROOT / ".work/pytest-cohort" / f"s{args.number:02d}-{args.variant}"),
            "--tb=short",
        ]
        (ROOT / ".work/pytest-cohort").mkdir(parents=True, exist_ok=True)
    else:
        if args.previous_only:
            parser.error("--previous-only is a test option")
        if extra and extra[0] == "--":
            extra = extra[1:]
        command = [sys.executable, "-m", "copilot", *(extra or item["default_command"])]
    result = subprocess.run(command, cwd=snapshot, env=environment)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
