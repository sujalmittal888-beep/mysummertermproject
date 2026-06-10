"""Domain and application exception hierarchy."""
from __future__ import annotations

from typing import Any


class TaskFlowError(Exception):
    """Base class for all TaskFlow errors."""


class DomainRuleError(TaskFlowError):
    """A domain invariant was violated while constructing entities."""


class SchemaValidationError(TaskFlowError):
    """The LLM-produced JSON failed schema or business-rule validation."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class LLMProviderError(TaskFlowError):
    """The LLM provider failed or returned unusable output."""


class GraphValidationError(TaskFlowError):
    """The generated graph failed one or more validation checks."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report or {}


class ArtifactNotFoundError(TaskFlowError):
    """A requested artifact or record does not exist."""
