"""Minimal Codex hooks for Plantly. Not a complete security sandbox.

Run manually for testing:
  echo '{"hook_event_name":"SessionStart","cwd":"..."}' | python tools/agentic/hooks.py start
  echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | python tools/agentic/hooks.py guard
"""
from __future__ import annotations

import json
import re
import sys

START_CONTEXT = (
    "Plantly: follow AGENTS.md; read one task from docs/agent/TASKS.json and relevant "
    "sections of PRODUCT/ARCHITECTURE/DESIGN. Skills are optional and must be "
    "discoverable. Use labeled missing-asset placeholders. Never invent science, "
    "change approved specs, or grant human approvals. The external runner, when "
    "used, owns verification and task status."
)

# These are defense-in-depth warnings/blocks, NOT exhaustive command parsing.
# Codex's sandbox, Git review, permissions and human approval remain necessary.
HIGH_RISK = [
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-[a-z]*f[a-z]*d\b", re.IGNORECASE),
    re.compile(r"\brm\s+(-[a-z]*r[a-z]*f|-\w*f\w*r)\s+(/|\.\.?)(?:\s|$)", re.IGNORECASE),
    re.compile(r"\bRemove-Item\b[^\r\n]*(?<!\w)-Recurse\b[^\r\n]*(?<!\w)-Force\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+DATABASE\b", re.IGNORECASE),
]


def evaluate(event: dict, action: str) -> dict:
    if action == "start":
        return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": START_CONTEXT}}
    if action != "guard":
        raise ValueError("Expected start or guard")
    inp = event.get("tool_input", {})
    if not isinstance(inp, dict):
        return {}
    cmd = inp.get("command")
    if not isinstance(cmd, str):
        return {}
    for pat in HIGH_RISK:
        if pat.search(cmd):
            return {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Plantly: destructive command requires explicit human/manual execution."
            }}
    return {}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in {"start", "guard"}:
        print("Usage: hooks.py start|guard", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    result = evaluate(payload if isinstance(payload, dict) else {}, argv[0])
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
