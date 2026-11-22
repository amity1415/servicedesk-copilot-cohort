import json
import os
from pathlib import Path

import httpx


def test_graph_resume_ports_diagnostics_and_freezes_the_ticket():
    from copilot.agents.diagnostic_graph import build_diagnostic_graph
    from langgraph.checkpoint.memory import InMemorySaver

    from copilot.agents.diagnostics import SLOW_REQUEST
    from copilot.agents.verify_react import EMPLOYEE, successful_trajectory
    from copilot.rag.service import VectorRag
    from copilot.tools.directory import Directory
    from copilot.tools.service_desk import ServiceDeskTools
    from copilot.tools.ticketing import TicketingClient

    data = Path(os.environ.get("COHORT_DATA_DIR", "data"))
    outgoing = []

    def respond(request):
        outgoing.append(request)
        if len(outgoing) <= 3:
            return httpx.Response(503)
        body = json.loads(request.content)
        return httpx.Response(
            201, json={"ticket_id": "INC0020061", "requester_id": body["requester_id"]}
        )

    ticketing = TicketingClient("http://ticketing.test", "fixture", httpx.MockTransport(respond))
    tools = ServiceDeskTools(Directory(data), VectorRag.from_data(data), ticketing)
    saver = InMemorySaver()
    first = build_diagnostic_graph(tools, saver, interrupt_after_tool=True)
    config = {"configurable": {"thread_id": "fixture-thread"}}
    first.invoke(
        {
            "actor": EMPLOYEE,
            "thread_id": "fixture-thread",
            "intent": "diagnose",
            "question": SLOW_REQUEST,
            "decisions": 0,
            "events": [],
            "observations": {},
        },
        config,
    )
    saved = first.get_state(config)
    assert saved.next == ("decision",)
    assert [event["tool"] for event in saved.values["events"]] == ["get_assets"]

    second = build_diagnostic_graph(tools, saver)
    result = second.invoke(None, config)["result"]
    assert successful_trajectory(result)["documents"] == ["KB-1054"]
    assert not outgoing

    failed = second.invoke(
        {"intent": "create_ticket", "failure_report": "The updates did not help."}, config
    )
    assert failed["result"]["status"] == "ticket_unavailable"
    assert failed["ticket_draft"]["steps_tried"][-1] == "The updates did not help."
    retry = second.invoke(
        {"intent": "create_ticket", "failure_report": "Please check again."}, config
    )
    assert retry["result"]["ticket"]["requester_id"] == EMPLOYEE
    assert retry["ticket_draft"] == failed["ticket_draft"]
    assert retry["ticket_key"] == failed["ticket_key"]
    assert len(outgoing) == 4
    assert len({request.headers["Idempotency-Key"] for request in outgoing}) == 1
    assert len({request.content for request in outgoing}) == 1
