"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI

from taskflow import __version__
from taskflow.config import get_settings
from taskflow.logging_config import configure_logging
from taskflow.presentation.api.error_handlers import register_error_handlers
from taskflow.presentation.api.routes.ollama import router as ollama_router
from taskflow.presentation.api.routes.pipeline import router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title="Language-to-Task Flow Graph Generator",
        description=(
            "Converts natural language industrial instructions into a validated "
            "Task Flow Graph (DAG) with downloadable artifacts. The pipeline "
            "terminates after graph validation and export - there is no "
            "execution engine, robot control, or ROS integration."
        ),
        version=__version__,
    )
    register_error_handlers(app)
    app.include_router(router)
    app.include_router(ollama_router)
    return app


app = create_app()
