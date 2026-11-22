"""Run the slow-laptop investigation with the Session 18 read tools."""

from __future__ import annotations

from functools import partial

from copilot.agents.react import DIAGNOSTIC_TOOLS, run_loop
from copilot.tools.service_desk import ServiceDeskTools

SLOW_REQUEST = "My laptop is slow"
SEARCH_QUERY = "laptop slow performance"
DEVICE_FIELDS = ("asset_tag", "device_type", "os", "pending_updates")
INCIDENT_FIELDS = ("incident_id", "service", "region", "status")


def local_decision(query: str, events: list[dict]) -> dict:
    observed = {
        event["tool"]: event["observation"] for event in events if event["outcome"] == "observed"
    }
    for tool in DIAGNOSTIC_TOOLS[:2]:
        if tool not in observed:
            return {"tool": tool}
    if "search_kb" in observed:
        return {"answer": observed["search_kb"]["excerpt"]}

    laptop = next(
        (row for row in observed["get_assets"]["devices"] if row["device_type"] == "laptop"), None
    )
    arguments = {"query": SEARCH_QUERY}
    if laptop and laptop["os"]:
        arguments["os_name"] = laptop["os"]
    return {"tool": "search_kb", "arguments": arguments}


def observe_diagnostic(
    tools: ServiceDeskTools, actor: str, name: str, arguments: dict
) -> tuple[dict, dict]:
    result = tools.execute(actor, name, arguments)
    if name == "get_assets":
        observation = {
            "devices": [{field: row[field] for field in DEVICE_FIELDS} for row in result["rows"]]
        }
    elif name == "check_service_status":
        result = {"rows": [row for row in result["rows"] if not row["resolved_at"]]}
        observation = {
            "active_incidents": [
                {field: row[field] for field in INCIDENT_FIELDS} for row in result["rows"]
            ]
        }
    else:
        observation = {
            "excerpt": result["answer"][:3200],
            "document_ids": sorted({citation["document_id"] for citation in result["citations"]}),
        }
    return result, observation


def summarize_diagnostic(outcome: dict, observed: dict, *, decision_source: str = "local") -> dict:
    article = observed.get("search_kb", {})
    citations = article.get("citations", [])
    status = outcome["status"]
    if status == "answered":
        if observed.keys() >= set(DIAGNOSTIC_TOOLS) and citations and not article.get("abstained"):
            status = "suggested_fixes"
        else:
            status = "escalated"
            outcome = {**outcome, "reason": "missing_diagnostic_evidence"}
    if status == "suggested_fixes":
        answer = article["answer"] if decision_source == "local" else outcome["answer"]
    else:
        answer = "The laptop diagnosis needs review by a service desk analyst."
    return {
        **outcome,
        "status": status,
        "answer": answer,
        "mode": article.get("mode", "diagnostic-loop"),
        "decision_source": decision_source,
        "citations": citations,
        "steps": [event["tool"] for event in outcome["events"]],
        "assets": observed.get("get_assets", {}).get("rows", []),
        "incidents": observed.get("check_service_status", {}).get("rows", []),
    }


def run_diagnostics(
    tools: ServiceDeskTools, actor: str, query: str, *, decide=None, max_steps: int = 6
) -> dict:
    observed = {}

    def observe(name, **arguments):
        result, observation = observe_diagnostic(tools, actor, name, arguments)
        observed[name] = result
        return observation

    bound = {name: partial(observe, name) for name in DIAGNOSTIC_TOOLS}
    outcome = run_loop(decide or local_decision, bound, query, max_steps=max_steps)
    return summarize_diagnostic(
        outcome, observed, decision_source="configured" if decide else "local"
    )
