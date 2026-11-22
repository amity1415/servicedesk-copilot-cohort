"""Expose authenticated checkpointed diagnostics and their streamed updates."""

import json
from contextlib import closing

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from copilot.agents.checkpointed_diagnostics import (
    CheckpointedDiagnostics,
    DiagnosticConflict,
    DiagnosticNotFound,
    DiagnosticTurn,
)


def as_sse(event: dict) -> str:
    return f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"


def register_graph(app: FastAPI, service: CheckpointedDiagnostics, identify) -> None:
    from psycopg import OperationalError

    @app.post("/diagnostics/graph")
    def diagnostic_turn(body: DiagnosticTurn, actor: str = Depends(identify)):
        events = service.events(actor, body)
        try:
            first = next(events)
            if not body.stream:
                with closing(events):
                    updates = [first, *events]
                return {**updates[-1]["data"], "updates": updates[:-1]}
        except DiagnosticNotFound as exc:
            raise HTTPException(404, str(exc)) from exc
        except DiagnosticConflict as exc:
            raise HTTPException(409, str(exc)) from exc
        except OperationalError as exc:
            raise HTTPException(503, "diagnostic checkpoints are unavailable") from exc

        def stream():
            with closing(events):
                yield as_sse(first)
                try:
                    for event in events:
                        yield as_sse(event)
                except OperationalError:
                    yield as_sse(
                        {
                            "event": "error",
                            "data": {"detail": "diagnostic checkpoints are unavailable"},
                        }
                    )

        return StreamingResponse(stream(), media_type="text/event-stream")
