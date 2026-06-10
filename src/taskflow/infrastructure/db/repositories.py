"""Repository pattern implementation over SQLAlchemy."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from taskflow.infrastructure.db.models import (
    ExportRecord,
    InstructionRecord,
    PlanRecord,
    ValidationRecord,
)
from taskflow.infrastructure.db.session import session_scope


class SqlAlchemyPlanRepository:
    """Persists pipeline records: instructions, plans, reports, export metadata."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    def save_instruction(self, pipeline_id: str, instruction: str, provider: str) -> None:
        with session_scope(self._factory) as s:
            s.add(InstructionRecord(
                pipeline_id=pipeline_id, instruction=instruction, provider=provider
            ))

    def save_plan(self, pipeline_id: str, plan_json: dict[str, Any]) -> None:
        with session_scope(self._factory) as s:
            s.merge(PlanRecord(pipeline_id=pipeline_id, plan_json=plan_json))

    def save_validation(self, pipeline_id: str, report: dict[str, Any]) -> None:
        with session_scope(self._factory) as s:
            s.merge(ValidationRecord(pipeline_id=pipeline_id, report_json=report))

    def save_exports(self, pipeline_id: str, artifacts: dict[str, str]) -> None:
        with session_scope(self._factory) as s:
            s.merge(ExportRecord(pipeline_id=pipeline_id, artifacts_json=artifacts))

    def get_plan(self, pipeline_id: str) -> dict[str, Any] | None:
        with session_scope(self._factory) as s:
            rec = s.get(PlanRecord, pipeline_id)
            return dict(rec.plan_json) if rec else None

    def get_validation(self, pipeline_id: str) -> dict[str, Any] | None:
        with session_scope(self._factory) as s:
            rec = s.get(ValidationRecord, pipeline_id)
            return dict(rec.report_json) if rec else None

    def get_exports(self, pipeline_id: str) -> dict[str, str] | None:
        with session_scope(self._factory) as s:
            rec = s.get(ExportRecord, pipeline_id)
            return dict(rec.artifacts_json) if rec else None
