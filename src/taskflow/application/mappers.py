"""Mapping between the JSON schema layer and domain entities."""
from __future__ import annotations

from taskflow.application.schemas import TaskItemSchema, TaskPlanSchema
from taskflow.domain.entities import Task, TaskPlan
from taskflow.domain.value_objects import ActionType, Condition, TaskId


def schema_to_entity(plan: TaskPlanSchema) -> TaskPlan:
    return TaskPlan(
        version=plan.version,
        instruction=plan.instruction,
        tasks=[_task_to_entity(t) for t in plan.tasks],
    )


def _task_to_entity(item: TaskItemSchema) -> Task:
    return Task(
        id=TaskId(item.id),
        action=ActionType(item.action),
        description=item.description,
        depends_on=tuple(TaskId(d) for d in item.depends_on),
        condition=Condition(item.condition) if item.condition else None,
        metadata=dict(item.metadata),
    )
