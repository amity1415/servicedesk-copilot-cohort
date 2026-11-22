"""Session experiments return measured outputs and explicitly named integration gaps."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import time
from dataclasses import asdict
from pathlib import Path


def _rag(root):
    from copilot.rag.pipeline import Retriever

    return Retriever.from_data(root / "data")


def _runtime(root):
    from copilot.tools.runtime import Runtime

    return Runtime(root / ".work" / "course.sqlite3", root / "data")


def experiment(number: int, root: Path) -> dict:
    data = root / "data"
    if number == 1:
        from copilot.tickets import count_by, load_tickets

        return {
            "ticket_counts": dict(
                count_by(load_tickets(data / "tickets/historical_tickets.jsonl"), "category")
            )
        }
    if number in {2, 3}:
        from copilot.ml.train import train

        return train(data, root / "reports", neural=number == 3)
    if number == 4:
        import httpx

        from copilot.llm.client import ModelClient

        calls = []

        def handle(request):
            calls.append(request)
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "Software"}}],
                    "usage": {"total_tokens": 12},
                },
            )

        client = ModelClient("fixture", api_key="fixture", transport=httpx.MockTransport(handle))
        result = client.complete([{"role": "user", "content": "Classify an install request"}])
        return {
            "mock_call": asdict(result),
            "requests": len(calls),
            "live_comparison": "requires configured provider; not measured",
        }
    if number == 6:
        from copilot.rag.pipeline import ingest

        output = root / ".work/documents.json"
        first = ingest(data, output)
        second = ingest(data, output)
        if second["changed"] != 0 or first["skipped"]:
            raise AssertionError("ingestion not repeatable or files skipped")
        return {"first": first, "repeat": second}
    if number == 15:
        from copilot.rag.evaluation import dataset_path, evaluate

        return evaluate(data, dataset_path(data))
    if number in {5, 7, 8, 9, 10, 11, 12, 13, 14}:
        from copilot.rag.advanced import reciprocal_rank_fusion, rewrite
        from copilot.rag.pipeline import Document, chunk

        retriever = _rag(root)
        query = (
            rewrite("it still doesn't work", "VPN Windows error 809")
            if number == 13
            else "VPN error 809"
        )
        start = time.monotonic()
        results = retriever.search(query, os_name="windows")
        output = {
            "mode": "lexical-reference",
            "query": query,
            "hits": [asdict(c) for c in results],
            "elapsed_s": time.monotonic() - start,
        }
        if number == 7:
            doc = Document(
                "steps",
                "1. " + "x" * 1600 + "\n\n2. Restart laptop.",
                {"audience": "employee"},
                "fixture",
                "hash",
            )
            output = {
                "fixed_sizes": [len(c.text) for c in chunk(doc, "fixed")],
                "recursive_sizes": [len(c.text) for c in chunk(doc)],
                "atomic_step_preserved": chunk(doc)[0].text.startswith("1. ")
                and len(chunk(doc)[0].text) > 1600,
            }
        if number == 12:
            output["fused_ids"] = [
                c.id for c in reciprocal_rank_fusion([results, list(reversed(results))])
            ]
            output["postgres_comparison"] = "not measured by lexical experiment"
        if number == 14:
            output["answer"] = retriever.answer("VPN setup Mac", os_name="macos")
            output["live_grounding"] = "requires model and human entailment check"
        if number in {8, 9, 10}:
            output["integration_gate"] = (
                "requires neural models, PostgreSQL or reviewed metric labels; "
                "not satisfied by lexical reference"
            )
        return output
    if number == 16:
        from fastapi.testclient import TestClient

        from copilot.api.app import create_app

        with (
            tempfile.TemporaryDirectory(dir=root / ".work") as temporary,
            TestClient(
                create_app(data, Path(temporary) / "api.sqlite3", tokens={"fixture": "E1261"})
            ) as client,
        ):
            denied = client.post("/ask", json={"question": "VPN", "thread_id": "one"})
            success = client.post(
                "/ask",
                json={"question": "VPN setup Mac", "thread_id": "one"},
                headers={"Authorization": "Bearer fixture"},
            )
            assert denied.status_code == 401 and success.status_code == 200
            return {
                "unauthenticated": denied.status_code,
                "authenticated": success.json(),
                "request_id": success.headers["X-Request-ID"],
            }
    if number in {17, 18, 24}:
        from copilot.tools.ticketing import TicketDraft

        draft = TicketDraft(
            category="Hardware & Devices",
            priority="P3",
            summary="Laptop slow",
            steps_tried=["Restart", "KB troubleshooting"],
            asset="LH-L-00166",
            assignment_group="Workplace Engineering",
        )
        return {
            "validated_draft": draft.model_dump(),
            "live_gate": (
                "run ticketing HTTP and fault-injection tests; "
                "no remote write made by this schema exercise"
            ),
        }
    if number in {19, 23, 26}:
        from copilot.agents.react import run_loop, specialist

        tools = {"get_assets": lambda: _runtime(root).assets("E1166", "E1166")}
        result = run_loop(
            lambda q, events: (
                {"answer": "Inspect the device and KB evidence"}
                if events
                else {"tool": "get_assets"}
            ),
            tools,
            "My laptop is slow",
        )
        runaway = run_loop(lambda q, events: {"tool": "get_assets"}, tools, "slow", max_steps=2)
        return {
            "trajectory": result,
            "runaway": runaway,
            "specialist": specialist("My laptop is slow"),
            "decision_source": "scripted fixture; model comparison not measured",
        }
    if number in {20, 22}:
        runtime = _runtime(root)
        runtime.save_thread("E1166", "course-resume", {"step": "device_checked"})
        reloaded = _runtime(root).load_thread("E1166", "course-resume")
        runtime.memory("E1166", "VPN troubleshooting completed")
        recalled = runtime.memory("E1166")
        runtime.memory("E1166", delete=True)
        return {
            "resumed_state": reloaded,
            "recalled": recalled,
            "deleted": runtime.memory("E1166") is None,
            "backend": "SQLite offline adapter",
            "postgres_checkpointer": "separate integration gate",
        }
    if number in {21, 27, 33}:
        from copilot.agents.planning import Step, execute, handoff

        steps = [Step("hr"), Step("account", ["hr"]), Step("laptop", ["account"])]
        trace = execute(
            steps, {"hr": lambda: {"status": "failed", "reason": "partner unavailable"}}
        )
        assert trace[1]["status"] == "pending"
        return {
            "failed_prerequisite": trace,
            "handoff": handoff("HR prerequisite failed", trace, "Contact HR partner"),
            "A2A_transport": "not exercised by dependency fixture",
        }
    if number in {25, 32}:
        runtime = _runtime(root)
        denied = False
        try:
            runtime.assets("E1261", "E1166")
        except PermissionError:
            denied = True
        request = runtime.request_access("E1237", "APP-020", "course-access-check")
        return {
            "cross_user_denied": denied,
            "request": request,
            "manager": runtime.employee("E1237")["manager_id"],
            "warning": (
                "does not auto-approve; use integration test for complete approval lifecycle"
            ),
        }
    if number == 28:
        from copilot.guardrails.checks import mask, suspicious

        attacks = [
            json.loads(line)
            for line in (root / "evals/redteam/attacks.jsonl").read_text().splitlines()
        ]
        return {
            "cases": len(attacks),
            "detected": sum(suspicious(a["text"]) for a in attacks),
            "masked": mask("E1122 at tom@example.test"),
            "scope": "detector coverage only; effect prevention is tested separately",
        }
    if number in {29, 30, 31, 34}:
        return {
            "mode": "protocol-preflight",
            "mcp_installed": importlib.util.find_spec("mcp") is not None,
            "psycopg_installed": importlib.util.find_spec("psycopg") is not None,
            "entrypoint": "python -m copilot.mcp_servers.servers documents",
            "gate": (
                "actual client/server initialize and contract tests required; "
                "preflight is not interoperability evidence"
            ),
        }
    if number in {35, 36, 37, 38}:
        datasets = {}
        for name in ("rag", "agent"):
            records = [
                json.loads(line)
                for line in (root / f"evals/{name}_golden.jsonl").read_text().splitlines()
            ]
            datasets[name] = {
                "count": len(records),
                "reviewed": sum(r.get("review_status") == "approved" for r in records),
            }
        return {
            "datasets": datasets,
            "judge_agreement": None,
            "task_success": None,
            "gate": (
                "review labels and run live end-state evaluation before reporting release metrics"
            ),
        }
    if number == 39:
        from copilot.guardrails.checks import mask

        return {
            "safe_attribute_example": mask("E1237 sofia@example.test"),
            "tokens": None,
            "cost": None,
            "p95_latency": None,
            "gate": "OTLP collector and cross-service propagated spans required",
        }
    if number == 40:
        return {
            "mode": "release-preflight",
            "session_count": len(json.loads((root / "sessions/manifest.json").read_text())),
            "release_gate": (
                "run six scenarios, live evaluation, security scan and clean Compose startup; "
                "do not tag on preflight alone"
            ),
        }
    raise ValueError(f"unsupported session {number}")


def run_session(number: int, root: Path):
    if not 1 <= number <= 40:
        raise ValueError("session must be between 1 and 40")
    (root / ".work").mkdir(exist_ok=True)
    result = {"session": number, "result": experiment(number, root)}
    reports = root / "reports" / "sessions"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / f"{number:02d}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        json.dumps({"session": number, "report": str(path), "result_keys": list(result["result"])})
    )
    return result
