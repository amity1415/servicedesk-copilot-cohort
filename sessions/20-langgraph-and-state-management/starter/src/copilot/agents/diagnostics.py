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


def run_diagnostics(
    tools: ServiceDeskTools, actor: str, query: str, *, decide=None, max_steps: int = 6
) -> dict:
    observed = {}

    def observe(name, **arguments):
        result = tools.execute(actor, name, arguments)
        if name == "check_service_status":
            result = {"rows": [row for row in result["rows"] if not row["resolved_at"]]}
        observed[name] = result
        if name == "get_assets":
            return {
                "devices": [
                    {field: row[field] for field in DEVICE_FIELDS} for row in result["rows"]
                ]
            }
        if name == "check_service_status":
            return {
                "active_incidents": [
                    {field: row[field] for field in INCIDENT_FIELDS} for row in result["rows"]
                ]
            }
        return {
            "excerpt": result["answer"][:3200],
            "document_ids": sorted({citation["document_id"] for citation in result["citations"]}),
        }

    bound = {name: partial(observe, name) for name in DIAGNOSTIC_TOOLS}
    outcome = run_loop(decide or local_decision, bound, query, max_steps=max_steps)
    article = observed.get("search_kb", {})
    citations = article.get("citations", [])
    status = outcome["status"]
    if status == "answered":
        if observed.keys() >= set(DIAGNOSTIC_TOOLS) and citations and not article.get("abstained"):
            status = "suggested_fixes"
        else:
            status = "escalated"
            outcome["reason"] = "missing_diagnostic_evidence"
    if status == "suggested_fixes":
        answer = outcome["answer"] if decide else article["answer"]
    else:
        answer = "The laptop diagnosis needs review by a service desk analyst."
    return {
        **outcome,
        "status": status,
        "answer": answer,
        "mode": article.get("mode", "diagnostic-loop"),
        "decision_source": "configured" if decide else "local",
        "citations": citations,
        "steps": [event["tool"] for event in outcome["events"]],
        "assets": observed.get("get_assets", {}).get("rows", []),
        "incidents": observed.get("check_service_status", {}).get("rows", []),
    }
