"""Authenticated HTTP access to the typed service desk tools."""

from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from copilot.tools.service_desk import (
    TOOLS,
    MissingIdempotencyKey,
    ServiceDeskTools,
    TicketingUnavailable,
)


def register_tools(app: FastAPI, tools: ServiceDeskTools, identify) -> None:
    @app.get("/tools")
    def describe_tools(actor: str = Depends(identify)):
        return tools.describe(actor)

    @app.post("/tools/{name}")
    def execute_tool(
        name: str,
        body: dict,
        idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
        actor: str = Depends(identify),
    ):
        if name not in TOOLS:
            raise HTTPException(404, "unknown service desk tool")
        try:
            return tools.execute(actor, name, body, idempotency_key=idempotency_key)
        except ValidationError as exc:
            raise RequestValidationError(
                exc.errors(include_input=False, include_context=False)
            ) from exc
        except MissingIdempotencyKey as exc:
            raise HTTPException(400, str(exc)) from exc
        except TicketingUnavailable as exc:
            raise HTTPException(503, "ticketing service is unavailable") from exc
        except httpx.HTTPStatusError as exc:
            error = {
                404: "ticket was not found",
                409: "ticket update or replay conflicted",
                422: "ticketing rejected the request",
            }
            status = exc.response.status_code
            if status in error:
                raise HTTPException(status, error[status]) from exc
            raise HTTPException(502, "ticketing service is unavailable") from exc
        except httpx.RequestError as exc:
            raise HTTPException(502, "ticketing service is unavailable") from exc
