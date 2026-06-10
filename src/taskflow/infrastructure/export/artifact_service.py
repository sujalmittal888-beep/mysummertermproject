"""Export & download system: writes artifacts and bundles the zip package."""
from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from taskflow.application.schemas import TaskPlanSchema, ValidationReport
from taskflow.domain.exceptions import ArtifactNotFoundError
from taskflow.logging_config import get_logger

logger = get_logger(__name__)

ARTIFACT_FILENAMES = (
    "task_plan.json",
    "validation_report.json",
    "task_graph.png",
    "task_graph.graphml",
    "task_graph.html",
    "task_flow_package.zip",
)


class ArtifactExportService:
    """Manages per-pipeline artifact directories and the zip bundle."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def artifact_dir(self, pipeline_id: str) -> Path:
        d = self._base_dir / pipeline_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def export_all(
        self,
        pipeline_id: str,
        plan: TaskPlanSchema,
        report: ValidationReport,
        extra_files: list[Path],
    ) -> dict[str, str]:
        out = self.artifact_dir(pipeline_id)

        plan_path = out / "task_plan.json"
        plan_payload = {
            "exported_at": datetime.now(UTC).isoformat(),
            "pipeline_id": pipeline_id,
            **plan.model_dump(),
        }
        plan_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")

        report_path = out / "validation_report.json"
        report_path.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")

        files = [plan_path, report_path, *extra_files]
        zip_path = out / "task_flow_package.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, arcname=f.name)
        files.append(zip_path)
        logger.info("Exported %d artifacts for pipeline %s", len(files), pipeline_id)
        return {f.name: str(f) for f in files}

    def resolve(self, pipeline_id: str, artifact_name: str) -> Path:
        """Resolve an artifact path safely (no traversal outside the artifact dir)."""
        if artifact_name not in ARTIFACT_FILENAMES:
            raise ArtifactNotFoundError(f"Unknown artifact {artifact_name!r}")
        path = (self._base_dir / pipeline_id / artifact_name).resolve()
        if not str(path).startswith(str(self._base_dir.resolve())) or not path.is_file():
            raise ArtifactNotFoundError(f"Artifact {artifact_name!r} not found for {pipeline_id}")
        return path
