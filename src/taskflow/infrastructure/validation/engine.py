"""Validation Engine: composes all graph validators into one report."""
from __future__ import annotations

from datetime import UTC, datetime

import networkx as nx

from taskflow.application.schemas import CheckResult, ValidationReport
from taskflow.domain.entities import TaskPlan
from taskflow.infrastructure.validation.validators import (
    ActionRegistryValidator,
    BaseValidator,
    ConditionalLogicValidator,
    DagValidator,
    DependencyValidator,
    GraphConsistencyValidator,
    ReachabilityValidator,
    StructuralValidator,
)
from taskflow.logging_config import get_logger

logger = get_logger(__name__)


class GraphValidationEngine:
    """Runs every registered validator and aggregates a ValidationReport."""

    def __init__(self, validators: list[BaseValidator] | None = None) -> None:
        self._validators: list[BaseValidator] = validators or [
            DagValidator(),
            DependencyValidator(),
            ReachabilityValidator(),
            ActionRegistryValidator(),
            ConditionalLogicValidator(),
            StructuralValidator(),
            GraphConsistencyValidator(),
        ]

    def validate(self, graph: nx.DiGraph, plan: TaskPlan) -> ValidationReport:
        results: dict[str, CheckResult] = {}
        for validator in self._validators:
            result = validator.check(graph, plan)
            results[validator.name] = result
            logger.info("Validator %s: %s", validator.name, result.status)

        issues = [issue for r in results.values() for issue in r.issues]
        valid = all(r.passed for r in results.values())
        return ValidationReport(
            valid=valid,
            cycle_check=results["cycle_check"].status,
            dependency_check=results["dependency_check"].status,
            reachability_check=results["reachability_check"].status,
            action_check=results["action_check"].status,
            conditional_check=results["conditional_check"].status,
            structural_check=results["structural_check"].status,
            consistency_check=results["consistency_check"].status,
            issues=issues,
            node_count=graph.number_of_nodes(),
            edge_count=graph.number_of_edges(),
            timestamp=datetime.now(UTC).isoformat(),
        )
