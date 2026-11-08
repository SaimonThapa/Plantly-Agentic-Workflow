# Plantly frontend rules

Follow root `AGENTS.md`. For each UI task, consult only relevant sections of `docs/DESIGN.md` and the relevant page spec. Landing work also consults `docs/LANDING_DESIGN.md`; design-skill routing is in `docs/agent/SKILLS.md`.

Use approved Next.js App Router, JavaScript, Tailwind v4 and accessible shared primitives. UI presents **persisted real data or explicitly labeled sample/unavailable states**, never invented scientific metrics. Preserve mobile layout, keyboard use, contrast, and reduced motion.

If artwork is missing, render a labeled in-layout placeholder describing the needed source and composition, and update `docs/agent/ASSETS.md`. Don't generate final-looking artwork. Do not claim Playwright MCP or test suites work until directly exercised.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
