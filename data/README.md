# Synthetic data pack

Everything in this folder is fictional and was written by `python -m datagen`. Larkhaven Group does not exist. Its domain, `larkhaven.example`, uses a reserved top-level domain that cannot resolve. Software charges are invented internal figures, not vendor prices. The pack is written as if exported on 13 November 2026.

Do not edit these files by hand: change `datagen/content/` and regenerate, so that `manifest.json` stays true.

## Contents

| Folder | What it holds | Count | First used |
| --- | --- | --- | --- |
| `tickets/historical_tickets.jsonl` | Closed tickets, May 2025 to November 2026, one JSON object per line | 5,000 | Session 1 |
| `tickets/open_tickets.json` | Tickets still open; the seed of the ticketing mock | 60 | Session 17 |
| `kb/` | Knowledge-base articles, 80 Markdown and 40 HTML, plus `index.csv` | 120 | Session 5 |
| `policies/` | IT policies as PDF, plus `register.csv` | 10 current, 2 superseded | Session 6 |
| `runbooks/` | Procedures for IT staff as Word documents | 15 | Session 6 |
| `reference/` | Service level targets (PDF), software catalogue (HTML and CSV), glossary (Markdown) | 4 files | Session 6 |
| `db/` | Database seed: `00_extensions.sql`, `01_schema.sql`, `02_seed.sql`, and the same tables as CSV | 300 employees, 450 devices | Session 10 |
| `hr/pending_joiners.json` | What HR knows about people who have not started; the HR agent's data | 3 | Session 33 |
| `personas.md` | The eight fixed employees behind the acceptance requests | 8 | Session 1 |
| `manifest.json` | Counts and a checksum for every file | | |

## Things that are difficult on purpose

The pack is meant to behave like a real export, so several lessons depend on its rough edges.

- **File names carry no meaning.** Articles are named by ID. Title, operating system, region, audience and dates are inside the file: YAML front matter in Markdown, `<meta name="kb:...">` tags in HTML.
- **HTML articles include the portal around them.** Navigation, search box, feedback widget and footer have to be stripped before chunking.
- **The same topic exists several times.** Many articles come in a Windows and a macOS version, and four topics come once per region. A good answer uses the one that fits the user.
- **Twenty articles and all runbooks are for IT staff only.** `audience` is `it-staff`. They must never reach an employee.
- **Two policies have an old version in the same folder.** The old PDFs do not say they are out of date; only `policies/register.csv` and the effective dates do. The old password policy says 12 characters and expiry every 90 days. The current one says 14 and no expiry.
- **Exact strings matter.** Twenty-two articles are about a specific error code, such as `809`, `0x80070005` or `LID-MFA-102`, which meaning-based search handles badly.
- **Tables do not survive naive PDF parsing.** The data classification policy and the service level targets both keep key facts in tables with wrapped cells.
- **Tickets are noisy.** About 12 percent say too little to classify from the text, 3 percent are filed under the wrong category, 1.5 percent are not IT matters, and some contain typos. Security is under 3 percent of tickets.
- **One day is unusual.** On 20 October 2026 a VPN incident produced a burst of similar tickets.
- **One open ticket attacks the assistant.** Its description contains an instruction to grant administrator rights. `personas.md` gives its ID.

## Ticket fields

`ticket_id`, `created_at`, `resolved_at`, `requester_id`, `department`, `region`, `office`, `channel`, `device_os`, `short_description`, `description`, `category`, `subcategory`, `priority`, `assignment_group`, `status`, `resolution_code`, `resolution_notes`, `kb_article_id`, `reopened`.

`kb_article_id` is the article that resolved the ticket, when one did. It is the link from which golden questions are built in sessions 5 and 15, and it never points to an IT-staff article.

## Database

`01_schema.sql` is portable SQL: it runs on PostgreSQL and on SQLite, which is how the tests check it. Two views do the common lookups:

- `licence_pool`: seats in use and free for each licensed application.
- `service_status`: the status of every service in every region right now.

Employees have an application role of `employee`, `analyst` or `admin`. Session 32 maps these to tool permissions.
