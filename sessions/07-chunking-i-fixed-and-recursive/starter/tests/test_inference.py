import json

import httpx
import pytest
from pydantic import ValidationError

from copilot.llm.classify import classify
from copilot.llm.client import ModelClient


def client_for(responses):
    calls = []

    def handle(request):
        calls.append(request)
        content = responses[min(len(calls) - 1, len(responses) - 1)]
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}], "usage": {"total_tokens": 20}},
        )

    return ModelClient("fixture", api_key="fixture", transport=httpx.MockTransport(handle)), calls


def test_one_output_repair_then_valid_classification():
    good = json.dumps(
        {"category": "Hardware & Devices", "priority": "P3", "summary": "Laptop remains slow"}
    )
    client, calls = client_for(["not JSON", good])
    result = classify(client, "My laptop is slow")
    assert result.priority == "P3" and len(calls) == 2


def test_invalid_output_stops_after_one_repair():
    client, calls = client_for(['{"category":"invented"}'])
    with pytest.raises(ValidationError):
        classify(client, "VPN issue")
    assert len(calls) == 2


def test_authentication_errors_are_not_retried():
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(401)

    client = ModelClient("fixture", api_key="fixture", transport=httpx.MockTransport(handle))
    with pytest.raises(httpx.HTTPStatusError):
        client.complete([])
    assert len(calls) == 1


def test_transient_error_retry_is_bounded(monkeypatch):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(503)

    monkeypatch.setattr("copilot.llm.client.time.sleep", lambda delay: None)
    client = ModelClient(
        "fixture", api_key="fixture", attempts=2, transport=httpx.MockTransport(handle)
    )
    with pytest.raises(httpx.HTTPStatusError):
        client.complete([])
    assert len(calls) == 2
