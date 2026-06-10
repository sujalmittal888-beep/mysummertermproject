"""Integration test: cyclic and structurally invalid plans never export cleanly."""
from taskflow.application.mappers import schema_to_entity
from taskflow.application.schemas import TaskPlanSchema
from taskflow.infrastructure.graph.builder import NetworkXGraphBuilder
from taskflow.infrastructure.validation.engine import GraphValidationEngine


def test_cyclic_plan_yields_invalid_report():
    payload = {
        "version": "1.0", "instruction": "cycle",
        "tasks": [
            {"id": "A", "action": "pick", "description": "a", "depends_on": ["C"]},
            {"id": "B", "action": "move", "description": "b", "depends_on": ["A"]},
            {"id": "C", "action": "place", "description": "c", "depends_on": ["B"]},
        ],
    }
    plan = schema_to_entity(TaskPlanSchema.model_validate(payload))
    graph = NetworkXGraphBuilder().build(plan)
    report = GraphValidationEngine().validate(graph, plan)
    assert report.valid is False
    assert report.cycle_check == "failed"
    assert report.consistency_check == "failed"
