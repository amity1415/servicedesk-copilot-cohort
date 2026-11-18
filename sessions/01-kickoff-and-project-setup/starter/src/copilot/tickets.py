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
    """TODO: implement iter_tickets following this session's BUILD_GUIDE.md"""
    raise NotImplementedError(
        "TODO: implement iter_tickets following this session's BUILD_GUIDE.md"
    )


def load_tickets(path: Path | None = None) -> list[Ticket]:
    return list(iter_tickets(path))


def count_by(tickets: Iterable[Ticket], field: str) -> Counter[str]:
    """TODO: implement count_by following this session's BUILD_GUIDE.md"""
    raise NotImplementedError("TODO: implement count_by following this session's BUILD_GUIDE.md")
