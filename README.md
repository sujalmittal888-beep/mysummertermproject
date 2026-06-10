# Language-to-Task Flow Graph Generator

Converts natural language industrial instructions into a **validated Task Flow Graph (DAG)** with downloadable artifacts.

```
"Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3."
        │
        ▼
  LLM (JSON only) ──► Pydantic v2 validation ──► NetworkX DAG ──► 7-stage
  graph validation ──► PNG / HTML / GraphML ──► task_flow_package.zip
```

**Scope boundary:** the pipeline terminates after graph validation and export.
There is **no execution engine, robot control, motion planning, ROS, or PLC
integration anywhere in this codebase** — by design.

## Quick start

```bash
pip install -e ".[dev]"
cp .env.example .env                  # defaults to the offline mock provider

# CLI (full pipeline, no server needed)
python -m taskflow "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3."

# API server
uvicorn taskflow.presentation.api.app:app --reload
# open http://localhost:8000/docs

# With PostgreSQL + Docker
docker compose up --build
```

## Switching LLM providers

Set `TASKFLOW_LLM_PROVIDER` to `openai`, `anthropic`, or `mock` and supply the
matching API key. Providers are adapters behind a single port
(`LLMProvider.generate_task_json`) — business logic never changes.

## API surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/instructions` | Full pipeline: NL → JSON → DAG → validation → export |
| POST | `/parse` | NL → validated JSON task schema only |
| POST | `/graph` | JSON task schema → DAG (node-link JSON) |
| POST | `/validate` | JSON task schema → validation report |
| POST | `/export` | JSON task schema → all downloadable artifacts |
| GET | `/graph/{id}` | Rebuild stored graph for a pipeline run |
| GET | `/validation/{id}` | Stored validation report |
| GET | `/downloads/{id}/{artifact}` | Download one artifact |
| GET | `/health` | Liveness probe |

## Generated artifacts

`task_plan.json` · `validation_report.json` · `task_graph.png` ·
`task_graph.graphml` (Gephi/Neo4j-compatible) · `task_graph.html`
(interactive PyVis) · `task_flow_package.zip` (bundle of all of the above).

## Development

```bash
pytest                # 39 unit + integration tests
ruff check src tests  # lint
mypy src/taskflow     # type check
```

See `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/DEPLOYMENT.md`, and
`docs/TESTING.md` for the full documentation set.
