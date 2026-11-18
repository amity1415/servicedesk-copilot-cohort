from __future__ import annotations

from pathlib import Path

import pytest

from copilot.cli import main
from copilot.tickets import count_by, load_tickets

EXPORT = Path(__file__).resolve().parents[1] / "data" / "tickets" / "historical_tickets.jsonl"
needs_data = pytest.mark.skipif(
    not EXPORT.is_file(), reason="no data pack: run `python -m datagen`"
)


@needs_data
def test_export_loads_in_time_order() -> None:
    tickets = load_tickets(EXPORT)
    assert len(tickets) >= 100
    created = [ticket.created_at for ticket in tickets]
    assert created == sorted(created)
    assert all(ticket.resolved_at >= ticket.created_at for ticket in tickets)
    assert len({ticket.ticket_id for ticket in tickets}) == len(tickets)


@needs_data
def test_counts_cover_every_ticket() -> None:
    tickets = load_tickets(EXPORT)
    by_category = count_by(tickets, "category")
    assert sum(by_category.values()) == len(tickets)
    assert len(by_category) == 8
    assert by_category.most_common()[-1][0] == "Security"  # the deliberately rare class


def test_count_by_refuses_free_text_fields() -> None:
    with pytest.raises(ValueError, match="cannot count by 'description'"):
        count_by([], "description")


def test_bad_line_is_reported_with_file_and_line_number(tmp_path: Path) -> None:
    path = tmp_path / "tickets.jsonl"
    path.write_text('{"ticket_id": "INC1"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"tickets\.jsonl:1: invalid ticket record"):
        load_tickets(path)


@needs_data
def test_cli_prints_counts(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["tickets-stats", "--path", str(EXPORT), "--by", "priority"]) == 0
    output = capsys.readouterr().out
    assert "tickets by priority" in output
    assert all(priority in output for priority in ("P1", "P2", "P3", "P4"))


def test_cli_explains_a_missing_export(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["tickets-stats", "--path", str(tmp_path / "missing.jsonl")]) == 1
    assert "python -m datagen" in capsys.readouterr().err
