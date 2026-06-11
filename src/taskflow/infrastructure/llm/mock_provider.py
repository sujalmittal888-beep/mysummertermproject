"""Deterministic rule-based provider for offline development, demos, and tests.

It performs a lightweight decomposition of common industrial instruction
patterns (pick / inspect / place / move / sort) into the JSON task schema.
Like all providers, its only output is JSON text.
"""
from __future__ import annotations

import json
import re

from taskflow.infrastructure.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "mock-deterministic-v1", **kwargs: float) -> None:
        super().__init__(model=model, **kwargs)

    @property
    def name(self) -> str:
        return f"mock:{self.model}"

    def generate_task_json(self, instruction: str) -> str:
        text = instruction.strip()
        lowered = text.lower()
        tasks: list[dict] = []
        tid = 0

        def next_id() -> str:
            nonlocal tid
            tid += 1
            return f"T{tid}"

        source = _first_match(lowered, r"from ([\w\s\-]+?)(?:,|\.| and | then |$)") or "source area"
        target = (
            _first_match(lowered, r"(?:to|on|onto|into) ([\w\s\-]+?)(?:,|\.| and | then |$)")
            or "target area"
        )
        obj_pattern = (
            r"(?:pick|move|transfer|inspect|scan|sort)(?: up)? "
            r"(?:the |all |each )?([\w\s\-]+?)(?: from| to| on| and|,|\.|$)"
        )
        obj = _first_match(lowered, obj_pattern) or "item"

        last: list[str] = []
        nav = {
            "id": next_id(),
            "action": "navigate",
            "description": f"Navigate to {source.title()}",
            "depends_on": [],
            "condition": None,
            "metadata": {"location": source.title()},
        }
        tasks.append(nav)
        last = [nav["id"]]

        if any(verb in lowered for verb in ("pick", "move", "transfer", "sort", "inspect", "scan")):
            loc = {
                "id": next_id(),
                "action": "locate",
                "description": f"Locate {obj}",
                "depends_on": last,
                "condition": None,
                "metadata": {"object": obj},
            }
            tasks.append(loc)
            last = [loc["id"]]

        if any(verb in lowered for verb in ("pick", "move", "transfer", "place")):
            pick = {
                "id": next_id(),
                "action": "pick",
                "description": f"Pick {obj}",
                "depends_on": last,
                "condition": None,
                "metadata": {"object": obj, "location": source.title()},
            }
            tasks.append(pick)
            last = [pick["id"]]

        if "scan" in lowered:
            scan = {
                "id": next_id(),
                "action": "scan",
                "description": f"Scan {obj}",
                "depends_on": last,
                "condition": None,
                "metadata": {"object": obj},
            }
            tasks.append(scan)
            last = [scan["id"]]

        inspected = "inspect" in lowered
        if inspected:
            ins = {
                "id": next_id(),
                "action": "inspect",
                "description": f"Inspect {obj}",
                "depends_on": last,
                "condition": None,
                "metadata": {"object": obj},
            }
            tasks.append(ins)
            last = [ins["id"]]

        branching = inspected and any(w in lowered for w in ("damaged", "defect", "reject", "sort"))
        if branching:
            parent = last
            ok = {
                "id": f"T{tid + 1}A",
                "action": "place",
                "description": f"Place {obj} on {target.title()}",
                "depends_on": parent,
                "condition": "undamaged",
                "metadata": {"object": obj, "location": target.title()},
            }
            bad = {
                "id": f"T{tid + 1}B",
                "action": "place",
                "description": f"Place {obj} in reject bin",
                "depends_on": parent,
                "condition": "damaged",
                "metadata": {"object": obj, "location": "Reject Bin"},
            }
            tid += 1
            tasks.extend([ok, bad])
        else:
            place = {
                "id": next_id(),
                "action": "place",
                "description": f"Place {obj} on {target.title()}",
                "depends_on": last,
                "condition": None,
                "metadata": {"object": obj, "location": target.title()},
            }
            tasks.append(place)
            last = [place["id"]]

        # Handle secondary "drop/place at <location>" clauses (e.g. "while dropping X at room 2")
        secondary_drops = list(re.finditer(
            r"(?:while |also |then )?(?:drop(?:ping)?|place|deliver(?:ing)?)\s+"
            r"(?:the |all |each |three |two |[\d]+ )?(?P<obj2>[\w\s\-]+?)\s+"
            r"(?:at|to|on|onto)\s+(?P<loc2>[\w\s\-]+?)(?:,|\.| and | then |while |$)",
            lowered,
        ))
        for m in secondary_drops:
            obj2 = m.group("obj2").strip()
            loc2 = m.group("loc2").strip()
            # Skip if this is just the primary operation re-matched
            if loc2 == target.lower() and obj2 in obj:
                continue
            nav2 = {
                "id": next_id(),
                "action": "navigate",
                "description": f"Navigate to {loc2.title()}",
                "depends_on": last,
                "condition": None,
                "metadata": {"location": loc2.title()},
            }
            drop2 = {
                "id": next_id(),
                "action": "place",
                "description": f"Place {obj2} at {loc2.title()}",
                "depends_on": [nav2["id"]],
                "condition": None,
                "metadata": {"object": obj2, "location": loc2.title()},
            }
            tasks.extend([nav2, drop2])
            last = [drop2["id"]]

        return json.dumps({"version": "1.0", "instruction": text, "tasks": tasks})


def _first_match(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None
