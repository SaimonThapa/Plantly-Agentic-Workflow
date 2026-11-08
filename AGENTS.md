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
- No custom Codex hooks or autonomous runner are included in this starter. See `docs/agent/WORKFLOW.md` for a supervised task loop.

## Close a task
- Run the checks that **actually exist** for the changed code; capture exact commands and results. UI work also needs real browser interaction and responsive verification once Playwright is configured.
- Update `docs/agent/STATE.md` and that task's status in `TASKS.json` **only after evidence**; record issues in `docs/agent/ISSUES.md`. A tool not installed or a test not runnable is `not verified`, not `passed`.
- Say what changed, what was tested, what remains unverified, and what human input is needed. Stop on unresolved fundamental decisions and human gates.
