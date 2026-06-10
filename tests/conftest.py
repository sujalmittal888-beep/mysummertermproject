"""Shared test fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from taskflow.application.schemas import TaskPlanSchema

EXAMPLE_PLAN = {
    "version": "1.0",
    "instruction": "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3",
    "tasks": [
        {"id": "T1", "action": "navigate", "description": "Navigate to Shelf A",
         "depends_on": [], "condition": None, "metadata": {"location": "Shelf A"}},
        {"id": "T2", "action": "locate", "description": "Locate red box",
         "depends_on": ["T1"], "condition": None},
        {"id": "T3", "action": "pick", "description": "Pick red box",
         "depends_on": ["T2"], "condition": None},
        {"id": "T4", "action": "inspect", "description": "Inspect box",
         "depends_on": ["T3"], "condition": None},
        {"id": "T5A", "action": "place", "description": "Place on Conveyor Belt 3",
         "depends_on": ["T4"], "condition": "undamaged"},
        {"id": "T5B", "action": "place", "description": "Place in reject bin",
         "depends_on": ["T4"], "condition": "damaged"},
    ],
}


@pytest.fixture
def example_payload() -> dict:
    return json.loads(json.dumps(EXAMPLE_PLAN))


@pytest.fixture
def example_plan(example_payload: dict) -> TaskPlanSchema:
    return TaskPlanSchema.model_validate(example_payload)


@pytest.fixture
def tmp_artifacts(tmp_path: Path) -> Path:
    d = tmp_path / "artifacts"
    d.mkdir()
    return d
