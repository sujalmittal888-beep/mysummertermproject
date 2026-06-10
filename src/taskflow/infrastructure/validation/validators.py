"""Individual graph validators.

Each validator is a small, single-responsibility check that inspects the
built NetworkX graph (and, where useful, the source TaskPlan) and returns a
``CheckResult``. The engine composes them into a full report.
"""
from __future__ import annotations

import abc

import networkx as nx

from taskflow.application.schemas import CheckResult, ValidationIssue
from taskflow.domain.action_registry import APPROVED_ACTIONS
from taskflow.domain.entities import TaskPlan


class BaseValidator(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult: ...

    def _result(self, issues: list[ValidationIssue]) -> CheckResult:
        errors = [i for i in issues if i.severity == "error"]
        return CheckResult(name=self.name, passed=not errors, issues=issues)


class DagValidator(BaseValidator):
    """Validation 1: graph must be a directed acyclic graph."""

    name = "cycle_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        if not graph.is_directed():
            issues.append(
                ValidationIssue(check=self.name, message="Graph is not directed")
            )
        elif not nx.is_directed_acyclic_graph(graph):
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles[:10]:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Cycle detected: {' -> '.join(cycle + [cycle[0]])}",
                    )
                )
        return self._result(issues)


class DependencyValidator(BaseValidator):
    """Validation 2: all declared dependencies resolve to real nodes/edges."""

    name = "dependency_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        for task in plan.tasks:
            for dep in task.depends_on:
                if dep.value not in graph:
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=f"Task {task.id} references missing node {dep}",
                            location=task.id.value,
                        )
                    )
                elif not graph.has_edge(dep.value, task.id.value):
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=f"Edge {dep} -> {task.id} missing from graph",
                            location=task.id.value,
                        )
                    )
        for u, v in graph.edges:
            if u not in graph.nodes or v not in graph.nodes:  # pragma: no cover - defensive
                issues.append(
                    ValidationIssue(check=self.name, message=f"Broken edge {u} -> {v}")
                )
        return self._result(issues)


class ReachabilityValidator(BaseValidator):
    """Validation 3: every node reachable from a root; no isolated components."""

    name = "reachability_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        if graph.number_of_nodes() == 0:
            issues.append(ValidationIssue(check=self.name, message="Graph has no nodes"))
            return self._result(issues)

        for node in nx.isolates(graph):
            if graph.number_of_nodes() > 1:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Node {node} is isolated (no edges)",
                        location=str(node),
                    )
                )

        components = list(nx.weakly_connected_components(graph))
        if len(components) > 1:
            issues.append(
                ValidationIssue(
                    check=self.name,
                    message=(
                        f"Graph has {len(components)} disconnected components; "
                        "expected a single connected task flow"
                    ),
                )
            )

        roots = [n for n, deg in graph.in_degree() if deg == 0]
        if not roots and graph.number_of_nodes() > 0:
            issues.append(
                ValidationIssue(check=self.name, message="Graph has no root (entry) node")
            )
        else:
            reachable: set[str] = set()
            for root in roots:
                reachable |= {root} | nx.descendants(graph, root)
            unreachable = set(graph.nodes) - reachable
            for node in sorted(unreachable):
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Node {node} is not reachable from any root",
                        location=str(node),
                    )
                )
        return self._result(issues)


class ActionRegistryValidator(BaseValidator):
    """Validation 4: every node's action must be in the approved registry."""

    name = "action_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        for node, data in graph.nodes(data=True):
            action = data.get("action")
            if action not in APPROVED_ACTIONS:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Node {node} has unapproved action {action!r}",
                        location=str(node),
                    )
                )
        return self._result(issues)


class ConditionalLogicValidator(BaseValidator):
    """Validation 5: branch structures are well-formed and non-contradictory."""

    name = "conditional_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        for parent in graph.nodes:
            children = list(graph.successors(parent))
            conditional = [
                c for c in children if graph.nodes[c].get("condition") is not None
            ]
            if not conditional:
                continue
            seen: dict[str, str] = {}
            for child in conditional:
                cond = str(graph.nodes[child]["condition"]).strip().lower()
                if not cond:
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=f"Node {child} has an empty condition",
                            location=str(child),
                        )
                    )
                    continue
                if cond in seen:
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=(
                                f"Contradictory branch: {seen[cond]} and {child} both "
                                f"branch from {parent} on condition {cond!r}"
                            ),
                            location=str(child),
                        )
                    )
                seen[cond] = str(child)
            if len(conditional) == 1 and len(children) == 1:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        severity="warning",
                        message=(
                            f"Node {parent} has a single conditional branch "
                            f"({conditional[0]}); the complementary outcome is unhandled"
                        ),
                        location=str(parent),
                    )
                )
            # Every conditional branch must be reachable (in-edges exist by construction)
        return self._result(issues)


class StructuralValidator(BaseValidator):
    """Validation 6: node/edge/metadata integrity and unique ids."""

    name = "structural_check"

    _REQUIRED_NODE_KEYS = ("task_id", "action", "description", "condition", "metadata")
    _REQUIRED_EDGE_KEYS = ("dependency_type", "conditional")

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        plan_ids = [t.id.value for t in plan.tasks]
        if len(plan_ids) != len(set(plan_ids)):
            issues.append(ValidationIssue(check=self.name, message="Duplicate task ids in plan"))
        if set(plan_ids) != set(graph.nodes):
            issues.append(
                ValidationIssue(
                    check=self.name,
                    message="Graph nodes do not match plan task ids exactly",
                )
            )
        for node, data in graph.nodes(data=True):
            for key in self._REQUIRED_NODE_KEYS:
                if key not in data:
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=f"Node {node} missing attribute {key!r}",
                            location=str(node),
                        )
                    )
            if data.get("task_id") != node:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Node {node} task_id attribute mismatch",
                        location=str(node),
                    )
                )
            if not isinstance(data.get("metadata", {}), dict):
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Node {node} metadata is not a mapping",
                        location=str(node),
                    )
                )
        for u, v, data in graph.edges(data=True):
            for key in self._REQUIRED_EDGE_KEYS:
                if key not in data:
                    issues.append(
                        ValidationIssue(
                            check=self.name,
                            message=f"Edge {u}->{v} missing attribute {key!r}",
                        )
                    )
        return self._result(issues)


class GraphConsistencyValidator(BaseValidator):
    """Validation 7: DAG topology, no duplicate edges, valid parent-child links."""

    name = "consistency_check"

    def check(self, graph: nx.DiGraph, plan: TaskPlan) -> CheckResult:
        issues: list[ValidationIssue] = []
        for u, v in graph.edges:
            if u == v:
                issues.append(
                    ValidationIssue(check=self.name, message=f"Self-loop on node {u}")
                )
        # nx.DiGraph cannot hold parallel edges, but plan-level duplicates collapse
        # silently; verify edge counts match the declared (deduplicated) dependencies.
        declared = {
            (dep.value, task.id.value) for task in plan.tasks for dep in task.depends_on
        }
        if len(declared) != graph.number_of_edges():
            issues.append(
                ValidationIssue(
                    check=self.name,
                    message=(
                        f"Edge count mismatch: plan declares {len(declared)} unique "
                        f"dependencies, graph has {graph.number_of_edges()} edges"
                    ),
                )
            )
        if nx.is_directed_acyclic_graph(graph):
            try:
                list(nx.topological_sort(graph))
            except nx.NetworkXError as exc:  # pragma: no cover - defensive
                issues.append(
                    ValidationIssue(check=self.name, message=f"Topological sort failed: {exc}")
                )
        else:
            issues.append(
                ValidationIssue(check=self.name, message="Graph topology is not a valid DAG")
            )
        for u, v, data in graph.edges(data=True):
            child_cond = graph.nodes[v].get("condition")
            if data.get("conditional") and child_cond is None:
                issues.append(
                    ValidationIssue(
                        check=self.name,
                        message=f"Edge {u}->{v} marked conditional but child has no condition",
                    )
                )
        return self._result(issues)
