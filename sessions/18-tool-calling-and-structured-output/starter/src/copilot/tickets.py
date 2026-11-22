"""Read access to the historical ticket export in the data pack.

The export is JSON Lines: one resolved ticket per line in
data/tickets/historical_tickets.jsonl. Session 2 trains on it and sessions 5,
15 and 35 draw golden questions and tasks from it.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from copilot.config import get_settings

HISTORICAL_TICKETS = Path("tickets") / "historical_tickets.jsonl"

COUNTABLE_FIELDS = (
    "category",
    "subcategory",
    "priority",
    "assignment_group",
    "region",
    "channel",
    "resolution_code",
)


class Ticket(BaseModel):
    ticket_id: str
    created_at: datetime
    resolved_at: datetime | None = None
    requester_id: str
    department: str
    region: str
    office: str
    channel: str
    device_os: str | None = None
    short_description: str
    description: str
    category: str
    subcategory: str
    priority: str
    assignment_group: str
    status: str
    resolution_code: str | None = None
    resolution_notes: str | None = None
    kb_article_id: str | None = None
    reopened: bool = False


def iter_tickets(path: Path | None = None) -> Iterator[Ticket]:
    """Yield tickets one at a time so large exports do not need to fit in memory."""
    path = path or get_settings().data_dir / HISTORICAL_TICKETS
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield Ticket.model_validate_json(line)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: invalid ticket record") from exc


def load_tickets(path: Path | None = None) -> list[Ticket]:
    return list(iter_tickets(path))


def count_by(tickets: Iterable[Ticket], field: str) -> Counter[str]:
    """Count tickets by one of COUNTABLE_FIELDS; missing values count as '(none)'."""
    if field not in COUNTABLE_FIELDS:
        raise ValueError(f"cannot count by {field!r}; choose one of {', '.join(COUNTABLE_FIELDS)}")
    return Counter(str(getattr(ticket, field) or "(none)") for ticket in tickets)
