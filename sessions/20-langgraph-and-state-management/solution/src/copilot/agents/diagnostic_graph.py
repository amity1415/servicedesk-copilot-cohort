"""LangGraph diagnosis and explicit ticket escalation over the same typed tools."""

from __future__ import annotations

from time import monotonic
from typing import Literal, TypedDict

import httpx

from copilot.agents.diagnostics import local_decision, observe_diagnostic, summarize_diagnostic
from copilot.agents.react import DIAGNOSTIC_TOOLS, decision_contract
from copilot.tools.service_desk import ServiceDeskTools, TicketingUnavailable
from copilot.tools.ticketing import TicketDraft

MAX_DECISIONS = 6
DEADLINE_SECONDS = 30


class DiagnosticState(TypedDict, total=False):
    actor: str
    thread_id: str
    intent: Literal["diagnose", "create_ticket"]
    question: str
    decisions: int
    action: dict
    events: list[dict]
    observations: dict[str, dict]
    result: dict
    failure_report: str
    ticket_draft: dict
    ticket_key: str


def build_diagnostic_graph(tools: ServiceDeskTools, checkpointer, *, interrupt_after_tool=False):
    from langgraph.graph import END, START, StateGraph

    deadline = monotonic() + DEADLINE_SECONDS

    def decide(state: DiagnosticState):
        events = state["events"]
        if events and events[-1]["outcome"] == "denied":
            return {"action": {"stop": "tool_denied"}}
        if monotonic() >= deadline:
            return {"action": {"stop": "deadline"}}
        if state["decisions"] >= MAX_DECISIONS:
            return {"action": {"stop": "step_limit"}}
        action = decision_contract.validate_python(local_decision(state["question"], events))
        return {"action": action.model_dump(), "decisions": state["decisions"] + 1}

    def choose_node(state: DiagnosticState) -> Literal["tools", "finish"]:
        return "tools" if "tool" in state["action"] else "finish"

    def use_tool(state: DiagnosticState):
        action = state["action"]
        name, args = action["tool"], action["arguments"]
        if monotonic() >= deadline:
            return {}
        event = {"step": len(state["events"]), "tool": name, "arguments": args}
        observations = state["observations"].copy()
        try:
            if name not in DIAGNOSTIC_TOOLS:
                raise PermissionError("tool is outside the diagnostic allow-list")
            observations[name], observation = observe_diagnostic(tools, state["actor"], name, args)
            event.update(outcome="observed", observation=observation)
        except PermissionError:
            event["outcome"] = "denied"
        except (ValueError, TimeoutError, httpx.HTTPError) as exc:
            event.update(outcome="failed", error={"type": type(exc).__name__})
        return {"events": [*state["events"], event], "observations": observations}

    def finish(state: DiagnosticState):
        action = state["action"]
        outcome = {"events": state["events"]}
        if "stop" in action:
            reason = action["stop"]
            outcome.update(
                status="blocked" if reason == "tool_denied" else "escalated", reason=reason
            )
        else:
            outcome.update(status="answered", answer=action["answer"])
        return {"result": summarize_diagnostic(outcome, state["observations"])}

    def prepare_ticket(state: DiagnosticState):
        if "ticket_draft" in state:
            return {}
        laptop = next(
            (row for row in state["result"]["assets"] if row["device_type"] == "laptop"), None
        )
        draft = TicketDraft(
            category="Hardware & Devices",
            priority="P3",
            summary="Laptop remains slow after troubleshooting",
            steps_tried=[state["question"], state["failure_report"]],
            asset=laptop["asset_tag"] if laptop else "unknown",
            assignment_group="Workplace Engineering",
        )
        return {
            "ticket_draft": draft.model_dump(),
            "ticket_key": f"graph-laptop:{state['thread_id']}",
        }

    def open_ticket(state: DiagnosticState):
        result = state["result"].copy()
        try:
            ticket = tools.execute(
                state["actor"],
                "create_ticket",
                {"draft": state["ticket_draft"]},
                idempotency_key=state["ticket_key"],
            )
        except PermissionError:
            result.update(
                status="blocked", answer="The ticket request is outside your current permissions."
            )
        except (httpx.HTTPError, TicketingUnavailable):
            result.update(
                status="ticket_unavailable",
                answer="Ticketing is unavailable. Retry this request in the same thread.",
            )
        else:
            result.update(
                status="ticket_created",
                ticket=ticket,
                answer=f"Ticket {ticket['ticket_id']} was opened for the slow laptop.",
                steps=[*result["steps"], "create_ticket"],
            )
        return {"result": result}

    def first_node(state: DiagnosticState) -> Literal["decision", "prepare_ticket"]:
        return "prepare_ticket" if state["intent"] == "create_ticket" else "decision"

    graph = StateGraph(DiagnosticState)
    graph.add_node("decision", decide)
    graph.add_node("tools", use_tool)
    graph.add_node("finish", finish)
    graph.add_node("prepare_ticket", prepare_ticket)
    graph.add_node("ticket", open_ticket)
    graph.add_conditional_edges(START, first_node)
    graph.add_conditional_edges("decision", choose_node)
    graph.add_edge("tools", "decision")
    graph.add_edge("finish", END)
    graph.add_edge("prepare_ticket", "ticket")
    graph.add_edge("ticket", END)
    return graph.compile(
        checkpointer=checkpointer, interrupt_after=["tools"] if interrupt_after_tool else None
    )
