# Plantly — clean Codex starter (manual-first)

This is a **fresh, minimal project scaffold**, **not a working application or an unattended agent runner**. It includes the latest provided Plantly PRODUCT, ARCHITECTURE, DESIGN and LANDING_DESIGN source documents; a lean task roadmap; lightweight Codex guidance; and blank directories for your real datasets and skills. No dependencies, skills, MCP servers, hooks, databases, credentials, app code, or tests have been installed by this ZIP.

## Setup (do manually)

1. **Start with your intended Git project.** Extract/merge into that repository, not over existing files without reviewing diffs. If creating a new repository, initialize Git yourself; inspect `.gitignore` first. Do not run unattended Codex execution from a non-Git folder.
2. **Add your current YAML/JSON files** to `data/curated/datasets/`, `data/curated/fixtures/`, and `data/curated/` for `sources.yaml`. Check references before moving files. `source_notes.yaml` can go under `research/` after its schema/path refs are checked.
3. **Install skills manually**, if wanted. The correct native Codex location is **`.agents/skills/`** (not `.agent/skills/`). See `docs/agent/SKILLS.md`. Confirm Codex recognizes each. Ponytail is a **plugin**, so don't copy it blindly as a project skill.
4. **Set up Playwright MCP and database yourself or approve those operations later.** A configured MCP entry is not proof that a browser works. No fake test successes.
5. Review `docs/agent/DECISIONS.md` and provide decisions as the applicable tasks require. Brand photos can wait; use labeled placeholders.
6. Start Codex in the repository root. Read `docs/agent/PROMPTS.md` and begin with the **baseline inspection prompt**. Only after inspection, request one task (usually `F-000`).

## What this starter intentionally does NOT include

- `tools/agentic/runner.py`, automatic next-task coordinator, retry escalation, or scheduled autonomous work.
- `.codex/hooks.json`, untrusted hooks, plugin binaries, installer scripts, or cost-estimating claims.
- Placeholder implementation code, invented scientific rules or fabricated product data.
- Node/Python dependency manifests or fake test suites; `F-000` will create those from `ARCHITECTURE.md`.
- Any source datasets or research PDFs; copy your own verified files.

## Trust the specifications, not the scaffolding

`docs/PRODUCT.md` owns features, `docs/ARCHITECTURE.md` owns implementation, `docs/DESIGN.md` owns global UI, and `docs/LANDING_DESIGN.md` owns the landing composition. The source specifications are preserved verbatim except for a brief **Codex skill handoff appendix** at the end of DESIGN.md. Proposed or open choices remain unresolved; the starter does not silently approve them.

## Repo layout

`AGENTS.md` (small global rules); `frontend/AGENTS.md` and `backend/AGENTS.md` (local rules); `docs/agent/{STATE,TASKS,WORKFLOW,SKILLS,DECISIONS,ISSUES,ASSETS,PROMPTS}` (lightweight agent workflow); `.agents/skills/` (manual skills); `data/curated/` (manual datasets).

**Reminder:** This workflow is supervised, one task per approved session. No magic full auto loop is promised; that was deliberately removed after problems with the previous runner.

## F-000 development foundation

See [local setup and real lint/test commands](docs/DEVELOPMENT.md). Application scaffolding now lives in frontend/ and backend/; the original starter inventory above describes the initial ZIP, not current implementation status.
