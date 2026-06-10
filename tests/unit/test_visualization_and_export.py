"""Unit tests: visualization renderers and export service."""
import json
import zipfile

import networkx as nx
import pytest

from taskflow.application.mappers import schema_to_entity
from taskflow.domain.exceptions import ArtifactNotFoundError
from taskflow.infrastructure.export.artifact_service import ArtifactExportService
from taskflow.infrastructure.graph.builder import NetworkXGraphBuilder
from taskflow.infrastructure.validation.engine import GraphValidationEngine
from taskflow.infrastructure.visualization.renderer import GraphVisualizationService


@pytest.fixture
def graph(example_plan):
    return NetworkXGraphBuilder().build(schema_to_entity(example_plan))


def test_png_render(graph, tmp_path):
    out = GraphVisualizationService().render_png(graph, tmp_path / "task_graph.png")
    assert out.exists() and out.stat().st_size > 1000


def test_html_render(graph, tmp_path):
    out = GraphVisualizationService().render_html(graph, tmp_path / "task_graph.html")
    text = out.read_text(encoding="utf-8")
    assert "T5A" in text and "vis-network" in text.lower()


def test_graphml_export_round_trips(graph, tmp_path):
    out = GraphVisualizationService().export_graphml(graph, tmp_path / "task_graph.graphml")
    loaded = nx.read_graphml(out)
    assert set(loaded.nodes) == set(graph.nodes)
    assert json.loads(loaded.nodes["T1"]["metadata"]) == {"location": "Shelf A"}


def test_export_all_creates_zip_bundle(example_plan, graph, tmp_artifacts):
    svc = ArtifactExportService(tmp_artifacts)
    report = GraphValidationEngine().validate(graph, schema_to_entity(example_plan))
    viz = GraphVisualizationService()
    out = svc.artifact_dir("abc123")
    extra = [
        viz.render_png(graph, out / "task_graph.png"),
        viz.render_html(graph, out / "task_graph.html"),
        viz.export_graphml(graph, out / "task_graph.graphml"),
    ]
    artifacts = svc.export_all("abc123", example_plan, report, extra)
    assert set(artifacts) == {
        "task_plan.json", "validation_report.json", "task_graph.png",
        "task_graph.html", "task_graph.graphml", "task_flow_package.zip",
    }
    with zipfile.ZipFile(artifacts["task_flow_package.zip"]) as zf:
        assert len(zf.namelist()) == 5
    report_payload = json.loads((out / "validation_report.json").read_text())
    assert report_payload["valid"] is True and report_payload["cycle_check"] == "passed"


def test_resolve_blocks_unknown_and_traversal(tmp_artifacts):
    svc = ArtifactExportService(tmp_artifacts)
    with pytest.raises(ArtifactNotFoundError):
        svc.resolve("abc123", "../../etc/passwd")
    with pytest.raises(ArtifactNotFoundError):
        svc.resolve("missing", "task_plan.json")
