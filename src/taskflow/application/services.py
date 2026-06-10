"""Application services orchestrating schema parsing and validation."""
from __future__ import annotations

import json

from pydantic import ValidationError

from taskflow.application.interfaces import LLMProvider
from taskflow.application.schemas import TaskPlanSchema, ValidationIssue
from taskflow.application.validation.business_rules import BusinessRuleValidator
from taskflow.domain.exceptions import LLMProviderError, SchemaValidationError
from taskflow.logging_config import get_logger

logger = get_logger(__name__)


class InstructionParsingService:
    """Turns a natural language instruction into a *validated* TaskPlanSchema.

    Responsibilities:
      1. Ask the LLM provider for raw JSON.
      2. Parse the JSON text.
      3. Validate against the Pydantic schema.
      4. Apply business-rule validation.
    Invalid JSON never proceeds past this service.
    """

    def __init__(self, provider: LLMProvider, rules: BusinessRuleValidator | None = None) -> None:
        self._provider = provider
        self._rules = rules or BusinessRuleValidator()

    def parse_instruction(self, instruction: str) -> TaskPlanSchema:
        raw = self._provider.generate_task_json(instruction)
        return self.validate_json_text(raw, instruction=instruction)

    def validate_json_text(self, raw: str, instruction: str | None = None) -> TaskPlanSchema:
        try:
            payload = json.loads(_strip_code_fences(raw))
        except json.JSONDecodeError as exc:
            logger.error("LLM returned non-JSON output: %s", exc)
            raise LLMProviderError(f"Provider returned invalid JSON: {exc}") from exc
        return self.validate_payload(payload, instruction=instruction)

    def validate_payload(self, payload: dict, instruction: str | None = None) -> TaskPlanSchema:
        try:
            plan = TaskPlanSchema.model_validate(payload)
        except ValidationError as exc:
            errors = [
                {
                    "check": "schema",
                    "location": ".".join(str(p) for p in e["loc"]),
                    "message": e["msg"],
                    "type": e["type"],
                }
                for e in exc.errors()
            ]
            raise SchemaValidationError("JSON failed schema validation", errors=errors) from exc

        if instruction and not plan.instruction:
            plan.instruction = instruction

        issues = self._rules.validate(plan)
        errors_only = [i for i in issues if i.severity == "error"]
        if errors_only:
            raise SchemaValidationError(
                "JSON failed business-rule validation",
                errors=[i.model_dump() for i in errors_only],
            )
        self._log_warnings(issues)
        return plan

    @staticmethod
    def _log_warnings(issues: list[ValidationIssue]) -> None:
        for issue in issues:
            if issue.severity == "warning":
                logger.warning("Business-rule warning [%s]: %s", issue.check, issue.message)


def _strip_code_fences(text: str) -> str:
    """Defensively strip markdown code fences if a provider misbehaves."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else ""
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3]
    return cleaned.strip()
