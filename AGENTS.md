# Plantly — Codex project instructions (lean)

**Build only from real repository evidence.** Never claim a file, skill, command, test, MCP server, integration, scientific approval, or feature exists without checking it. Do not launch unattended loops, deploy, install plugins or trust new hooks without the user's approval.

## Start a task
1. Read `docs/agent/STATE.md` and the **single chosen task** in `docs/agent/TASKS.json`.
2. Inspect existing code and files. Read only the **relevant sections** of `docs/PRODUCT.md` (what), `docs/ARCHITECTURE.md` (how), and, for UI, `docs/DESIGN.md` plus `docs/LANDING_DESIGN.md` for the landing page.
3. Check task dependencies and missing human decisions. If blocked, explain precisely what is missing and stop that part. Never invent an answer.
4. Implement the smallest complete, testable vertical slice. Keep dependencies and abstractions minimal. Do not work on an unrelated task without approval.

## Efficiency / Ponytail
- If the **Ponytail plugin is installed, discoverable, and trusted**, follow its simplicity-first guidance. Reuse existing code, choose the smallest safe solution, and keep changes narrowly scoped. **Do not claim Ponytail automatically lowers tokens, selects a model, or imposes spending caps.**
- If Ponytail is missing, apply the same principles manually. Do not install it or fake its activation.
- Avoid repeatedly reading entire specs, overexplaining in tool outputs, generating huge exploratory logs, or activating unrelated skills. Never trade away security, correctness, accessible UX, or scientific review to save tokens.

## Project contracts
- Stack: Next.js App Router + JavaScript + Tailwind v4 frontend; FastAPI + SQLAlchemy/psycopg + Alembic + PostgreSQL/pgvector backend. Use the approved architecture for the details; this file does not supersede it.
- Research is curated and versioned. **No auto-approval** of agronomy rules; no fabricated pH, nutrient/lime rates, citations, weather, product prices or savings. Unknown means unknown.
- Keep data private with ownership checks, CSRF and approved session strategy; never print or commit secrets.
- User-supplied images absent? Keep the required slot with a visible label explaining the image needed. Do not generate fake final artwork. Track in `docs/agent/ASSETS.md`.

## Skills and tooling
- Codex project skills belong in `.agents/skills/<skill>/SKILL.md` (plural `agents`). The user installs third-party skills/plugins manually. **Check availability before invoking.**
- Read `docs/agent/SKILLS.md` only for UI/tooling tasks. Taste = composition; Impeccable = targeted review; Animate = appropriate motion; Ponytail = simplicity; Playwright MCP = browser inspection **when available**. No skill can override approved product/design/science rules.

## Optional external task runner / Codex hooks
- A manually installed, supervised runner may live at `tools/agentic/runner.py`, configured by `tools/agentic/config.json`.
- The runner reads `docs/agent/TASKS.json`; only the runner may change status to `code_verified` when it is used, after all real configured checks pass. Never self-certify or fabricate test evidence.
- A task is authorized only when listed in `config.json` **and** the user explicitly invokes `run TASK_ID --execute` with `PLANTLY_ALLOW_MODEL_RUN=1`. Do not invoke the runner yourself as a subtask.
- Runtime logs/attempt limits persist under ignored `.agentic/`; hooks live under `.codex/hooks.json`. Neither is a substitute for user approvals, safe sandboxing or tests.
- Review actual installed skills under `.agents/skills/` and plugin discovery; consult `docs/agent/SKILLS.md`. Never assume Ponytail, Taste, Impeccable or Animate is installed just because it is documented.

## Close a task
When an external runner owns the task, DO NOT edit `docs/agent/TASKS.json` or its verification configuration. Supply code/tests and concise evidence; the runner updates status after real verifiers pass. In manual sessions without the runner, follow supervised checks and clearly document manual status updates.
