"""Structured error handling: maps domain exceptions to HTTP responses."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from taskflow.domain.exceptions import (
    ArtifactNotFoundError,
    DomainRuleError,
    GraphValidationError,
    LLMProviderError,
    SchemaValidationError,
)
from taskflow.logging_config import get_logger

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SchemaValidationError)
    async def schema_error(_: Request, exc: SchemaValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "schema_validation_failed", "detail": str(exc),
                     "errors": exc.errors},
        )

    @app.exception_handler(DomainRuleError)
    async def domain_error(_: Request, exc: DomainRuleError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "domain_rule_violation", "detail": str(exc)},
        )

    @app.exception_handler(LLMProviderError)
    async def llm_error(_: Request, exc: LLMProviderError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"error": "llm_provider_error", "detail": str(exc)},
        )

    @app.exception_handler(GraphValidationError)
    async def graph_error(_: Request, exc: GraphValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "graph_validation_failed", "detail": str(exc),
                     "report": exc.report},
        )

    @app.exception_handler(ArtifactNotFoundError)
    async def artifact_error(_: Request, exc: ArtifactNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "not_found", "detail": str(exc)})
