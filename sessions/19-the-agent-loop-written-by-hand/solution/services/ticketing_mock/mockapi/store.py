"""SQLite-backed ticket store. One connection guarded by a lock; fine for a mock."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path

from mockapi.models import OPEN_STATUSES

TICKET_COLUMNS = (
    "ticket_id",
    "created_at",
    "updated_at",
    "requester_id",
    "short_description",
    "description",
    "category",
    "subcategory",
    "priority",
    "assignment_group",
    "status",
    "resolution_notes",
)
FIRST_NUMBER = 20001
INSERT_TICKET = (
    f"INSERT INTO tickets (number, {', '.join(TICKET_COLUMNS)}) "
    f"VALUES ({', '.join('?' * (len(TICKET_COLUMNS) + 1))})"
)
INSERT_COMMENT = (
    "INSERT INTO comments (ticket_id, author_id, created_at, body, internal) VALUES (?, ?, ?, ?, ?)"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id         TEXT PRIMARY KEY,
    number            INTEGER NOT NULL UNIQUE,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    requester_id      TEXT NOT NULL,
    short_description TEXT NOT NULL,
    description       TEXT NOT NULL,
    category          TEXT NOT NULL,
    subcategory       TEXT,
    priority          TEXT NOT NULL,
    assignment_group  TEXT NOT NULL,
    status            TEXT NOT NULL,
    resolution_notes  TEXT
);
CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id  TEXT NOT NULL REFERENCES tickets (ticket_id),
    author_id  TEXT NOT NULL,
    created_at TEXT NOT NULL,
    body       TEXT NOT NULL,
    internal   INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency_keys (
    key         TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    ticket_id   TEXT NOT NULL REFERENCES tickets (ticket_id)
);
"""


class StoreError(Exception):
    """A request the store refuses. `code` is the machine-readable reason."""

    status_code = 409
    code = "conflict"

    def __init__(self, message: str, **details: object) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class TicketNotFound(StoreError):
    status_code = 404
    code = "ticket_not_found"


class UnknownRequester(StoreError):
    status_code = 422
    code = "unknown_requester"


class IdempotencyConflict(StoreError):
    code = "idempotency_key_reused"


class TicketClosed(StoreError):
    code = "ticket_closed"


class ResolutionNotesRequired(StoreError):
    status_code = 422
    code = "resolution_notes_required"


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def ticket_number(ticket_id: str) -> int:
    return int(ticket_id.removeprefix("INC"))


class TicketStore:
    def __init__(
        self,
        db_path: str = ":memory:",
        seed_path: Path | None = None,
        employees_path: Path | None = None,
    ) -> None:
        self._lock = threading.RLock()
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._seed_path = seed_path
        self._employees = self._load_employees(employees_path)
        with self._lock:
            self._db.executescript(SCHEMA)
            if self.count() == 0:
                self._load_seed()

    @staticmethod
    def _load_employees(path: Path | None) -> frozenset[str] | None:
        """Known employee IDs, or None when no directory export is available."""
        if path is None or not path.is_file():
            return None
        with path.open(encoding="utf-8", newline="") as handle:
            return frozenset(row["employee_id"] for row in csv.DictReader(handle))

    def _load_seed(self) -> None:
        if self._seed_path is None or not self._seed_path.is_file():
            return
        for ticket in json.loads(self._seed_path.read_text(encoding="utf-8")):
            self._db.execute(
                INSERT_TICKET,
                [ticket_number(ticket["ticket_id"])]
                + [ticket.get(column) for column in TICKET_COLUMNS],
            )
            for comment in ticket.get("comments", []):
                self._db.execute(
                    INSERT_COMMENT,
                    (
                        ticket["ticket_id"],
                        comment["author_id"],
                        comment["created_at"],
                        comment["body"],
                        int(comment["internal"]),
                    ),
                )
        self._db.commit()

    def reset(self) -> int:
        """Drop every change and reload the seed. Returns the number of tickets afterwards."""
        with self._lock:
            for table in ("idempotency_keys", "comments", "tickets"):
                self._db.execute(f"DELETE FROM {table}")
            self._db.execute("DELETE FROM sqlite_sequence WHERE name = 'comments'")
            self._db.commit()
            self._load_seed()
            return self.count()

    def count(self) -> int:
        with self._lock:
            return self._db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]

    def _comments(self, ticket_id: str) -> list[dict[str, object]]:
        rows = self._db.execute(
            "SELECT * FROM comments WHERE ticket_id = ? ORDER BY comment_id", (ticket_id,)
        ).fetchall()
        return [{**dict(row), "internal": bool(row["internal"])} for row in rows]

    def _ticket(self, row: sqlite3.Row) -> dict[str, object]:
        ticket = {column: row[column] for column in TICKET_COLUMNS}
        ticket["comments"] = self._comments(row["ticket_id"])
        return ticket

    def get(self, ticket_id: str) -> dict[str, object]:
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
            ).fetchone()
            if row is None:
                raise TicketNotFound(f"No ticket with ID {ticket_id}.", ticket_id=ticket_id)
            return self._ticket(row)

    def _check_requester(self, employee_id: str) -> None:
        if self._employees is not None and employee_id not in self._employees:
            raise UnknownRequester(f"No employee with ID {employee_id}.", requester_id=employee_id)

    def create(
        self, fields: dict[str, object], idempotency_key: str | None = None
    ) -> tuple[dict[str, object], bool]:
        """Create a ticket. Returns (ticket, replayed).

        With an idempotency key, a repeat of the same request returns the ticket
        created the first time instead of creating another one.
        """
        fingerprint = hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()
        with self._lock:
            if idempotency_key:
                seen = self._db.execute(
                    "SELECT fingerprint, ticket_id FROM idempotency_keys WHERE key = ?",
                    (idempotency_key,),
                ).fetchone()
                if seen:
                    if seen["fingerprint"] != fingerprint:
                        raise IdempotencyConflict(
                            "This idempotency key was already used with a different request body.",
                            ticket_id=seen["ticket_id"],
                        )
                    return self.get(seen["ticket_id"]), True
            self._check_requester(str(fields["requester_id"]))
            last = self._db.execute("SELECT MAX(number) FROM tickets").fetchone()[0]
            number = max(FIRST_NUMBER, (last or 0) + 1)
            ticket_id = f"INC{number:07d}"
            timestamp = now_iso()
            record = {
                **fields,
                "ticket_id": ticket_id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "status": "New",
                "resolution_notes": None,
            }
            self._db.execute(
                INSERT_TICKET,
                [number] + [record.get(column) for column in TICKET_COLUMNS],
            )
            if idempotency_key:
                self._db.execute(
                    "INSERT INTO idempotency_keys (key, fingerprint, ticket_id) VALUES (?, ?, ?)",
                    (idempotency_key, fingerprint, ticket_id),
                )
            self._db.commit()
            return self.get(ticket_id), False

    def update(self, ticket_id: str, changes: dict[str, object]) -> dict[str, object]:
        with self._lock:
            current = self.get(ticket_id)
            if current["status"] == "Closed":
                raise TicketClosed(
                    f"Ticket {ticket_id} is closed and cannot be changed.", ticket_id=ticket_id
                )
            merged = {**current, **changes}
            if merged["status"] in ("Resolved", "Closed") and not merged.get("resolution_notes"):
                raise ResolutionNotesRequired(
                    "resolution_notes is required to set a ticket to Resolved or Closed.",
                    ticket_id=ticket_id,
                )
            if changes:
                assignments = ", ".join(f"{column} = ?" for column in changes)
                self._db.execute(
                    f"UPDATE tickets SET {assignments}, updated_at = ? WHERE ticket_id = ?",
                    [*changes.values(), now_iso(), ticket_id],
                )
                self._db.commit()
            return self.get(ticket_id)

    def add_comment(
        self, ticket_id: str, author_id: str, body: str, internal: bool
    ) -> dict[str, object]:
        with self._lock:
            self.get(ticket_id)
            self._check_requester(author_id)
            timestamp = now_iso()
            cursor = self._db.execute(
                INSERT_COMMENT,
                (ticket_id, author_id, timestamp, body, int(internal)),
            )
            self._db.execute(
                "UPDATE tickets SET updated_at = ? WHERE ticket_id = ?", (timestamp, ticket_id)
            )
            self._db.commit()
            return {
                "comment_id": cursor.lastrowid,
                "ticket_id": ticket_id,
                "author_id": author_id,
                "created_at": timestamp,
                "body": body,
                "internal": internal,
            }

    def comments(self, ticket_id: str) -> list[dict[str, object]]:
        with self._lock:
            self.get(ticket_id)
            return self._comments(ticket_id)

    def search(
        self,
        *,
        requester_id: str | None = None,
        status: str | None = None,
        category: str | None = None,
        assignment_group: str | None = None,
        priority: str | None = None,
        text: str | None = None,
        open_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, object]], int]:
        clauses, values = [], []
        for column, value in (
            ("requester_id", requester_id),
            ("status", status),
            ("category", category),
            ("assignment_group", assignment_group),
            ("priority", priority),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                values.append(value)
        if open_only:
            clauses.append(f"status IN ({', '.join('?' * len(OPEN_STATUSES))})")
            values.extend(OPEN_STATUSES)
        if text:
            escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            clauses.append(
                "(short_description LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')"
            )
            values.extend([f"%{escaped}%"] * 2)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock:
            total = self._db.execute(f"SELECT COUNT(*) FROM tickets {where}", values).fetchone()[0]
            rows = self._db.execute(
                f"SELECT * FROM tickets {where} ORDER BY number DESC LIMIT ? OFFSET ?",
                [*values, limit, offset],
            ).fetchall()
            return [self._ticket(row) for row in rows], total
