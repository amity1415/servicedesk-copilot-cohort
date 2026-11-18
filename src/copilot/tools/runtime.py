"""Authoritative local system of record for repeatable teaching exercises.

SQLite is an offline adapter, not a substitute for the PostgreSQL/MCP gates.
All mutation checks live here, outside model control.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path


class Runtime:
    def __init__(self, path: Path, data: Path):
        self.path, self.data = path, data
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY, employee TEXT NOT NULL, app TEXT NOT NULL,
                    status TEXT NOT NULL, approver TEXT NOT NULL, key TEXT UNIQUE NOT NULL,
                    data_owner TEXT NOT NULL DEFAULT '');
                CREATE TABLE IF NOT EXISTS decisions (
                    request INTEGER, actor TEXT NOT NULL, decision TEXT NOT NULL,
                    created TEXT NOT NULL, PRIMARY KEY(request,actor));
                CREATE TABLE IF NOT EXISTS grants (
                    employee TEXT, app TEXT, PRIMARY KEY(employee, app));
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY, employee TEXT NOT NULL, state TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS memory (
                    employee TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY, actor TEXT, action TEXT, outcome TEXT, created TEXT);
                CREATE TABLE IF NOT EXISTS onboarding_steps (
                    candidate TEXT, step TEXT, evidence TEXT NOT NULL,
                    PRIMARY KEY(candidate,step));
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def rows(self, table: str) -> list[dict]:
        if table not in {
            "employees",
            "devices",
            "service_incidents",
            "software_catalogue",
            "entitlements",
        }:
            raise ValueError("unknown reference table")
        with (self.data / "db" / "csv" / f"{table}.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            return list(csv.DictReader(stream))

    def employee(self, employee_id: str) -> dict:
        return next(row for row in self.rows("employees") if row["employee_id"] == employee_id)

    def audit(self, actor: str, action: str, outcome: str):
        with self.connect() as db:
            db.execute(
                "INSERT INTO audit(actor,action,outcome,created) VALUES (?,?,?,?)",
                (actor, action, outcome, datetime.now(UTC).isoformat()),
            )

    def assets(self, actor: str, employee_id: str) -> list[dict]:
        if actor != employee_id and self.employee(actor)["role"] not in {"admin", "analyst"}:
            self.audit(actor, "get_assets", "denied")
            raise PermissionError("employees may only read their own assets")
        return [row for row in self.rows("devices") if row["assigned_to"] == employee_id]

    def request_access(self, actor: str, app: str, key: str) -> dict:
        employee = self.employee(actor)
        software = next(row for row in self.rows("software_catalogue") if row["app_id"] == app)
        if not software["approval_rule"]:
            raise ValueError("no approval policy")
        # The synthetic catalogue explicitly requires both manager and data owner
        # for FinSight. Unknown multi-owner policies fail closed.
        data_owner = ""
        if "data owner" in software["approval_rule"].lower():
            if software["name"] != "FinSight":
                raise ValueError("no configured data-owner mapping")
            data_owner = next(
                r["employee_id"]
                for r in self.rows("employees")
                if r["job_title"] == "Chief Financial Officer"
            )
        with self.connect() as db:
            db.execute(
                "INSERT OR IGNORE INTO requests(employee,app,status,approver,key,data_owner) "
                "VALUES (?,?, 'pending',?,?,?)",
                (actor, app, employee["manager_id"], key, data_owner),
            )
            request = dict(db.execute("SELECT * FROM requests WHERE key=?", (key,)).fetchone())
            if request["employee"] != actor or request["app"] != app:
                raise ValueError("idempotency key already bound to different arguments")
            return request

    def decide(self, actor: str, request_id: int, decision: str) -> dict:
        if decision not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
            if row is None:
                raise KeyError(request_id)
            if actor not in {row["approver"], row["data_owner"]}:
                raise PermissionError("only the named manager or data owner may decide")
            if row["status"] != "pending":
                raise ValueError("request already decided")
            if db.execute(
                "SELECT 1 FROM decisions WHERE request=? AND actor=?", (request_id, actor)
            ).fetchone():
                raise ValueError("actor already decided")
            db.execute(
                "INSERT INTO decisions VALUES (?,?,?,?)",
                (request_id, actor, decision, datetime.now(UTC).isoformat()),
            )
            approved = {
                r["actor"]
                for r in db.execute(
                    "SELECT actor FROM decisions WHERE request=? AND decision='approve'",
                    (request_id,),
                )
            }
            required = {row["approver"], row["data_owner"]} - {""}
            status = (
                "rejected"
                if decision == "reject"
                else "approved"
                if required <= approved
                else "pending"
            )
            db.execute("UPDATE requests SET status=? WHERE id=?", (status, request_id))
            return {"id": request_id, "status": status}

    def fulfil(self, actor: str, request_id: int) -> dict:
        if self.employee(actor)["role"] not in {"admin", "analyst"}:
            raise PermissionError("fulfilment requires analyst or admin")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
            if row is None or row["status"] not in {"approved", "fulfilled"}:
                raise PermissionError("no approved immutable decision")
            approved = {
                r["actor"]
                for r in db.execute(
                    "SELECT actor FROM decisions WHERE request=? AND decision='approve'",
                    (request_id,),
                )
            }
            if not ({row["approver"], row["data_owner"]} - {""}) <= approved:
                raise PermissionError("missing required approval decision")
            catalogue = next(
                a for a in self.rows("software_catalogue") if a["app_id"] == row["app"]
            )
            existing = {(a["employee_id"], a["app_id"]) for a in self.rows("entitlements")}
            grants = {(a["employee"], a["app"]) for a in db.execute("SELECT * FROM grants")}
            all_grants = existing | grants
            desired = (row["employee"], row["app"])
            if (
                desired not in all_grants
                and catalogue["licence_type"] == "Named"
                and sum(app == row["app"] for _, app in all_grants) >= int(catalogue["seats_total"])
            ):
                raise ValueError("no available licence; escalate")
            db.execute("INSERT OR IGNORE INTO grants VALUES (?,?)", desired)
            db.execute("UPDATE requests SET status='fulfilled' WHERE id=?", (request_id,))
            db.execute(
                "INSERT INTO audit(actor,action,outcome,created) VALUES (?, 'fulfil', ?, ?)",
                (actor, str(request_id), datetime.now(UTC).isoformat()),
            )
            return {"id": request_id, "status": "fulfilled"}

    def save_thread(self, actor: str, thread: str, state: dict):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT employee FROM threads WHERE id=?", (thread,)).fetchone()
            if row and row["employee"] != actor:
                raise PermissionError("thread belongs to another employee")
            db.execute(
                "INSERT INTO threads VALUES (?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET state=excluded.state",
                (thread, actor, json.dumps(state)),
            )

    def load_thread(self, actor: str, thread: str) -> dict:
        with self.connect() as db:
            row = db.execute("SELECT * FROM threads WHERE id=?", (thread,)).fetchone()
            if row and row["employee"] != actor:
                raise PermissionError("thread belongs to another employee")
            return json.loads(row["state"]) if row else {}

    def memory(self, actor: str, value: str | None = None, delete: bool = False):
        with self.connect() as db:
            if delete:
                db.execute("DELETE FROM memory WHERE employee=?", (actor,))
                return None
            if value is not None:
                db.execute(
                    "INSERT INTO memory VALUES (?,?) "
                    "ON CONFLICT(employee) DO UPDATE SET value=excluded.value",
                    (actor, value),
                )
            row = db.execute("SELECT value FROM memory WHERE employee=?", (actor,)).fetchone()
            return row["value"] if row else None

    def onboard(self, actor: str, candidate_id: str, start_date: str, hr_verify) -> dict:
        candidates = json.loads((self.data / "hr/pending_joiners.json").read_text())
        candidate = next(c for c in candidates if c["candidate_id"] == candidate_id)
        if candidate["manager_id"] != actor:
            raise PermissionError("only the hiring manager can request onboarding")
        evidence = hr_verify(candidate_id, actor, start_date)
        if evidence.get("candidate_id") != candidate_id or evidence.get("status") != "complete":
            raise ValueError("HR prerequisite not complete for this candidate")
        # All enterprise systems in this program are simulated. These persisted
        # work items are the IT system-of-record effects, not real AD provisioning.
        steps = ["hr_verified", "account", "laptop", "licences", "access_groups"]
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for step in steps:
                db.execute(
                    "INSERT OR IGNORE INTO onboarding_steps VALUES (?,?,?)",
                    (
                        candidate_id,
                        step,
                        json.dumps(
                            evidence
                            if step == "hr_verified"
                            else {"status": "complete", "simulation": True}
                        ),
                    ),
                )
            return {
                "candidate_id": candidate_id,
                "status": "complete",
                "steps": [
                    dict(r)
                    for r in db.execute(
                        "SELECT * FROM onboarding_steps WHERE candidate=?", (candidate_id,)
                    )
                ],
            }
