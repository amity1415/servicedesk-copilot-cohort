from __future__ import annotations

import io
import json
import logging

from copilot.logging_setup import configure_logging, request_id_var


def test_json_lines_carry_request_id_and_extra_fields() -> None:
    stream = io.StringIO()
    configure_logging("INFO", "json", stream)
    token = request_id_var.set("req-42")
    try:
        logging.getLogger("copilot.test").info("ticket created", extra={"ticket_id": "INC0020061"})
    finally:
        request_id_var.reset(token)

    record = json.loads(stream.getvalue())
    assert record["message"] == "ticket created"
    assert record["level"] == "INFO"
    assert record["logger"] == "copilot.test"
    assert record["request_id"] == "req-42"
    assert record["ticket_id"] == "INC0020061"
    assert record["ts"].endswith("+00:00")


def test_json_lines_include_the_exception() -> None:
    stream = io.StringIO()
    configure_logging("INFO", "json", stream)
    try:
        raise ValueError("bad input")
    except ValueError:
        logging.getLogger("copilot.test").exception("failed")
    record = json.loads(stream.getvalue())
    assert "ValueError: bad input" in record["exception"]
    assert "request_id" not in record


def test_console_format_is_one_readable_line() -> None:
    stream = io.StringIO()
    configure_logging("INFO", "console", stream)
    logging.getLogger("copilot.test").warning("disk almost full")
    line = stream.getvalue().strip()
    assert line.endswith("WARNING copilot.test: disk almost full")
    assert "\n" not in line


def test_level_filters_and_reconfiguring_does_not_duplicate_lines() -> None:
    first, second = io.StringIO(), io.StringIO()
    configure_logging("DEBUG", "console", first)
    configure_logging("WARNING", "console", second)
    log = logging.getLogger("copilot.test")
    log.info("hidden")
    log.error("shown")
    assert first.getvalue() == ""
    assert second.getvalue().count("\n") == 1
