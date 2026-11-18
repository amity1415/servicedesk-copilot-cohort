"""Write policies and service levels as PDF, runbooks as Word, and the reference tables.

Needs the optional `datagen` dependencies: fpdf2 and python-docx.
"""

from __future__ import annotations

import csv
import html
import io
import zipfile
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from datagen.company import COMPANY, REGIONS
from datagen.content import catalogue, policies, runbooks
from datagen.docmodel import App, Policy, Runbook, app_id

# Fixed document timestamp so regenerated files do not differ only by their creation time.
DOCUMENT_TIME = datetime(2026, 11, 13, 9, 0, tzinfo=UTC)
GREY = (110, 110, 110)


def long_date(value: date) -> str:
    return f"{value.day} {value:%B %Y}"


class _Pdf(FPDF):
    """A4 document with a running header, page numbers and a few text helpers."""

    def __init__(self, header_left: str, header_right: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._header_left = header_left
        self._header_right = header_right
        self.set_margins(20, 18, 20)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_creation_date(DOCUMENT_TIME)
        self.set_author(COMPANY)
        self.set_creator("Larkhaven document management")

    def header(self) -> None:
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, self._header_left, new_x=XPos.LMARGIN, new_y=YPos.TOP)
        self.cell(0, 5, self._header_right, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(190, 190, 190)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, f"{COMPANY} | Internal | Page {self.page_no()} of {{nb}}", align="C")
        self.set_text_color(0, 0, 0)

    def kicker(self, text: str) -> None:
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.cell(0, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def title_line(self, text: str) -> None:
        self.set_font("Helvetica", "B", 18)
        self.multi_cell(0, 9, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def heading(self, text: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def para(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)

    def clause(self, number: str, text: str) -> None:
        """A numbered clause with a hanging indent."""
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin)
        self.cell(12, 5.2, number)
        self.multi_cell(0, 5.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.2)

    def grid(self, header, rows, widths=None, size: float = 9) -> None:
        self.set_font("Helvetica", "", size)
        with self.table(
            col_widths=widths, text_align="LEFT", line_height=size * 0.5, padding=1.5
        ) as table:
            for cells in (header, *rows):
                row = table.row()
                for cell in cells:
                    row.cell(str(cell))
        self.ln(2)


def write_policy(policy: Policy, out_dir: Path) -> Path:
    pdf = _Pdf(f"{COMPANY} | {policy.id} {policy.title}", f"Version {policy.version}")
    pdf.set_title(f"{policy.id} {policy.title}")
    pdf.set_subject("IT policy")
    pdf.add_page()
    pdf.kicker("IT POLICY")
    pdf.title_line(policy.title)
    pdf.grid(
        ("Document ID", "Version", "Effective date", "Owner", "Classification"),
        ((policy.id, policy.version, long_date(policy.effective), policy.owner, "Internal"),),
        widths=(22, 16, 30, 60, 24),
    )

    number = 1
    pdf.heading(f"{number}  Purpose")
    pdf.para(policy.purpose)
    number += 1
    pdf.heading(f"{number}  Scope")
    pdf.para(policy.scope)
    for section in policy.sections:
        number += 1
        pdf.heading(f"{number}  {section.heading}")
        for index, text in enumerate(section.clauses, start=1):
            pdf.clause(f"{number}.{index}", text)
        if section.table:
            table_header, table_rows = section.table
            pdf.grid(table_header, table_rows, size=8.5)

    number += 1
    pdf.heading(f"{number}  Roles and responsibilities")
    pdf.clause(
        f"{number}.1",
        f"The {policy.owner} owns this policy and reviews it at least every 12 months.",
    )
    pdf.clause(f"{number}.2", "Managers make sure that their teams know and follow this policy.")
    pdf.clause(f"{number}.3", "Everyone in scope is responsible for complying with this policy.")
    number += 1
    pdf.heading(f"{number}  Exceptions")
    pdf.clause(
        f"{number}.1", f"Exceptions are requested in HelpHub and decided by the {policy.owner}."
    )
    pdf.clause(
        f"{number}.2",
        "Every exception is recorded, has an end date no more than 12 months ahead and is reviewed before renewal.",
    )
    number += 1
    pdf.heading(f"{number}  Enforcement")
    pdf.clause(
        f"{number}.1",
        "A breach of this policy may lead to withdrawal of access and to disciplinary action.",
    )
    if policy.related:
        number += 1
        pdf.heading(f"{number}  Related documents")
        for item in policy.related:
            pdf.clause("-", item)
    number += 1
    pdf.heading(f"{number}  Revision history")
    pdf.grid(("Version", "Effective", "Change"), policy.history, widths=(16, 24, 112))

    path = out_dir / f"{policy.file_stem}.pdf"
    pdf.output(str(path))
    return path


def write_policies(out_dir: Path) -> list[Path]:
    """Write every policy version plus register.csv, the list that says which are current."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [write_policy(policy, out_dir) for policy in policies.ALL]
    with (out_dir / "register.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            ["id", "title", "version", "effective_date", "status", "superseded_by", "owner", "file"]
        )
        for policy in policies.ALL:
            writer.writerow(
                [
                    policy.id,
                    policy.title,
                    policy.version,
                    policy.effective.isoformat(),
                    policy.status,
                    policy.superseded_by or "",
                    policy.owner,
                    f"{policy.file_stem}.pdf",
                ]
            )
    return paths


def write_sla_matrix(out_dir: Path) -> Path:
    pdf = _Pdf(f"{COMPANY} | REF-001 IT Service Level Targets", "Version 3.0")
    pdf.set_title("REF-001 IT Service Level Targets")
    pdf.set_subject("Service levels")
    pdf.add_page()
    pdf.kicker("REFERENCE")
    pdf.title_line("IT Service Level Targets")
    pdf.grid(
        ("Document ID", "Version", "Effective date", "Owner", "Classification"),
        (
            (
                "REF-001",
                "3.0",
                long_date(date(2026, 1, 5)),
                "Head of IT Service Management",
                "Internal",
            ),
        ),
        widths=(22, 16, 30, 60, 24),
    )
    pdf.heading("1  Incident priorities")
    pdf.para(
        "Priority is set by the service desk from impact and urgency. "
        "Response and resolution times are measured in support hours unless stated otherwise."
    )
    pdf.grid(
        (
            "Priority",
            "Definition",
            "First response",
            "Resolution target",
            "Service hours",
            "Updates",
        ),
        catalogue.SLA_PRIORITIES,
        widths=(15, 46, 18, 20, 30, 30),
        size=8,
    )
    pdf.heading("2  Request targets")
    pdf.para(
        "Targets for common requests. The clock starts at the event shown in the third column."
    )
    pdf.grid(
        ("Request", "Target", "Clock starts at"),
        catalogue.SLA_REQUESTS,
        widths=(60, 45, 55),
        size=8.5,
    )
    pdf.heading("3  Support hours by region")
    pdf.grid(
        ("Region", "Service desk hours", "Telephone", "Tech Bar"),
        tuple((r.name, r.support_hours, r.phone, r.tech_bar) for r in REGIONS.values()),
        widths=(28, 44, 38, 60),
        size=8,
    )
    pdf.heading("4  Measurement")
    pdf.clause("4.1", "A target is met when 90 percent of tickets in a calendar month meet it.")
    pdf.clause(
        "4.2", "Time spent waiting for the requester's reply or for an approval does not count."
    )
    pdf.clause(
        "4.3", "Results are published on the intranet by the fifth business day of each month."
    )
    path = out_dir / "sla_matrix.pdf"
    pdf.output(str(path))
    return path


def catalogue_rows() -> list[dict[str, object]]:
    rows = []
    for index, app in enumerate(catalogue.APPS):
        rows.append(
            {
                "app_id": app_id(index),
                "name": app.name,
                "vendor": app.vendor,
                "category": app.category,
                "licence_type": app.licence,
                "annual_charge_usd": app.charge,
                "approval_rule": app.approval,
                "platforms": app.platforms,
                "delivery": app.delivery,
                "restricted": app.restricted,
                "seats_total": app.seats,
            }
        )
    return rows


def write_software_catalogue(out_dir: Path) -> list[Path]:
    """The catalogue as a CSV file and as an exported intranet page with an HTML table."""
    rows = catalogue_rows()
    csv_path = out_dir / "software_catalogue.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {**row, "seats_total": "" if row["seats_total"] is None else row["seats_total"]}
            )

    def charge(app: App) -> str:
        return "No charge" if app.charge == 0 else f"USD {app.charge}"

    body = "\n".join(
        "        <tr>"
        f"<td>{app_id(i)}</td><td>{html.escape(a.name)}</td><td>{html.escape(a.vendor)}</td>"
        f"<td>{html.escape(a.category)}</td><td>{a.licence}</td><td>{charge(a)}</td>"
        f"<td>{html.escape(a.approval)}</td><td>{a.platforms}</td><td>{html.escape(a.delivery)}</td>"
        f"<td>{'Yes' if a.restricted else 'No'}</td></tr>"
        for i, a in enumerate(catalogue.APPS)
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Software catalogue | Larkhaven intranet</title>
  <meta name="doc:id" content="REF-002">
  <meta name="doc:title" content="Software catalogue">
  <meta name="doc:type" content="reference">
  <meta name="doc:audience" content="employee">
  <meta name="doc:version" content="2026.11">
  <meta name="doc:effective_date" content="2026-11-02">
  <meta name="doc:owner" content="IT Asset Manager">
</head>
<body>
  <header class="site-header"><a href="/">Larkhaven intranet</a> <nav><a href="/it">IT</a> <a href="/hr">HR</a> <a href="/finance">Finance</a></nav></header>
  <main>
    <h1>Software catalogue</h1>
    <p>Every application approved for use at Larkhaven Group. The annual charge is the internal charge per user per year and decides who must approve a request.</p>
    <h2>Approval rules</h2>
    <ul>
      <li>None: install from App Hub without a request.</li>
      <li>Manager: annual charge under USD 300.</li>
      <li>Manager + cost-centre owner: annual charge of USD 300 or more.</li>
      <li>Manager + data owner: restricted applications, whatever the charge.</li>
    </ul>
    <h2>Applications</h2>
    <table id="software-catalogue">
      <thead>
        <tr><th>ID</th><th>Application</th><th>Vendor</th><th>Category</th><th>Licence</th><th>Annual charge</th><th>Approval</th><th>Platforms</th><th>Delivery</th><th>Restricted</th></tr>
      </thead>
      <tbody>
{body}
      </tbody>
    </table>
    <p>A licence that is not used for 60 days is reclaimed. Software that is not listed here needs a review of up to 10 business days.</p>
  </main>
  <footer><p>REF-002 | Updated 2 November 2026 | Owner: IT Asset Manager | Internal</p></footer>
</body>
</html>
"""
    html_path = out_dir / "software_catalogue.html"
    html_path.write_text(page, encoding="utf-8", newline="\n")
    return [csv_path, html_path]


def write_glossary(out_dir: Path) -> Path:
    lines = [
        "---",
        'id: "REF-003"',
        'title: "Glossary of IT terms and abbreviations"',
        'type: "reference"',
        'audience: "employee"',
        'version: "1.4"',
        'effective_date: "2026-09-01"',
        'owner: "Service Desk L1"',
        "---",
        "",
        "# Glossary of IT terms and abbreviations",
        "",
        "| Term | Meaning |",
        "| --- | --- |",
    ]
    lines += [f"| {term} | {meaning} |" for term, meaning in catalogue.GLOSSARY]
    path = out_dir / "glossary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def write_reference(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return [write_sla_matrix(out_dir), *write_software_catalogue(out_dir), write_glossary(out_dir)]


def _save_reproducible(document, path: Path) -> None:
    """Save a Word file whose bytes do not depend on the time it was written.

    A .docx is a zip archive and every entry records the current time, so two
    identical documents would otherwise never have the same checksum.
    """
    buffer = io.BytesIO()
    document.save(buffer)
    stamp = DOCUMENT_TIME.timetuple()[:6]
    with zipfile.ZipFile(buffer) as source, zipfile.ZipFile(path, "w") as target:
        for item in source.infolist():
            entry = zipfile.ZipInfo(item.filename, date_time=stamp)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = item.external_attr
            target.writestr(entry, source.read(item.filename))


def write_runbook(runbook: Runbook, out_dir: Path) -> Path:
    document = Document()
    properties = document.core_properties
    properties.title = f"{runbook.id} {runbook.title}"
    properties.author = runbook.group
    properties.category = "Runbook"
    properties.keywords = "it-staff"
    properties.created = DOCUMENT_TIME.replace(tzinfo=None)
    properties.modified = DOCUMENT_TIME.replace(tzinfo=None)

    document.add_heading(f"{runbook.id} {runbook.title}", level=1)
    facts = (
        ("Runbook ID", runbook.id),
        ("Version", runbook.version),
        ("Effective date", long_date(runbook.effective)),
        ("Owner", runbook.group),
        ("Audience", "IT staff only"),
        ("Risk tier", runbook.risk),
        ("Approval needed", runbook.approval),
    )
    table = document.add_table(rows=len(facts), cols=2)
    table.style = "Table Grid"
    for row, (label, value) in zip(table.rows, facts, strict=True):
        row.cells[0].text = label
        row.cells[1].text = value

    document.add_heading("Purpose", level=2)
    document.add_paragraph(runbook.purpose)
    document.add_heading("When to use", level=2)
    for item in runbook.when:
        document.add_paragraph(item, style="List Bullet")
    document.add_heading("Before you start", level=2)
    for item in runbook.prerequisites:
        document.add_paragraph(item, style="List Bullet")
    document.add_heading("Steps", level=2)
    for item in runbook.steps:
        document.add_paragraph(item, style="List Number")
    document.add_heading("Check it worked", level=2)
    for item in runbook.verification:
        document.add_paragraph(item, style="List Bullet")
    document.add_heading("Rollback", level=2)
    document.add_paragraph(runbook.rollback)
    if runbook.related:
        document.add_heading("Related", level=2)
        for item in runbook.related:
            document.add_paragraph(item, style="List Bullet")

    path = out_dir / f"{runbook.id}.docx"
    _save_reproducible(document, path)
    return path


def write_runbooks(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return [write_runbook(runbook, out_dir) for runbook in runbooks.ALL]
