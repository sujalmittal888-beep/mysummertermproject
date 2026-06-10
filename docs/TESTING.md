# TaskFlow Testing Strategy

## Goals

1. Prove the pipeline boundary: NL → JSON → validation → graph → validation →
   export, and **nothing after export**.
2. Keep tests deterministic and offline — no live LLM calls anywhere in the
   suite.
3. Test each Clean Architecture layer at the appropriate level of isolation.

---

## Test pyramid

| Level        | Location             | Scope | External deps |
|--------------|----------------------|-------|---------------|
| Unit         | `tests/unit/`        | One class/module per test file | None |
| Integration  | `tests/integration/` | Full API via `TestClient`, real SQLite, real file exports | None (mock LLM) |

Total: **39 tests**, all runnable with `pytest` in a few seconds.

### Determinism

- `MockLLMProvider` decomposes instructions with deterministic rules, so the
  same instruction always yields the same plan. It doubles as the test LLM and
  the offline demo provider.
- Visualization layout is derived from `topological_generations`, so PNG/HTML
  output is stable across runs.
- Integration tests use a temporary SQLite database per test via fixtures —
  no shared state, no PostgreSQL requirement in CI.

---

## Unit tests (`tests/unit/`)

**`test_schemas.py`** — Pydantic layer. Accepts the canonical example plan;
rejects unknown fields (`extra="forbid"`), bad task-id formats, wrong types;
normalizes actions to lowercase and empty conditions to `None`.

**`test_business_rules.py`** — `BusinessRuleValidator`. Duplicate IDs,
unapproved actions, unknown/self dependencies, contradictory duplicate
sibling conditions.

**`test_graph_builder.py`** — `NetworkXGraphBuilder`. Node attribute
completeness (`task_id`, `action`, `description`, `condition`, `metadata`),
edge attributes (`dependency_type`, `conditional`), correct node/edge counts
for the example plan.

**`test_validation_engine.py`** — All seven validators, exercised through
hand-built graphs:

| Validator | Failure cases covered |
|-----------|----------------------|
| DAG / cycle | injected cycle fails `cycle_check` |
| Dependency | edge to missing node |
| Reachability | isolated node, disconnected component |
| Action registry | unknown action on a node |
| Conditional logic | contradictory duplicate sibling conditions (error); single unhandled branch (warning, plan still valid) |
| Structural | missing node attributes, duplicate IDs |
| Consistency | self-loop, edge-count mismatch vs plan |

Also asserts the report contract: `valid` flips only on error severity,
per-check `passed`/`failed` strings, node/edge counts, UTC timestamp.

**`test_mock_provider_and_parser.py`** — `InstructionParsingService` with the
mock provider: code-fence stripping, JSON parse errors surfacing as
`SchemaValidationError`, end-to-end parse of the canonical instruction into a
6-task plan with conditional branches.

**`test_visualization_and_export.py`** — Renders PNG/HTML/GraphML to a temp
dir and asserts files exist and are non-trivial; GraphML round-trips through
`networkx.read_graphml`; `ArtifactExportService` writes all six artifacts,
zips five into the package, and `resolve()` rejects unknown filenames and
path traversal (`../`).

---

## Integration tests (`tests/integration/`)

**`test_api.py`** — Full FastAPI app with dependency overrides (mock LLM,
tmp SQLite, tmp artifact dir):

- `GET /health` returns status + provider.
- `POST /instructions` returns 201, `valid: true`, six artifacts; artifacts
  exist on disk; `GET /downloads/...` streams each one with the right
  content type; unknown artifact name → 404.
- `POST /parse` → `POST /graph` → `POST /validate` → `POST /export` chained by
  `pipeline_id`; `GET /graph/{id}` and `GET /validation/{id}` return stored
  results; unknown id → 404.
- Schema-invalid payloads → 422 with the structured error envelope.

**`test_cycle_rejection_end_to_end.py`** — Submits a plan whose dependencies
form a cycle through the inline-plan path and asserts the pipeline reports
`valid: false` with `cycle_check: "failed"`, and that no zip artifact is
produced for an invalid plan beyond the validation report.

---

## What is intentionally *not* tested

- Live OpenAI/Anthropic calls — provider adapters are thin HTTP wrappers;
  their contract (JSON-only output) is enforced and tested at the parsing
  service layer with canned responses.
- Anything execution-related — no such code exists to test (scope boundary).

---

## Running

```bash
pytest                       # full suite
pytest tests/unit -q         # fast inner loop
pytest --cov=taskflow --cov-report=term-missing
ruff check src tests         # lint
mypy src                     # static types
```

CI (`.github/workflows/ci.yml`) runs ruff, mypy (informational), pytest with
coverage, and a Docker build on every push and pull request.
