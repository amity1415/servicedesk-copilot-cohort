"""LangGraph teaching adapter with explicit checkpoint lifecycle."""

from contextlib import contextmanager
from typing import TypedDict


class State(TypedDict):
    actor: str
    question: str
    thread: str
    result: dict


class ToolState(TypedDict, total=False):
    actor: str
    question: str
    action: dict
    events: list[dict]
    result: dict
    steps: int


def build_tool_graph(decide, tools: dict, allowed: set[str], checkpointer, max_steps=6):
    """Actual decision/tool loop; tools must already bind authenticated identity."""
    from langgraph.graph import END, START, StateGraph

    def decision(state):
        if state.get("steps", 0) >= max_steps:
            return {"action": {"stop": "step_limit"}}
        return {"action": decide(state["question"], state.get("events", []))}

    def route(state):
        return "finish" if "answer" in state["action"] or "stop" in state["action"] else "tools"

    def tool_node(state):
        action = state["action"]
        name = action.get("tool")
        event = {"tool": name, "arguments": action.get("arguments", {})}
        if name not in allowed or name not in tools:
            event["error"] = "denied"
        else:
            try:
                event["observation"] = tools[name](**event["arguments"])
            except (ValueError, PermissionError, TimeoutError) as exc:
                event["error"] = type(exc).__name__
        return {"events": [*state.get("events", []), event], "steps": state.get("steps", 0) + 1}

    def finish(state):
        action = state["action"]
        return {
            "result": {
                "status": "answered" if "answer" in action else "escalated",
                "answer": action.get("answer"),
                "reason": action.get("stop"),
                "events": state.get("events", []),
            }
        }

    graph = StateGraph(ToolState)
    graph.add_node("decision", decision)
    graph.add_node("tools", tool_node)
    graph.add_node("finish", finish)
    graph.add_edge(START, "decision")
    graph.add_conditional_edges("decision", route)
    graph.add_edge("tools", "decision")
    graph.add_edge("finish", END)
    return graph.compile(checkpointer=checkpointer)


def invoke_for_identity(graph, actor: str, thread: str, question: str):
    """Call only with the server-authenticated actor, never an arbitrary request field."""
    return graph.invoke(
        {"actor": actor, "question": question, "events": [], "steps": 0},
        {"configurable": {"thread_id": f"{actor}:{thread}"}},
    )


def build(engine, checkpointer):
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(State)
    graph.add_node(
        "workflow",
        lambda state: {"result": engine.run(state["actor"], state["question"], state["thread"])},
    )
    graph.add_edge(START, "workflow")
    graph.add_edge("workflow", END)
    return graph.compile(checkpointer=checkpointer)


@contextmanager
def postgres_graph(engine, url: str):
    from langgraph.checkpoint.postgres import PostgresSaver

    with PostgresSaver.from_conn_string(url) as saver:
        saver.setup()
        yield build(engine, saver)
