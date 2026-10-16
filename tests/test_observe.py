"""hooks/observe.py — ghi log có cấu trúc, không ghi nội dung, không chặn, fail-open."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import HOOKS, clean_env, write
from test_contracts_brief import build

HOOK = os.path.join(HOOKS, "observe.py")


def fire(root, payload, env_extra=None):
    env = clean_env()
    env.update(env_extra or {})
    payload = dict({"session_id": "abcdef1234567890", "cwd": root}, **payload)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True, env=env, cwd=root)
    assert p.returncode == 0, p.stderr
    assert p.stderr == "", "hook phải im lặng: %s" % p.stderr
    return p


def lines(root):
    d = os.path.join(root, ".ai-dlc", "log")
    out = []
    for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        with open(os.path.join(d, n), encoding="utf-8") as f:
            out += [json.loads(l) for l in f if l.strip()]
    return out


def bash(cmd, stdout="", stderr=""):
    return {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": cmd},
            "tool_response": {"stdout": stdout, "stderr": stderr}}


class Observe(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_silent_outside_known_engines(self):
        fire(self.root, bash("pytest -q", "1 passed"))
        self.assertFalse(os.path.isdir(os.path.join(self.root, ".ai-dlc")))

    def test_validate_event_parses_result_line(self):
        build(self.root)
        fire(self.root, bash("python3 .agents/skills/aidlc/scripts/validate_workflow.py docs/intents/0001-sample --stage execute",
                             "ERROR E001: x\nResult: 1 error(s), 2 warning(s)"))
        e = lines(self.root)[-1]
        self.assertEqual((e["ev"], e["change"], e["stage"], e["errors"], e["warnings"]), ("validate", "0001-sample", "execute", 1, 2))
        self.assertEqual(e["s"], "abcdef12")
        self.assertTrue(e["ts"])

    def test_approve_event_has_gate_and_decision_but_no_name(self):
        build(self.root)
        fire(self.root, bash('python3 .agents/skills/aidlc/scripts/approvals.py docs/intents/0001-sample --gate plan --decision approve --by "Lan Nguyen"',
                             "Recorded approve for plan; no contract file changed."))
        e = lines(self.root)[-1]
        self.assertEqual((e["ev"], e["gate"], e["decision"], e["ok"]), ("approve", "plan", "approve", True))
        self.assertNotIn("Lan", json.dumps(e))

    def test_test_command_keeps_two_tokens_and_outcome_only(self):
        build(self.root)
        fire(self.root, bash("API_TOKEN=s3cret cd sources/backend && pytest tests/test_status.py -x", "", "FAILED tests/test_status.py::t - assert 0"))
        e = lines(self.root)[-1]
        self.assertEqual((e["ev"], e["outcome"]), ("test", "fail"))
        self.assertEqual(e["head"], "pytest tests/test_status.py")
        self.assertNotIn("s3cret", json.dumps(e))
        self.assertNotIn("API_TOKEN", json.dumps(e))
        fire(self.root, bash("pnpm test", "Tests: 12 passed, 12 total"))
        self.assertEqual(lines(self.root)[-1]["outcome"], "pass")

    def test_write_event_records_path_and_change_not_content(self):
        build(self.root)
        fire(self.root, {"hook_event_name": "PostToolUse", "tool_name": "Edit",
                         "tool_input": {"file_path": os.path.join(self.root, "docs/intents/0001-sample/plan.md"),
                                        "old_string": "SECRET BODY", "new_string": "OTHER BODY"}})
        e = lines(self.root)[-1]
        self.assertEqual((e["ev"], e["path"], e["change"], e["tool"]), ("write", "docs/intents/0001-sample/plan.md", "0001-sample", "Edit"))
        self.assertNotIn("SECRET BODY", json.dumps(e))

    def test_secret_paths_are_redacted(self):
        build(self.root)
        fire(self.root, {"hook_event_name": "PostToolUse", "tool_name": "Write",
                         "tool_input": {"file_path": os.path.join(self.root, "sources/backend/.env.production"), "content": "X=1"}})
        self.assertEqual(lines(self.root)[-1]["path"], "«redacted»")

    def test_plain_shell_is_not_logged(self):
        build(self.root)
        fire(self.root, bash("ls -la && cat README.md", "stuff"))
        self.assertEqual(lines(self.root), [])

    def test_git_logs_subcommand_only(self):
        build(self.root)
        fire(self.root, bash("git add docs/intents && git commit -m 'feat: secret-ish message'", "[feat abc] 1 file"))
        e = lines(self.root)[-1]
        self.assertEqual((e["ev"], e["sub"]), ("git", "add"))
        self.assertNotIn("secret-ish", json.dumps(e))

    def test_lifecycle_events(self):
        build(self.root)
        fire(self.root, {"hook_event_name": "SessionStart", "source": "startup"})
        fire(self.root, {"hook_event_name": "Stop", "stop_hook_active": False})
        fire(self.root, {"hook_event_name": "SessionEnd", "reason": "exit"})
        self.assertEqual([e["ev"] for e in lines(self.root)], ["session_start", "stop", "session_end"])

    def test_env_off_disables(self):
        build(self.root)
        fire(self.root, bash("pytest", "1 passed"), env_extra={"AI_DLC_OBSERVE": "off"})
        self.assertEqual(lines(self.root), [])

    def test_garbage_stdin_is_fail_open(self):
        build(self.root)
        p = subprocess.run([sys.executable, HOOK], input="not json", capture_output=True, text=True, env=clean_env(), cwd=self.root)
        self.assertEqual((p.returncode, p.stderr), (0, ""))


if __name__ == "__main__":
    unittest.main()
