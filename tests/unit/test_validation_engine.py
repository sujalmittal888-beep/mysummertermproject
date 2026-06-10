"""Unit tests: graph validation engine and individual validators."""
import networkx as nx

from taskflow.application.mappers import schema_to_entity
from taskflow.application.schemas import TaskPlanSchema
from taskflow.infrastructure.graph.builder import NetworkXGraphBuilder
from taskflow.infrastructure.validation.engine import GraphValidationEngine
from taskflow.infrastructure.validation.validators import (
    DagValidator,
    ReachabilityValidator,
)


def _build(payload):
    plan = schema_to_entity(TaskPlanSchema.model_validate(payload))
    return NetworkXGraphBuilder().build(plan), plan


def test_valid_plan_passes_all_checks(example_payload):
    graph, plan = _build(example_payload)
    report = GraphValidationEngine().validate(graph, plan)
    assert report.valid is True
    assert report.cycle_check == "passed"
    assert report.dependency_check == "passed"
    assert report.reachability_check == "passed"
    assert report.action_check == "passed"
    assert report.conditional_check == "passed"
    assert report.structural_check == "passed"
    assert report.consistency_check == "passed"
    assert report.node_count == 6 and report.edge_count == 5


def test_cycle_detected():
    payload = {
        "version": "1.0", "instruction": "cyclic",
        "tasks": [
            {"id": "A", "action": "pick", "description": "a", "depends_on": ["B"]},
            {"id": "B", "action": "place", "description": "b", "depends_on": ["A"]},
        ],
    }
    graph, plan = _build(payload)
    report = GraphValidationEngine().validate(graph, plan)
    assert report.valid is False
    assert report.cycle_check == "failed"
    assert any("Cycle" in i.message for i in report.issues)


def test_disconnected_component_detected():
    payload = {
        "version": "1.0", "instruction": "disconnected",
        "tasks": [
            {"id": "A", "action": "pick", "description": "a"},
            {"id": "B", "action": "place", "description": "b", "depends_on": ["A"]},
            {"id": "C", "action": "scan", "description": "isolated"},
        ],
    }
    graph, plan = _build(payload)
    result = ReachabilityValidator().check(graph, plan)
    assert result.passed is False


def test_unapproved_action_detected(example_payload):
    graph, plan = _build(example_payload)
    graph.nodes["T3"]["action"] = "explode"
    report = GraphValidationEngine().validate(graph, plan)
    assert report.action_check == "failed"


def test_contradictory_conditions_detected():
    payload = {
        "version": "1.0", "instruction": "dup branch",
        "tasks": [
            {"id": "A", "action": "inspect", "description": "inspect"},
            {"id": "B", "action": "place", "description": "b", "depends_on": ["A"],
             "condition": "ok"},
            {"id": "C", "action": "place", "description": "c", "depends_on": ["A"],
             "condition": "ok"},
        ],
    }
    graph, plan = _build(payload)
    report = GraphValidationEngine().validate(graph, plan)
    assert report.conditional_check == "failed"


def test_single_conditional_branch_warns_but_passes():
    payload = {
        "version": "1.0", "instruction": "half branch",
        "tasks": [
            {"id": "A", "action": "inspect", "description": "inspect"},
            {"id": "B", "action": "place", "description": "b", "depends_on": ["A"],
             "condition": "damaged"},
        ],
    }
    graph, plan = _build(payload)
    report = GraphValidationEngine().validate(graph, plan)
    assert report.conditional_check == "passed"
    assert any(i.severity == "warning" for i in report.issues)


def test_structural_check_catches_missing_attrs(example_payload):
    graph, plan = _build(example_payload)
    del graph.nodes["T2"]["description"]
    report = GraphValidationEngine().validate(graph, plan)
    assert report.structural_check == "failed"


def test_dag_validator_on_empty_graph(example_payload):
    _, plan = _build(example_payload)
    assert DagValidator().check(nx.DiGraph(), plan).passed is True
