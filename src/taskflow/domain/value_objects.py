"""Domain value objects: immutable, validated primitives of the task domain."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class ActionType(StrEnum):
    """Approved action registry. Unknown actions must fail validation."""

    NAVIGATE = "navigate"
    LOCATE = "locate"
    PICK = "pick"
    PLACE = "place"
    INSPECT = "inspect"
    MOVE = "move"
    SCAN = "scan"
    SORT = "sort"
    TRANSFER = "transfer"

    @classmethod
    def allowed(cls) -> frozenset[str]:
        return frozenset(member.value for member in cls)


_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]*$")


@dataclass(frozen=True, slots=True)
class TaskId:
    """Validated task identifier."""

    value: str

    def __post_init__(self) -> None:
        if not _TASK_ID_RE.match(self.value):
            raise ValueError(f"Invalid task id: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Condition:
    """Branch condition attached to a task (e.g. 'damaged' / 'undamaged')."""

    expression: str

    def __post_init__(self) -> None:
        if not self.expression or not self.expression.strip():
            raise ValueError("Condition expression must be a non-empty string")

    def __str__(self) -> str:
        return self.expression
