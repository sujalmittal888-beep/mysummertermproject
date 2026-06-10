"""OpenAI provider adapter (Chat Completions, JSON mode)."""
from __future__ import annotations

import httpx

from taskflow.domain.exceptions import LLMProviderError
from taskflow.infrastructure.llm.base import SYSTEM_PROMPT, BaseLLMProvider
from taskflow.logging_config import get_logger

logger = get_logger(__name__)

_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs: float) -> None:
        super().__init__(model=model, **kwargs)
        if not api_key:
            raise LLMProviderError("OpenAI API key is not configured")
        self._api_key = api_key

    @property
    def name(self) -> str:
        return f"openai:{self.model}"

    def generate_task_json(self, instruction: str) -> str:
        body = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": instruction},
            ],
        }
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = httpx.post(
                    _API_URL,
                    json=body,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                return str(data["choices"][0]["message"]["content"])
            except (httpx.HTTPError, KeyError, IndexError) as exc:
                last_error = exc
                logger.warning("OpenAI attempt %d failed: %s", attempt + 1, exc)
        raise LLMProviderError(f"OpenAI provider failed: {last_error}") from last_error
