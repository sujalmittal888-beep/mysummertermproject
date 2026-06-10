"""Unit tests: Pydantic schema validation."""
import pytest
from pydantic import ValidationError

from taskflow.application.schemas import TaskItemSchema, TaskPlanSchema


def test_valid_plan_parses(example_payload):
    plan = TaskPlanSchema.model_validate(example_payload)
    assert len(plan.tasks) == 6
    assert plan.tasks[0].action == "navigate"


def test_action_is_normalized():
    item = TaskItemSchema(id="T1", action="  PICK ", description="x")
    assert item.action == "pick"


def test_missing_required_field_fails():
    with pytest.raises(ValidationError):
        TaskItemSchema(id="T1", action="pick")  # type: ignore[call-arg]


def test_extra_fields_forbidden(example_payload):
    example_payload["tasks"][0]["robot_command"] = "MOVE J1"
    with pytest.raises(ValidationError):
        TaskPlanSchema.model_validate(example_payload)


def test_bad_task_id_pattern_fails():
    with pytest.raises(ValidationError):
        TaskItemSchema(id="bad id!", action="pick", description="x")


def test_empty_tasks_fails(example_payload):
    example_payload["tasks"] = []
    with pytest.raises(ValidationError):
        TaskPlanSchema.model_validate(example_payload)


def test_empty_condition_becomes_none():
    item = TaskItemSchema(id="T1", action="pick", description="x", condition="   ")
    assert item.condition is None
