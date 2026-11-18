import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def gate(monkeypatch, tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts/complete_session.py"
    spec = importlib.util.spec_from_file_location("completion_gate_under_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / "sessions").mkdir()
    return module, tmp_path


def test_next_session_requires_previous_verified_commit(gate, monkeypatch):
    module, root = gate
    manifest = {
        "sessions": [
            {"session": 1, "completion_state": "verified_awaiting_commit"},
            {"session": 2, "status": "implemented"},
        ]
    }
    (root / "sessions/implementation_manifest.json").write_text(json.dumps(manifest))
    calls = []
    monkeypatch.setattr(module, "git", lambda *args: calls.append(args))
    with pytest.raises(RuntimeError, match="Previous session"):
        module.complete(2)
    assert calls == []


def test_failed_execution_never_commits_or_marks_complete(gate, monkeypatch):
    module, root = gate
    path = root / "sessions/implementation_manifest.json"
    path.write_text(
        json.dumps(
            {
                "sessions": [
                    {"session": 1, "solution": "sessions/01-example/solution"},
                ]
            }
        )
    )
    calls = []
    monkeypatch.setattr(module, "git", lambda *args: calls.append(args))
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="failed", stderr=""),
    )
    with pytest.raises(RuntimeError, match="session-tests failed"):
        module.complete(1)
    assert json.loads(path.read_text())["sessions"][0]["completion_state"] == "verification_failed"
    assert calls == []


def test_failed_commit_does_not_unlock_next_session(gate, monkeypatch):
    module, root = gate
    path = root / "sessions/implementation_manifest.json"
    path.write_text(
        json.dumps(
            {
                "sessions": [
                    {"session": 1, "solution": "sessions/01-example/solution"},
                ]
            }
        )
    )
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="ok", stderr=""),
    )

    def git(*args):
        if args[0] == "commit":
            raise RuntimeError("commit failed")
        return "existing-source-commit"

    monkeypatch.setattr(module, "git", git)
    with pytest.raises(RuntimeError, match="commit failed"):
        module.complete(1)
    item = json.loads(path.read_text())["sessions"][0]
    assert item["completion_state"] == "verified_awaiting_commit"
    assert "completion_commit" not in item
