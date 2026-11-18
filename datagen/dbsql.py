"""Write the database seed as SQL files and CSV copies.

The SQL is deliberately portable: it loads into PostgreSQL (the target, through
docker-compose.yml) and into SQLite (used by the tests to check it is valid).
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from datetime import date, datetime
from pathlib import Path

from datagen.company import OFFICES, REGIONS, SERVICES
from datagen.content import catalogue
from datagen.docmodel import app_id
from datagen.people import ROLE_PROFILES, Population

EXTENSIONS = """-- Runs first when the PostgreSQL container is created. Used from session 10.
CREATE EXTENSION IF NOT EXISTS vector;
"""

SCHEMA = """-- IT Service Desk Copilot: enterprise data the agent reads (a 300-person sample).
-- Portable SQL: PostgreSQL 14 or later, and SQLite 3.35 or later. All times are UTC.

CREATE TABLE regions (
    region        TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    support_hours TEXT NOT NULL,
    phone         TEXT NOT NULL,
    tech_bar      TEXT NOT NULL
);

CREATE TABLE offices (
    office TEXT PRIMARY KEY,
    code   TEXT NOT NULL UNIQUE,
    region TEXT NOT NULL REFERENCES regions (region)
);

CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    full_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    department  TEXT NOT NULL,
    job_title   TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('employee', 'analyst', 'admin')),
    is_manager  BOOLEAN NOT NULL,
    manager_id  TEXT REFERENCES employees (employee_id),
    office      TEXT NOT NULL REFERENCES offices (office),
    region      TEXT NOT NULL REFERENCES regions (region),
    start_date  DATE NOT NULL,
    status      TEXT NOT NULL
);

CREATE TABLE devices (
    asset_tag       TEXT PRIMARY KEY,
    device_type     TEXT NOT NULL CHECK (device_type IN ('laptop', 'phone')),
    model           TEXT NOT NULL,
    os              TEXT NOT NULL,
    os_version      TEXT NOT NULL,
    serial_number   TEXT NOT NULL UNIQUE,
    purchase_date   DATE NOT NULL,
    ram_gb          INTEGER,
    storage_gb      INTEGER NOT NULL,
    assigned_to     TEXT REFERENCES employees (employee_id),
    status          TEXT NOT NULL CHECK (status IN ('in use', 'in stock', 'in repair', 'lost', 'retired')),
    encrypted       BOOLEAN NOT NULL,
    compliant       BOOLEAN NOT NULL,
    last_patch_date DATE,
    pending_updates INTEGER NOT NULL
);

CREATE TABLE software_catalogue (
    app_id            TEXT PRIMARY KEY,
    name              TEXT NOT NULL UNIQUE,
    vendor            TEXT NOT NULL,
    category          TEXT NOT NULL,
    licence_type      TEXT NOT NULL CHECK (licence_type IN ('Free', 'Site', 'Named')),
    annual_charge_usd INTEGER NOT NULL,
    approval_rule     TEXT NOT NULL,
    platforms         TEXT NOT NULL,
    delivery          TEXT NOT NULL,
    restricted        BOOLEAN NOT NULL,
    seats_total       INTEGER
);

CREATE TABLE entitlements (
    employee_id TEXT NOT NULL REFERENCES employees (employee_id),
    app_id      TEXT NOT NULL REFERENCES software_catalogue (app_id),
    granted_at  DATE NOT NULL,
    last_used   DATE NOT NULL,
    PRIMARY KEY (employee_id, app_id)
);

CREATE TABLE role_profiles (
    profile_id  TEXT PRIMARY KEY,
    department  TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    laptop_type TEXT NOT NULL
);

CREATE TABLE role_profile_apps (
    profile_id TEXT NOT NULL REFERENCES role_profiles (profile_id),
    app_id     TEXT NOT NULL REFERENCES software_catalogue (app_id),
    PRIMARY KEY (profile_id, app_id)
);

CREATE TABLE services (
    service     TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE service_incidents (
    incident_id INTEGER PRIMARY KEY,
    service     TEXT NOT NULL REFERENCES services (service),
    region      TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('degraded', 'outage')),
    started_at  TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    message     TEXT NOT NULL
);

-- Seats in use and free for every licensed application.
CREATE VIEW licence_pool AS
SELECT c.app_id,
       c.name,
       c.seats_total,
       COUNT(e.employee_id) AS seats_used,
       c.seats_total - COUNT(e.employee_id) AS seats_free
FROM software_catalogue c
LEFT JOIN entitlements e ON e.app_id = c.app_id
WHERE c.seats_total IS NOT NULL
GROUP BY c.app_id, c.name, c.seats_total;

-- Status of every service in every region right now. No open incident means operational.
CREATE VIEW service_status AS
SELECT s.service,
       r.region,
       COALESCE(i.status, 'operational') AS status,
       i.started_at,
       i.message
FROM services s
CROSS JOIN regions r
LEFT JOIN service_incidents i
       ON i.service = s.service
      AND i.resolved_at IS NULL
      AND i.region IN (r.region, 'Global');
"""


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value:%Y-%m-%d %H:%M:%S}'"
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    return "'" + str(value).replace("'", "''") + "'"


def insert(
    table: str, columns: Sequence[str], rows: Iterable[Sequence[object]], batch: int = 200
) -> str:
    rows = list(rows)
    statements = []
    for start in range(0, len(rows), batch):
        values = ",\n".join(
            "    (" + ", ".join(sql_literal(value) for value in row) + ")"
            for row in rows[start : start + batch]
        )
        statements.append(f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n{values};\n")
    return "\n".join(statements)


def _tables(population: Population) -> list[tuple[str, tuple[str, ...], list[tuple]]]:
    """Every table as (name, columns, rows), in an order that satisfies the foreign keys."""
    app_ids = {app.name: app_id(index) for index, app in enumerate(catalogue.APPS)}
    return [
        (
            "regions",
            ("region", "name", "support_hours", "phone", "tech_bar"),
            [(r.code, r.name, r.support_hours, r.phone, r.tech_bar) for r in REGIONS.values()],
        ),
        ("offices", ("office", "code", "region"), [(o.city, o.code, o.region) for o in OFFICES]),
        (
            "employees",
            (
                "employee_id",
                "full_name",
                "email",
                "department",
                "job_title",
                "role",
                "is_manager",
                "manager_id",
                "office",
                "region",
                "start_date",
                "status",
            ),
            [
                (
                    e.employee_id,
                    e.full_name,
                    e.email,
                    e.department,
                    e.job_title,
                    e.role,
                    e.is_manager,
                    e.manager_id,
                    e.office,
                    e.region,
                    e.start_date,
                    e.status,
                )
                for e in population.employees
            ],
        ),
        (
            "devices",
            (
                "asset_tag",
                "device_type",
                "model",
                "os",
                "os_version",
                "serial_number",
                "purchase_date",
                "ram_gb",
                "storage_gb",
                "assigned_to",
                "status",
                "encrypted",
                "compliant",
                "last_patch_date",
                "pending_updates",
            ),
            [
                (
                    d.asset_tag,
                    d.device_type,
                    d.model,
                    d.os,
                    d.os_version,
                    d.serial_number,
                    d.purchase_date,
                    d.ram_gb,
                    d.storage_gb,
                    d.assigned_to,
                    d.status,
                    d.encrypted,
                    d.compliant,
                    d.last_patch_date,
                    d.pending_updates,
                )
                for d in population.devices
            ],
        ),
        (
            "software_catalogue",
            (
                "app_id",
                "name",
                "vendor",
                "category",
                "licence_type",
                "annual_charge_usd",
                "approval_rule",
                "platforms",
                "delivery",
                "restricted",
                "seats_total",
            ),
            [
                (
                    app_id(i),
                    a.name,
                    a.vendor,
                    a.category,
                    a.licence,
                    a.charge,
                    a.approval,
                    a.platforms,
                    a.delivery,
                    a.restricted,
                    a.seats,
                )
                for i, a in enumerate(catalogue.APPS)
            ],
        ),
        (
            "entitlements",
            ("employee_id", "app_id", "granted_at", "last_used"),
            [(e.employee_id, e.app_id, e.granted_at, e.last_used) for e in population.entitlements],
        ),
        (
            "role_profiles",
            ("profile_id", "department", "name", "laptop_type"),
            [(pid, department, name, laptop) for pid, department, name, laptop, _ in ROLE_PROFILES],
        ),
        (
            "role_profile_apps",
            ("profile_id", "app_id"),
            [(pid, app_ids[app]) for pid, _, _, _, apps in ROLE_PROFILES for app in apps],
        ),
        ("services", ("service", "description"), list(SERVICES)),
        (
            "service_incidents",
            ("incident_id", "service", "region", "status", "started_at", "resolved_at", "message"),
            [
                (
                    i.incident_id,
                    i.service,
                    i.region,
                    i.status,
                    i.started_at,
                    i.resolved_at,
                    i.message,
                )
                for i in population.incidents
            ],
        ),
    ]


def write_database(population: Population, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = out_dir / "csv"
    csv_dir.mkdir(exist_ok=True)
    tables = _tables(population)

    paths = []
    for name, text in (
        ("00_extensions.sql", EXTENSIONS),
        ("01_schema.sql", SCHEMA),
        (
            "02_seed.sql",
            "-- Generated by `python -m datagen`. Do not edit by hand.\n\n"
            + "\n".join(insert(table, columns, rows) for table, columns, rows in tables),
        ),
    ):
        path = out_dir / name
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)

    for table, columns, rows in tables:
        path = csv_dir / f"{table}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(columns)
            for row in rows:
                writer.writerow(
                    ""
                    if value is None
                    else value.strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(value, datetime)
                    else str(value).lower()
                    if isinstance(value, bool)
                    else value
                    for value in row
                )
        paths.append(path)
    return paths
