"""Domain entities: the canonical in-memory representation of a task plan.

These entities are constructed only from a *validated* JSON task schema.
They carry the business rules of the planning domain and are persistence-
and framework-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from taskflow.domain.exceptions import DomainRuleError
from taskflow.domain.value_objects import ActionType, Condition, TaskId


@dataclass(slots=True)
class Task:
    """A single atomic step in an industrial task plan."""

    id: TaskId
    action: ActionType
    description: str
    depends_on: tuple[TaskId, ...] = ()
    condition: Condition | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_root(self) -> bool:
        return not self.depends_on

    @property
    def is_conditional(self) -> bool:
        return self.condition is not None


@dataclass(slots=True)
class TaskPlan:
    """Aggregate root: an ordered collection of tasks derived from one instruction."""

    version: str
    instruction: str
    tasks: list[Task]

    def __post_init__(self) -> None:
        ids = [t.id.value for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise DomainRuleError("Task ids must be unique within a plan")
        known = set(ids)
        for task in self.tasks:
            for dep in task.depends_on:
                if dep.value not in known:
                    raise DomainRuleError(f"Task {task.id} depends on unknown task {dep}")
                if dep.value == task.id.value:
                    raise DomainRuleError(f"Task {task.id} depends on itself")

    def get(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id.value == task_id:
                return task
        raise KeyError(task_id)

    @property
    def roots(self) -> list[Task]:
        return [t for t in self.tasks if t.is_root]
