"""LLM provider abstraction layer.

Each provider adapter is responsible for exactly one thing: returning raw
JSON text conforming to the task schema contract. Providers never build
graphs, never emit code, and never produce execution plans.
"""
from __future__ import annotations

import abc

from taskflow.application.schemas import TaskPlanSchema
from taskflow.domain.action_registry import APPROVED_ACTIONS

SYSTEM_PROMPT = f"""You are an industrial task-planning parser.

Convert the user's natural language industrial instruction into a JSON task
schema. Respond with ONLY a valid JSON object - no markdown, no code fences,
no explanations, no extra text.

Rules:
- Output must conform exactly to this JSON Schema:
{TaskPlanSchema.model_json_schema()}
- "action" must be one of: {sorted(APPROVED_ACTIONS)}
- Task ids must be unique short identifiers (T1, T2, T3A...).
- "depends_on" lists ids of tasks that must complete first.
- Use "condition" only for conditional branches (e.g. "damaged"/"undamaged");
  otherwise use null.
- Decompose compound instructions into atomic steps (navigate, locate, pick,
  inspect, place, ...). Include relevant locations/objects in "metadata".
- Do NOT output graph structures, code, robot commands, or execution plans.
"""


class BaseLLMProvider(abc.ABC):
    """Abstract base for provider adapters."""

    def __init__(self, model: str, timeout: float = 60.0, max_retries: int = 2) -> None:
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    def model(self) -> str:
        return self._model

    @abc.abstractmethod
    def generate_task_json(self, instruction: str) -> str:
        """Return raw JSON text for the instruction."""
