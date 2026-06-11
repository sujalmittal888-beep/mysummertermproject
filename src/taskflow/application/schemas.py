"""Pydantic v2 schemas: the canonical JSON Task Schema contract.

The LLM's only permitted output is JSON conforming to ``TaskPlanSchema``.
Everything downstream (graph building, validation, export) derives from a
validated instance of this schema.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

TASK_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_\-]*$"


class TaskItemSchema(BaseModel):
    """One task entry inside the JSON task schema."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    id: str = Field(..., pattern=TASK_ID_PATTERN, max_length=64, description="Unique task id")
    action: str = Field(..., min_length=1, max_length=64, description="Action verb")
    description: str = Field(..., min_length=1, max_length=512)
    depends_on: list[str] = Field(default_factory=list, max_length=64)
    condition: str | None = Field(default=None, max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("action")
    @classmethod
    def normalize_action(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("condition")
    @classmethod
    def empty_condition_is_none(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            return None
        return v


class TaskPlanSchema(BaseModel):
    """Top-level JSON task schema produced by the LLM."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    version: str = Field(default="1.0", max_length=16)
    instruction: str = Field(..., min_length=1, max_length=2048)
    tasks: list[TaskItemSchema] = Field(..., min_length=1, max_length=256)


class ValidationIssue(BaseModel):
    """A single validation problem (schema, business rule, or graph level)."""

    check: str
    severity: str = "error"  # "error" | "warning"
    message: str
    location: str | None = None


class CheckResult(BaseModel):
    """Outcome of one named validation check."""

    name: str
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"


class ValidationReport(BaseModel):
    """Aggregated validation report covering all graph-level checks."""

    valid: bool
    cycle_check: str
    dependency_check: str
    reachability_check: str
    action_check: str
    conditional_check: str
    structural_check: str
    consistency_check: str
    issues: list[ValidationIssue] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    timestamp: str
