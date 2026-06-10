"""Initial schema: instructions, task_plans, validation_reports, exports.

Revision ID: 0001
Revises:
Create Date: 2026-06-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "instructions",
        sa.Column("pipeline_id", sa.String(32), primary_key=True),
        sa.Column("instruction", sa.Text, nullable=False),
        sa.Column("provider", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for table, col in (
        ("task_plans", "plan_json"),
        ("validation_reports", "report_json"),
        ("exports", "artifacts_json"),
    ):
        op.create_table(
            table,
            sa.Column(
                "pipeline_id", sa.String(32),
                sa.ForeignKey("instructions.pipeline_id"), primary_key=True,
            ),
            sa.Column(col, sa.JSON, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    for table in ("exports", "validation_reports", "task_plans", "instructions"):
        op.drop_table(table)
