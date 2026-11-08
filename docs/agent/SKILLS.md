# Optional skills and tools — manual setup, verified before use

**Do not claim any skill/plugin is installed just because it is named here.** Check actual discovery in the current Codex session. The user handles third-party installation and hook trust.

| Tool | Job | Invocation policy |
|---|---|---|
| Taste (Leonxlnx/taste-skill) | First-pass composition and frontend quality | Consult on meaningful UI creation if available; never override DESIGN/LANDING_DESIGN |
| Impeccable | Targeted visual/accessibility review | Use after a meaningful UI implementation if available; avoid dumping full context unnecessarily |
| Animate (delphi-ai/animate-skill) | Purposeful transitions and motion | Use only when motion is needed and installed; honor reduced motion |
| Ponytail (DietrichGebert/ponytail) | Simplicity-first engineering guidance | **Plugin, not a proven token-cost controller**; use if installed/trusted; no requirement to invoke unavailable commands |
| Playwright MCP | Real-browser interaction/screenshots | Use when configured and functional; Playwright Test remains a separate test suite |

## Manual installation references (don't run automatically)

- Taste: `npx skills add Leonxlnx/taste-skill` (verify target agent and installed skill name)
- Impeccable: `npx impeccable install` and follow its supported initialization for current version
- Animate: `npx skills add delphi-ai/animate-skill --skill animate`
- Ponytail: `codex plugin marketplace add DietrichGebert/ponytail` then `codex plugin add ponytail@ponytail`; use `/hooks` to review/trust its hooks, and restart the Codex thread if required
- Playwright MCP: inspect `codex mcp list`; add the official server manually if missing

Codex's documented repository skill path is `.agents/skills/<name>/SKILL.md`, **not** `.agent/skills/`. This directory is intentionally empty until you install skills. Ponytail plugin files usually live in the Codex plugin environment and should not be fabricated in this project.

## Selection rules

1. Product and architecture truth always outrank aesthetic suggestions.
2. DESIGN.md governs global tokens, LANDING_DESIGN.md the landing page, and this file only orchestrates tools.
3. Marketing = PERSUADE, workspace = OPERATE, explanations/chat = EXPLAIN.
4. Activate only skills needed for the task; don't load all of them on a backend change.
5. Use explicit **missing-asset** labels; don't generate fake photos or logo artwork.
6. No plugin may weaken auth, privacy, test requirements or human-reviewed agronomy rules.
7. Ponytail may promote smaller diffs; **no assumption of actual token/currency savings** and no automatic model/retry budget.
