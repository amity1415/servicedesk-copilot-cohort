"""Offline citation-contract checks against the actual knowledge corpus."""

import json

import httpx

from copilot.llm.client import ModelClient
from copilot.rag.grounded import GroundedRag
from copilot.rag.service import VectorRag


def verify_grounded_fixture(data):
    rag = VectorRag.from_data(data)
    cases = [
        ("How do I set up VPN on my Mac?", "macos", "KB-1017"),
        ("How do I fix Windows VPN error 809?", "windows", "KB-1018"),
        ("What does policy POL-999999999 require?", "macos", None),
    ]
    observed = []
    for question, os_name, expected in cases:
        calls = []

        def respond(request, *, calls=calls, expected=expected):
            payload = json.loads(request.content)
            user = json.loads(payload["messages"][1]["content"])
            calls.append(len(user["sources"]))
            target = "App Hub" if expected == "KB-1017" else "try the VPN"
            source, quote = next(
                (item, line)
                for item in user["sources"]
                if item["chunk_id"].startswith(expected)
                for line in item["content"].splitlines()
                if target in line
            )
            answer = {
                "abstained": False,
                "citations": [{"chunk_id": source["chunk_id"], "quote": quote}],
            }
            return httpx.Response(
                200, json={"choices": [{"message": {"content": json.dumps(answer)}}]}
            )

        client = ModelClient(
            "fixture",
            base_url="https://fixture.invalid/v1",
            api_key="fixture",
            transport=httpx.MockTransport(respond),
        )
        response = GroundedRag(rag, client).answer(question, os_name=os_name)
        citations = [item["document_id"] for item in response["citations"]]
        if expected:
            if citations != [expected] or response["abstained"] or len(calls) != 1:
                raise RuntimeError(f"Expected checked citation {expected}: {response}")
        elif citations or not response["abstained"] or calls:
            raise RuntimeError(f"Unknown policy exercised the provider: {response}")
        observed.append({"question": question, "result": response, "provider_requests": len(calls)})
    return {
        "mode": "offline-citation-contract-fixture",
        "live_generation_verified": False,
        "human_review_completed": False,
        "cases": observed,
    }
