"""REST endpoints for the language-to-graph pipeline."""
from __future__ import annotations

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from taskflow import __version__
from taskflow.application.mappers import schema_to_entity
from taskflow.config import get_settings
from taskflow.domain.exceptions import ArtifactNotFoundError
from taskflow.presentation.api.dependencies import Container, get_container
from taskflow.presentation.api.dto import (
    ExportResponse,
    GraphResponse,
    HealthResponse,
    InstructionRequest,
    ParseResponse,
    PipelineResponse,
    PlanRequest,
    ProviderSwitchRequest,
    ProviderSwitchResponse,
)

router = APIRouter()

ContainerDep = Annotated[Container, Depends(get_container)]


def _downloads(pipeline_id: str, artifacts: dict[str, str]) -> dict[str, str]:
    return {name: f"/downloads/{pipeline_id}/{name}" for name in artifacts}


@router.post("/instructions", response_model=PipelineResponse, status_code=201,
             summary="Run the full pipeline: NL -> JSON -> DAG -> validation -> export")
def process_instruction(req: InstructionRequest, c: ContainerDep) -> PipelineResponse:
    result = c.use_case.execute(req.instruction)
    return PipelineResponse(
        pipeline_id=result.pipeline_id,
        plan=result.plan,
        validation=result.report,
        artifacts=result.artifacts,
        downloads=_downloads(result.pipeline_id, result.artifacts),
    )


@router.post("/parse", response_model=ParseResponse,
             summary="NL -> validated JSON task schema only (no graph, no export)")
def parse_instruction(req: InstructionRequest, c: ContainerDep) -> ParseResponse:
    plan = c.parser.parse_instruction(req.instruction)
    return ParseResponse(plan=plan, provider=c.provider.name)


@router.post("/graph", response_model=GraphResponse,
             summary="Validated JSON task schema -> NetworkX DAG (node-link JSON)")
def build_graph(req: PlanRequest, c: ContainerDep) -> GraphResponse:
    plan = c.parser.validate_payload(req.plan.model_dump())
    payload = c.use_case.build_graph_payload(plan)
    return GraphResponse(
        graph=payload,
        node_count=len(payload.get("nodes", [])),
        edge_count=len(payload.get("edges", [])),
    )


@router.post("/validate",
             summary="Validate a JSON task schema and its derived graph; returns the report")
def validate_plan(req: PlanRequest, c: ContainerDep) -> dict:
    plan = c.parser.validate_payload(req.plan.model_dump())
    report = c.use_case.validate_plan(plan)
    return report.model_dump()


@router.post("/export", response_model=ExportResponse,
             summary="Validate a JSON task schema and export all downloadable artifacts")
def export_plan(req: PlanRequest, c: ContainerDep) -> ExportResponse:
    plan_schema = c.parser.validate_payload(req.plan.model_dump())
    from taskflow.application.use_cases.process_instruction import make_pipeline_id
    pipeline_id = make_pipeline_id()
    c.repository.save_instruction(pipeline_id, plan_schema.instruction, "client-supplied-json")
    c.repository.save_plan(pipeline_id, plan_schema.model_dump())

    plan = schema_to_entity(plan_schema)
    graph = c.use_case._graph_builder.build(plan)  # noqa: SLF001 - composition-root access
    report = c.use_case._graph_validator.validate(graph, plan)  # noqa: SLF001
    c.repository.save_validation(pipeline_id, report.model_dump())
    artifacts = c.use_case._export(pipeline_id, plan_schema, graph, report)  # noqa: SLF001
    c.repository.save_exports(pipeline_id, artifacts)
    return ExportResponse(
        pipeline_id=pipeline_id, artifacts=artifacts,
        downloads=_downloads(pipeline_id, artifacts),
    )


@router.get("/graph/{pipeline_id}", response_model=GraphResponse,
            summary="Rebuild and return the stored graph for a pipeline run")
def get_graph(pipeline_id: str, c: ContainerDep) -> GraphResponse:
    stored = c.repository.get_plan(pipeline_id)
    if stored is None:
        raise ArtifactNotFoundError(f"No plan stored for pipeline {pipeline_id!r}")
    plan = c.parser.validate_payload(stored)
    payload = c.use_case.build_graph_payload(plan)
    return GraphResponse(
        graph=payload,
        node_count=len(payload.get("nodes", [])),
        edge_count=len(payload.get("edges", [])),
    )


@router.get("/validation/{pipeline_id}",
            summary="Return the stored validation report for a pipeline run")
def get_validation(pipeline_id: str, c: ContainerDep) -> dict:
    report = c.repository.get_validation(pipeline_id)
    if report is None:
        raise ArtifactNotFoundError(f"No validation report for pipeline {pipeline_id!r}")
    return report


@router.get("/downloads/{pipeline_id}/{artifact}",
            summary="Download a generated artifact")
def download_artifact(pipeline_id: str, artifact: str, c: ContainerDep) -> FileResponse:
    path = c.exporter.resolve(pipeline_id, artifact)
    media = {
        ".json": "application/json",
        ".png": "image/png",
        ".html": "text/html",
        ".graphml": "application/xml",
        ".zip": "application/zip",
    }.get(path.suffix, "application/octet-stream")
    return FileResponse(path, media_type=media, filename=path.name)


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health(c: ContainerDep) -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, provider=c.provider.name)


@router.patch("/provider", response_model=ProviderSwitchResponse, summary="Hot-swap LLM provider")
def switch_provider(req: ProviderSwitchRequest) -> ProviderSwitchResponse:
    VALID = {"openai", "anthropic", "gemini", "ollama", "mock"}
    if req.provider not in VALID:
        raise HTTPException(422, f"provider must be one of {sorted(VALID)}")

    # write into the process environment so get_settings() picks them up
    os.environ["TASKFLOW_LLM_PROVIDER"] = req.provider
    if req.model:
        os.environ["TASKFLOW_LLM_MODEL"] = req.model
    else:
        os.environ.pop("TASKFLOW_LLM_MODEL", None)
    if req.api_key:
        key_map = {"openai": "TASKFLOW_OPENAI_API_KEY",
                   "anthropic": "TASKFLOW_ANTHROPIC_API_KEY",
                   "gemini": "TASKFLOW_GEMINI_API_KEY"}
        env_key = key_map.get(req.provider)
        if env_key:
            os.environ[env_key] = req.api_key
    if req.base_url and req.provider == "ollama":
        os.environ["TASKFLOW_OLLAMA_BASE_URL"] = req.base_url

    # clear caches so the next request rebuilds with new settings
    get_settings.cache_clear()
    get_container.cache_clear()

    # rebuild now to surface config errors immediately (bad key, unreachable Ollama, etc.)
    from taskflow.presentation.api.dependencies import build_container
    try:
        build_container(get_settings())
    except Exception as exc:
        # roll back — restore previous container on next request via cache clear
        get_settings.cache_clear()
        get_container.cache_clear()
        raise HTTPException(400, str(exc)) from exc

    new_settings = get_settings()
    return ProviderSwitchResponse(
        provider=new_settings.llm_provider,
        model=new_settings.resolved_llm_model,
    )
