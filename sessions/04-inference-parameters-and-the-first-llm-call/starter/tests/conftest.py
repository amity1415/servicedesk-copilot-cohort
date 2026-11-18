"""Shared fixtures: every test starts with clean settings and leaves logging as it found it."""

from __future__ import annotations

import logging
import os

import pytest

from copilot.config import get_settings


@pytest.fixture(autouse=True)
def clean_settings(monkeypatch: pytest.MonkeyPatch):
    """Remove COPILOT_* variables so a developer's shell cannot change test results."""
    for name in list(os.environ):
        if name.startswith("COPILOT_"):
            monkeypatch.delenv(name)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def restore_logging():
    """configure_logging replaces the root handlers; put pytest's own handlers back afterwards."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
