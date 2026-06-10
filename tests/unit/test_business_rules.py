"""Unit tests: business-rule validation."""
from taskflow.application.schemas import TaskPlanSchema
from taskflow.application.validation.business_rules import BusinessRuleValidator


def _plan(tasks):
    return TaskPlanSchema.model_validate(
        {"version": "1.0", "instruction": "test", "tasks": tasks}
    )


def test_clean_plan_has_no_issues(example_plan):
    assert BusinessRuleValidator().validate(example_plan) == []


def test_unknown_action_rejected():
    plan = _plan([{"id": "T1", "action": "weld", "description": "weld it"}])
    issues = BusinessRuleValidator().validate(plan)
    assert any(i.check == "action_registry" for i in issues)


def test_unknown_dependency_rejected():
    plan = _plan([
        {"id": "T1", "action": "pick", "description": "x", "depends_on": ["T9"]},
    ])
    issues = BusinessRuleValidator().validate(plan)
    assert any(i.check == "dependency_integrity" for i in issues)


def test_self_dependency_rejected():
    plan = _plan([{"id": "T1", "action": "pick", "description": "x", "depends_on": ["T1"]}])
    issues = BusinessRuleValidator().validate(plan)
    assert any("itself" in i.message for i in issues)


def test_duplicate_condition_branches_rejected():
    plan = _plan([
        {"id": "T1", "action": "inspect", "description": "inspect"},
        {"id": "T2", "action": "place", "description": "a", "depends_on": ["T1"],
         "condition": "damaged"},
        {"id": "T3", "action": "place", "description": "b", "depends_on": ["T1"],
         "condition": "Damaged"},
    ])
    issues = BusinessRuleValidator().validate(plan)
    assert any(i.check == "conditional_consistency" for i in issues)
