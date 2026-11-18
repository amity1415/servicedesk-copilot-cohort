"""Cumulative course CLI; this source belongs to the selected session."""

import argparse
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
    args = parser.parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
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
    parser.error("unknown command")
    return 2
