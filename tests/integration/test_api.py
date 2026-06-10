"""Integration tests: full pipeline through the FastAPI surface."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from taskflow.config import Settings
from taskflow.presentation.api.app import create_app
from taskflow.presentation.api.dependencies import build_container, get_container

INSTRUCTION = (
    "Pick the red box from Shelf A, inspect it, "
    "and sort damaged items onto Conveyor Belt 3."
)


@pytest.fixture
def client(tmp_path):
    settings = Settings(
        env="test",
        llm_provider="mock",
        database_url=f"sqlite:///{tmp_path}/test.db",
        artifact_dir=tmp_path / "artifacts",
    )
    container = build_container(settings)
    app = create_app()
    app.dependency_overrides[get_container] = lambda: container
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_full_pipeline_endpoint(client):
    resp = client.post("/instructions", json={"instruction": INSTRUCTION})
    assert resp.status_code == 201
    body = resp.json()
    assert body["validation"]["valid"] is True
    assert set(body["artifacts"]) == {
        "task_plan.json", "validation_report.json", "task_graph.png",
        "task_graph.html", "task_graph.graphml", "task_flow_package.zip",
    }
    pid = body["pipeline_id"]

    # Stored graph retrieval
    g = client.get(f"/graph/{pid}")
    assert g.status_code == 200
    assert g.json()["node_count"] == len(body["plan"]["tasks"])

    # Stored validation report retrieval
    v = client.get(f"/validation/{pid}")
    assert v.status_code == 200 and v.json()["valid"] is True

    # Artifact downloads
    for name, media in [
        ("task_plan.json", "application/json"),
        ("task_graph.png", "image/png"),
        ("task_flow_package.zip", "application/zip"),
    ]:
        d = client.get(f"/downloads/{pid}/{name}")
        assert d.status_code == 200
        assert d.headers["content-type"].startswith(media)


def test_parse_then_graph_then_validate_then_export(client):
    parsed = client.post("/parse", json={"instruction": INSTRUCTION}).json()
    plan = parsed["plan"]

    g = client.post("/graph", json={"plan": plan})
    assert g.status_code == 200 and g.json()["node_count"] >= 4

    v = client.post("/validate", json={"plan": plan})
    assert v.status_code == 200 and v.json()["valid"] is True

    e = client.post("/export", json={"plan": plan})
    assert e.status_code == 200
    assert "task_flow_package.zip" in e.json()["artifacts"]


def test_invalid_plan_rejected_with_422(client):
    bad_plan = {
        "version": "1.0",
        "instruction": "bad",
        "tasks": [
            {"id": "T1", "action": "pick", "description": "a", "depends_on": ["GHOST"]},
        ],
    }
    resp = client.post("/validate", json={"plan": bad_plan})
    assert resp.status_code == 422
    assert resp.json()["error"] == "schema_validation_failed"


def test_unknown_pipeline_returns_404(client):
    assert client.get("/graph/doesnotexist").status_code == 404
    assert client.get("/validation/doesnotexist").status_code == 404
    assert client.get("/downloads/doesnotexist/task_plan.json").status_code == 404
