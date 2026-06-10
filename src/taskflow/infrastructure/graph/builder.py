"""Graph Builder Service.

Builds a NetworkX ``DiGraph`` exclusively from a validated, domain-level
``TaskPlan``. The LLM is never involved in graph construction; the JSON
schema (via the domain entities) is the only input.
"""
from __future__ import annotations

import networkx as nx

from taskflow.domain.entities import TaskPlan
from taskflow.logging_config import get_logger

logger = get_logger(__name__)


class NetworkXGraphBuilder:
    """Constructs the Task Flow Graph (DAG) from a validated TaskPlan."""

    def build(self, plan: TaskPlan) -> nx.DiGraph:
        graph = nx.DiGraph(
            instruction=plan.instruction,
            schema_version=plan.version,
        )
        for task in plan.tasks:
            graph.add_node(
                task.id.value,
                task_id=task.id.value,
                action=task.action.value,
                description=task.description,
                condition=str(task.condition) if task.condition else None,
                metadata=dict(task.metadata),
            )
        for task in plan.tasks:
            for dep in task.depends_on:
                graph.add_edge(
                    dep.value,
                    task.id.value,
                    dependency_type="conditional" if task.is_conditional else "sequential",
                    conditional=task.is_conditional,
                    condition=str(task.condition) if task.condition else None,
                )
        logger.info(
            "Built graph: %d nodes, %d edges", graph.number_of_nodes(), graph.number_of_edges()
        )
        return graph
