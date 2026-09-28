"""gate_guard.py — hàng rào ghi code trước Gate D. Autopilot đóng Gate D bằng DEC thật ⇒ guard phải mở."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import HOOKS, build, clean_env


def guard(root, file_path, env_extra=None):
    env = clean_env()
    env.update(env_extra or {})
    payload = json.dumps({"cwd": root, "tool_name": "Write", "tool_input": {"file_path": file_path}})
    p = subprocess.run([sys.executable, os.path.join(HOOKS, "gate_guard.py")], input=payload,
                       capture_output=True, text=True, env=env, cwd=root)
    return p.returncode, p.stderr


class GateGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.code = os.path.join(self.root, "src", "api", "orders.py")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_code_before_gate_d(self):
        build(self.root, gates_auto=("A", "B", "C"))
        rc, err = guard(self.root, self.code)
        self.assertEqual(rc, 2)
        self.assertIn("Gate D", err)

    def test_allows_code_after_gate_d_closed_by_autopilot(self):
        build(self.root, gates_auto=("A", "B", "C", "D"))
        self.assertEqual(guard(self.root, self.code)[0], 0)

    def test_allows_code_after_gate_d_closed_by_human(self):
        build(self.root, mode="lead", gates_auto=("A", "B", "C", "D"))
        self.assertEqual(guard(self.root, self.code)[0], 0)

    def test_allows_non_code_paths_before_gate_d(self):
        build(self.root, gates_auto=("A",))
        self.assertEqual(guard(self.root, os.path.join(self.root, "README.md"))[0], 0)
        self.assertEqual(guard(self.root, os.path.join(self.root, ".ai-dlc", "context-memory", "x.md"))[0], 0)

    def test_kill_switch_and_fail_open(self):
        build(self.root, gates_auto=("A",))
        self.assertEqual(guard(self.root, self.code, {"AI_DLC_GUARD": "off"})[0], 0)
        self.assertEqual(guard(self.root, self.code, {"AI_DLC_ENGINE": "off"})[0], 0)
        with tempfile.TemporaryDirectory() as plain:                      # không phải dự án ai-dlc
            self.assertEqual(guard(plain, os.path.join(plain, "src", "a.py"))[0], 0)

    def test_custom_state_dir_still_guarded(self):
        build(self.root, gates_auto=("A",))
        os.rename(os.path.join(self.root, ".ai-dlc"), os.path.join(self.root, "state"))
        with open(os.path.join(self.root, "ai-dlc.config.json"), "w") as f:
            json.dump({"engine": "ai-dlc", "state": "state"}, f)
        self.assertEqual(guard(self.root, self.code)[0], 2)


if __name__ == "__main__":
    unittest.main()
