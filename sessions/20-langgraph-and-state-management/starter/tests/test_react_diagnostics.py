import os
from pathlib import Path

from fastapi.testclient import TestClient


def test_react_budget_and_allowed_actions(monkeypatch):
    from copilot.agents import react

    calls = []
    tools = {name: lambda: calls.append(1) for name in ("get_assets", "create_ticket")}

    def repeated(query, events):
        return {"tool": "get_assets"}

    result = react.run_loop(repeated, tools, "Slow laptop", max_steps=2)
    assert result["status"] == "escalated" and result["reason"] == "step_limit"
    assert [event["step"] for event in result["events"]] == [0, 1]
    assert len(calls) == 2

    invalid = react.run_loop(
        lambda q, e: {"tool": "get_assets", "arguments": []}, tools, "Slow laptop"
    )
    assert invalid["reason"] == "invalid_decision" and len(calls) == 2

    denied = react.run_loop(lambda q, e: {"tool": "create_ticket"}, tools, "Slow laptop")
    assert denied["status"] == "blocked" and denied["events"][0]["outcome"] == "denied"
    assert len(calls) == 2

    ticks = iter((0.0, 0.0, 31.0))
    monkeypatch.setattr(react, "monotonic", lambda: next(ticks))
    expired = react.run_loop(repeated, tools, "Slow laptop", deadline_s=30)
    assert expired == {"status": "escalated", "reason": "deadline", "events": []}
    assert len(calls) == 2


def test_slow_laptop_uses_typed_tools_and_keeps_the_thread_scoped(tmp_path, monkeypatch):
    from copilot.agents.verify_react import HEADERS, TOKENS, successful_trajectory
    from copilot.api.app import create_app

    monkeypatch.setenv("COPILOT_ANSWER_MODE", "extractive")
    monkeypatch.setenv("COPILOT_RETRIEVAL_BACKEND", "tfidf")
    monkeypatch.setenv("COPILOT_TRANSPORT", "direct")
    data = Path(os.environ.get("COHORT_DATA_DIR", "data"))
    body = {"question": "My laptop is slow", "thread_id": "diag-test"}
    with TestClient(create_app(data, tmp_path / "diag.sqlite3", TOKENS)) as api:
        result = api.post("/ask", headers=HEADERS, json=body).raise_for_status().json()
        report = successful_trajectory(result)
        assert report["decision_source"] == "local"
        assert "Restart the laptop" in report["answer"]
        assert "serial_number" not in report["events"][0]["observation"]["devices"][0]
        denied = api.post("/ask", headers={"Authorization": "Bearer mac-fixture"}, json=body)
        assert denied.status_code == 403
