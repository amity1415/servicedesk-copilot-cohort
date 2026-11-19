"""Deterministic workflow baseline, persisted across requests.

This deliberately exposes its routing rules. Live model and LangGraph experiments
compare against this baseline rather than attributing its behaviour to an LLM.
"""

from __future__ import annotations

import re

from copilot.guardrails.checks import suspicious
from copilot.rag.pipeline import Retriever
from copilot.rag.query import rewrite
from copilot.telemetry import traced
from copilot.tools.runtime import Runtime
from copilot.tools.ticketing import TicketDraft, TicketingClient


class Engine:
    def __init__(
        self,
        runtime: Runtime,
        retriever: Retriever,
        ticketing: TicketingClient | None = None,
        onboard_handler=None,
    ):
        self.runtime, self.retriever, self.ticketing = runtime, retriever, ticketing
        self.onboard_handler = onboard_handler

    @traced("agent.run")
    def run(self, actor: str, query: str, thread: str = "demo") -> dict:
        employee = self.runtime.employee(actor)
        state = self.runtime.load_thread(actor, thread)
        if suspicious(query):
            self.runtime.audit(actor, "injection", "blocked")
            return {
                "answer": (
                    "I cannot change privileges or follow instructions embedded in source text."
                ),
                "status": "blocked",
                "steps": [],
            }
        steps = []
        lower = query.lower()
        if "access" in lower and ("finance" in lower or "finsight" in lower):
            app = next(
                a for a in self.runtime.rows("software_catalogue") if a["name"] == "FinSight"
            )
            steps.extend(["check_policy", "check_licences", "request_access"])
            request = self.runtime.request_access(
                actor, app["app_id"], f"{actor}:{thread}:FinSight"
            )
            result = {
                "answer": "Access request recorded; waiting for the named manager's decision.",
                "status": request["status"],
                "request": request,
                "steps": steps,
            }
        elif "joiner" in lower:
            result = {
                "answer": (
                    "Confirm the candidate ID and absolute start date before executing onboarding."
                ),
                "status": "needs_details",
                "plan": [
                    {"id": "hr", "owner": "hr_partner", "depends_on": []},
                    {"id": "account", "owner": "onboarding", "depends_on": ["hr"]},
                    {"id": "laptop", "owner": "onboarding", "depends_on": ["account"]},
                    {"id": "licences", "owner": "onboarding", "depends_on": ["account"]},
                    {"id": "access", "owner": "onboarding", "depends_on": ["licences"]},
                ],
                "steps": ["plan"],
            }
            candidate = re.search(r"\bC-\d{4}\b", query)
            start_date = re.search(r"\b\d{4}-\d{2}-\d{2}\b", query)
            if candidate and start_date and self.onboard_handler:
                completed = self.onboard_handler(candidate.group(), start_date.group())
                result.update(
                    answer="HR verification and simulated IT onboarding completed.",
                    status=completed["status"],
                    onboarding=completed,
                )
        elif "slow" in lower or state.get("diagnostics"):
            assets = self.runtime.assets(actor, actor)
            incidents = [
                r
                for r in self.runtime.rows("service_incidents")
                if r["region"] in {employee["region"], "global"} and not r["resolved_at"]
            ]
            steps.extend(["get_assets", "check_service_status", "search_kb"])
            answer = self.retriever.answer(
                "laptop slow performance",
                role=employee["role"],
                os_name=assets[0]["os"] if assets else None,
                region=employee["region"],
            )
            result = {
                **answer,
                "assets": assets,
                "incidents": incidents,
                "steps": steps,
                "status": "suggested_fixes",
            }
            state["diagnostics"] = True
            if any(t in lower for t in ("still", "failed", "raise", "create ticket")):
                if self.ticketing:
                    draft = TicketDraft(
                        category="Hardware & Devices",
                        priority="P3",
                        summary="Laptop remains slow after troubleshooting",
                        steps_tried=[state.get("last_query", "KB troubleshooting"), query],
                        asset=assets[0]["asset_tag"] if assets else "unknown",
                        assignment_group="Workplace Engineering",
                    )
                    if "ticket_draft" in state:
                        draft = TicketDraft.model_validate(state["ticket_draft"])
                    else:
                        state["ticket_draft"] = draft.model_dump()
                        self.runtime.save_thread(actor, thread, state)
                    result["ticket"] = self.ticketing.create(actor, draft, f"{actor}:{thread}:slow")
                    result["status"] = "ticket_created"
                    steps.append("create_ticket")
                else:
                    result.update(
                        status="escalated",
                        answer="Ticketing is unavailable; hand this case to an analyst.",
                    )
        else:
            assets = self.runtime.assets(actor, actor)
            retrieval_query = rewrite(query, state.get("last_query", ""))
            scope_query = lower if "mac" in lower or "windows" in lower else retrieval_query.lower()
            os_name = (
                "macos"
                if "mac" in scope_query
                else "windows"
                if "windows" in scope_query
                else (assets[0]["os"] if assets else None)
            )
            result = self.retriever.answer(
                retrieval_query,
                role=employee["role"],
                os_name=os_name,
                region=employee["region"],
            )
            result.update(status="answered", steps=["search_kb"])
        state.update(last_query=query, last_result=result)
        self.runtime.save_thread(actor, thread, state)
        return {**result, "mode": "deterministic-offline-workflow"}
