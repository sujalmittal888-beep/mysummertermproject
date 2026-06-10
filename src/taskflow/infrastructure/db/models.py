"""SQLAlchemy 2.0 ORM models (PostgreSQL in production, SQLite for tests)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class InstructionRecord(Base):
    __tablename__ = "instructions"

    pipeline_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    plan: Mapped[PlanRecord | None] = relationship(back_populates="instruction_rec")
    validation: Mapped[ValidationRecord | None] = relationship(back_populates="instruction_rec")
    export: Mapped[ExportRecord | None] = relationship(back_populates="instruction_rec")


class PlanRecord(Base):
    __tablename__ = "task_plans"

    pipeline_id: Mapped[str] = mapped_column(
        ForeignKey("instructions.pipeline_id"), primary_key=True
    )
    plan_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    instruction_rec: Mapped[InstructionRecord] = relationship(back_populates="plan")


class ValidationRecord(Base):
    __tablename__ = "validation_reports"

    pipeline_id: Mapped[str] = mapped_column(
        ForeignKey("instructions.pipeline_id"), primary_key=True
    )
    report_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    instruction_rec: Mapped[InstructionRecord] = relationship(back_populates="validation")


class ExportRecord(Base):
    __tablename__ = "exports"

    pipeline_id: Mapped[str] = mapped_column(
        ForeignKey("instructions.pipeline_id"), primary_key=True
    )
    artifacts_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    instruction_rec: Mapped[InstructionRecord] = relationship(back_populates="export")
