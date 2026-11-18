import pytest

from copilot.course.scoring import agent_suite, agreement, release_gate, trajectory


def test_plausible_answer_cannot_replace_end_state():
    tasks = [
        {
            "id": "one",
            "expected_tool_calls": ["create_ticket"],
            "forbidden_actions": [],
            "review_status": "approved",
        }
    ]
    result = agent_suite(
        tasks, lambda task: {"answer": "Ticket created!", "events": []}, lambda task, output: False
    )
    assert result["task_success"] == 0 and result["tool_call_accuracy"] == 0


def test_order_rules_and_missing_measurements_fail():
    result = trajectory(
        [{"tool": "request_access"}, {"tool": "check_policy"}, {"tool": "fulfil_access"}], [], []
    )
    assert len(result["violations"]) == 2
    assert not release_gate({}, {"faithfulness": 0.90})["passed"]
    assert not release_gate({"successful_attacks": 1}, {"successful_attacks": 0})["passed"]


def test_draft_tasks_are_not_treated_as_ground_truth():
    with pytest.raises(ValueError):
        agent_suite([{"review_status": "draft"}], lambda task: {}, lambda task, output: True)
    assert agreement([1] * 30, [1] * 27 + [0] * 3)["agreement"] == 0.9
