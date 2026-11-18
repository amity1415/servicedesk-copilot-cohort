"""Build the synthetic data pack.

    python -m datagen                 # rebuild everything under data/
    python -m datagen --tickets 500   # a smaller ticket export for quick experiments

Needs the optional dependencies: pip install -e ".[datagen]"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from datagen import dbsql, docs, kb
from datagen.company import AS_OF, COMPANY
from datagen.content import policies
from datagen.people import PERSONAS, Population, build_population
from datagen.tickets import TicketFactory

GENERATED_DIRS = ("kb", "policies", "runbooks", "reference", "tickets", "db", "hr")
OPEN_TICKETS = 60


def write_json(path: Path, payload: object) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def personas_markdown(population: Population, open_tickets: list[dict[str, object]]) -> str:
    lines = [
        "# Personas",
        "",
        "Eight fixed employees stand behind the acceptance requests in the build plan.",
        "They are regenerated identically by `python -m datagen`, whatever the seed.",
        "",
        "| Persona | Employee | Name | Role | Office | Laptop | Used for |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in PERSONAS:
        employee = population.personas[spec.key]
        laptop = population.laptop_of(employee.employee_id)
        lines.append(
            f"| `{spec.key}` | {employee.employee_id} | {employee.full_name} | "
            f"{employee.job_title}, {employee.department} ({employee.role}) | {employee.office} | "
            f"{laptop.asset_tag}: {laptop.model}, {laptop.ram_gb} GB | {spec.used_for} |"
        )
    analyst = population.personas["finance_analyst"]
    manager = population.by_id[analyst.manager_id]
    hiring = population.personas["hiring_manager"]
    joiner = population.pending_joiners[0]
    slow = population.personas["slow_laptop"]
    injected = next(t for t in open_tickets if "SYSTEM NOTE" in str(t["description"]))
    earlier = next(t for t in open_tickets if t["requester_id"] == slow.employee_id)
    lines += [
        "",
        "## Details the scenarios depend on",
        "",
        f"- {analyst.full_name}'s line manager is {manager.full_name} ({manager.employee_id}), who approves her FinSight request. "
        "The Finance data owner is the Chief Financial Officer.",
        "- FinSight has 60 licences and 58 are in use; two of those have been idle for more than 60 days.",
        "- Microsoft Visio has 25 licences and all 25 are in use; one has been idle for 68 days.",
        f"- {hiring.full_name}'s new joiner is {joiner['full_name']} ({joiner['candidate_id']}), starting {joiner['start_date']}. "
        "Her PeopleHub record is complete. A second pending joiner has an incomplete record.",
        "- Two incidents are open on the export date: SecureTunnel VPN is degraded in APAC and FollowMe Printing is down in EMEA.",
        f"- {slow.full_name} already has an open ticket, {earlier['ticket_id']} ({earlier['short_description']}), "
        "waiting for his reply.",
        f"- Open ticket {injected['ticket_id']} from the `injection_requester` persona contains an instruction "
        "addressed to the AI assistant. It is in `data/tickets/open_tickets.json`.",
        "",
    ]
    return "\n".join(lines)


def build_manifest(out: Path, seed: int, counts: dict[str, int]) -> dict[str, object]:
    files = {}
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"):
        data = path.read_bytes()
        files[path.relative_to(out).as_posix()] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return {
        "company": COMPANY,
        "note": "Synthetic data. The company, people, systems, prices and incidents are fictional.",
        "as_of": AS_OF.isoformat(),
        "seed": seed,
        "counts": counts,
        "files": files,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m datagen", description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=Path("data"), help="output folder (default: data)"
    )
    parser.add_argument("--seed", type=int, default=42, help="random seed (default: 42)")
    parser.add_argument(
        "--tickets", type=int, default=5000, help="historical tickets (default: 5000)"
    )
    args = parser.parse_args(argv)
    out: Path = args.out

    for name in GENERATED_DIRS:
        shutil.rmtree(out / name, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)

    articles = kb.build_articles(args.seed)
    kb.write_articles(articles, out / "kb")
    docs.write_policies(out / "policies")
    runbooks = docs.write_runbooks(out / "runbooks")
    reference = docs.write_reference(out / "reference")

    population = build_population(args.seed)
    dbsql.write_database(population, out / "db")

    factory = TicketFactory(population, articles, args.seed)
    historical = factory.historical(args.tickets)
    open_tickets = factory.open_tickets(OPEN_TICKETS)
    (out / "tickets").mkdir()
    write_jsonl(out / "tickets" / "historical_tickets.jsonl", historical)
    write_json(out / "tickets" / "open_tickets.json", open_tickets)

    (out / "hr").mkdir()
    write_json(out / "hr" / "pending_joiners.json", population.pending_joiners)
    personas = personas_markdown(population, open_tickets)
    (out / "personas.md").write_text(personas, encoding="utf-8", newline="\n")

    devices = Counter(device.device_type for device in population.devices)
    counts = {
        "kb_articles": len(articles),
        "kb_articles_markdown": sum(1 for a in articles if a.fmt == "md"),
        "kb_articles_html": sum(1 for a in articles if a.fmt == "html"),
        "kb_articles_it_staff_only": sum(1 for a in articles if a.topic.audience == "it-staff"),
        "policies_current": len(policies.CURRENT),
        "policies_superseded": len(policies.SUPERSEDED),
        "runbooks": len(runbooks),
        "reference_files": len(reference),
        "historical_tickets": len(historical),
        "open_tickets": len(open_tickets),
        "employees": len(population.employees),
        "devices": len(population.devices),
        "laptops": devices["laptop"],
        "phones": devices["phone"],
        "entitlements": len(population.entitlements),
        "service_incidents": len(population.incidents),
        "pending_joiners": len(population.pending_joiners),
    }
    write_json(out / "manifest.json", build_manifest(out, args.seed, counts))

    print(f"Data pack written to {out}/ (seed {args.seed})")
    for name, value in counts.items():
        print(f"  {name:<28} {value:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
