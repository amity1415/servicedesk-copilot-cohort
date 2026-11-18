"""Bounded A2A JSON-RPC client with task status and candidate binding checks."""

import json
import uuid

import httpx


def verify_joiner(
    base_url: str, token: str, candidate: str, manager: str, start_date: str, transport=None
) -> dict:
    from a2a.types import Message, MessageSendParams, Part, Role, SendMessageRequest, TextPart

    message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text=json.dumps(
                        {"candidate_id": candidate, "manager_id": manager, "start_date": start_date}
                    )
                )
            )
        ],
    )
    request = SendMessageRequest(id=str(uuid.uuid4()), params=MessageSendParams(message=message))
    with httpx.Client(base_url=base_url, transport=transport, timeout=30) as client:
        card = client.get("/.well-known/agent-card.json")
        card.raise_for_status()
        if not any(s["id"] == "onboard" for s in card.json()["skills"]):
            raise ValueError("HR partner does not advertise onboarding")
        response = client.post(
            "/",
            headers={"Authorization": f"Bearer {token}"},
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        response.raise_for_status()
        envelope = response.json()
        if "error" in envelope:
            raise ValueError(envelope["error"])
        task = envelope["result"]
        if task.get("status", {}).get("state") != "completed":
            raise ValueError("HR task not completed; keep IT steps blocked")
        result = json.loads(task["artifacts"][0]["parts"][0]["text"])
        if result["candidate_id"] != candidate:
            raise ValueError("HR result bound to another candidate")
        return result
