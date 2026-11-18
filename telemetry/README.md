# Tracing and operational measurements

`src/copilot/telemetry.py` provides optional OTLP setup, named spans, W3C outbound
headers, safe token counts and a bounded in-process latency/error sample. Set
`OTEL_EXPORTER_OTLP_ENDPOINT` before startup to export to a compatible collector.

`GET /metrics` requires an analyst or admin bearer. It reports sampled workflow
p95 and operation errors. Cost stays null until provider prices and resolved
request attribution are configured. The Streamlit UI records user feedback.

This is a local instrumentation reference. A cross-service collector/dashboard,
durable metrics backend, complete MCP/HR context propagation and Presidio-based
PII analysis remain session 39 integration work. The regex masker only covers
known email and synthetic employee ID patterns; it is not a general PII detector.
No raw prompts, source text or exception messages are deliberately put in spans.
