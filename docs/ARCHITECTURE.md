# Architecture

## 1. Purpose and scope

The system converts a natural language industrial instruction into a validated
Task Flow Graph (a NetworkX `DiGraph` that must be a DAG) plus a set of
downloadable artifacts. The pipeline is strictly bounded:

```
NL instruction → LLM → JSON task schema → Pydantic validation →
NetworkX graph builder → DAG → validation engine → visualization → export
```

The pipeline **terminates after export generation**. Execution engines, robot
control, motion planning, ROS/PLC integration, runtime schedulers, and
simulators are explicitly out of scope and have no representation in the code,
the schema, or the API.

## 2. Core architectural principle: JSON as the canonical source of truth

The LLM is responsible for exactly one thing: emitting a JSON document that
conforms to `TaskPlanSchema`. It never produces graph objects, NetworkX code,
execution plans, or robot commands (the system prompt forbids it, and the
schema's `extra="forbid"` rejects any smuggled fields). Every downstream
component — domain entities, the graph builder, the validation engine, the
exporters — derives from the validated JSON. The graph can therefore always be
rebuilt deterministically from the stored JSON (`GET /graph/{id}` does exactly
this).

## 3. Clean Architecture layers

```
presentation/   FastAPI app, routes, DTOs, error handlers, DI container
application/    use cases, parsing service, business rules, ports, schemas
domain/         entities (Task, TaskPlan), value objects (TaskId, ActionType,
                Condition), action registry, exceptions
infrastructure/ LLM adapters, NetworkX builder, validation engine,
                visualization, export, SQLAlchemy persistence
```

Dependency rule: source-code dependencies point inward. The application layer
depends on *ports* (`application/interfaces.py`, plain `Protocol`s); the
infrastructure layer provides adapters. The composition root
(`presentation/api/dependencies.py:build_container`) wires concrete adapters
into the use case — the only place where all layers meet.

### Domain layer
- `ActionType` — the approved action registry (navigate, locate, pick, place,
  inspect, move, scan, sort, transfer). Unknown actions fail validation.
- `TaskId`, `Condition` — validated value objects.
- `Task`, `TaskPlan` — aggregate enforcing unique ids, no self/unknown
  dependencies at construction time.

### Application layer
- `TaskPlanSchema` (Pydantic v2) — the JSON contract. Strict: extra fields
  forbidden, id pattern enforced, actions normalized to lowercase.
- `BusinessRuleValidator` — semantic rules beyond shape: unique ids, approved
  actions, dependency integrity, conditional consistency.
- `InstructionParsingService` — LLM call → JSON parse → schema validation →
  business rules. Invalid JSON never reaches graph generation.
- `ProcessInstructionUseCase` — orchestrates the end-to-end pipeline.

### Infrastructure layer
- **LLM adapters** (`OpenAIProvider`, `AnthropicProvider`, `MockLLMProvider`)
  behind `create_llm_provider(settings)`. Swapping providers is a config
  change; business logic is untouched. The mock provider is deterministic and
  used for offline development, demos, and the test suite.
- **`NetworkXGraphBuilder`** — builds `nx.DiGraph` from the domain `TaskPlan`.
  Node attributes: `task_id`, `action`, `description`, `condition`,
  `metadata`. Edge attributes: `dependency_type`
  (`sequential`/`conditional`), `conditional`, `condition`.
- **`GraphValidationEngine`** — composes seven single-responsibility
  validators (see §4) into a `ValidationReport`.
- **`GraphVisualizationService`** — PNG (matplotlib, deterministic layered
  layout from topological generations, dashed red conditional edges with
  labels, per-action legend), interactive HTML (PyVis: zoom, pan, hover
  metadata, conditional highlighting), GraphML (Gephi/Neo4j-compatible;
  metadata serialized to JSON strings because GraphML only supports
  primitives).
- **`ArtifactExportService`** — writes the six artifacts per pipeline run and
  resolves download paths with traversal protection.
- **Persistence** — SQLAlchemy 2.0 models behind `SqlAlchemyPlanRepository`
  (repository pattern). PostgreSQL in production (Alembic migrations), SQLite
  for tests/dev.

## 4. Validation engine

| # | Validator | Verifies |
|---|---|---|
| 1 | `DagValidator` | directed, acyclic (`nx.is_directed_acyclic_graph`), reports cycles |
| 2 | `DependencyValidator` | every declared dependency resolves to a real node and edge |
| 3 | `ReachabilityValidator` | no isolated nodes, single weakly-connected component, every node reachable from a root |
| 4 | `ActionRegistryValidator` | every node action is in the approved registry |
| 5 | `ConditionalLogicValidator` | non-empty conditions, no contradictory (duplicate) sibling branches, warns on unhandled complementary outcomes |
| 6 | `StructuralValidator` | unique ids, plan↔graph node parity, required node/edge attributes, metadata is a mapping |
| 7 | `GraphConsistencyValidator` | no self-loops, plan-declared edge count matches graph, topological sort succeeds, conditional edges align with child conditions |

Each validator returns a `CheckResult`; the engine aggregates them into a
`ValidationReport` (per-check pass/fail strings, issue list with severities,
node/edge counts, timestamp). `valid` is true only if every check passes;
warnings do not fail a check.

## 5. Data flow and persistence

Each pipeline run gets a `pipeline_id`. The repository stores: the raw
instruction + provider, the validated plan JSON, the validation report, and
export metadata (tables: `instructions`, `task_plans`, `validation_reports`,
`exports`). Artifacts live on disk under `TASKFLOW_ARTIFACT_DIR/{pipeline_id}/`.

## 6. Error handling

Domain exceptions map to structured HTTP responses:
`SchemaValidationError` → 422 with field-level errors,
`DomainRuleError` → 422, `LLMProviderError` → 502,
`ArtifactNotFoundError` → 404. All logs are structured JSON.

## 7. System diagram

```
┌──────────────┐   ┌─────────────────────┐   ┌──────────────────┐
│  REST client │──►│ FastAPI (DTOs, DI)  │──►│ ProcessInstruction│
└──────────────┘   └─────────────────────┘   │     UseCase       │
                                             └───┬──────────┬───┘
              ┌──────────────────────────────────┘          │
              ▼                                             ▼
   ┌─────────────────────┐                       ┌──────────────────┐
   │ InstructionParsing  │                       │ SqlAlchemyPlan   │
   │  Service            │                       │  Repository ──► PostgreSQL
   │  • LLMProvider port │                       └──────────────────┘
   │    ├ OpenAI adapter │
   │    ├ Anthropic      │        validated JSON (source of truth)
   │    └ Mock           │ ───────────────┐
   │  • Pydantic schema  │                ▼
   │  • Business rules   │      ┌────────────────────┐
   └─────────────────────┘      │ NetworkXGraphBuilder│
                                └─────────┬──────────┘
                                          ▼
                              ┌────────────────────────┐
                              │ GraphValidationEngine  │ (7 validators)
                              └─────────┬──────────────┘
                                        ▼
                  ┌─────────────────────────────────────────┐
                  │ Visualization + ArtifactExportService    │
                  │ png · html · graphml · json · zip        │
                  └─────────────────────────────────────────┘
                                        ▼
                                ███ PIPELINE ENDS ███
                          (no execution layer exists)
```
