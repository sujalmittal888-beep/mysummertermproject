"""Centralized configuration management (12-factor, env-driven)."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_prefix="TASKFLOW_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    # LLM provider configuration
    llm_provider: Literal["openai", "anthropic", "mock"] = "mock"
    llm_model: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2

    # Persistence
    database_url: str = "sqlite:///./taskflow.db"

    # Artifacts
    artifact_dir: Path = Path("./artifacts")

    @property
    def resolved_llm_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        return {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "mock": "mock-deterministic-v1",
        }[self.llm_provider]


@lru_cache
def get_settings() -> Settings:
    return Settings()
