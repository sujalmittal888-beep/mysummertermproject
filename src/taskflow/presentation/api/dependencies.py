"""Composition root: dependency injection container for the API layer."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from taskflow.application.interfaces import LLMProvider, PlanRepository
from taskflow.application.services import InstructionParsingService
from taskflow.application.use_cases.process_instruction import ProcessInstructionUseCase
from taskflow.application.validation.business_rules import BusinessRuleValidator
from taskflow.config import Settings, get_settings
from taskflow.infrastructure.db.repositories import SqlAlchemyPlanRepository
from taskflow.infrastructure.db.session import create_db_engine, create_session_factory, init_db
from taskflow.infrastructure.export.artifact_service import ArtifactExportService
from taskflow.infrastructure.graph.builder import NetworkXGraphBuilder
from taskflow.infrastructure.llm.factory import create_llm_provider
from taskflow.infrastructure.validation.engine import GraphValidationEngine
from taskflow.infrastructure.visualization.renderer import GraphVisualizationService


@dataclass(slots=True)
class Container:
    settings: Settings
    provider: LLMProvider
    parser: InstructionParsingService
    repository: PlanRepository
    exporter: ArtifactExportService
    use_case: ProcessInstructionUseCase


def build_container(settings: Settings) -> Container:
    provider = create_llm_provider(settings)
    parser = InstructionParsingService(provider, BusinessRuleValidator())
    engine = create_db_engine(settings.database_url)
    init_db(engine)
    repository = SqlAlchemyPlanRepository(create_session_factory(engine))
    exporter = ArtifactExportService(settings.artifact_dir)
    use_case = ProcessInstructionUseCase(
        provider=provider,
        parser=parser,
        graph_builder=NetworkXGraphBuilder(),
        graph_validator=GraphValidationEngine(),
        visualizer=GraphVisualizationService(),
        exporter=exporter,
        repository=repository,
    )
    return Container(
        settings=settings, provider=provider, parser=parser,
        repository=repository, exporter=exporter, use_case=use_case,
    )


@lru_cache
def get_container() -> Container:
    return build_container(get_settings())
