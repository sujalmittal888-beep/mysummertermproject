"""Business-rule validation applied to a schema-valid task plan.

Pydantic guarantees shape and types; this module enforces the semantic
rules that must hold before a plan may proceed to graph generation:
unique ids, approved actions, dependency integrity, conditional consistency.
"""
from __future__ import annotations

from collections import Counter

from taskflow.application.schemas import TaskPlanSchema, ValidationIssue
from taskflow.domain.action_registry import APPROVED_ACTIONS


class BusinessRuleValidator:
    """Validates domain rules on a parsed TaskPlanSchema."""

    def validate(self, plan: TaskPlanSchema) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        issues += self._check_unique_ids(plan)
        issues += self._check_actions(plan)
        issues += self._check_dependency_integrity(plan)
        issues += self._check_conditional_consistency(plan)
        return issues

    @staticmethod
    def _check_unique_ids(plan: TaskPlanSchema) -> list[ValidationIssue]:
        counts = Counter(t.id for t in plan.tasks)
        return [
            ValidationIssue(
                check="unique_ids",
                message=f"Duplicate task id {tid!r} appears {n} times",
                location=tid,
            )
            for tid, n in counts.items()
            if n > 1
        ]

    @staticmethod
    def _check_actions(plan: TaskPlanSchema) -> list[ValidationIssue]:
        return [
            ValidationIssue(
                check="action_registry",
                message=(
                    f"Action {t.action!r} is not in the approved registry "
                    f"{sorted(APPROVED_ACTIONS)}"
                ),
                location=t.id,
            )
            for t in plan.tasks
            if t.action not in APPROVED_ACTIONS
        ]

    @staticmethod
    def _check_dependency_integrity(plan: TaskPlanSchema) -> list[ValidationIssue]:
        known = {t.id for t in plan.tasks}
        issues: list[ValidationIssue] = []
        for t in plan.tasks:
            seen: set[str] = set()
            for dep in t.depends_on:
                if dep not in known:
                    issues.append(
                        ValidationIssue(
                            check="dependency_integrity",
                            message=f"Task {t.id!r} depends on unknown task {dep!r}",
                            location=t.id,
                        )
                    )
                if dep == t.id:
                    issues.append(
                        ValidationIssue(
                            check="dependency_integrity",
                            message=f"Task {t.id!r} depends on itself",
                            location=t.id,
                        )
                    )
                if dep in seen:
                    issues.append(
                        ValidationIssue(
                            check="dependency_integrity",
                            severity="warning",
                            message=f"Task {t.id!r} lists duplicate dependency {dep!r}",
                            location=t.id,
                        )
                    )
                seen.add(dep)
        return issues

    @staticmethod
    def _check_conditional_consistency(plan: TaskPlanSchema) -> list[ValidationIssue]:
        """Conditional siblings (same parent) must not duplicate conditions."""
        issues: list[ValidationIssue] = []
        children_by_parent: dict[str, list[str]] = {}
        by_id = {t.id: t for t in plan.tasks}
        for t in plan.tasks:
            for dep in t.depends_on:
                children_by_parent.setdefault(dep, []).append(t.id)
        for parent, children in children_by_parent.items():
            conds = [
                (cid, by_id[cid].condition)
                for cid in children
                if cid in by_id and by_id[cid].condition is not None
            ]
            seen: dict[str, str] = {}
            for cid, cond in conds:
                assert cond is not None
                key = cond.strip().lower()
                if key in seen:
                    issues.append(
                        ValidationIssue(
                            check="conditional_consistency",
                            message=(
                                f"Tasks {seen[key]!r} and {cid!r} branch from {parent!r} "
                                f"with the same condition {cond!r}"
                            ),
                            location=cid,
                        )
                    )
                seen[key] = cid
        return issues
