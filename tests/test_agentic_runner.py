"""Stdlib tests. They never call a real Codex model, network, or database."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

BASE = Path(__file__).resolve().parents[1]
STANDALONE_STARTER = Path(__file__).resolve().parents[2] / "plantly-clean-agentic-starter"
TASKS_SOURCE = BASE / "docs/agent/TASKS.json"
if not TASKS_SOURCE.is_file():
    TASKS_SOURCE = STANDALONE_STARTER / "docs/agent/TASKS.json"


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, BASE / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner = load_module("plantly_runner", "tools/agentic/runner.py")
hooks = load_module("plantly_hooks", "tools/agentic/hooks.py")


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs/agent").mkdir(parents=True)
        (self.root / "tools/agentic").mkdir(parents=True)
        cfg = json.loads((BASE / "tools/agentic/config.json").read_text())
        registry = json.loads(TASKS_SOURCE.read_text())
        for task in registry["tasks"]:
            task["status"] = "todo"
        (self.root / "tools/agentic/config.json").write_text(json.dumps(cfg))
        (self.root / "docs/agent/TASKS.json").write_text(json.dumps(registry))
        for attr, new in (
            ("ROOT", self.root), ("TASK_FILE", self.root / "docs/agent/TASKS.json"),
            ("CONFIG_FILE", self.root / "tools/agentic/config.json"),
            ("LOCAL", self.root / ".agentic"),
            ("RUN_FILE", self.root / ".agentic/runtime.json"),
            ("LOCK_FILE", self.root / ".agentic/runner.lock"),
            ("LOG_DIR", self.root / ".agentic/logs"),
        ):
            p = mock.patch.object(runner, attr, new)
            p.start()
            self.addCleanup(p.stop)
        self.cfg, self.reg = cfg, registry
        self.task = self.reg["tasks"][0]
        self.runtime = {"schema_version": 1, "tasks": {}}

    def test_registry_topology(self):
        ordered = runner.validate(self.reg, self.cfg)
        ids = [t["id"] for t in ordered]
        self.assertLess(ids.index("D-010"), ids.index("F-040"))
        self.assertLess(ids.index("F-040"), ids.index("F-050"))

    def test_cycle_rejected(self):
        self.reg["tasks"][0]["depends_on"] = ["F-050"]
        with self.assertRaisesRegex(runner.RunnerError, "Cyclic"):
            runner.validate(self.reg, self.cfg)

    def test_human_gates_never_autorun(self):
        task = next(x for x in self.reg["tasks"] if x["id"] == "G-010")
        self.cfg["approved_task_ids"].append("G-010")
        self.assertTrue(any("Human gates" in s for s in runner.readiness(task, self.reg, self.cfg, self.runtime)))

    def test_no_verification_not_verified(self):
        self.cfg["verification"].pop("F-000")
        self.assertTrue(any("No verification" in s for s in runner.readiness(self.task, self.reg, self.cfg, self.runtime)))

    def test_attempt_budget_persists(self):
        self.runtime["tasks"]["F-000"] = {"attempts_used": 3, "status": "idle"}
        runner.save_runtime(self.runtime)
        restored = runner.get_runtime()
        self.assertEqual(restored["tasks"]["F-000"]["attempts_used"], 3)
        self.assertTrue(any("exhausted" in e for e in runner.readiness(self.task, self.reg, self.cfg, restored)))

    def test_lock_blocks_concurrent_run(self):
        runner.acquire_lock()
        with self.assertRaisesRegex(runner.RunnerError, "lock"):
            runner.acquire_lock()
        runner.release_lock()
        self.assertFalse(runner.LOCK_FILE.exists())

    def test_stage_progression_and_sensitive_bound(self):
        self.assertEqual(runner.stage_for(self.task, self.cfg, 0)["reasoning_effort"], "low")
        self.assertEqual(runner.stage_for(self.task, self.cfg, 2)["reasoning_effort"], "high")
        sec = next(x for x in self.reg["tasks"] if x["id"] == "F-020")
        self.assertEqual(runner.stage_for(sec, self.cfg, 0)["reasoning_effort"], "medium")
        with self.assertRaises(runner.RunnerError):
            runner.stage_for(sec, self.cfg, 2)

    def test_success_requires_real_verification(self):
        def fake_exec(*args, **kwargs):
            return "codex-bin"
        def fake_run(argv, cwd, log, timeout, stdin_text=None):
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text('{"type":"turn.completed","usage":{"total_tokens":222}}\n')
            Path(argv[argv.index("--output-last-message") + 1]).write_text("Implemented code.")
            return 0, False
        with mock.patch.object(runner, "check_git"), mock.patch.object(runner, "executable", side_effect=fake_exec), \
             mock.patch.object(runner, "run_logged", side_effect=fake_run), \
             mock.patch.object(runner, "verify", return_value=(True, "tests passed")) as verification:
            self.assertEqual(runner.run_one(self.task, self.reg, self.cfg, self.runtime), 0)
        self.assertTrue(verification.called)
        self.assertEqual(self.task["status"], "code_verified")
        self.assertEqual(self.runtime["tasks"]["F-000"]["attempts_used"], 1)
        self.assertEqual(self.runtime["tasks"]["F-000"]["attempts"][0]["reported_tokens"], 222)

    def test_verify_only_succeeds_without_codex_or_attempt_reset(self):
        self.task["status"] = "blocked_infra"
        self.runtime["tasks"]["F-000"] = {"attempts_used": 2, "attempts": [], "status": "blocked_infra"}
        runner.save_runtime(self.runtime)
        runner.atomic_json(runner.TASK_FILE, self.reg)
        with mock.patch.dict("os.environ", {"TEST_DATABASE_URL": "postgresql+psycopg://plantly:local@127.0.0.1:5433/plantly_test"}), \
             mock.patch.object(runner, "check_git"), \
             mock.patch.object(runner, "verify", return_value=(True, "All configured checks passed")) as verifier, \
             mock.patch.object(runner, "run_one", side_effect=AssertionError("Must not run Codex")):
            self.assertEqual(runner.main(["verify", "F-000"]), 0)
        self.assertTrue(verifier.called)
        self.assertEqual(self.task["status"], "blocked_infra")  # main loads registry from disk
        updated = runner.load_json(runner.TASK_FILE)
        self.assertEqual(updated["tasks"][0]["status"], "code_verified")
        self.assertEqual(runner.get_runtime()["tasks"]["F-000"]["attempts_used"], 2)
        self.assertEqual(updated["tasks"][0]["evidence"][-1]["kind"], "verification_only")

    def test_verify_only_failure_preserves_blocked_state(self):
        self.task["status"] = "blocked_infra"
        runner.save_runtime(self.runtime)
        runner.atomic_json(runner.TASK_FILE, self.reg)
        with mock.patch.dict("os.environ", {"TEST_DATABASE_URL": "postgresql+psycopg://plantly:local@127.0.0.1:5433/plantly_test"}), \
             mock.patch.object(runner, "check_git"), \
             mock.patch.object(runner, "verify", return_value=(False, "Ruff failed")), \
             mock.patch.object(runner, "run_one", side_effect=AssertionError("Must not run Codex")):
            self.assertEqual(runner.main(["verify", "F-000"]), 1)
        self.assertEqual(runner.load_json(runner.TASK_FILE)["tasks"][0]["status"], "blocked_infra")
        self.assertEqual(runner.get_runtime()["tasks"], {})

    def test_verify_only_refuses_nondisposable_database(self):
        self.task["status"] = "blocked_infra"
        runner.save_runtime(self.runtime)
        runner.atomic_json(runner.TASK_FILE, self.reg)
        with mock.patch.dict("os.environ", {"TEST_DATABASE_URL": "postgresql+psycopg://plantly:local@127.0.0.1:5432/plantly"}), \
             self.assertRaisesRegex(runner.RunnerError, "disposable"):
            runner.main(["verify", "F-000"])

    def test_backend_verifier_prefers_project_venv(self):
        backend = self.root / "backend"
        local_python = backend / ".venv" / ("Scripts/python.exe" if runner.os.name == "nt" else "bin/python")
        local_python.parent.mkdir(parents=True, exist_ok=True)
        local_python.touch()
        self.assertEqual(runner.verifier_executable("python", backend), str(local_python))

    def test_failed_verification_escalates_then_exhausts(self):
        def fake_run(argv, cwd, log, timeout, stdin_text=None):
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text('{}\n')
            Path(argv[argv.index("--output-last-message") + 1]).write_text("Still working.")
            return 0, False
        with mock.patch.object(runner, "check_git"), mock.patch.object(runner, "executable", return_value="codex-bin"), \
             mock.patch.object(runner, "run_logged", side_effect=fake_run), \
             mock.patch.object(runner, "verify", return_value=(False, "test failed")):
            self.assertEqual(runner.run_one(self.task, self.reg, self.cfg, self.runtime), 4)
        self.assertEqual(self.task["status"], "exhausted")
        self.assertEqual(self.runtime["tasks"]["F-000"]["attempts_used"], 3)
        self.assertTrue(runner.readiness(self.task, self.reg, self.cfg, self.runtime))

    def test_blocked_human_no_retry(self):
        def fake_run(argv, cwd, log, timeout, stdin_text=None):
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text('{}\n')
            Path(argv[argv.index("--output-last-message") + 1]).write_text("BLOCKED_BY_HUMAN: need credentials")
            return 0, False
        with mock.patch.object(runner, "check_git"), mock.patch.object(runner, "executable", return_value="codex-bin"), \
             mock.patch.object(runner, "run_logged", side_effect=fake_run):
            self.assertEqual(runner.run_one(self.task, self.reg, self.cfg, self.runtime), 3)
        self.assertEqual(self.task["status"], "blocked_human")
        self.assertEqual(self.runtime["tasks"]["F-000"]["attempts_used"], 1)

    def test_timeout_is_infra_stop_after_one_attempt(self):
        def fake_run(argv, cwd, log, timeout, stdin_text=None):
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text('{}\n')
            return 124, True
        with mock.patch.object(runner, "check_git"), mock.patch.object(runner, "executable", return_value="codex-bin"), \
             mock.patch.object(runner, "run_logged", side_effect=fake_run) as invoker:
            self.assertEqual(runner.run_one(self.task, self.reg, self.cfg, self.runtime), 3)
        self.assertEqual(invoker.call_count, 1)
        self.assertEqual(self.task["status"], "blocked_infra")

    def test_execute_requires_environment_opt_in(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(runner.RunnerError, "PLANTLY_ALLOW_MODEL_RUN"):
                runner.main(["run", "F-000", "--execute"])
        self.assertFalse(runner.LOCK_FILE.exists())

    def test_unsafe_path_refused(self):
        self.cfg["verification"]["F-000"]["required_paths"] = ["../../otherplace"]
        passed, reason = runner.verify("F-000", self.cfg, self.root)
        self.assertFalse(passed)
        self.assertIn("absent", reason)


class HooksTests(unittest.TestCase):
    def test_start_context_is_short(self):
        result = hooks.evaluate({}, "start")
        self.assertLess(len(json.dumps(result)), 550)
        self.assertIn("TASKS.json", result["hookSpecificOutput"]["additionalContext"])

    def test_dangerous_command_denied(self):
        for cmd in ("git reset --hard", "git clean -fd", "rm -rf /", "Remove-Item . -Recurse -Force", "DROP DATABASE plantly"):
            with self.subTest(cmd=cmd):
                result = hooks.evaluate({"tool_input": {"command": cmd}}, "guard")
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_safe_command_no_output(self):
        self.assertEqual(hooks.evaluate({"tool_input": {"command": "git status --short"}}, "guard"), {})


if __name__ == "__main__":
    unittest.main()
