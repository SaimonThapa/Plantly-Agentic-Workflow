# Local development foundation (F-000)

Requires Node.js 20.9+ (22/24 LTS recommended), Python 3.12+, and Docker Compose with a running Docker engine. This is local infrastructure only; hosting, scientific rules and providers remain undecided. No worker is implemented until there is queue work to execute.

## Install

From the repository root:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -e "backend[dev]"
cd frontend
npm install
```

## Run

From the root, start the persistent local development database:

```powershell
docker compose up -d --wait db
```

In a backend terminal:

```powershell
cd backend
$env:DATABASE_URL = "postgresql+psycopg://plantly:local-development-only@localhost:5432/plantly"
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a frontend terminal, run `cd frontend` then `npm run dev`. Open http://localhost:3000. `/api/v1/health` is proxied to FastAPI; `/health` on port 8000 is a process liveness check, not database readiness. Environment example files are documentation, not automatically loaded by the backend. Set environment variables explicitly. Never expose DATABASE_URL through NEXT_PUBLIC variables.

## Checks

From `frontend`:

```powershell
npm run lint
npm test
npm run build
```

From `backend`:

```powershell
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m pytest -m "not integration"
```

For real database integration, start the isolated database from the repository root:

```powershell
docker compose --profile test up -d --wait test-db
cd backend
$env:TEST_DATABASE_URL = "postgresql+psycopg://plantly:local-test-only@localhost:5433/plantly_test"
.venv/Scripts/python -m pytest
```

The integration test fails if its database URL is absent; it does not silently skip. It exercises Alembic upgrade/downgrade/re-upgrade, schema drift, real vector distance and transaction rollback. It only accepts the PostgreSQL psycopg driver and database name `plantly_test`. Supply only a disposable test database; the test changes its migration revision. No scientific tables, embedding dimensions or approval records are seeded.

Stop the disposable database from the root with `docker compose --profile test rm -sf test-db`. Its tmpfs contents are discarded. `docker compose stop db` preserves development data. Do not remove the development volume unless intentionally discarding it. The pgvector extension survives Alembic downgrade to avoid removing shared database capabilities.

On macOS/Linux use `backend/.venv/bin/python` and shell-appropriate environment assignment. The credentials in Compose are local-only fixtures, with ports bound to loopback.

