# How this project's datasets are produced

## Origin and collection method

The company, people, incidents, documents, software charges and ticket histories are **synthetic**. There is no connected live IT system, scraping pipeline, downloaded public ticket benchmark or collection of real employee records behind this data pack. Python code combines authored support-topic templates with a seeded fictional company population. The data generator itself does not call an LLM API.

- Company: **Larkhaven Group**.
- Snapshot date: **2026-11-13**; this is a fixture date, not today's live data.
- Generation seed: **42**.
- Historical tickets: **5,000**; open-ticket seed: **60**.
- KB: **120** articles, including **80 Markdown**, **40 HTML** and **20 IT-only articles**.
- Policies: **10 current + 2 superseded PDFs**; runbooks: **15 DOCX files**.
- Company sample: **300 employees**, **450 devices**, **830 entitlements**, **12 incident records** and **3 pending joiners**.

## Step-by-step lineage

1. [Authored topic content](../datagen/content/) defines support subjects, OS-specific steps, error codes, ticket phrases, policy requirements, runbooks and catalogue rules.
2. [Topic/TicketSpec schemas](../datagen/model.py) connect a support topic's article content to the request/description/resolution phrases used for its tickets.
3. [KB generation](../datagen/kb.py) expands topics by OS or region, assigns stable KB IDs and writes Markdown frontmatter or HTML metadata. Titles and metadata are inside the files; filenames only carry IDs.
4. [Document generation](../datagen/docs.py) renders policies, old policy versions, runbooks, SLA tables and references from the authored definitions. PDF and Word are alternative source formats, not independently collected datasets.
5. [Population generation](../datagen/people.py) creates employees, manager relationships, devices, software allocations and incidents while preserving eight fixed acceptance personas and HR fixtures.
6. [Ticket generation](../datagen/tickets.py) samples topic phrases and population context with seeded randomness. It injects vague descriptions, typos, misfiled categories, non-IT requests and an incident-related burst. Category/priority/resolution labels are **generated**, not observed and adjudicated real-world outcomes.
7. [Database export](../datagen/dbsql.py) writes the same company records as SQL seed scripts and CSV tables, preserving join keys.
8. [Generator entry point](../datagen/__main__.py) writes the pack and its manifest. Each seed file's byte length and SHA-256 are recorded in [data/manifest.json](../data/manifest.json). Reproducibility also depends on unchanged source code and renderer/dependency versions, not the seed alone.
9. [Evaluation preparation](../scripts/prepare_evals.py) creates a separate draft layer: 90 ticket-derived RAG pairs with distinct linked article IDs plus ten authored unanswerables; six acceptance agent scenarios plus 34 ticket-derived tasks; and 25 authored adversarial cases. Evaluation files are **not covered by the seed manifest**. Their hashes and observed schemas are recorded separately in [dataset_metadata.json](dataset_metadata.json).
10. Running the software creates new threads, ticket mutations, approvals, grants, audit records and onboarding work items. These are **runtime outputs**, not additional independently gathered training examples. Judge labels from a real human are still a required future calibration artifact.

## How to inspect without changing data

From `D:\AI-Engineering\servicedesk-copilot` in PowerShell:

```powershell
.\.venv\Scripts\copilot.exe tickets-stats
Get-Content data\manifest.json -TotalCount 28
Get-Content data\tickets\historical_tickets.jsonl -TotalCount 1
Get-Content data\db\csv\employees.csv -TotalCount 3
Get-Content evals\rag_golden.jsonl -TotalCount 1
```

## Reproduce into an isolated output directory

Learners do not need to regenerate the supplied corpus. If the instructor wants a separate reproduction, install the renderer extra and choose a fresh output path:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[datagen]"
.\.venv\Scripts\python.exe -m datagen --seed 42 --tickets 5000 --out .work\reproduced-data
```

The generator removes and recreates its generated subdirectories under `--out`; do not point it at a directory containing work you want to preserve. Generating into `.work/reproduced-data` avoids replacing the course's existing seed pack. It does not rebuild the evaluation files. Evaluation preparation separately overwrites its output datasets, so preserve reviewed labels before deliberately rebuilding them. No regeneration was performed while adding these guides.

## Metadata and relationships

See [the field-level data dictionary](DATA_DICTIONARY.md). Core joins are ticket.requester_id to employee.employee_id, device.assigned_to to employee.employee_id, entitlement.app_id to catalogue.app_id, employee.manager_id to employee.employee_id, ticket.kb_article_id to KB.id, KB.related_policy to policy-register.id and HR.role_profile to role_profiles.profile_id.

KB `audience=it-staff` is not the same concept as employee application `role=analyst/admin`. Missing metadata must not silently widen access. Ticket display OS labels need normalization before comparing them with KB `os` values. CSV empty strings need table-specific interpretation and are not the same representation as JSON null.

## What learners must not infer from these datasets

- Five thousand template-generated tickets are not five thousand independent real incidents. Template overlap can inflate random-split accuracy and retrieval scores.
- The ML reference groups by normalized short description and holds out roughly 20 percent of groups, not exactly 20 percent of rows or every semantic topic family. Fit vocabulary/normalization on training data only; report the actual row counts.
- Use request text as features. Resolution notes/codes, linked KB IDs, assignment groups, target labels and post-outcome timestamps must not leak into baseline classification inputs or answering prompts.
- The configured noise probabilities are simulation settings, not exact measured dataset percentages. Labels can be noisy and priority may not be inferable from the request text alone.
- Distinct KB IDs and a `heldout` field do not guarantee an independent heldout benchmark; the current retrieval evaluator reports across the supplied pool. Review and enforce the split explicitly before claiming heldout quality.
- Draft golden sets and desired red-team outcomes are not proof of model quality, human agreement or attack resistance. Missing measurements stay unknown.
- Fictional prices, SLA values and historic fixture dates are not live vendor pricing, organizational policy or current outage status. No generalization to production traffic is established.
