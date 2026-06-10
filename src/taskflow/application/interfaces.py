"""Application-layer ports (interfaces).

Concrete adapters live in the infrastructure layer; the application layer
depends only on these protocols (Dependency Inversion).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import networkx as nx

from taskflow.application.schemas import ValidationReport
from taskflow.domain.entities import TaskPlan


class LLMProvider(Protocol):
    """Port for any LLM capable of emitting a JSON task schema."""

    @property
    def name(self) -> str: ...

    def generate_task_json(self, instruction: str) -> str:
        """Return raw JSON text for the given instruction. JSON only."""
        ...


class GraphBuilder(Protocol):
    """Port for building a NetworkX DAG from a validated task plan."""

    def build(self, plan: TaskPlan) -> nx.DiGraph: ...


class GraphValidator(Protocol):
    """Port for the graph validation engine."""

    def validate(self, graph: nx.DiGraph, plan: TaskPlan) -> ValidationReport: ...


class VisualizationService(Protocol):
    """Port for rendering graph artifacts."""

    def render_png(self, graph: nx.DiGraph, path: Path) -> Path: ...
    def render_html(self, graph: nx.DiGraph, path: Path) -> Path: ...
    def export_graphml(self, graph: nx.DiGraph, path: Path) -> Path: ...


class PlanRepository(Protocol):
    """Port for persistence of pipeline records."""

    def save_instruction(self, pipeline_id: str, instruction: str, provider: str) -> None: ...
    def save_plan(self, pipeline_id: str, plan_json: dict[str, Any]) -> None: ...
    def save_validation(self, pipeline_id: str, report: dict[str, Any]) -> None: ...
    def save_exports(self, pipeline_id: str, artifacts: dict[str, str]) -> None: ...
    def get_plan(self, pipeline_id: str) -> dict[str, Any] | None: ...
    def get_validation(self, pipeline_id: str) -> dict[str, Any] | None: ...
    def get_exports(self, pipeline_id: str) -> dict[str, str] | None: ...
