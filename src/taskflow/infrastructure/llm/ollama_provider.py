"""Ollama local LLM provider (OpenAI-compatible /v1/chat/completions)."""
from __future__ import annotations

import json
import re

import httpx

from taskflow.domain.action_registry import APPROVED_ACTIONS
from taskflow.domain.exceptions import LLMProviderError
from taskflow.infrastructure.llm.base import BaseLLMProvider
from taskflow.logging_config import get_logger

logger = get_logger(__name__)

# Simpler, example-driven prompt — small models do better with concrete examples
# than with abstract JSON Schema definitions.
_OLLAMA_PROMPT = f"""You are a JSON task planner. Convert industrial instructions into JSON.

Output ONLY valid JSON. No markdown, no explanation, no code fences.

Required format:
{{
  "version": "1.0",
  "instruction": "<the original instruction text>",
  "tasks": [
    {{
      "id": "T1",
      "action": "navigate",
      "description": "Go to Room 1",
      "depends_on": [],
      "condition": null,
      "metadata": {{"location": "Room 1"}}
    }},
    {{
      "id": "T2",
      "action": "pick",
      "description": "Pick up the red box",
      "depends_on": ["T1"],
      "condition": null,
      "metadata": {{"object": "red box"}}
    }}
  ]
}}

Rules:
- "action" MUST be one of: {sorted(APPROVED_ACTIONS)}
- "id" must be T1, T2, T3 ... (letters and numbers only, no spaces)
- "depends_on" is a list of task ids that must finish first (empty list [] if none)
- "condition" is null unless this is a conditional branch (e.g. "damaged")
- "metadata" is a dict with relevant details like location, object name
- Decompose compound instructions into multiple atomic tasks
- Output the JSON object only — nothing before or after it
"""

# Common action synonyms small models tend to use
_ACTION_SYNONYMS: dict[str, str] = {
    "go": "navigate", "move_to": "navigate", "travel": "navigate", "goto": "navigate",
    "grab": "pick", "pickup": "pick", "take": "pick", "collect": "pick",
    "put": "place", "drop": "place", "deposit": "place", "set": "place",
    "check": "inspect", "examine": "inspect", "look": "inspect", "review": "inspect",
    "transport": "transfer", "carry": "transfer", "bring": "transfer",
    "find": "locate", "search": "locate", "look_for": "locate",
    "read": "scan", "barcode": "scan",
    "build": "assemble", "attach": "assemble", "combine": "assemble",
    "ship": "deliver", "send": "deliver",
    "confirm": "verify", "validate": "verify", "check_weight": "verify",
}


def _extract_json(text: str) -> str:
    """Pull the first complete JSON object out of the model's output."""
    text = text.strip()
    # strip code fences
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text.rstrip())
        text = text.strip()
    # find outermost { ... }
    start = text.find("{")
    if start == -1:
        return text
    depth, end = 0, -1
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    return text[start:end + 1] if end != -1 else text[start:]


def _repair(raw: str, instruction: str) -> str:
    """Best-effort repair of LLM output before Pydantic validation."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise

    # top-level: inject missing instruction
    if not data.get("instruction"):
        data["instruction"] = instruction
    if not data.get("version"):
        data["version"] = "1.0"

    # some models nest tasks under a different key
    if "tasks" not in data:
        for key in ("task_list", "plan", "steps", "task_plan"):
            if key in data and isinstance(data[key], list):
                data["tasks"] = data.pop(key)
                break

    tasks = data.get("tasks", [])
    seen_ids: set[str] = set()
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue

        # fix id
        tid = str(task.get("id", f"T{i+1}")).strip()
        tid = re.sub(r"[^A-Za-z0-9_\-]", "", tid) or f"T{i+1}"
        if tid in seen_ids:
            tid = f"{tid}_{i+1}"
        seen_ids.add(tid)
        task["id"] = tid

        # fix action — normalise synonyms, default to navigate
        action = str(task.get("action", "")).strip().lower().replace(" ", "_")
        action = _ACTION_SYNONYMS.get(action, action)
        if action not in APPROVED_ACTIONS:
            action = "navigate"
        task["action"] = action

        # ensure depends_on is a list of strings
        dep = task.get("depends_on", [])
        if isinstance(dep, str):
            dep = [d.strip() for d in dep.split(",") if d.strip()]
        elif not isinstance(dep, list):
            dep = []
        task["depends_on"] = [str(d) for d in dep]

        # ensure condition is null not empty string
        cond = task.get("condition")
        if cond is not None and not str(cond).strip():
            cond = None
        task["condition"] = cond

        # ensure metadata is a dict
        if not isinstance(task.get("metadata"), dict):
            task["metadata"] = {}

        # ensure description exists
        if not task.get("description"):
            task["description"] = f"{action.capitalize()} step {i+1}"

    data["tasks"] = tasks
    return json.dumps(data)


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "llama3.2", **kwargs: float) -> None:
        super().__init__(model=model, **kwargs)
        self._base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return f"ollama:{self._model}"

    def generate_task_json(self, instruction: str) -> str:
        url = f"{self._base_url}/v1/chat/completions"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _OLLAMA_PROMPT},
                {"role": "user",   "content": instruction},
            ],
            "stream": False,
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = httpx.post(url, json=payload, timeout=self._timeout)
                if resp.status_code == 404:
                    raise LLMProviderError(
                        f"Ollama model '{self._model}' not found. "
                        f"Pull it first: ollama pull {self._model}"
                    )
                resp.raise_for_status()
                data = resp.json()
                raw = data["choices"][0]["message"]["content"]
                raw = _extract_json(raw)
                raw = _repair(raw, instruction)
                json.loads(raw)   # final sanity check
                return raw
            except LLMProviderError:
                raise
            except (httpx.ConnectError, httpx.ConnectTimeout):
                raise LLMProviderError(
                    "Cannot reach Ollama — is it running? Start with: ollama serve"
                )
            except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
                last_error = exc
                logger.warning("Ollama attempt %d failed: %s", attempt + 1, exc)
        raise LLMProviderError(f"Ollama provider failed after retries: {last_error}") from last_error
