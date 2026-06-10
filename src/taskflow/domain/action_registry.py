"""Approved action registry.

Single source of truth for which actions a task plan may contain. The
registry is a domain concern: it encodes the business rule "only these
operations are plannable", independent of any LLM or graph library.
"""
from taskflow.domain.value_objects import ActionType

APPROVED_ACTIONS: frozenset[str] = ActionType.allowed()


def is_approved(action: str) -> bool:
    return action in APPROVED_ACTIONS
