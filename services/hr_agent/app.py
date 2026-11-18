"""A2A SDK server for the synthetic HR onboarding boundary."""

from __future__ import annotations

import json
import os
import secrets
from pathlib import Path

from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Part, TaskState, TextPart
from a2a.utils import new_agent_text_message
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class HRExecutor(AgentExecutor):
    def __init__(self, data: Path):
        self.data = data

    async def execute(self, context, event_queue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(TaskState.working)
        try:
            request = json.loads(context.get_user_input())
            candidates = json.loads((self.data / "hr/pending_joiners.json").read_text())
            candidate = next(c for c in candidates if c["candidate_id"] == request["candidate_id"])
            if candidate["manager_id"] != request["manager_id"]:
                raise ValueError("candidate does not belong to requesting manager")
            if candidate["peoplehub_record"] != "complete":
                raise ValueError("PeopleHub record incomplete")
            if request["start_date"] != candidate["start_date"]:
                raise ValueError("confirm the absolute start date against PeopleHub")
            result = {
                "candidate_id": candidate["candidate_id"],
                "status": "complete",
                "hr_checklist": candidate["hr_checklist"],
                "source": "synthetic PeopleHub",
            }
            await updater.add_artifact(
                [Part(root=TextPart(text=json.dumps(result)))], name="hr-checklist"
            )
            await updater.update_status(TaskState.completed, final=True)
        except (KeyError, ValueError, StopIteration) as exc:
            await updater.update_status(
                TaskState.failed, message=new_agent_text_message(str(exc)), final=True
            )

    async def cancel(self, context, event_queue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(TaskState.canceled, final=True)


def create_app(data: Path = Path("data"), token: str | None = None):
    expected = token or os.environ["COPILOT_HR_TOKEN"]
    card = AgentCard(
        name="Larkhaven HR",
        description="Synthetic HR onboarding verification",
        url=os.getenv("COPILOT_HR_URL", "http://localhost:8090/"),
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="onboard",
                name="Verify joiner",
                description="Verify an existing synthetic PeopleHub checklist",
                tags=["onboarding"],
            )
        ],
    )
    server = A2AStarletteApplication(
        card, DefaultRequestHandler(HRExecutor(data), InMemoryTaskStore())
    ).build()

    async def authenticate(request, call_next):
        # Discovery card is public; all task operations require partner auth.
        if not request.url.path.startswith("/.well-known/"):
            supplied = request.headers.get("Authorization", "").removeprefix("Bearer ")
            if not secrets.compare_digest(supplied, expected):
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    server.add_middleware(BaseHTTPMiddleware, dispatch=authenticate)
    return server
