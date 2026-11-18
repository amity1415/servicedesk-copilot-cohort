"""Optional OpenTelemetry with safe attributes and W3C context propagation."""

from __future__ import annotations

import functools
import os
import time
from collections import deque
from contextlib import contextmanager

MEASUREMENTS = deque(maxlen=10000)


def configure(service: str):
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider(resource=Resource.create({"service.name": service}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)


@contextmanager
def span(name: str, headers: dict | None = None):
    from opentelemetry import trace
    from opentelemetry.propagate import extract

    context = extract(headers) if headers else None
    with trace.get_tracer("copilot").start_as_current_span(
        name, context=context, record_exception=False, set_status_on_exception=False
    ) as current:
        yield current


def outbound_headers() -> dict:
    from opentelemetry.propagate import inject

    headers = {}
    inject(headers)
    return headers


def traced(name: str):
    def decorate(function):
        @functools.wraps(function)
        def call(*args, **kwargs):
            start = time.monotonic()
            with span(name) as current:
                try:
                    result = function(*args, **kwargs)
                    usage = getattr(result, "tokens", None)
                    if usage is not None:
                        current.set_attribute("gen_ai.usage.total_tokens", usage)
                    MEASUREMENTS.append(
                        {"operation": name, "seconds": time.monotonic() - start, "error": False}
                    )
                    return result
                except Exception:
                    # Do not attach raw exception text: it can contain source PII.
                    current.set_attribute("operation.failed", True)
                    MEASUREMENTS.append(
                        {"operation": name, "seconds": time.monotonic() - start, "error": True}
                    )
                    raise

        return call

    return decorate


def dashboard() -> dict:
    rows = list(MEASUREMENTS)
    latencies = sorted(r["seconds"] for r in rows if r["operation"] == "agent.run")
    return {
        "sample_count": len(rows),
        "request_p95_s": latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))]
        if latencies
        else None,
        "operation_error_rate": sum(r["error"] for r in rows) / len(rows) if rows else None,
        "cost_per_resolved_request": None,
        "cost_status": "configure provider usage and pricing before reporting cost",
    }
