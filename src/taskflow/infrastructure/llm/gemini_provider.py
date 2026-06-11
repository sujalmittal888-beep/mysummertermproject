"""Google Gemini provider adapter (generateContent REST API)."""
from __future__ import annotations

import httpx

from taskflow.domain.exceptions import LLMProviderError
from taskflow.infrastructure.llm.base import SYSTEM_PROMPT, BaseLLMProvider
from taskflow.logging_config import get_logger

logger = get_logger(__name__)

_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", **kwargs: float) -> None:
        super().__init__(model=model, **kwargs)
        if not api_key:
            raise LLMProviderError("Gemini API key is not configured")
        self._api_key = api_key

    @property
    def name(self) -> str:
        return f"gemini:{self.model}"

    def generate_task_json(self, instruction: str) -> str:
        url = _API_URL.format(model=self.model)
        body = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": instruction}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = httpx.post(
                    url,
                    json=body,
                    params={"key": self._api_key},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                return str(data["candidates"][0]["content"]["parts"][0]["text"])
            except (httpx.HTTPError, KeyError, IndexError) as exc:
                last_error = exc
                logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)
        raise LLMProviderError(f"Gemini provider failed: {last_error}") from last_error
