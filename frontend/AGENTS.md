# Plantly frontend rules

Follow root `AGENTS.md`. For each UI task, consult only relevant sections of `docs/DESIGN.md` and the relevant page spec. Landing work also consults `docs/LANDING_DESIGN.md`; design-skill routing is in `docs/agent/SKILLS.md`.

Use approved Next.js App Router, JavaScript, Tailwind v4 and accessible shared primitives. UI presents **persisted real data or explicitly labeled sample/unavailable states**, never invented scientific metrics. Preserve mobile layout, keyboard use, contrast, and reduced motion.

If artwork is missing, render a labeled in-layout placeholder describing the needed source and composition, and update `docs/agent/ASSETS.md`. Don't generate final-looking artwork. Do not claim Playwright MCP or test suites work until directly exercised.
