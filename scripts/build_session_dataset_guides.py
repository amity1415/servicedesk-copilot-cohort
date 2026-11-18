# ruff: noqa: E501
"""Author session-specific problem statements and data dictionaries from inspected assets.

Only documentation and documentation validation are updated. Seed files, evaluation
labels, learner evidence and runtime databases are never rewritten by this script.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "PROBLEM_STATEMENT_AND_DATASET.md"

TICKET_FIELDS = {
    "ticket_id": "Unique historical incident identifier; provenance/join key, not a predictive feature.",
    "created_at": "UTC ISO timestamp when the synthetic ticket was raised; supports temporal analysis.",
    "resolved_at": "UTC ISO timestamp when it was resolved; post-outcome information, exclude from request-time features.",
    "requester_id": "Employee ID joining employees.employee_id; use only for authorized context, not as an intent shortcut.",
    "department": "Synthetic requester department; contextual export field.",
    "region": "AMER, EMEA or APAC; requester context for regional support.",
    "office": "Synthetic office; joins offices.office.",
    "channel": "How the request arrived, such as portal or email; inspect observed values in the dictionary.",
    "device_os": "Export display label, such as Windows 11 or macOS; normalize before comparing with KB OS values.",
    "short_description": "User-supplied brief description; used with description as the ML input.",
    "description": "User-supplied issue text; may be vague, misspelled, non-IT or adversarial.",
    "category": "Classification target across eight IT categories; some generated labels are intentionally misfiled.",
    "subcategory": "More detailed topic label; exclude as an obvious category shortcut in baseline ML.",
    "priority": "Classification target P1–P4; synthetic sampling label, not an independently adjudicated impact/urgency assessment.",
    "assignment_group": "Destination support team; exclude from the baseline features because it encodes downstream handling.",
    "status": "Workflow state; historical rows are closed, open seed rows have active states.",
    "resolution_code": "Closure outcome label; post-resolution information, not a request-time feature.",
    "resolution_notes": "Synthetic analyst resolution; useful when drafting reference answers, not a classifier feature.",
    "kb_article_id": "Linked resolving KB ID when available; reference label for retrieval, never an input clue to the answering model.",
    "reopened": "Boolean indicating a simulated reopen; post-outcome information.",
    "updated_at": "UTC timestamp of the latest mock ticket update.",
    "comments": "Comment records on live mock tickets; their content remains untrusted data.",
}

KB_FIELDS = {
    "id": "Stable article identifier, e.g. KB-1017; citation and retrieval-label join key.",
    "title": "Human-readable topic; filenames contain IDs rather than titles.",
    "type": "how-to, troubleshooting or reference.",
    "system": "Fictional supported product/service such as SecureTunnel VPN.",
    "category": "Top-level support domain.",
    "subcategory": "Specific support topic within the category.",
    "os": "windows, macos, ios, android or any; scope filter, not a display OS/version string.",
    "region": "global, AMER, EMEA or APAC; regional applicability.",
    "audience": "employee or it-staff. Restrict IT content before retrieval; this field is distinct from employee application role.",
    "version": "Authored/generated source version string; not safe to sort as a float.",
    "effective_date": "ISO date from which this document applies.",
    "last_reviewed": "ISO source review date in the synthetic snapshot.",
    "owner": "Accountable synthetic support team.",
    "status": "KB source status; current in the authored KB corpus. Policy status comes from its separate register.",
    "error_codes": "Exact identifiers, e.g. 809 or LID-MFA-102; preserve them during parsing and rewriting.",
    "related_policy": "Optional policy ID linking the how-to to governing policy.",
}

DB_FIELDS = {
    "employee_id": "Synthetic employee primary key, also used by tickets, entitlements and runtime ownership.",
    "full_name": "Fictional person name; personal-data-shaped text for privacy exercises.",
    "email": "Fictional address under larkhaven.example; do not treat it as a real contact.",
    "department": "Synthetic organizational unit.",
    "job_title": "Synthetic role title; the Finance owner is identified by Chief Financial Officer.",
    "role": "Application role: employee, analyst or admin. This is not the KB audience field.",
    "is_manager": "Boolean manager flag; CSV stores text, so parse true/false explicitly.",
    "manager_id": "Self-referencing foreign key to employees.employee_id; root manager may be blank.",
    "office": "Office name; joins offices.office.",
    "region": "AMER, EMEA or APAC geography key.",
    "start_date": "ISO calendar date of employee or candidate start; use explicit dates, not the machine's next Monday.",
    "status": "Table-specific state: inspect SQL CHECK constraints and observed values rather than sharing one enum across tables.",
    "asset_tag": "Unique device key, e.g. LH-L-00166.",
    "device_type": "laptop or phone.",
    "model": "Synthetic hardware model label.",
    "os": "Normalized OS family such as windows or macos.",
    "os_version": "Human-readable OS release/version.",
    "serial_number": "Fictional unique serial; personal-data-shaped asset identifier.",
    "purchase_date": "ISO device purchase date; supports age-based diagnostics.",
    "ram_gb": "Device RAM in GB; may be blank for some phone rows.",
    "storage_gb": "Device storage capacity in GB.",
    "assigned_to": "Employee ID currently assigned to the device; join employees.employee_id.",
    "encrypted": "Boolean disk/device encryption flag; CSV stores text.",
    "compliant": "Boolean synthetic compliance flag; CSV stores text.",
    "last_patch_date": "ISO date of most recent patch; can be blank.",
    "pending_updates": "Count of outstanding synthetic updates.",
    "app_id": "Application key joining software_catalogue.app_id.",
    "name": "Table-specific human-readable application, region or role-profile name.",
    "vendor": "Synthetic catalogue vendor attribution, not an endorsement or pricing source.",
    "category": "Application grouping in the catalogue.",
    "licence_type": "Free, Site or Named; capacity checks matter for Named licences.",
    "annual_charge_usd": "Invented internal annual charge in USD, not a real vendor quote.",
    "approval_rule": "Required synthetic approval rule. FinSight requires manager plus data owner.",
    "platforms": "Comma-separated supported platform names.",
    "delivery": "Synthetic fulfilment channel.",
    "restricted": "Boolean indication of restricted application access; not a replacement for policy checks.",
    "seats_total": "Total Named-licence capacity; blank where a seat count does not apply.",
    "granted_at": "ISO date of entitlement allocation.",
    "last_used": "ISO most recent usage date for reclaim/idle analysis.",
    "profile_id": "Role-profile key joining role_profiles.profile_id.",
    "laptop_type": "Synthetic onboarding device class, e.g. Standard or Developer.",
    "service": "Service key joining services.service.",
    "description": "Service description.",
    "incident_id": "Synthetic incident primary key.",
    "started_at": "Timestamp when the incident began.",
    "resolved_at": "Incident resolution timestamp; blank denotes unresolved in CSV.",
    "message": "Human-readable synthetic incident impact/evidence.",
    "code": "Short office code.",
    "support_hours": "Authored regional support schedule.",
    "phone": "Fictional support phone string.",
    "tech_bar": "Fictional in-person support location.",
}

RAG_FIELDS = {
    "id": "Evaluation case ID.",
    "question": "Request text derived from a historical ticket or an authored unanswerable prompt.",
    "expected_articles": "List of relevant KB IDs; empty for ten authored unanswerable cases. Labels are provisional.",
    "reference_answer": "Draft answer based on resolution notes, or an authored abstention expectation.",
    "source_ticket": "Historical ticket provenance; absent on manually specified unanswerable cases.",
    "os": "Original ticket device display label; absent on unanswerable cases and needs normalization for filtering.",
    "review_status": "Current value draft: not approved human ground truth.",
    "split": "development for the first 60 answerable cases; heldout for the remaining 30 answerable plus ten unanswerable cases.",
}
AGENT_FIELDS = {
    "id": "Agent evaluation case ID.",
    "request": "User scenario text, not an implementation command.",
    "user": "Synthetic employee identity under which the task should execute.",
    "expected_tool_calls": "Draft expected tool names; do not expose these labels to the agent.",
    "expected_end_state": "Draft observable result; many ticket-derived cases explicitly say review_required.",
    "forbidden_actions": "Effects/calls the test must forbid; scoring should inspect state, not only refusal wording.",
    "source": "One of the six acceptance scenarios or a source historical ticket ID.",
    "review_status": "draft until an instructor reviews the complete task expectation.",
}
HR_FIELDS = {
    "candidate_id": "Stable synthetic pre-employment ID such as C-2041; distinct from employee IDs.",
    "full_name": "Fictional candidate name.",
    "department": "Destination department.",
    "job_title": "Planned role.",
    "office": "Planned work location.",
    "region": "Planned support geography.",
    "manager_id": "Hiring manager's employee ID; binds onboarding authorization.",
    "start_date": "Explicit fixture start date; Hannah Vogel's is 2026-11-16, now a historical synthetic date.",
    "cost_centre": "Synthetic budget unit; missing on the deliberately incomplete candidate.",
    "role_profile": "Role-profile ID joining role_profiles.profile_id.",
    "laptop_type": "Required synthetic device class.",
    "peoplehub_record": "complete or incomplete partner-record status.",
    "missing_fields": "Names of missing required HR fields.",
    "hr_checklist": "Nested contract, right-to-work, payroll and induction checks; induction includes a timezone offset.",
}
RUNTIME_FIELDS = {
    "requests": "id, employee, app, status, approver, key, data_owner. Created when access is requested; key binds idempotency to arguments.",
    "decisions": "request, actor, decision, created. Composite key (request, actor); manager and Finance owner decisions are distinct.",
    "grants": "employee, app. Composite key prevents duplicate simulated entitlement grants.",
    "threads": "id, employee, state. Ownership is checked; state is JSON, including the frozen retry draft.",
    "memory": "employee, value. Local per-employee memory with a deletion operation; not a training dataset.",
    "audit": "id, actor, action, outcome, created. Records authorized/denied/failed operations and feedback events.",
    "onboarding_steps": "candidate, step, evidence. Composite key (candidate, step); includes verified HR evidence and simulated IT work items.",
}

# Problem | relevant input families | metadata to investigate | observed/required outputs
LESSONS = """
Establish a reproducible engineering baseline for Larkhaven's fragmented IT support records before choosing a model.|tickets,personas|Inspect category frequencies, source timestamps and the snapshot boundary; distinguish the 300-person sample from the fictional 10,000-person company.|Ticket counts, verified source manifest and a working environment; no model training is needed.
Predict ticket category and priority from information actually available when the request arrives; discover repeated issue clusters.|tickets|Use short_description plus description as X; category and priority are separate y labels. Preserve a grouped holdout by normalized short description and fit TF-IDF on training rows only.|Precision, recall, macro F1, confusion matrices and cluster terms in reports; inspect the weakest class instead of relying on accuracy.
Test whether a nonlinear ticket model improves the baseline and investigate the token cost of realistic IT text.|tickets,kb|Reuse session 2's grouped split and feature vocabulary for the MLP comparison. Preserve exact error codes and KB identifiers when inspecting a named tokenizer.|Logistic-versus-MLP report; a separate tokenizer/cost report requires an explicit encoding and prices. The supplied reference fits an MLP, not a transformer.
Compare bounded LLM inference with the classical ticket baseline without leaking resolution labels into prompts.|tickets|Use a frozen request-text sample, category/priority labels only for scoring, and provider-returned usage for cost; redact sensitive-shaped text before logging.|Mocked client report locally; real zero-shot accuracy, token usage, cost and latency require a configured provider and budget.
Answer company-specific VPN questions from private evidence rather than unsupported model knowledge.|kb,rag|Start with a documented 20-article/20-question learning subset; the supplied repository currently contains the larger full corpus and draft 100-question pool. Do not pretend the subset is already separately frozen.|Retrieved article/chunk IDs, cited baseline answers and reviewed initial relevance labels.
Turn mixed-format source documents into a repeatable and auditable corpus without losing tables or access metadata.|kb,policies,runbooks,reference|Read Markdown frontmatter, kb:-prefixed HTML tags, the policy register and runbook restrictions. Preserve source path, content digest and skip reasons; PDFs/DOCX require metadata enrichment rather than guessing visibility.|Normalized Document records and ingestion reports; the second unchanged run reports zero changes and no unexpected skipped files.
Find chunk boundaries that retain complete troubleshooting instructions while respecting practical context size.|kb,runbooks|Track document ID, chunk ID, source, metadata, strategy, size and overlap. Long atomic steps may exceed a soft target size; document this tradeoff.|Fixed/recursive chunk inspections and boundary checks; chunks are derived artifacts, not new source truth.
Compare semantic and parent-child chunking on the same relevance questions rather than judging visual chunk quality.|kb,policies,rag|Keep child-to-parent mapping and document-level relevance IDs; record the semantic model and threshold and deduplicate repeated parents for scoring.|Four-strategy Recall@5/context-budget comparison; neural experiments require local model weights.
Choose and cache an embedding model without mixing incompatible vector spaces or hiding exact-code retrieval failures.|kb,rag|Record model identity/revision, vector dimension, normalization, content hash and cache provenance; a cached vector is valid only under the same embedding configuration.|Embedding cache and two-model comparison on a frozen reviewed question set; the default local reference remains lexical.
Store searchable knowledge in PostgreSQL and replace changed documents atomically so stale source chunks do not survive.|kb,policies,runbooks,reference,rag|Record source and chunk IDs, metadata JSON, vector dimension, source hash and index configuration. Generated SQL company records are separate from the derived rag_chunks index.|PostgreSQL chunk/vector rows, HNSW search timings and update/withdrawal checks; the database runtime gate is not a preflight result.
Retrieve only the OS, regional, audience and policy versions that the authenticated employee is permitted to see.|kb,policies,runbooks,employees|Distinguish audience=it-staff from application role=analyst/admin. Normalize OS display labels and join policy versions to register.csv before ranking.|Cross-OS, cross-role and superseded-policy retrieval checks; missing audience must fail closed.
Recover exact IT error-code and KB-ID matches while retaining semantic paraphrase coverage.|kb,rag|Keep exact identifiers and authorization predicates in both keyword and vector paths; record sparse rank, dense rank and fused rank separately.|Vector/keyword/hybrid scorecard and error-code retrieval evidence; lexical-only output is not a measured vector comparison.
Resolve follow-up questions in the right conversation and rerank only authorized candidates.|kb,rag,threads|Bind thread ownership to identity; preserve explicit error codes during rewriting and separate 30-candidate recall from five-result reranking quality.|Two-turn article IDs, reranking quality change and added latency; scripted rewriting is not a measured model rewrite.
Produce source-supported answers with checkable citations and an explicit abstention when evidence is insufficient.|kb,rag|Map every returned chunk_id to retrieved evidence; keep source OS/version scope and check claim support separately from citation membership.|Mac VPN cites KB-1017, Windows 809 cites KB-1018; versioned prompt and abstention evidence for live generation.
Measure retrieval, context selection and answer quality on a reviewed dataset with unanswerable coverage.|rag,kb,policies,runbooks|The supplied pool has 90 answerable drafts and ten authored unanswerables; preserve source_ticket and split, review labels, and never tune on the heldout subset.|Recall@5 plus context precision, faithfulness and relevance with configuration/provenance; unmeasured values stay null.
Expose authorized knowledge answers as a typed service and present the evidence in a chat interface.|kb,rag,threads,audit|Distinguish API request fields question/thread_id/stream from data labels. Identity comes from the server's bearer map, not a user-supplied requester field.|Authenticated API/UI responses, citation records and request IDs; completed-result SSE is not token streaming.
Establish safe enterprise-action semantics with a fixed workflow before allowing model-selected actions.|open,employees,devices,software_catalogue|Open tickets seed the mock REST service; employees bind requester ownership, the catalogue expresses approval requirements, and action risk tiers live in policy configuration.|A real mock-API ticket creation and risk inventory; seed records are not the post-action system-of-record state.
Translate requests into schema-valid and authorized tool calls and complete ticket drafts.|tickets,open,kb,employees,devices,service_incidents|TicketDraft fields are category, priority, summary, steps_tried, asset and assignment_group. Validate shape independently from requester authorization.|Typed tool/draft examples and schema failure/repair checks; live model tool-choice scoring needs configured model calls.
Diagnose a slow laptop with a bounded act/observe loop using actual device and outage evidence.|devices,service_incidents,kb,threads|Join assigned_to to the requester, apply incident region and unresolved status, and record tool name/arguments/observations as structured data.|Bounded trajectory and explicit success or escalation; the local loop fixture uses scripted decisions.
Resume a tool-using conversation after interruption while keeping checkpoints and side effects tied to the same employee.|threads,open,devices,service_incidents|Separate graph checkpoint identity from application thread ownership; preserve the frozen ticket draft and idempotency key across retry/restart.|Typed graph state and restart/resume evidence; SQLite and in-memory checks do not validate PostgreSQL checkpoint durability.
Plan onboarding as dependent HR/IT work instead of falsely completing steps after a failed prerequisite.|hr,role_profiles,role_profile_apps,software_catalogue|Bind candidate_id, hiring manager and explicit start_date; map role_profile to recommended software and laptop type. Preserve plan dependencies and completion evidence.|Persisted dependency plan and failed-prerequisite blocking; do not infer next Monday from the machine clock.
Retain useful employee context within a conversation budget and support deliberate deletion without using memory as authorization.|threads,memory,devices,open|Separate short-term thread state from long-term per-employee memory and system-of-record facts; document which fields have consent to persist.|Scoped recall, budget and deletion checks; deleting memory does not automatically erase old checkpoints or audit records.
Combine policy and procedural evidence, then catch unsupported draft instructions before returning an answer.|kb,policies,rag|Keep both document IDs, retrieved passages, policy version and draft claims; score support rather than a draft's confident tone.|Two-document grounded answer and bounded correction/abstention trace; model reflection quality remains a measured live gate.
Recover from transient ticket API faults without duplicate writes, unbounded retries or invented completion.|open,threads,audit|Persist the exact draft with its idempotency key before writing; distinguish an after-commit timeout from an unperformed write and record each observed outcome.|Fault-injection matrix, duplicate-count check and clean escalation; do not regenerate a key or alter arguments during retry.
Fulfil a restricted finance-access request only after matching approvals and a capacity check.|employees,software_catalogue,entitlements,requests,decisions,grants,audit|Join employee manager, FinSight APP-020, 60 seed seats/58 allocations, manager E1234 and data owner E1233; inspect decision records and post-action grants separately.|Pending-to-approved-to-fulfilled effect evidence; both named approvals are required and rejection is terminal.
Compare a supervisor and scoped specialists against the single-agent baseline on the same frozen tasks.|agent,kb,devices,open,audit|Keep task user, expected tools, forbidden effects and end state separate from the agent's input; capture actual trajectories and provider usage for comparison.|Quality/token/latency ADR on 15 reviewed tasks; role-specific allow-lists are enforced outside prompts.
Coordinate the onboarding subteam and hand unresolved work to an analyst with complete evidence.|hr,role_profiles,role_profile_apps,open,threads,onboarding_steps|Carry candidate/manager IDs, dependency state, evidence, steps tried and the suggested next action across handoffs without transferring arbitrary executable instructions.|IT work-item evidence and an analyst case summary; a summary alone is not evidence that provisioning ran.
Resist instructions hidden in source text and prevent forbidden effects even when an attack evades pattern detection.|redteam,kb,open,audit|Attack records carry id/text/expected/review_status; open ticket INC0020058 is a separate seeded injection. Audit outcomes and authoritative state matter more than refusal prose.|25-case effect-oriented red-team results; the supplied detector coverage report alone is not an attack-success measurement.
Move ticket actions behind a typed MCP boundary while preserving requester identity and retry semantics.|open,employees,audit,contracts|Inspect the create_ticket input schema, server-bound bearer identity, requester ownership and stable idempotency key; do not treat transport arguments as trusted roles.|SDK initialize/list/call transcript, ticket end state and preserved permission regressions.
Expose authorized document search, article resources and reusable prompts without allowing direct-resource visibility bypass.|kb,contracts|Map article IDs to kb://articles/{article_id}, preserve audience/version/region scope for tools and resources, and distinguish prompt templates from dataset content.|Search/resource/prompt client evidence; resource access must not reveal a restricted document that search would exclude.
Expose bounded enterprise database reads through MCP rather than arbitrary SQL, then compare HTTP service behaviour.|employees,devices,software_catalogue,entitlements,services,service_incidents|Use fixed query inputs and parameterized lookups with row limits; inspect key relationships and actual database grants. Current reference assets tools read CSV snapshots.|Three-server HTTP checks and a real SELECT-only PostgreSQL role denial test; CSV read-only behaviour is not a database-permission proof.
Enforce authenticated role and record ownership at each tool boundary, including denied calls.|employees,devices,open,audit,contracts|Map bearer tokens to employee IDs server-side, distinguish analyst/admin from named approvers, and audit tool name/outcome without source text or secrets.|Employee/analyst/admin permission matrix and cross-user denial evidence; supplied YAML inventories are not a replacement for enforcement tests.
Delegate HR onboarding to a separately owned agent and unblock IT work only after a verified completed task.|hr,role_profiles,role_profile_apps,onboarding_steps|Validate partner candidate/manager/date binding, HR completeness, A2A task status and returned artifact identity. C-2041 uses fixture date 2026-11-16.|Authenticated HR task artifact and persisted IT work items; incomplete/mismatched HR results must keep downstream steps blocked.
Choose direct calls, MCP or A2A by ownership/trust boundaries and benchmark equivalent service-status work.|services,service_incidents,contracts|Freeze the service/region query and payload before timing; preserve canonical input schemas, sample counts, warm-up policy and actual transport configuration.|Measured latency/code-complexity ADR and schema-drift check; a schema snapshot is not a latency benchmark.
Create a defensible agent benchmark from historical support cases with measurable end states and forbidden actions.|tickets,agent,open|The supplied 40 drafts start with six acceptance scenarios plus 34 ticket-derived cases; review each expected end state, reset policy and provenance before approving labels.|Reviewed task schema and isolated reset evidence; existing draft cases are not certified ground truth.
Calibrate an answer-quality judge against independent human labels rather than assuming the judge is authoritative.|rag,agent,human_labels|Keep question, sources, candidate answer, rubric/model version, human score and judge score separate; 30 independent human-labelled examples are required but not supplied.|Agreement/confusion/uncertainty report; never relabel generated or self-judged scores as human annotations.
Score actual task completion, tool arguments and action ordering instead of plausible success text.|agent,requests,decisions,grants,audit,onboarding_steps|Inspect persisted end state for each task; evaluate policy-before-request, approval-before-fulfilment and forbidden calls against the recorded trajectory.|Task success, tool accuracy and zero-violation report on reviewed tasks; missing measurements cannot pass a release threshold.
Block regressions by freezing data, prompts, policy and index identity and separating offline checks from live quality gates.|rag,agent,redteam,contracts,release|Track dataset split/review status and hashes alongside release model/index/prompt/policy versions. Seeded data checksums do not automatically cover evaluation files.|CI artifacts and intentional-regression rejection; included CI runs offline checks and still needs full-stack/nightly quality gates.
Observe request cost, latency, tool failures and feedback without leaking personal-data-shaped inputs into telemetry.|audit,threads,telemetry|Use request/trace/span correlation, safe role and operation names, provider token usage and an explicit price version. Process-local p95 samples are not durable fleet metrics.|Cross-service traces and dashboards with measured cost/latency; absent prices/usage remain unknown rather than zero.
Demonstrate the complete support lifecycle from a clean environment with reproducible data and observed release evidence.|tickets,kb,policies,runbooks,reference,employees,devices,software_catalogue,entitlements,service_incidents,hr,rag,agent,redteam,release|Verify manifest revision/checksums, fixture identities and absolute dates, reviewed evaluation versions and clean post-action state; preserve all six acceptance scenarios.|Six-request demonstration, evaluation reports, security/deployment checks and readiness evidence; local references do not certify an unrun production release.
""".strip()


def read_jsonl(path):
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return "string"


def field_metadata(rows, descriptions):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    return [
        {
            "field": key,
            "types": sorted({kind(row[key]) for row in rows if key in row}),
            "missing_rows": sum(key not in row for row in rows),
            "null_rows": sum(row.get(key, "__absent__") is None for row in rows),
            "meaning": descriptions.get(
                key, "See the source schema for this field's table-specific meaning."
            ),
        }
        for key in keys
    ]


def snapshot_hashes():
    paths = [
        p
        for base in (ROOT / "data", ROOT / "evals")
        for p in base.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    ]
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
    }


def collect():
    assets = {}

    def add(key, label, paths, origin, fields=None, rows=None, notes=""):
        files = [ROOT / path for path in paths]
        assets[key] = {
            "label": label,
            "paths": paths,
            "origin": origin,
            "file_count": len(files),
            "record_count": len(rows) if rows is not None else None,
            "fields": fields or [],
            "notes": notes,
            "sha256": {
                str(p.relative_to(ROOT).as_posix()): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in files
                if p.is_file()
            },
        }

    ticket_rows = read_jsonl(ROOT / "data/tickets/historical_tickets.jsonl")
    add(
        "tickets",
        "Historical support tickets",
        ["data/tickets/historical_tickets.jsonl"],
        "datagen/tickets.py: TicketFactory.historical; topic wording from datagen/content/ and seeded population context.",
        field_metadata(ticket_rows, TICKET_FIELDS),
        ticket_rows,
        "JSONL: one object per line. Labels and resolutions are generated, not independently observed real-world outcomes. Tickets cover May 2025 to November 2026 in this fixture.",
    )
    opened = json.loads((ROOT / "data/tickets/open_tickets.json").read_text())
    add(
        "open",
        "Open ticket seed",
        ["data/tickets/open_tickets.json"],
        "datagen/tickets.py: TicketFactory.open_tickets; consumed by services/ticketing_mock/.",
        field_metadata(opened, TICKET_FIELDS),
        opened,
        "JSON array seed, not the live mutable API database. One seeded request contains an injection attempt.",
    )
    kbpaths = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "data/kb").glob("*")
        if p.suffix in {".md", ".html"}
    )
    add(
        "kb",
        "Knowledge-base corpus",
        kbpaths,
        "Authored Topic/TicketSpec templates in datagen/content/ expanded by datagen/kb.py per OS or region.",
        [
            {
                "field": name,
                "types": ["array" if name == "error_codes" else "string"],
                "meaning": meaning,
            }
            for name, meaning in KB_FIELDS.items()
        ],
        notes='Markdown YAML frontmatter and HTML <meta name="kb:..."> encode the same metadata. Parser normalization currently converts metadata values to strings; distinguish that representation from source-level arrays/nulls.',
    )
    policy_fields = {
        "id": "Policy ID, e.g. POL-003; joins KB related_policy.",
        "title": "Policy title.",
        "version": "Document version string.",
        "effective_date": "Date this version starts applying.",
        "status": "current or superseded; the register is authoritative for this distinction.",
        "superseded_by": "Successor version, blank for current records.",
        "owner": "Accountable synthetic policy owner.",
        "file": "Exact PDF filename in data/policies/.",
    }
    register_path = ROOT / "data/policies/register.csv"
    with register_path.open(encoding="utf-8", newline="") as stream:
        register = list(csv.DictReader(stream))
    add(
        "policies",
        "Policy PDFs and version register",
        [
            "data/policies/register.csv",
            *sorted(p.relative_to(ROOT).as_posix() for p in register_path.parent.glob("*.pdf")),
        ],
        "datagen/content/policies.py and datagen/docs.py; old versions are explicitly authored, not scraped.",
        field_metadata(register, policy_fields),
        register,
        "PDF text alone may not identify a superseded version. Missing PDF audience metadata must not silently make the document visible to employees.",
    )
    add(
        "runbooks",
        "IT-only runbooks",
        sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "data/runbooks").glob("*.docx")),
        "datagen/content/runbooks.py and datagen/docs.py.",
        [
            {"field": k, "types": ["source document field"], "meaning": v}
            for k, v in {
                "id/title/version/effective": "Runbook identity and version from authored content.",
                "group/risk/approval": "Accountable support group, read/write risk tier and approver requirement.",
                "prerequisites/steps/verification/rollback": "Procedure inputs, ordered actions, evidence and recovery instructions.",
                "audience": "All runbooks are IT-only by source contract; attach enforced it-staff metadata during ingestion.",
            }.items()
        ],
        notes="DOCX files contain paragraphs and tables. They are not intended for employee retrieval; current loader does not automatically enrich all metadata.",
    )
    add(
        "reference",
        "SLA, catalogue and glossary references",
        sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "data/reference").glob("*")),
        "Authored catalogue/reference definitions rendered by datagen/docs.py.",
        notes="Includes sla_matrix.pdf, software_catalogue.csv, software_catalogue.html and glossary.md. Preserve table rows/columns and treat charges/SLA values as fictional training policy.",
    )
    for path in sorted((ROOT / "data/db/csv").glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        add(
            path.stem,
            f"Company table: {path.stem}",
            [path.relative_to(ROOT).as_posix()],
            "Seeded population in datagen/people.py; catalogue definitions in datagen/content/catalogue.py; SQL/CSV export in datagen/dbsql.py.",
            field_metadata(rows, DB_FIELDS),
            rows,
            "CSV values are text, including booleans and numbers. Empty cells represent missing or non-applicable values; use data/db/01_schema.sql for SQL types and keys. The same records are represented in data/db/02_seed.sql.",
        )
    hr = json.loads((ROOT / "data/hr/pending_joiners.json").read_text())
    add(
        "hr",
        "Pending HR joiners",
        ["data/hr/pending_joiners.json"],
        "Fixed synthetic partner fixtures in datagen/people.py, exported by datagen/__main__.py.",
        field_metadata(hr, HR_FIELDS),
        hr,
        "Nested JSON array. Some records are intentionally incomplete. A completed HR artifact verifies existing synthetic checklist data; it does not perform real HR work.",
    )
    for key, path, descriptions, note in [
        (
            "rag",
            "evals/rag_golden.jsonl",
            RAG_FIELDS,
            "First 90 distinct linked KB IDs encountered in historical ticket order yield 90 provisional question/answer pairs; ten authored unanswerables are appended. Distinct IDs are not a guarantee of independent template families. Current evaluator ignores split and reports on the supplied pool, so its score is not a heldout-only result.",
        ),
        (
            "agent",
            "evals/agent_golden.jsonl",
            AGENT_FIELDS,
            "Six authored acceptance scenarios plus the first 34 selected historical tickets. Expected end states need manual review; the dataset is not a validated agent benchmark yet.",
        ),
        (
            "redteam",
            "evals/redteam/attacks.jsonl",
            {
                "id": "Attack case ID.",
                "text": "Authored malicious/forbidden scenario text.",
                "expected": "Desired absence of forbidden effects, requiring state-based checks.",
                "review_status": "draft until reviewed; not evidence the system resists every attack.",
            },
            "25 authored adversarial scenarios, not naturally collected attack traffic. Some require direct tool/concurrency fixtures rather than simply passing text to a detector.",
        ),
    ]:
        rows = read_jsonl(ROOT / path)
        add(
            key,
            {
                "rag": "Draft RAG evaluation questions",
                "agent": "Draft agent task set",
                "redteam": "Draft adversarial scenario set",
            }[key],
            [path],
            "scripts/prepare_evals.py; separate from the datagen seed-pack generator.",
            field_metadata(rows, descriptions),
            rows,
            note,
        )
        assets[key]["review_status_counts"] = dict(
            Counter(row.get("review_status", "missing") for row in rows)
        )
    add(
        "personas",
        "Fixed acceptance identities and source manifest",
        ["data/personas.md", "data/manifest.json"],
        "datagen/people.py: PERSONAS and datagen/__main__.py: build_manifest/personas_markdown.",
        notes="Eight fixed personas make acceptance checks reproducible. manifest.json records company/as_of/seed/counts and byte length/SHA-256 for seed files; it does not cover later evals or runtime outputs.",
    )
    for key, description in RUNTIME_FIELDS.items():
        assets[key] = {
            "label": f"Runtime records: {key}",
            "paths": [],
            "origin": "src/copilot/tools/runtime.py; created by actual local workflow interactions, not pre-collected training records.",
            "record_count": None,
            "file_count": None,
            "fields": [],
            "notes": description
            + " Stored in the configured SQLite state database, normally .work/runtime.sqlite3; session experiments may use separate databases. No runtime database was read to author this guide.",
        }
    assets["contracts"] = {
        "label": "MCP tool schema snapshot",
        "paths": ["tests/contracts/mcp_schemas.json"],
        "origin": "scripts/snapshot_contracts.py introspects registered tool inputs.",
        "record_count": None,
        "fields": [],
        "notes": "Schema metadata, not employee training examples. Compare snapshots in CI and review breaking changes; never auto-approve a changed snapshot.",
    }
    assets["release"] = {
        "label": "Release identity and thresholds",
        "paths": ["release/manifest.yaml"],
        "origin": "Authored release configuration.",
        "record_count": None,
        "fields": [],
        "notes": "Records model/prompt/index/policy and target metrics. Unconfigured revisions and null measurements do not certify readiness.",
    }
    assets["human_labels"] = {
        "label": "Required human calibration examples (not supplied)",
        "paths": [],
        "origin": "Instructor/learner annotation required in session 36.",
        "record_count": None,
        "fields": [],
        "notes": "Expected schema: example_id, question, sources, candidate_answer, rubric_version, human_score, annotator/review metadata. Store judge_score and judge_model/revision separately. This describes the required future artifact, not an existing file or a completed set of 30 labels.",
    }
    assets["telemetry"] = {
        "label": "Operational observations",
        "paths": ["src/copilot/telemetry.py"],
        "origin": "Emitted while running the API/tools/model; optional OTLP export and bounded in-memory samples.",
        "record_count": None,
        "fields": [],
        "notes": "Current measurement rows: operation, seconds, error. Dashboard fields: sample_count, request_p95_s, operation_error_rate, cost_per_resolved_request and cost_status. Provider tokens and trace/span IDs are operational metadata, not training labels. No durable collector dataset is bundled.",
    }
    return assets, ticket_rows


def render_asset(key, asset, prefix="../../"):
    count = (
        f"{asset['record_count']:,} records"
        if asset.get("record_count") is not None
        else (
            f"{asset.get('file_count')} files"
            if asset.get("file_count") is not None
            else "runtime/configuration artifact; no fixed record count"
        )
    )
    lines = [f"### {asset['label']}", "", f"**Size:** {count}. **Origin:** {asset['origin']}", ""]
    paths = asset["paths"]
    if key == "kb":
        paths = ["data/kb/index.csv", "data/kb/KB-1001.md", "data/kb/KB-1017.html"]
    elif key == "policies":
        paths = ["data/policies/register.csv", "data/policies/POL-003_v4.0.pdf"]
    elif key == "runbooks":
        paths = ["data/runbooks/RB-001.docx"]
    for path in paths:
        lines.append(f"- [{path}]({prefix}{path})")
    if paths:
        lines.append("")
    lines.extend([asset["notes"], ""])
    if asset.get("review_status_counts"):
        lines.extend(
            [
                "**Observed review status:** "
                + ", ".join(
                    f"{status}: {count}" for status, count in asset["review_status_counts"].items()
                )
                + ".",
                "",
            ]
        )
    if asset["fields"]:
        lines.extend(["| Field | Representation / missingness | Meaning |", "| --- | --- | --- |"])
        for field in asset["fields"]:
            representation = "/".join(field["types"])
            if "missing_rows" in field:
                representation += f"; absent {field['missing_rows']}, null {field['null_rows']}"
            lines.append(f"| `{field['field']}` | {representation} | {field['meaning']} |")
        lines.append("")
    return "\n".join(lines)


def build():
    protected_before = snapshot_hashes()
    sessions = json.loads((ROOT / "sessions/manifest.json").read_text())
    lessons = [line.split("|") for line in LESSONS.splitlines()]
    assert len(sessions) == len(lessons) == 40
    assets, tickets = collect()
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    metadata = {
        "company": manifest["company"],
        "synthetic": True,
        "snapshot_as_of": manifest["as_of"],
        "generation_seed": manifest["seed"],
        "assets": assets,
        "historical_ticket_category_counts": dict(Counter(row["category"] for row in tickets)),
        "historical_ticket_priority_counts": dict(Counter(row["priority"] for row in tickets)),
        "protected_file_hashes": protected_before,
    }
    docs = ROOT / "docs"
    (docs / "dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    dictionary = [
        "# Dataset dictionary",
        "",
        "This describes the inspected synthetic seed, draft evaluation records and separate runtime artifacts. Types/absent/null counts are observed in the existing files. CSV types are strings until parsed. It does not assert that draft labels have been reviewed.",
        "",
        "See [provenance](DATASET_PROVENANCE.md) for the generation pipeline and limitations.",
        "",
    ]
    dictionary.extend(render_asset(key, asset, "../") for key, asset in assets.items())
    (docs / "DATA_DICTIONARY.md").write_text("\n".join(dictionary), encoding="utf-8")
    counts = manifest["counts"]
    provenance = f"""# How this project's datasets are produced

## Origin and collection method

The company, people, incidents, documents, software charges and ticket histories are **synthetic**. There is no connected live IT system, scraping pipeline, downloaded public ticket benchmark or collection of real employee records behind this data pack. Python code combines authored support-topic templates with a seeded fictional company population. The data generator itself does not call an LLM API.

- Company: **{manifest["company"]}**.
- Snapshot date: **{manifest["as_of"]}**; this is a fixture date, not today's live data.
- Generation seed: **{manifest["seed"]}**.
- Historical tickets: **{counts["historical_tickets"]:,}**; open-ticket seed: **{counts["open_tickets"]}**.
- KB: **{counts["kb_articles"]}** articles, including **{counts["kb_articles_markdown"]} Markdown**, **{counts["kb_articles_html"]} HTML** and **{counts["kb_articles_it_staff_only"]} IT-only articles**.
- Policies: **{counts["policies_current"]} current + {counts["policies_superseded"]} superseded PDFs**; runbooks: **{counts["runbooks"]} DOCX files**.
- Company sample: **{counts["employees"]} employees**, **{counts["devices"]} devices**, **{counts["entitlements"]} entitlements**, **{counts["service_incidents"]} incident records** and **{counts["pending_joiners"]} pending joiners**.

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

From `D:\\AI-Engineering\\servicedesk-copilot` in PowerShell:

```powershell
.\\.venv\\Scripts\\copilot.exe tickets-stats
Get-Content data\\manifest.json -TotalCount 28
Get-Content data\\tickets\\historical_tickets.jsonl -TotalCount 1
Get-Content data\\db\\csv\\employees.csv -TotalCount 3
Get-Content evals\\rag_golden.jsonl -TotalCount 1
```

## Reproduce into an isolated output directory

Learners do not need to regenerate the supplied corpus. If the instructor wants a separate reproduction, install the renderer extra and choose a fresh output path:

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -e ".[datagen]"
.\\.venv\\Scripts\\python.exe -m datagen --seed 42 --tickets 5000 --out .work\\reproduced-data
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
"""
    (docs / "DATASET_PROVENANCE.md").write_text(provenance, encoding="utf-8")
    index_rows = [
        "# Session problem statements and dataset guides",
        "",
        "Each guide distinguishes source records, labels, metadata and runtime outputs. For the common production method see [dataset provenance](../docs/DATASET_PROVENANCE.md).",
        "",
        "| Session | Guide |",
        "| --- | --- |",
    ]
    for session, lesson in zip(sessions, lessons, strict=True):
        number = session["session"]
        problem, selected, focus, outputs = lesson
        keys = selected.split(",")
        assert all(key in assets for key in keys)
        folder = ROOT / "sessions" / session["folder"]
        sections = [
            f"# Session {number:02d}: problem statement and dataset metadata",
            "",
            f"## {session['title']}",
            "",
            "## Problem statement",
            "",
            problem,
            "",
            "This is one increment of the same IT Service Desk Copilot. Keep the previous session's passing behaviour and record new evidence rather than replacing the larger project.",
            "",
            "## How the data is obtained",
            "",
            f"All seed records come from the locally generated Larkhaven synthetic pack (snapshot {manifest['as_of']}, seed {manifest['seed']}). Evaluation examples are separately derived/authored drafts. Runtime state is created by executing workflows; it is not pre-collected training data. This session uses the following specific sources, not a new external dataset.",
            "",
            "Read [the complete generation lineage](../../docs/DATASET_PROVENANCE.md) and [the shared field dictionary](../../docs/DATA_DICTIONARY.md) for provenance, relationships and observed missingness.",
            "",
            "## Input datasets and field metadata",
            "",
        ]
        sections.extend(render_asset(key, assets[key]) for key in keys)
        sections.extend(
            [
                "## How this session uses the data",
                "",
                focus,
                "",
                "## Outputs and evidence",
                "",
                outputs,
                "",
                f"The curriculum exit criterion is: {session['evidence']}. Save observed results in this session's `evidence.md`; do not treat a requested target value as an observed score.",
                "",
                "## Before running",
                "",
                "1. Inspect the input paths and field names above. Distinguish fields available at request time from outcome labels.",
                "2. Preserve seed records and evaluation labels. Do not regenerate the shared pack to perform an ordinary session exercise.",
                "3. Identify the join keys, authorization scope, missing-value convention and version/date that affect this task.",
                "4. Run the [session steps](STEPS_TO_FOLLOW.md) and compare outputs with the problem statement.",
                "5. Record split/review status, source/model configuration, actual measurements and any unperformed integration check.",
                "",
                "## Reference implementation and scope",
                "",
            ]
        )
        for source in session["sources"]:
            sections.append(f"- [{source}](../../{source})")
        sections.extend(
            [
                "",
                "The adjacent `reference.py` currently launches shared application code. Some sessions execute offline fixtures or preflights; that does not establish that the full live-model, database or deployment requirement has run. Consult [implementation status](../../docs/IMPLEMENTATION_STATUS.md).",
                "",
            ]
        )
        (folder / NAME).write_text("\n".join(sections), encoding="utf-8")
        readme = folder / "README.md"
        text = readme.read_text(encoding="utf-8")
        link = f"[Problem statement and dataset metadata]({NAME})"
        if link not in text:
            first, rest = text.split("\n", 1)
            readme.write_text(first + "\n\n" + link + "\n" + rest, encoding="utf-8")
        index_rows.append(f"| {number:02d} | [{session['title']}]({session['folder']}/{NAME}) |")
    (ROOT / "sessions/DATASET_GUIDES.md").write_text("\n".join(index_rows) + "\n", encoding="utf-8")
    main_readme = ROOT / "README.md"
    text = main_readme.read_text(encoding="utf-8")
    marker = "- [Dataset provenance and generation](docs/DATASET_PROVENANCE.md)"
    if marker not in text:
        text = text.replace(
            "## Start here\n",
            "## Start here\n\n"
            + marker
            + "\n- [Session problem statements and dataset metadata](sessions/DATASET_GUIDES.md)\n",
        )
        main_readme.write_text(text, encoding="utf-8")
    # Keep the documentation requirement and regeneration flow durable.
    checker = ROOT / "scripts/check_course.py"
    text = checker.read_text(encoding="utf-8")
    if '"PROBLEM_STATEMENT_AND_DATASET.md"' not in text:
        text = text.replace('"evidence.md"', '"evidence.md", "PROBLEM_STATEMENT_AND_DATASET.md"')
        checker.write_text(text, encoding="utf-8")
    builder = ROOT / "scripts/build_course.py"
    text = builder.read_text(encoding="utf-8")
    if "from build_session_dataset_guides import build as build_dataset_guides" not in text:
        text = text.replace(
            '    print(f"Authored {len(manifest)} session folders")',
            '    from build_session_dataset_guides import build as build_dataset_guides\n\n    build_dataset_guides()\n    print(f"Authored {len(manifest)} session folders")',
        )
        builder.write_text(text, encoding="utf-8")
    assert protected_before == snapshot_hashes(), (
        "Documentation generation changed protected seed/evaluation files"
    )
    # Verify count, title, paths, dictionaries and links; fail before reporting success.
    assert len(list((ROOT / "sessions").glob(f"[0-9][0-9]-*/{NAME}"))) == 40
    for path in [
        docs / "DATASET_PROVENANCE.md",
        docs / "DATA_DICTIONARY.md",
        ROOT / "sessions/DATASET_GUIDES.md",
        *list((ROOT / "sessions").glob(f"[0-9][0-9]-*/{NAME}")),
    ]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if not target.startswith(("http:", "https:", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (
                    f"Broken link in {path}: {target}"
                )
    print(
        f"Wrote 40 session-specific guides, shared provenance/dictionary and metadata snapshot; {len(protected_before)} seed/evaluation files unchanged"
    )


if __name__ == "__main__":
    build()
