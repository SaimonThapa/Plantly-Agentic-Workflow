# Exact manual edits for Plantly's clean starter

These are changes to **existing** files; this add-on intentionally does not
overwrite your approved specs or AGENTS.md. Inspect each before editing.

## 1. Root `AGENTS.md`

Replace the old line claiming *"No custom Codex hooks or autonomous runner are
included"* with this concise paragraph:

```md
## Optional external task runner / Codex hooks
- A manually installed, supervised runner may live at `tools/agentic/runner.py`, configured by `tools/agentic/config.json`.
- The runner reads `docs/agent/TASKS.json`; only the runner may change status to `code_verified` when it is used, after all real configured checks pass. Never self-certify or fabricate test evidence.
- A task is authorized only when listed in `config.json` **and** the user explicitly invokes `run TASK_ID --execute` with `PLANTLY_ALLOW_MODEL_RUN=1`. Do not invoke the runner yourself as a subtask.
- Runtime logs/attempt limits persist under ignored `.agentic/`; hooks live under `.codex/hooks.json`. Neither is a substitute for user approvals, safe sandboxing or tests.
- Review actual installed skills under `.agents/skills/` and plugin discovery; consult `docs/agent/SKILLS.md`. Never assume Ponytail, Taste, Impeccable or Animate is installed just because it is documented.
```

In **Close a task**, replace any line telling Codex to directly edit
`TASKS.json` with:

```md
When an external runner owns the task, DO NOT edit `docs/agent/TASKS.json` or its verification configuration. Supply code/tests and concise evidence; the runner updates status after real verifiers pass. In manual sessions without the runner, follow supervised checks and clearly document manual status updates.
```

Keep all product, security and scientific safeguards unchanged.

## 2. `docs/agent/WORKFLOW.md`

Change its title to `# Plantly — supervised development and optional bounded runner`.
Replace its false *"previous runner absent"* paragraph with:

```md
An optional Python runner is available only if the user has manually copied `tools/agentic/` into this repository. It requires explicit approved task IDs and a second environment opt-in; it never self-starts and selects no more than one task per run. In the runner mode it owns task status and verification. Manual Codex sessions remain supported, but must not edit the runner's active task concurrently.
```

Replace any outdated "two attempts then ask" clause in **runner mode only**:

```md
Runner mode uses the bounded stage list in `tools/agentic/config.json` (normal: low -> medium -> high; security/science: medium -> high) and persists attempt history across restarts. It halts at explicit human/infra blocks, rejects unapproved tasks, and never auto-grants scientific or release approvals. Manual sessions may still stop after two failed targeted fixes.
```

## 3. `docs/agent/STATE.md`

Change only the old `**Runner/hooks:** None bundled...` line to:

```md
**Runner/hooks:** Optional manually installed `tools/agentic/runner.py` and `.codex/hooks.json`; availability and trust must be checked. TASKS.json is the runner-owned code-verification source when used. See `MANUAL_INSTALL.md`.
```

The project status stays **starter**, not "application completed".

## 4. `docs/DESIGN.md`

The clean starter already contains a small **Codex skill handoff** appendix at
its end. Replace that appendix (do not append repeated blocks) with:

```md
## Design skills — execution routing, not a new design authority

Visual requirements, approved tokens, page geometry, composition, and honest-data rules in this document remain authoritative. The landing page additionally follows `docs/LANDING_DESIGN.md`.

Repository-local Codex skills are discovered from `.agents/skills/<skill-name>/SKILL.md`. A reference to a skill is **not proof of installation**. Read the actual skill `name:` field and confirm its availability before invocation.

For meaningful new frontend work, consult **Taste** (typically `design-taste-frontend`) for composition and implementation only when installed. For a completed UI slice, consult **Impeccable** for targeted layout/accessibility/responsive critique when installed. Consult **Animate** only when an interaction genuinely needs motion; prefer reduced-motion-friendly CSS before adding dependencies. These tools may suggest improvements but cannot override this design system or invent missing image assets.

**Plantly visual-review** and Playwright MCP/Test provide actual browser evidence at 320×700, 390×844, 768×1024, 1440×900 and 1920×1080 where configured. Missing artwork is a visibly labeled `AWAITING USER ASSET` placeholder until the user supplies a real asset; do not generate fake final photography.

**Ponytail** is a separately installed engineering-simplicity plugin, not a design system or a guaranteed token/currency limiter. Follow its guidance only if installed and trusted; avoid unnecessary boilerplate, repeated large context loads, and unrelated skill invocations without weakening tests, accessibility, data provenance, or scientific approval.

Exact tool selection and installation policy: `docs/agent/SKILLS.md`. Agent-specific task routing: root `AGENTS.md` and `frontend/AGENTS.md`. Do not repeat detailed skill installation instructions throughout this visual specification.
```

Do not modify PRODUCT or ARCHITECTURE merely because a skill was installed.
If either contains **demonstrably stale skill-path/tooling claims**, correct just
that reference; no changes to approved features, stack, science, or data contracts.

## 5. `docs/agent/SKILLS.md`

Ensure these role rules appear once, without claiming installations:

```md
### Scoped design-skill routing

- **Marketing / new UI (PERSUADE):** read relevant DESIGN and LANDING_DESIGN sections, then Taste if discovered. Preserve real specified composition and truthful CTA states.
- **Workspace / input / dashboard UI (OPERATE):** DESIGN + relevant PRODUCT/ARCHITECTURE sections; Taste only for major layout work. No invented metrics.
- **Chat / explanation UI (EXPLAIN):** DESIGN + actual chat contract; prioritize cited evidence and accessible reading hierarchy.
- **Review:** Impeccable on meaningful implemented UI, not every minor patch; browser review must test actual working screens.
- **Motion:** Animate only if available and motion helps the task. Respect reduced motion and performance constraints.
- **Efficiency:** Ponytail only if installed/trusted as a plugin, not a skill folder. Simplicity guidance only; the external Python runner controls retries/reasoning efforts, not Ponytail.
- **Fallback:** absent skill -> do the work directly according to approved docs and record that optional assistance was unavailable; do not hallucinate a skill run.
```

Add a short pointer from `frontend/AGENTS.md` to this section if missing.

## 6. `.agents/skills/`

You install the third-party skills manually. Avoid copying Ponytail into this
folder: it is a **plugin**. Confirm each installed SKILL.md has valid YAML frontmatter.
Do not create a file named `taste/SKILL.md` unless that is genuinely the
installation path and the correct frontmatter name.

If you create your own Plantly-local skills, use distinct names such as
`plantly-visual-review`; local skills may enforce project-specific constraints,
but must not silently change the approved product or design system.
