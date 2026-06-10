"""Request/response DTOs for the REST API (kept separate from domain schemas)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from taskflow.application.schemas import TaskPlanSchema, ValidationReport


class InstructionRequest(BaseModel):
    instruction: str = Field(..., min_length=3, max_length=2048)


class PlanRequest(BaseModel):
    plan: TaskPlanSchema


class ParseResponse(BaseModel):
    plan: TaskPlanSchema
    provider: str


class GraphResponse(BaseModel):
    graph: dict[str, Any]
    node_count: int
    edge_count: int


class PipelineResponse(BaseModel):
    pipeline_id: str
    plan: TaskPlanSchema
    validation: ValidationReport
    artifacts: dict[str, str]
    downloads: dict[str, str]


class ExportResponse(BaseModel):
    pipeline_id: str
    artifacts: dict[str, str]
    downloads: dict[str, str]


class HealthResponse(BaseModel):
    status: str
    version: str
    provider: str
