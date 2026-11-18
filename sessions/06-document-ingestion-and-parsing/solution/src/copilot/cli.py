"""Cumulative course CLI; this source belongs to the selected session."""

import argparse
import json
import os
from pathlib import Path

from copilot.config import get_settings
from copilot.logging_setup import configure_logging
from copilot.tickets import COUNTABLE_FIELDS, count_by, load_tickets


def main(argv=None):
    parser = argparse.ArgumentParser(prog="copilot")
    commands = parser.add_subparsers(dest="command", required=True)
    stats = commands.add_parser("tickets-stats")
    stats.add_argument("--by", default="category", choices=COUNTABLE_FIELDS)
    stats.add_argument("--path", type=Path)
    commands.add_parser("train")
    commands.add_parser("compare")
    token_parser = commands.add_parser("token-report")
    token_parser.add_argument("--encoding", default="cl100k_base")
    token_parser.add_argument("--input-price-per-million", type=float)
    token_parser.add_argument("--output-price-per-million", type=float)
    commands.add_parser("llm-smoke")
    from copilot.rag.cli import register

    register(commands, stage=6)

    args = parser.parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)

    from copilot.rag.cli import execute

    rag_result = execute(args, settings, stage=6)
    if rag_result is not None:
        return rag_result
    if args.command == "tickets-stats":
        try:
            rows = load_tickets(args.path)
        except FileNotFoundError:
            import logging

            logging.getLogger(__name__).error("ticket export missing; run python -m datagen")
            return 1
        counts = count_by(rows, args.by)
        total = sum(counts.values())
        print(f"{total} tickets by {args.by}")
        for label, count in counts.most_common():
            print(f"  {label}: {count}")
        return 0
    reports = Path(os.getenv("COHORT_REPORT_DIR", "reports"))
    if args.command in ("train", "compare"):
        from copilot.ml.train import train

        result = train(settings.data_dir, reports, neural=args.command == "compare")
        print(
            json.dumps(
                {
                    "report": str(reports / "ml.json"),
                    "train": result["train"],
                    "test": result["test"],
                    "models": list(result["models"]),
                }
            )
        )
        return 0
    if args.command == "token-report":
        from copilot.ml.token_report import measure

        result = measure(
            settings.data_dir,
            reports,
            encoding_name=args.encoding,
            input_price_per_million=args.input_price_per_million,
            output_price_per_million=args.output_price_per_million,
        )
        print(
            json.dumps(
                {
                    "report": str(reports / "tokens.json"),
                    "encoding": result["encoding"],
                    "cost_status": result["cost_status"],
                }
            )
        )
        return 0
    if args.command == "llm-smoke":
        import httpx

        from copilot.llm.classify import classify
        from copilot.llm.client import ModelClient

        def handle(request):
            text = json.dumps(
                {"category": "Hardware & Devices", "priority": "P3", "summary": "Laptop is slow"}
            )
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": text}}], "usage": {"total_tokens": 20}},
            )

        client = ModelClient("fixture", api_key="fixture", transport=httpx.MockTransport(handle))
        result = classify(client, "My laptop is slow")
        output = {
            "mode": "offline_schema_fixture",
            "paid_calls": 0,
            "classification": result.model_dump(),
            "accuracy": None,
            "cost": None,
            "live_comparison": "requires approved provider, model and budget; not measured",
        }
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "llm-smoke.json").write_text(json.dumps(output, indent=2))
        print(json.dumps(output))
        return 0
    parser.error("unknown command")
    return 2
