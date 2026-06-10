"""CLI entry point: run the full pipeline locally without the API server.

Usage:
    python -m taskflow "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3."
"""
from __future__ import annotations

import json
import sys

from taskflow.config import get_settings
from taskflow.logging_config import configure_logging
from taskflow.presentation.api.dependencies import build_container


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    if len(sys.argv) < 2:
        print('usage: python -m taskflow "<instruction>"', file=sys.stderr)
        return 2
    container = build_container(settings)
    result = container.use_case.execute(" ".join(sys.argv[1:]))
    print(json.dumps({
        "pipeline_id": result.pipeline_id,
        "valid": result.report.valid,
        "artifacts": result.artifacts,
    }, indent=2))
    return 0 if result.report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
