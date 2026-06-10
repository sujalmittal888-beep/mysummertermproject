"""Use case: full pipeline from natural language to exported artifacts.

Pipeline (and hard stop):
    NL instruction -> LLM -> JSON schema -> Pydantic + business rules
    -> NetworkX DAG -> graph validation -> visualization -> export.

The pipeline terminates after export generation. There is intentionally no
execution, scheduling, or robot-control step anywhere downstream.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx

from taskflow.application.interfaces import (
    GraphBuilder,
    GraphValidator,
    LLMProvider,
    PlanRepository,
    VisualizationService,
)
from taskflow.application.mappers import schema_to_entity
from taskflow.application.schemas import TaskPlanSchema, ValidationReport
from taskflow.application.services import InstructionParsingService
from taskflow.infrastructure.export.artifact_service import ArtifactExportService
from taskflow.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class PipelineResult:
    pipeline_id: str
    plan: TaskPlanSchema
    report: ValidationReport
    artifacts: dict[str, str]


class ProcessInstructionUseCase:
    """Orchestrates the end-to-end pipeline. No execution semantics."""

    def __init__(
        self,
        provider: LLMProvider,
        parser: InstructionParsingService,
        graph_builder: GraphBuilder,
        graph_validator: GraphValidator,
        visualizer: VisualizationService,
        exporter: ArtifactExportService,
        repository: PlanRepository,
    ) -> None:
        self._provider = provider
        self._parser = parser
        self._graph_builder = graph_builder
        self._graph_validator = graph_validator
        self._visualizer = visualizer
        self._exporter = exporter
        self._repository = repository

    def execute(self, instruction: str) -> PipelineResult:
        pipeline_id = uuid.uuid4().hex[:12]
        logger.info("Pipeline %s started for instruction: %s", pipeline_id, instruction)
        self._repository.save_instruction(pipeline_id, instruction, self._provider.name)

        # Phase 1-3: NL -> JSON -> schema + business-rule validation
        plan_schema = self._parser.parse_instruction(instruction)
        self._repository.save_plan(pipeline_id, plan_schema.model_dump())

        # Phase 4: validated JSON -> NetworkX DAG (graph built only from JSON)
        plan = schema_to_entity(plan_schema)
        graph = self._graph_builder.build(plan)

        # Phase 5: graph validation engine
        report = self._graph_validator.validate(graph, plan)
        self._repository.save_validation(pipeline_id, report.model_dump())

        # Phase 6-7: visualization + export (pipeline terminates here)
        artifacts = self._export(pipeline_id, plan_schema, graph, report)
        self._repository.save_exports(pipeline_id, artifacts)
        logger.info("Pipeline %s complete. valid=%s", pipeline_id, report.valid)
        return PipelineResult(pipeline_id, plan_schema, report, artifacts)

    def build_graph_payload(self, plan_schema: TaskPlanSchema) -> dict[str, Any]:
        """Build and serialize a graph (node-link JSON) without exporting."""
        plan = schema_to_entity(plan_schema)
        graph = self._graph_builder.build(plan)
        return nx.node_link_data(graph, edges="edges")

    def validate_plan(self, plan_schema: TaskPlanSchema) -> ValidationReport:
        plan = schema_to_entity(plan_schema)
        graph = self._graph_builder.build(plan)
        return self._graph_validator.validate(graph, plan)

    def _export(
        self,
        pipeline_id: str,
        plan_schema: TaskPlanSchema,
        graph: nx.DiGraph,
        report: ValidationReport,
    ) -> dict[str, str]:
        out_dir = self._exporter.artifact_dir(pipeline_id)
        png = self._visualizer.render_png(graph, out_dir / "task_graph.png")
        html = self._visualizer.render_html(graph, out_dir / "task_graph.html")
        graphml = self._visualizer.export_graphml(graph, out_dir / "task_graph.graphml")
        return self._exporter.export_all(
            pipeline_id=pipeline_id,
            plan=plan_schema,
            report=report,
            extra_files=[png, html, graphml],
        )


def make_pipeline_id() -> str:
    return uuid.uuid4().hex[:12]


__all__ = ["PipelineResult", "ProcessInstructionUseCase", "Path"]
