"""Plantly: bounded, manual-first Codex task runner (stdlib only).

This runner is deliberately *not* a paid-spend or scientific approval authority.
It never starts model work without an explicit --execute and environment opt-in.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TASK_FILE = ROOT / "docs/agent/TASKS.json"
CONFIG_FILE = ROOT / "tools/agentic/config.json"
LOCAL = ROOT / ".agentic"
RUN_FILE = LOCAL / "runtime.json"
LOCK_FILE = LOCAL / "runner.lock"
LOG_DIR = LOCAL / "logs"
VALID_STATES = {
    "todo", "in_progress", "blocked_human", "blocked_infra", "blocked_bug",
    "code_verified", "released", "exhausted"
}
VALID_TIERS = {"low", "medium", "high", "xhigh"}


class RunnerError(RuntimeError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def validate(registry: dict, config: dict) -> list[dict]:
    if registry.get("schema_version") != 1 or config.get("schema_version") != 1:
        raise RunnerError("Expected schema_version 1 in TASKS.json and config.json")
    tasks = registry.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise RunnerError("TASKS.json requires nonempty tasks list")
    ids = [x["id"] for x in tasks]
    if len(ids) != len(set(ids)):
        raise RunnerError("Duplicate task IDs")
    known = set(ids)
    for task in tasks:
        if task.get("status") not in VALID_STATES:
            raise RunnerError(f"Invalid task status for {task['id']}")
        if not set(task.get("depends_on", [])).issubset(known):
            raise RunnerError(f"Unknown dependency for {task['id']}")
    ordered, pending = [], {x["id"]: x for x in tasks}
    while pending:
        ready = [x for x in pending.values() if all(d in ordered for d in x.get("depends_on", []))]
        if not ready:
            raise RunnerError("Cyclic dependency graph")
        for x in ready:
            ordered.append(x["id"])
            del pending[x["id"]]
    if config.get("max_attempts_per_task", 0) not in range(1, 11):
        raise RunnerError("max_attempts_per_task must be 1..10")
    if not isinstance(config.get("approved_task_ids"), list) or not set(config["approved_task_ids"]).issubset(known):
        raise RunnerError("approved_task_ids must be a list of known task IDs")
    for risk, tiers in config.get("tiers", {}).items():
        if not isinstance(tiers, list) or not tiers:
            raise RunnerError(f"No escalation tiers for {risk}")
        for stage in tiers:
            if stage.get("reasoning_effort") not in VALID_TIERS:
                raise RunnerError(f"Invalid reasoning effort for {risk}")
            if stage.get("model") is not None and not isinstance(stage.get("model"), str):
                raise RunnerError(f"Invalid model for {risk}")
    for task_id, spec in config.get("verification", {}).items():
        if task_id not in known:
            raise RunnerError(f"Verification refers to unknown task {task_id}")
        for item in spec.get("commands", []):
            if not isinstance(item.get("argv"), list) or not item["argv"] or not all(isinstance(x, str) for x in item["argv"]):
                raise RunnerError(f"Invalid verifier argv in {task_id}")
            if not isinstance(item.get("cwd"), str):
                raise RunnerError(f"Missing verifier cwd in {task_id}")
    return [next(t for t in tasks if t["id"] == x) for x in ordered]


def stage_for(task: dict, config: dict, attempt_index: int) -> dict:
    risk = config.get("task_risk", {}).get(task["id"], "normal")
    stages = config["tiers"].get(risk)
    if stages is None:
        raise RunnerError(f"No tiers for risk {risk}")
    if attempt_index >= len(stages):
        raise RunnerError("Configured stage limit reached")
    return stages[attempt_index]


def executable(program: str) -> str:
    """Resolve bare Node commands to .cmd on native Windows; do not use shell=True."""
    if os.name == "nt" and program.lower() in {"npm", "npx", "codex"}:
        program += ".cmd"
    path = shutil.which(program)
    if path is None:
        raise RunnerError(f"Missing executable: {program}")
    return path


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([executable("git"), *args], cwd=ROOT, capture_output=True, text=True, timeout=12, check=False)


def check_git(clean: bool) -> None:
    out = git("rev-parse", "--show-toplevel")
    if out.returncode or Path(out.stdout.strip()).resolve() != ROOT.resolve():
        raise RunnerError("Run from the intended Git repository root (initialize Git manually first)")
    if clean and git("status", "--porcelain").stdout.strip():
        raise RunnerError("Working tree has changes. Review/commit or disable clean-start guard explicitly")


def get_runtime() -> dict:
    return load_json(RUN_FILE) if RUN_FILE.exists() else {"schema_version": 1, "tasks": {}}


def save_runtime(runtime: dict) -> None:
    atomic_json(RUN_FILE, runtime)


def acquire_lock() -> None:
    LOCAL.mkdir(parents=True, exist_ok=True)
    try:
        with LOCK_FILE.open("x", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "started": now()}, f)
    except FileExistsError as exc:
        raise RunnerError("Existing runner lock; check for running process, then use recover if stale") from exc


def release_lock() -> None:
    LOCK_FILE.unlink(missing_ok=True)


def readiness(task: dict, registry: dict, config: dict, runtime: dict) -> list[str]:
    errors = []
    if task["id"] not in config["approved_task_ids"]:
        errors.append("Task not explicitly authorized in config.approved_task_ids")
    state = task.get("status")
    if state not in {"todo", "blocked_bug"}:
        errors.append(f"Task status {state}; no automatic rerun/recovery")
    if task.get("human_gates"):
        errors.append("Human gates present; runner deliberately never auto-approves: " + ", ".join(task["human_gates"]))
    lookup = {t["id"]: t for t in registry["tasks"]}
    for dep in task.get("depends_on", []):
        if lookup[dep]["status"] not in {"code_verified", "released"}:
            errors.append(f"Dependency {dep} not code_verified")
    record = runtime.get("tasks", {}).get(task["id"], {})
    used = int(record.get("attempts_used", 0))
    stages = config["tiers"][config.get("task_risk", {}).get(task["id"], "normal")]
    if used >= min(config["max_attempts_per_task"], len(stages)):
        errors.append("Persistent retry budget exhausted; explicit manual reset needed")
    if record.get("status") == "interrupted":
        errors.append("Previous run interrupted; inspect logs and reconcile before retry")
    if not config.get("verification", {}).get(task["id"], {}).get("commands"):
        errors.append("No verification commands configured; refuse to mark verified")
    return errors


def choose_next(ordered: list[dict], registry: dict, config: dict, runtime: dict) -> dict:
    for task in ordered:
        if not readiness(task, registry, config, runtime):
            return task
    raise RunnerError("No eligible approved task; list blockers instead")


def mark_status(registry: dict, task: dict, state: str, evidence: dict | None = None) -> None:
    if state not in VALID_STATES:
        raise RunnerError("Bad state")
    task["status"] = state
    if evidence is not None:
        task.setdefault("evidence", []).append(evidence)
    atomic_json(TASK_FILE, registry)


def terminate_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, check=False, timeout=15)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_logged(argv: list[str], cwd: Path, log_path: Path, timeout: int, stdin_text: str | None = None) -> tuple[int, bool]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("wb") as output:
        proc = subprocess.Popen(
            argv, cwd=cwd, stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
            stdout=output, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            start_new_session=os.name != "nt",
        )
        try:
            proc.communicate(input=stdin_text.encode("utf-8") if stdin_text is not None else None, timeout=timeout)
            return proc.returncode, False
        except subprocess.TimeoutExpired:
            terminate_tree(proc)
            return 124, True


def parse_usage(jsonl_path: Path) -> int | None:
    """Diagnostic only. Does not claim provider-billed token/currency amounts."""
    latest = None
    for line in jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = event.get("usage", {})
        if event.get("type") == "turn.completed" and isinstance(usage, dict) and isinstance(usage.get("total_tokens"), int):
            latest = usage["total_tokens"]
    return latest


def safe_cwd(rel: str) -> Path:
    dst = (ROOT / rel).resolve()
    if not dst.is_relative_to(ROOT.resolve()):
        raise RunnerError("Verifier cwd escapes repository")
    if not dst.is_dir():
        raise RunnerError(f"Missing verifier directory: {rel}")
    return dst


def verifier_executable(program: str, cwd: Path) -> str:
    """Prefer the backend's project venv rather than an unrelated active Python."""
    if program == "python" and cwd.name == "backend":
        candidate = cwd / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if candidate.is_file():
            return str(candidate)
    return executable(program)


def verify(task_id: str, config: dict, run_folder: Path) -> tuple[bool, str]:
    spec = config["verification"][task_id]
    for rel in spec.get("required_paths", []):
        target = (ROOT / rel).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.exists():
            return False, f"Required artifact absent: {rel}"
    for idx, item in enumerate(spec["commands"], 1):
        try:
            cwd = safe_cwd(item["cwd"])
            argv = [verifier_executable(item["argv"][0], cwd), *item["argv"][1:]]
            result, timed_out = run_logged(argv, cwd, run_folder / f"verify-{idx:02d}.log", config["verification_timeout_seconds"])
        except (RunnerError, OSError) as exc:
            return False, f"Verifier cannot run: {exc}"
        if timed_out or result != 0:
            return False, f"Verifier {idx} failed (exit {result}); see {run_folder / f'verify-{idx:02d}.log'}"
    return True, "All configured checks passed"


def verify_only(task: dict, registry: dict, config: dict, runtime: dict) -> int:
    """Verify existing files without running Codex or spending another attempt."""
    task_id = task["id"]
    if task_id not in config["approved_task_ids"]:
        raise RunnerError("Task is not approved for runner verification")
    if task.get("human_gates"):
        raise RunnerError("Cannot bypass human gates using verification-only mode")
    if task["status"] in {"code_verified", "released"}:
        raise RunnerError(f"Task already has status {task['status']}")
    lookup = {item["id"]: item for item in registry["tasks"]}
    for dependency in task.get("depends_on", []):
        if lookup[dependency]["status"] not in {"code_verified", "released"}:
            raise RunnerError(f"Dependency {dependency} is not verified")
    spec = config.get("verification", {}).get(task_id, {})
    if not spec.get("commands"):
        raise RunnerError("No verification commands are configured")
    if task_id == "F-000":
        from urllib.parse import urlsplit
        test_url = os.environ.get("TEST_DATABASE_URL", "")
        if urlsplit(test_url).path.lstrip("/") != "plantly_test":
            raise RunnerError("Set TEST_DATABASE_URL to the disposable plantly_test database")

    check_git(clean=False)  # preserve uncommitted implementation work
    folder = LOG_DIR / task_id / f"manual-verify-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}-{os.getpid()}"
    acquire_lock()
    try:
        passed, reason = verify(task_id, config, folder)
        if not passed:
            append_issue(task_id, "verification", reason, folder)
            print(f"[Plantly] Verification failed: {reason}")
            print(f"[Plantly] Existing task status preserved: {task['status']}")
            return 1
        evidence = {
            "at": now(), "kind": "verification_only",
            "checks": spec["commands"], "logs": str(folder.relative_to(ROOT)),
        }
        record = runtime["tasks"].setdefault(task_id, {"attempts_used": 0, "attempts": []})
        record["status"] = "code_verified"
        record["verified_at"] = now()
        save_runtime(runtime)
        mark_status(registry, task, "code_verified", evidence)
        print(f"[Plantly] {task_id} code_verified using existing files; no Codex model invoked")
        print(f"[Plantly] Verification logs: {folder.relative_to(ROOT)}")
        return 0
    finally:
        release_lock()


def append_issue(task_id: str, category: str, explanation: str, folder: Path) -> None:
    """Brief audit trail outside Codex outputs; never include secrets or full logs."""
    issue_file = ROOT / "docs/agent/ISSUES.md"
    issue_file.parent.mkdir(parents=True, exist_ok=True)
    relative = str(folder.relative_to(ROOT))
    with issue_file.open("a", encoding="utf-8") as file:
        file.write(f"\n- **{now()} / {task_id} / {category}:** {explanation[:260]}\n"
                   f"  - Evidence: `{relative}` (local, git-ignored logs)\n")


def environment_issues() -> list[str]:
    issues = []
    try:
        check_git(clean=False)
    except (RunnerError, OSError) as exc:
        issues.append("Git root: " + str(exc))
    try:
        executable("codex")
    except RunnerError as exc:
        issues.append("Codex CLI: " + str(exc))
    return issues


def task_prompt(task: dict, stage: dict, attempt: int, last_reason: str) -> str:
    return f"""Implement ONLY Plantly task {task['id']}: {task['title']}.
Goal: {task['goal']}
Retry attempt: {attempt + 1}. Reasoning effort: {stage['reasoning_effort']}.
Previous verifier failure: {last_reason[:500] if last_reason else '(first attempt)'}
Read root AGENTS.md, docs/agent/STATE.md, this exact TASKS.json entry, and only relevant sections of PRODUCT/ARCHITECTURE/DESIGN. Use installed skills only when discovered. Do not approve science, change financial/hosting decisions, modify TASKS.json, or self-certify. Human gate? Output BLOCKED_BY_HUMAN and explain. Missing essential runtime? Output BLOCKED_BY_INFRA. If uncertain scientific approval, output BLOCKED_BY_SCIENCE.
Keep changes scoped, avoid invented data/assets, and implement the explicit tests that prove the task. Do NOT run or mutate the runner or its verification configuration.
The external runner will run verifiers and owns task status. Finish with a concise summary and any blockers.
"""


def stop_classification(last_message: str) -> str | None:
    text = last_message.upper()
    for marker in ("BLOCKED_BY_HUMAN", "BLOCKED_BY_INFRA", "BLOCKED_BY_SCIENCE"):
        if re.search(r"(?m)^\s*(?:[-*]\s*)?" + marker + r"\s*(?:[:—–]|$)", text):
            return marker
    return None


def run_one(task: dict, registry: dict, config: dict, runtime: dict) -> int:
    issues = readiness(task, registry, config, runtime)
    if issues:
        raise RunnerError("; ".join(issues))
    check_git(config.get("require_clean_git_at_task_start", True) and not runtime["tasks"].get(task["id"], {}).get("attempts_used"))
    codex = executable("codex")
    record = runtime["tasks"].setdefault(task["id"], {"attempts_used": 0, "attempts": [], "status": "idle"})
    attempt_cap = min(config["max_attempts_per_task"], len(config["tiers"][config.get("task_risk", {}).get(task["id"], "normal")]))
    record["status"] = "running"
    save_runtime(runtime)
    mark_status(registry, task, "in_progress")
    last_reason = ""
    while record["attempts_used"] < attempt_cap:
        i = record["attempts_used"]
        stage = stage_for(task, config, i)
        folder = LOG_DIR / task["id"] / f"attempt-{i+1:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        last_message = folder / "codex-last-message.txt"
        argv = [codex, "exec", "--cd", str(ROOT), "--sandbox", "workspace-write",
        "--json", "--output-last-message", str(last_message),
        "-c", f'model_reasoning_effort="{stage["reasoning_effort"]}"']
        if stage.get("model"):
            argv.extend(["--model", stage["model"]])
        argv.append("-")
        # Reserve the attempt BEFORE invoking Codex to preserve the budget across crashes.
        record["attempts_used"] += 1
        record["attempts"].append({"at": now(), "effort": stage["reasoning_effort"], "model": stage.get("model"), "folder": str(folder.relative_to(ROOT))})
        save_runtime(runtime)
        print(f"[Plantly] {task['id']} attempt {i+1}/{attempt_cap}, effort={stage['reasoning_effort']}", flush=True)
        try:
            ret, timed_out = run_logged(argv, ROOT, folder / "codex-events.jsonl", config["attempt_timeout_seconds"], task_prompt(task, stage, i, last_reason))
        except (OSError, RunnerError) as exc:
            last_reason = f"Codex launch error: {exc}"
            record["status"] = "blocked_infra"
            save_runtime(runtime)
            mark_status(registry, task, "blocked_infra")
            append_issue(task["id"], "infrastructure", last_reason, folder)
            print(last_reason)
            return 2
        message = last_message.read_text(encoding="utf-8", errors="replace") if last_message.exists() else ""
        usage = parse_usage(folder / "codex-events.jsonl")
        record["attempts"][-1].update({"cli_exit": ret, "timed_out": timed_out, "reported_tokens": usage})
        classification = stop_classification(message)
        if not message.strip() and ret == 0:
            classification = "BLOCKED_BY_INFRA"  # absent final message is not completed work
        if timed_out or ret != 0:
            # CLI/tooling failures are not verifier/implementation errors. Stop rather than spend retries.
            classification = "BLOCKED_BY_INFRA"
        if classification:
            state = "blocked_infra" if classification == "BLOCKED_BY_INFRA" else "blocked_human"
            record["status"] = state
            save_runtime(runtime)
            mark_status(registry, task, state)
            append_issue(task["id"], "human" if state == "blocked_human" else "infrastructure", classification, folder)
            print(f"[Plantly] {classification}: see {last_message}")
            return 3
        if ret == 0 and not timed_out:
            passed, last_reason = verify(task["id"], config, folder)
            if passed:
                evidence = {"at": now(), "kind": "runner_verification", "checks": config["verification"][task["id"]]["commands"], "logs": str(folder.relative_to(ROOT))}
                record["status"] = "code_verified"
                record["verified_at"] = now()
                save_runtime(runtime)
                mark_status(registry, task, "code_verified", evidence)
                print(f"[Plantly] {task['id']} code_verified (not science/release approved)")
                return 0
        else:
            last_reason = "Codex timed out" if timed_out else f"Codex exited {ret}. Read {folder / 'codex-events.jsonl'}"
        record["attempts"][-1]["failure"] = last_reason[:600]
        save_runtime(runtime)
        print("[Plantly] " + last_reason[:240], flush=True)
    record["status"] = "exhausted"
    save_runtime(runtime)
    mark_status(registry, task, "exhausted")
    append_issue(task["id"], "implementation/exhausted", last_reason, folder)
    print(f"[Plantly] {task['id']} attempts exhausted. Inspect {LOG_DIR / task['id']} before manual reset.")
    return 4


def doctor(registry: dict, config: dict) -> int:
    print("Plantly runner doctor: no models called")
    for command in ("git", "python", "codex"):
        try:
            print(f"  {command}: {executable(command)}")
        except RunnerError as exc:
            print(f"  {command}: {exc}")
    try:
        check_git(clean=False)
        print("  Git root: OK")
    except (RunnerError, OSError) as exc:
        print(f"  Git root: NOT READY ({exc})")
    print(f"  Tasks: {len(registry['tasks'])} | Explicitly approved: {config['approved_task_ids']}")
    print("  No reliable currency spending cap. Use explicit one-task execution, short timeouts and your provider's billing controls.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plantly supervised, bounded Codex runner")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("list")
    p_plan = sub.add_parser("plan")
    p_plan.add_argument("task_id")
    p_run = sub.add_parser("run")
    p_run.add_argument("task_id")
    p_run.add_argument("--execute", action="store_true")
    p_next = sub.add_parser("next")
    p_next.add_argument("--execute", action="store_true")
    p_verify = sub.add_parser("verify", help="Verify existing code without invoking Codex")
    p_verify.add_argument("task_id")
    p_recover = sub.add_parser("recover")
    p_recover.add_argument("--confirm-no-runner-active", action="store_true")
    p_reset = sub.add_parser("reset-attempts")
    p_reset.add_argument("task_id")
    p_reset.add_argument("--confirm", action="store_true")
    args = parser.parse_args(argv)
    registry, config = load_json(TASK_FILE), load_json(CONFIG_FILE)
    ordered = validate(registry, config)
    lookup = {t["id"]: t for t in registry["tasks"]}
    runtime = get_runtime()
    if args.command == "doctor":
        return doctor(registry, config)
    if args.command == "list":
        for t in ordered:
            print(f"{t['id']:6} {t['status']:15} {t['title']}")
        return 0
    if args.command == "verify":
        task = lookup.get(args.task_id)
        if task is None:
            raise RunnerError(f"Unknown task {args.task_id}")
        return verify_only(task, registry, config, runtime)
    if args.command == "recover":
        if not args.confirm_no_runner_active:
            raise RunnerError("First confirm no Python runner or child Codex process remains active")
        release_lock()
        for rec in runtime.get("tasks", {}).values():
            if rec.get("status") == "running":
                rec["status"] = "interrupted"
        save_runtime(runtime)
        print("Recovered lock; interrupted tasks still require manual review/reset")
        return 0
    if args.command == "reset-attempts":
        if not args.confirm or args.task_id not in lookup:
            raise RunnerError("Explicit --confirm and valid task ID required")
        if LOCK_FILE.exists():
            raise RunnerError("Cannot reset while runner lock exists")
        rec = runtime["tasks"].get(args.task_id, {})
        rec["attempts_used"] = 0
        rec["status"] = "idle"
        runtime["tasks"][args.task_id] = rec
        save_runtime(runtime)
        if lookup[args.task_id]["status"] in {"exhausted", "blocked_bug", "blocked_infra", "in_progress"}:
            mark_status(registry, lookup[args.task_id], "todo")
        print("Reset complete; previous logs retained. Review failure causes before another run.")
        return 0
    if args.command == "next":
        if not config.get("allow_next_task_selection"):
            raise RunnerError("next task selection disabled in config; use run TASK_ID")
        task = choose_next(ordered, registry, config, runtime)
    else:
        task = lookup.get(args.task_id)
        if task is None:
            raise RunnerError(f"Unknown task {args.task_id}")
    issues = readiness(task, registry, config, runtime)
    if args.command == "plan" or not args.execute:
        print(f"Task: {task['id']} — {task['title']}")
        print(f"Policy ready: {'yes' if not issues else 'NO'}")
        env_issues = environment_issues()
        print(f"Environment ready: {'yes' if not env_issues else 'NO'}")
        for issue in issues + env_issues:
            print(" - " + issue)
        print("Model attempts NOT started. Use run TASK_ID --execute with PLANTLY_ALLOW_MODEL_RUN=1")
        return 0
    if os.environ.get("PLANTLY_ALLOW_MODEL_RUN") != "1":
        raise RunnerError("Set PLANTLY_ALLOW_MODEL_RUN=1 intentionally to allow paid model execution")
    acquire_lock()
    try:
        return run_one(task, registry, config, runtime)
    finally:
        release_lock()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RunnerError as exc:
        print(f"[Plantly] BLOCKED: {exc}", file=sys.stderr)
        sys.exit(2)
