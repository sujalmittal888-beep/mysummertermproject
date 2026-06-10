"""Provider factory: swaps model providers without touching business logic."""
from __future__ import annotations

from taskflow.application.interfaces import LLMProvider
from taskflow.config import Settings
from taskflow.infrastructure.llm.anthropic_provider import AnthropicProvider
from taskflow.infrastructure.llm.mock_provider import MockLLMProvider
from taskflow.infrastructure.llm.openai_provider import OpenAIProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    common = {
        "timeout": settings.llm_timeout_seconds,
        "max_retries": settings.llm_max_retries,
    }
    match settings.llm_provider:
        case "openai":
            return OpenAIProvider(
                api_key=settings.openai_api_key, model=settings.resolved_llm_model, **common
            )
        case "anthropic":
            return AnthropicProvider(
                api_key=settings.anthropic_api_key, model=settings.resolved_llm_model, **common
            )
        case "mock":
            return MockLLMProvider(model=settings.resolved_llm_model, **common)
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
