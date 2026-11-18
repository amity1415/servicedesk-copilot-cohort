from __future__ import annotations

import pytest
from pydantic import ValidationError

from copilot.config import Settings, get_settings


def settings() -> Settings:
    # _env_file=None keeps a developer's local .env out of the tests.
    return Settings(_env_file=None)


def test_defaults_work_without_any_configuration() -> None:
    config = settings()
    assert (config.env, config.log_level, config.log_format) == ("dev", "INFO", "console")
    assert config.llm_provider is None
    assert config.ticketing_base_url == "http://localhost:8081"


def test_environment_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPILOT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("COPILOT_REQUEST_TIMEOUT_S", "5")
    config = settings()
    assert config.log_level == "DEBUG"
    assert config.request_timeout_s == 5.0


def test_empty_variables_count_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPILOT_LLM_PROVIDER", "")
    assert settings().llm_provider is None


def test_secrets_never_appear_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPILOT_LLM_API_KEY", "not-a-real-key-123")
    config = settings()
    assert "not-a-real-key-123" not in repr(config)
    assert "not-a-real-key-123" not in config.model_dump_json()
    assert config.llm_api_key.get_secret_value() == "not-a-real-key-123"


def test_invalid_values_fail_at_start_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPILOT_REQUEST_TIMEOUT_S", "0")
    with pytest.raises(ValidationError):
        settings()
    monkeypatch.setenv("COPILOT_REQUEST_TIMEOUT_S", "30")
    monkeypatch.setenv("COPILOT_ENV", "staging")
    with pytest.raises(ValidationError):
        settings()


def test_get_settings_returns_one_shared_instance() -> None:
    assert get_settings() is get_settings()
