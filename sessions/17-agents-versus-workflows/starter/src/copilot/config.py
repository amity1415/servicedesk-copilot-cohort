"""Application settings, read once from environment variables and the .env file.

Every setting is an environment variable with the COPILOT_ prefix, for example
COPILOT_LOG_LEVEL=DEBUG. Secrets are typed as SecretStr so they never appear in
logs or in repr() output; call .get_secret_value() only where the value is used.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="COPILOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    log_format: Literal["console", "json"] = "console"
    data_dir: Path = Path("data")

    # Used from session 10 (PostgreSQL with pgvector in Docker Compose).
    database_url: SecretStr = SecretStr(
        "postgresql://copilot:copilot_dev_only@127.0.0.1:5432/copilot"
    )

    # Used from session 17 (trainer-provided ticketing mock).
    ticketing_base_url: str = "http://localhost:8081"
    ticketing_api_key: SecretStr = SecretStr("dev-ticketing-key")

    # Filled in session 4.
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: SecretStr | None = None
    request_timeout_s: float = Field(default=30.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings. Tests call get_settings.cache_clear()."""
    return Settings()
