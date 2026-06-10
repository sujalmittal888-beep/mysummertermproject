"""Unit tests: mock provider output and instruction parsing service."""
import json

import pytest

from taskflow.application.services import InstructionParsingService, _strip_code_fences
from taskflow.domain.exceptions import LLMProviderError, SchemaValidationError
from taskflow.infrastructure.llm.mock_provider import MockLLMProvider


def test_mock_provider_emits_valid_json():
    raw = MockLLMProvider().generate_task_json(
        "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3."
    )
    payload = json.loads(raw)
    assert payload["version"] == "1.0"
    assert len(payload["tasks"]) >= 4


def test_parser_full_path_with_mock():
    svc = InstructionParsingService(MockLLMProvider())
    plan = svc.parse_instruction(
        "Pick the red box from Shelf A, inspect it, and sort damaged items."
    )
    conditions = {t.condition for t in plan.tasks}
    assert {"damaged", "undamaged"} <= {c for c in conditions if c}


class _BadProvider:
    name = "bad"

    def generate_task_json(self, instruction: str) -> str:
        return "this is not json"


class _RuleBreakingProvider:
    name = "rule-breaker"

    def generate_task_json(self, instruction: str) -> str:
        return json.dumps({
            "version": "1.0", "instruction": instruction,
            "tasks": [{"id": "T1", "action": "detonate", "description": "boom"}],
        })


def test_non_json_output_raises_provider_error():
    with pytest.raises(LLMProviderError):
        InstructionParsingService(_BadProvider()).parse_instruction("x")


def test_business_rule_failure_raises_schema_error():
    with pytest.raises(SchemaValidationError) as exc:
        InstructionParsingService(_RuleBreakingProvider()).parse_instruction("x")
    assert exc.value.errors


def test_strip_code_fences():
    fenced = "```json\n{\"a\": 1}\n```"
    assert json.loads(_strip_code_fences(fenced)) == {"a": 1}
