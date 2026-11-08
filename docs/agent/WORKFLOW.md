# Plantly — supervised development and optional bounded runner

An optional Python runner is available only if the user has manually copied `tools/agentic/` into this repository. It requires explicit approved task IDs and a second environment opt-in; it never self-starts and selects no more than one task per run. In the runner mode it owns task status and verification. Manual Codex sessions remain supported, but must not edit the runner's active task concurrently.

## Before a task

1. User selects a task ID from `TASKS.json` and approves its scope.
2. Codex reads `STATE.md` and that task; checks dependency status, actual source tree, required human decisions and installed skills.
3. Codex explains any true blocker (credential, approval, missing architecture choice) without silently choosing one. A missing decorative image is not a blocker: the approved labeled placeholder rule applies.
4. Codex states the smallest implementation and concrete checks; then changes only that task.

## Completion standard

- Run **real** lint, build, tests or integration checks relevant to changed files. Do not create meaningless tests to make a green result.
- Frontend: exercise real page interactions in browser when tools/app exist, inspect actual screenshots at 320×700, 390×844, 768×1024, 1440×900, and 1920×1080. Missing Playwright means not verified.
- Backend: test relevant auth/security, migrations, data cases against actual disposable services where required. No fake DB or retrieval-evidence pass.
- An approved implementation may be `code_verified` while scientific review, final images or public release remain pending.
- Report commands and results and update `TASKS.json` + `STATE.md` **only after evidence exists**. Otherwise keep `todo` or mark `blocked` with reason in `ISSUES.md`.

## Retry and interruption

Runner mode uses the bounded stage list in `tools/agentic/config.json` (normal: low -> medium -> high; security/science: medium -> high) and persists attempt history across restarts. It halts at explicit human/infra blocks, rejects unapproved tasks, and never auto-grants scientific or release approvals. Manual sessions may still stop after two failed targeted fixes.

## Not claims

Tasks in `TASKS.json` are a *roadmap*, not runnable automation. Their acceptance language is not evidence the app or test suites exist. Provider selection, embeddings, pricing/trial, scientific approval, retention and deployment decisions remain open until actually recorded in `DECISIONS.md`.
