"""Explicit dependency planning and structured analyst handoff."""

from dataclasses import asdict, dataclass, field


@dataclass
class Step:
    id: str
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"
    evidence: dict = field(default_factory=dict)


def validate(steps: list[Step]):
    ids = {s.id for s in steps}
    if len(ids) != len(steps):
        raise ValueError("duplicate step IDs")
    remaining, complete = list(steps), set()
    while remaining:
        ready = [s for s in remaining if set(s.depends_on) <= complete]
        if not ready:
            raise ValueError("cycle or unknown dependency")
        for step in ready:
            complete.add(step.id)
            remaining.remove(step)


def execute(steps: list[Step], handlers: dict) -> list[dict]:
    validate(steps)
    for _ in range(len(steps)):
        complete = {s.id for s in steps if s.status == "complete"}
        ready = [s for s in steps if s.status == "pending" and set(s.depends_on) <= complete]
        if not ready:
            break
        for step in ready:
            try:
                result = handlers[step.id]()
                step.status = "complete" if result.get("status") == "complete" else "failed"
                step.evidence = result
            except (ValueError, TimeoutError, KeyError) as exc:
                step.status, step.evidence = "failed", {"error": str(exc)}
    return [asdict(s) for s in steps]


def handoff(summary: str, events: list[dict], next_step: str) -> dict:
    if not summary or not next_step:
        raise ValueError("handoff needs summary and next step")
    return {
        "summary": summary,
        "steps_tried": events,
        "suggested_next_step": next_step,
        "status": "analyst_queue",
    }
