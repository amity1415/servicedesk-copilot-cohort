"""Content model for policies, runbooks and the software catalogue."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date


def app_id(index: int) -> str:
    """Catalogue ID of the application at this position in content.catalogue.APPS."""
    return f"APP-{index + 1:03d}"


@dataclass(frozen=True)
class Section:
    heading: str
    clauses: tuple[str, ...] = ()
    # Optional table shown after the clauses: (header row, data rows).
    table: tuple[tuple[str, ...], tuple[tuple[str, ...], ...]] | None = None


@dataclass(frozen=True)
class Policy:
    id: str
    title: str
    version: str
    effective: date
    owner: str
    purpose: str
    scope: str
    sections: tuple[Section, ...]
    history: tuple[tuple[str, str, str], ...]  # version, effective date, change
    related: tuple[str, ...] = ()
    status: str = "current"  # current | superseded
    superseded_by: str | None = None

    @property
    def file_stem(self) -> str:
        return f"{self.id}_v{self.version}"


def earlier_version(
    policy: Policy,
    *,
    version: str,
    effective: date,
    changes: dict[str, str | None],
    drop_sections: tuple[str, ...] = (),
) -> Policy:
    """Build a superseded version from the current one.

    `changes` maps a clause of the current policy to its older wording, or to
    None when the clause did not exist yet. Every key must match exactly, so a
    later edit to the current policy cannot silently break the old version.
    """
    remaining = dict(changes)
    sections = []
    for section in policy.sections:
        if section.heading in drop_sections:
            continue
        clauses = []
        for clause in section.clauses:
            if clause in remaining:
                old = remaining.pop(clause)
                if old is not None:
                    clauses.append(old)
            else:
                clauses.append(clause)
        sections.append(replace(section, clauses=tuple(clauses)))
    if remaining:
        raise ValueError(f"{policy.id}: clauses not found for version {version}: {list(remaining)}")
    history = tuple(row for row in policy.history if row[0] <= version)
    return replace(
        policy,
        version=version,
        effective=effective,
        sections=tuple(sections),
        history=history,
        status="superseded",
        superseded_by=policy.version,
    )


@dataclass(frozen=True)
class Runbook:
    id: str
    title: str
    group: str
    risk: str  # read | low-risk write | approval-required
    approval: str  # who must approve, or "None"
    purpose: str
    when: tuple[str, ...]
    prerequisites: tuple[str, ...]
    steps: tuple[str, ...]
    verification: tuple[str, ...]
    rollback: str
    related: tuple[str, ...] = ()
    version: str = "1.0"
    effective: date = date(2026, 1, 12)


@dataclass(frozen=True)
class App:
    name: str
    vendor: str
    category: str
    licence: str  # Free | Site | Named
    charge: int  # internal annual charge per user, USD (fictional)
    approval: str
    platforms: str
    delivery: str
    restricted: bool = False
    seats: int | None = None  # pool size for Named licences
    used: int | None = None  # fixed number in use, for apps the scenarios depend on
