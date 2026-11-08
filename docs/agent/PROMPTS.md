# Short prompts for Codex (manual task handoff)

## First session: inspect without building

> Inspect this new Plantly repository and read root `AGENTS.md`, `docs/agent/STATE.md`, and only the sections of authoritative docs necessary to evaluate starting `F-000`. Check actual Git status, runtime tools and missing project files. Show a short table of verified prerequisites, blockers and decisions needed from me. **Do not install software, edit files or start F-000** until I approve.

## Then: implement one approved task

> I authorize task `<TASK_ID>` only. Follow root/nested AGENTS instructions. Read the matching entry in `docs/agent/TASKS.json`, check dependencies and real code, consult exact relevant spec sections, then implement the smallest correct vertical slice. Use installed skills only if actually discoverable. For missing images, create visibly labeled slots, not fabricated artwork. Run actual checks and update task state only with evidence. Stop on human gates or after two distinct failed fixes. Do not advance to another task without approval.

## Verify / handoff

> Review the diff for `<TASK_ID>` against the approved acceptance criteria. Run available relevant tests and inspect real browser behavior if this is UI work. Report test commands, outcomes, missing verification, and next task suggestion. Never claim scientific or deployment approval from code checks.
