"""Read the seeded directory and apply employee asset scope."""

import csv
from pathlib import Path


class Directory:
    def __init__(self, data: Path):
        self.data = data

    def rows(self, table: str) -> list[dict]:
        if table not in {
            "employees",
            "devices",
            "service_incidents",
            "software_catalogue",
            "entitlements",
        }:
            raise ValueError("unknown reference table")
        with (self.data / "db/csv" / f"{table}.csv").open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def employee(self, employee_id: str) -> dict:
        return next(row for row in self.rows("employees") if row["employee_id"] == employee_id)

    def assets(self, actor: str, employee_id: str) -> list[dict]:
        if actor != employee_id and self.employee(actor)["role"] not in {"admin", "analyst"}:
            raise PermissionError("employees may only read their own assets")
        return [row for row in self.rows("devices") if row["assigned_to"] == employee_id]
