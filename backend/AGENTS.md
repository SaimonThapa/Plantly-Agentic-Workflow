# Plantly backend rules

Follow root `AGENTS.md` and `docs/ARCHITECTURE.md`. Use approved FastAPI feature modules, SQLAlchemy 2 + psycopg3, Alembic and PostgreSQL. Data enters through explicit validation, schemas, services and repositories. Keep authorization/ownership/CSRF enforced.

For YAML/research work, read `docs/DATA_INGESTION.md` and inspect actual source files first. Alembic schema migrations and idempotent data ingestion are **separate**. Never grant scientific approval automatically, enable placeholder lime rates, or pretend embeddings are configured before a real model/dimension decision. Test against real disposable PostgreSQL before claiming integration verified.
