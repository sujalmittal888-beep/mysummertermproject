# TaskFlow Deployment Guide

This guide covers local development, Docker, Docker Compose with PostgreSQL,
database migrations, and production hardening.

---

## 1. Configuration

All settings are environment variables with the `TASKFLOW_` prefix, loaded via
`pydantic-settings` (`src/taskflow/config.py`). Copy `.env.example` to `.env`
and adjust:

| Variable                  | Default                       | Purpose |
|---------------------------|-------------------------------|---------|
| `TASKFLOW_LLM_PROVIDER`   | `mock`                        | `openai`, `anthropic`, or `mock` |
| `TASKFLOW_OPENAI_API_KEY` | —                             | Required when provider is `openai` |
| `TASKFLOW_OPENAI_MODEL`   | `gpt-4o-mini`                 | OpenAI model name |
| `TASKFLOW_ANTHROPIC_API_KEY` | —                          | Required when provider is `anthropic` |
| `TASKFLOW_ANTHROPIC_MODEL`| `claude-sonnet-4-20250514`    | Anthropic model name |
| `TASKFLOW_DATABASE_URL`   | `sqlite:///./taskflow.db`     | SQLAlchemy URL; use PostgreSQL in production |
| `TASKFLOW_ARTIFACT_DIR`   | `./artifacts`                 | Root directory for exported artifacts |
| `TASKFLOW_LOG_LEVEL`      | `INFO`                        | Logging level |

The `mock` provider is deterministic and offline — useful for CI, demos, and
air-gapped environments. Switching providers requires **no code change**.

---

## 2. Local development (no Docker)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Run the API
uvicorn taskflow.presentation.api.app:create_app --factory --reload --port 8000

# Or run the CLI pipeline directly
python -m taskflow "Pick the red box from Shelf A and place it on Conveyor Belt 3."
```

SQLite is used by default locally; tables are created automatically at startup
(`init_db`). For PostgreSQL, prefer Alembic migrations (section 5).

---

## 3. Docker (single container)

The provided `Dockerfile` is a slim Python 3.12 image, runs as a non-root
user, and includes a container healthcheck hitting `/health`.

```bash
docker build -t taskflow:latest .
docker run --rm -p 8000:8000 \
  -e TASKFLOW_LLM_PROVIDER=mock \
  -e TASKFLOW_DATABASE_URL=sqlite:////data/taskflow.db \
  -v taskflow-data:/data \
  taskflow:latest
```

---

## 4. Docker Compose (API + PostgreSQL)

`docker-compose.yml` starts the API alongside `postgres:16-alpine` with a
named volume and healthcheck-based startup ordering.

```bash
# Provide secrets via .env (compose reads it automatically)
docker compose up --build -d
docker compose logs -f api
```

The API container receives
`TASKFLOW_DATABASE_URL=postgresql+psycopg://taskflow:taskflow@db:5432/taskflow`.
Change the credentials in `docker-compose.yml` (or override via `.env`) before
any non-local use.

---

## 5. Database migrations (Alembic)

Migrations live in `alembic/versions/`. Initial schema:
`0001_initial.py` (instructions, plans, validations, exports — keyed by
`pipeline_id`).

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

In containerized deployments run migrations as a release step **before**
starting new application instances:

```bash
docker compose run --rm api alembic upgrade head
```

---

## 6. Production checklist

**Process model.** Run uvicorn behind a reverse proxy (nginx, Traefik, or a
cloud load balancer). Scale horizontally; the app is stateless except for the
artifact directory and database.

**Artifacts.** Mount `TASKFLOW_ARTIFACT_DIR` on a persistent volume shared by
all replicas (or a network filesystem / object-storage gateway). Artifact
filenames are whitelisted and path-traversal is rejected at the download
endpoint, but the directory should still not be world-writable.

**Database.** Use managed PostgreSQL with TLS. Apply migrations via CI, not at
container boot.

**Secrets.** Inject API keys via your orchestrator's secret store, never bake
them into images. Only the configured provider's key is required.

**Observability.** Logs are structured JSON on stdout — point your log
shipper at container stdout. The `/health` endpoint is suitable for liveness
and readiness probes.

**Network egress.** The only outbound calls the system makes are to the
configured LLM provider's HTTPS API. With `TASKFLOW_LLM_PROVIDER=mock`, the
system requires no egress at all.

**Scope guarantee.** The service has no robot, ROS, PLC, or execution
pathways — it is safe to deploy in environments where accidental actuation
would be unacceptable. The pipeline terminates at artifact export by design.

---

## 7. CI/CD

`.github/workflows/ci.yml` runs on every push/PR:

1. Ruff lint
2. MyPy (informational)
3. Pytest with coverage
4. Docker image build

Recommended release flow: tag → CI green → build/push image → run
`alembic upgrade head` → rolling deploy → verify `/health`.
