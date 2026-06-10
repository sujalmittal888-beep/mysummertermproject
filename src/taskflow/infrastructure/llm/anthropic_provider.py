"""Anthropic Claude provider adapter (Messages API)."""
from __future__ import annotations

import httpx

from taskflow.domain.exceptions import LLMProviderError
from taskflow.infrastructure.llm.base import SYSTEM_PROMPT, BaseLLMProvider
from taskflow.logging_config import get_logger

logger = get_logger(__name__)

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"


class AnthropicProvider(BaseLLMProvider):
    def __init__(
        self, api_key: str, model: str = "claude-sonnet-4-20250514", **kwargs: float
    ) -> None:
        super().__init__(model=model, **kwargs)
        if not api_key:
            raise LLMProviderError("Anthropic API key is not configured")
        self._api_key = api_key

    @property
    def name(self) -> str:
        return f"anthropic:{self.model}"

    def generate_task_json(self, instruction: str) -> str:
        body = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": instruction},
                # Prefill nudges the model to start a JSON object immediately.
                {"role": "assistant", "content": "{"},
            ],
        }
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = httpx.post(
                    _API_URL,
                    json=body,
                    headers={"x-api-key": self._api_key, "anthropic-version": _API_VERSION},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                text = "".join(
                    block["text"] for block in data["content"] if block["type"] == "text"
                )
                return "{" + text
            except (httpx.HTTPError, KeyError, IndexError) as exc:
                last_error = exc
                logger.warning("Anthropic attempt %d failed: %s", attempt + 1, exc)
        raise LLMProviderError(f"Anthropic provider failed: {last_error}") from last_error
