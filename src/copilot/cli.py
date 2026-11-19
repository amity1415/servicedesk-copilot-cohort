"""Command line entry point: `copilot <command>` or `python -m copilot <command>`."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from copilot.config import get_settings
from copilot.logging_setup import configure_logging
from copilot.tickets import COUNTABLE_FIELDS, count_by, load_tickets

log = logging.getLogger(__name__)


def _tickets_stats(by: str, path: Path | None) -> int:
    try:
        tickets = load_tickets(path)
    except FileNotFoundError as exc:
        log.error(
            "ticket export not found: %s (run `python -m datagen` to create it)", exc.filename
        )
        return 1
    counts = count_by(tickets, by)
    total = sum(counts.values())
    width = max(len(value) for value in counts)
    print(f"{total} tickets by {by}")
    for value, count in counts.most_common():
        print(f"  {value:<{width}}  {count:>5}  {count / total:6.1%}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="copilot", description="IT Service Desk Copilot")
    commands = parser.add_subparsers(dest="command", required=True)

    stats = commands.add_parser("tickets-stats", help="count historical tickets by a field")
    stats.add_argument("--by", default="category", choices=COUNTABLE_FIELDS)
    stats.add_argument("--path", type=Path, default=None, help="ticket export (JSON Lines)")

    ask = commands.add_parser("ask", help="run the offline reference workflow")
    ask.add_argument("question")
    ask.add_argument("--employee", default="E1261")
    ask.add_argument("--thread", default="cli")
    session = commands.add_parser("session", help="run one teaching experiment")
    session.add_argument("number", type=int, choices=range(1, 41))
    commands.add_parser("evaluate-retrieval", help="score lexical retrieval on draft labels")
    serve = commands.add_parser("serve", help="start authenticated teaching API")
    serve.add_argument("--host", default="127.0.0.1", help="bind address (default: local only)")
    serve.add_argument("--port", type=int, default=8082, help="API port (default: 8082)")

    from copilot.foundation_cli import register

    register(commands)

    from copilot.rag.cli import register as register_rag

    register_rag(commands, stage=13)

    args = parser.parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)

    from copilot.foundation_cli import execute
    from copilot.rag.cli import execute as execute_rag

    rag_result = execute_rag(args, settings, stage=13)
    if rag_result is not None:
        return rag_result

    foundation_result = execute(args, settings, Path("reports/integrated"))
    if foundation_result is not None:
        return foundation_result

    if args.command == "tickets-stats":
        return _tickets_stats(args.by, args.path)
    if args.command == "session":
        from copilot.course.experiments import run_session

        implementation_manifest = Path.cwd() / "sessions/implementation_manifest.json"
        if implementation_manifest.exists():
            import json
            import subprocess
            import sys

            implementations = json.loads(implementation_manifest.read_text())["sessions"]
            if any(
                item["session"] == args.number and item["status"] == "implemented"
                for item in implementations
            ):
                return subprocess.call(
                    [
                        sys.executable,
                        str(Path.cwd() / "scripts/session.py"),
                        "run",
                        str(args.number),
                    ]
                )
        run_session(args.number, Path.cwd())
        return 0
    if args.command == "evaluate-retrieval":
        import json

        from copilot.course.evaluate import retrieval_report

        report = retrieval_report(Path.cwd())
        print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
        return 0
    if args.command == "ask":
        import json

        from copilot.agents.engine import Engine
        from copilot.tools.runtime import Runtime

        runtime = Runtime(Path(".work/runtime.sqlite3"), settings.data_dir)
        from copilot.rag.service import VectorRag

        engine = Engine(runtime, VectorRag.configured(settings.data_dir))
        print(json.dumps(engine.run(args.employee, args.question, args.thread), indent=2))
        return 0
    if args.command == "serve":
        import uvicorn

        if not 1 <= args.port <= 65535:
            parser.error("--port must be between 1 and 65535")
        uvicorn.run("copilot.api.app:production_app", factory=True, host=args.host, port=args.port)
        return 0
    parser.error(f"unknown command {args.command!r}")
    return 2
