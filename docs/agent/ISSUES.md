# Blockers and verification failures

No failures have been observed in **this new starter**. Previous starter's preflight findings are not evidence that this clean scaffold is functional or broken.

Template for future entries:

- **Date / Task:**
- **Blocker class:** `human`, `infrastructure`, `implementation`, or `scientific_review`
- **Observed evidence:** precise command and short error text
- **Attempts made:**
- **Required human input / next fix:**
- **Resolved evidence:** leave blank until actually verified

- **2026-11-08T08:45:13+00:00 / F-000 / infrastructure:** BLOCKED_BY_INFRA
  - Evidence: `.agentic\logs\F-000\attempt-01` (local, git-ignored logs)

- **2026-11-08 / F-000 / infrastructure:** BLOCKED_BY_INFRA
  - Docker, psql and postgres were not found on PATH. Real PostgreSQL/pgvector and Alembic checks remain unverified.
  - `backend/.venv/Scripts/python -m pip install -e "backend[dev]"` failed fetching setuptools with WinError 10013 (network socket access forbidden).
  - `npm.cmd install` did not finish and was interrupted; no dependency lockfile was generated. Frontend lint/build and browser checks remain unverified.
  - `node --test frontend/tests/*.test.mjs`: 1 passed. `python -m compileall -q backend/app backend/migrations backend/tests`: exit 0. `git diff --check`: exit 0.
  - Required infrastructure: package registry access and a running Docker Compose engine (or disposable PostgreSQL with pgvector). External runner owns verification and task status.

- **2026-11-08 / F-000 retry 2 / infrastructure:** BLOCKED_BY_INFRA
  - Previous verifier stopped at `npm run lint`: ESLint was not installed.
  - `npm.cmd install --ignore-scripts --fetch-retries=0 --fetch-timeout=20000 --no-audit --no-fund` (from `frontend`) exited 1: npm registry request failed with `EACCES`.
  - `backend/.venv/Scripts/python -m pip install --retries 0 --timeout 15 -e "backend[dev]"` exited 1: build dependency download failed with `WinError 10013`.
  - Docker, psql and postgres were not found on PATH; the standard Docker Desktop CLI path was also absent.
  - `node --test frontend/tests/*.test.mjs`: 1 passed. `python -m compileall -q backend/app backend/migrations backend/tests`: exit 0. `git diff --check`: exit 0.
  - Frontend lint/build, backend lint/API tests, and real PostgreSQL/pgvector migrations remain unverified. Dependency lock generation remains blocked by registry access.
  - Required next step: provide package registry access and a disposable PostgreSQL/pgvector runtime, then install dependencies and run the documented checks. No runner configuration or task status changed by this retry.

- **2026-11-08T09:02:20+00:00 / F-000 / infrastructure:** BLOCKED_BY_INFRA
  - Evidence: `.agentic\logs\F-000\attempt-02` (local, git-ignored logs)
