"""Unit tests: NetworkX graph builder."""
import networkx as nx

from taskflow.application.mappers import schema_to_entity
from taskflow.infrastructure.graph.builder import NetworkXGraphBuilder


def test_builds_dag_with_expected_topology(example_plan):
    graph = NetworkXGraphBuilder().build(schema_to_entity(example_plan))
    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 6
    assert graph.number_of_edges() == 5
    assert nx.is_directed_acyclic_graph(graph)
    assert set(graph.successors("T4")) == {"T5A", "T5B"}


def test_node_attributes_complete(example_plan):
    graph = NetworkXGraphBuilder().build(schema_to_entity(example_plan))
    data = graph.nodes["T1"]
    assert data["task_id"] == "T1"
    assert data["action"] == "navigate"
    assert data["description"] == "Navigate to Shelf A"
    assert data["condition"] is None
    assert data["metadata"] == {"location": "Shelf A"}


def test_edge_attributes_mark_conditionals(example_plan):
    graph = NetworkXGraphBuilder().build(schema_to_entity(example_plan))
    seq = graph.edges["T1", "T2"]
    assert seq["dependency_type"] == "sequential"
    assert seq["conditional"] is False
    cond = graph.edges["T4", "T5A"]
    assert cond["dependency_type"] == "conditional"
    assert cond["conditional"] is True
    assert cond["condition"] == "undamaged"
