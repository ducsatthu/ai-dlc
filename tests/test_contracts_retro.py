"""contracts_retro.py — ứng viên LL từ approvals.json + evidence.md + log của observe.py. Ca sạch rồi đột biến."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import SCRIPTS, clean_env, write
from test_contracts_brief import build

SCRIPT = os.path.join(SCRIPTS, "contracts_retro.py")


def log(root, events):
    lines = []
    for i, e in enumerate(events):
        e = dict({"ts": "2026-10-%02dT10:%02d:00+07:00" % (1 + i // 50, i % 50), "s": "sess0001"}, **e)
        lines.append(json.dumps(e, ensure_ascii=False))
    write(os.path.join(root, ".ai-dlc", "log", "2026-10.jsonl"), "\n".join(lines) + "\n")


def run(root, *flags):
    p = subprocess.run([sys.executable, SCRIPT, root, "--json"] + list(flags), capture_output=True, text=True, env=clean_env(), cwd=root)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def codes(j):
    return sorted(c["code"] for c in j["candidates"])


class ContractsRetro(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_project_has_no_candidates(self):
        build(self.root)
        log(self.root, [{"ev": "validate", "change": "0001-sample", "stage": "draft", "errors": 0, "warnings": 1},
                        {"ev": "test", "head": "pytest", "outcome": "pass", "change": "0001-sample"}, {"ev": "stop"}])
        j = run(self.root)
        self.assertEqual(j["candidates"], [])
        self.assertEqual((j["stats"]["validate_clean"], j["stats"]["tests"], j["stats"]["turns"]), (1, 1, 1))

    def test_r01_request_changes_twice_same_gate(self):
        d = build(self.root)
        ev = [{"gate": "intent", "decision": "request-changes", "by": "Lan", "at": "2026-10-01T01:00:00Z", "files": {}},
              {"gate": "intent", "decision": "request-changes", "by": "Lan", "at": "2026-10-01T02:00:00Z", "files": {}}]
        write(os.path.join(d, "approvals.json"), json.dumps({"version": 1, "events": ev}))
        self.assertIn("R01", codes(run(self.root)))

    def test_r02_same_test_red_three_times_in_a_row(self):
        build(self.root)
        log(self.root, [{"ev": "test", "head": "pytest tests/x.py", "outcome": "fail", "change": "0001-sample"}] * 3)
        self.assertIn("R02", codes(run(self.root)))
        log(self.root, [{"ev": "test", "head": "pytest tests/x.py", "outcome": "fail"},
                        {"ev": "test", "head": "pytest tests/x.py", "outcome": "pass"},
                        {"ev": "test", "head": "pytest tests/x.py", "outcome": "fail"}])
        self.assertNotIn("R02", codes(run(self.root)), "đỏ–xanh–đỏ không phải chuỗi liên tiếp")
        log(self.root, [{"ev": "test", "head": "pytest tests/x.py", "outcome": "fail"}] * 2)
        self.assertIn("R02", codes(run(self.root, "--max-self-fix", "2")))

    def test_r03_validator_errors_after_approval_twice(self):
        build(self.root)
        log(self.root, [{"ev": "validate", "change": "0001-sample", "stage": "execute", "errors": 2, "warnings": 0},
                        {"ev": "validate", "change": "0001-sample", "stage": "outcome", "errors": 1, "warnings": 0},
                        {"ev": "validate", "change": "0001-sample", "stage": "draft", "errors": 5, "warnings": 0}])
        j = run(self.root)
        self.assertIn("R03", codes(j))
        self.assertIn("execute/outcome", next(c for c in j["candidates"] if c["code"] == "R03")["msg"])

    def test_r04_unit_fail_twice_in_evidence(self):
        build(self.root, rows="| U-001 | AC-001 | Fail | pytest | a | l |\n| U-001 | AC-001 | Fail | pytest | b | l |\n| U-001 | AC-001 | Pass | pytest | c | l |\n")
        self.assertIn("R04", codes(run(self.root)))

    def test_r05_gate_waited_long_after_clean_validator(self):
        d = build(self.root)
        log(self.root, [{"ts": "2026-10-01T08:00:00+00:00", "ev": "validate", "change": "0001-sample", "stage": "draft", "errors": 0, "warnings": 0}])
        write(os.path.join(d, "approvals.json"), json.dumps({"version": 1, "events": [
            {"gate": "intent", "decision": "approve", "by": "Lan", "at": "2026-10-03T08:00:00Z", "files": {}}]}))
        j = run(self.root)
        self.assertIn("R05", codes(j))
        self.assertEqual(next(c for c in j["candidates"] if c["code"] == "R05")["level"], "INFO")
        self.assertNotIn("R05", codes(run(self.root, "--wait-hours", "72")))

    def test_x01_same_pattern_across_two_changes_is_top(self):
        d1 = build(self.root)
        d2 = os.path.join(self.root, "docs", "intents", "0002-other")
        for f in ("intent.md", "plan.md", "evidence.md"):
            write(os.path.join(d2, f), open(os.path.join(d1, f), encoding="utf-8").read())
        ev = [{"gate": "intent", "decision": "request-changes", "by": "Lan", "at": "2026-10-01T01:00:00Z", "files": {}}] * 2
        for d in (d1, d2):
            write(os.path.join(d, "approvals.json"), json.dumps({"version": 1, "events": ev}))
        j = run(self.root)
        self.assertEqual(j["candidates"][0]["code"], "X01")
        self.assertEqual(j["candidates"][0]["level"], "FIX")
        self.assertEqual(j["candidates"][0]["evidence"], ["0001-sample", "0002-other"])

    def test_since_filters_log(self):
        build(self.root)
        log(self.root, [{"ev": "test", "head": "pytest", "outcome": "fail"}] * 3)
        self.assertEqual(run(self.root, "--since", "2026-11-01")["stats"]["events"], 0)

    def test_write_creates_generated_candidates_file(self):
        build(self.root)
        j = run(self.root, "--write")
        p = j["written"]
        self.assertTrue(p.endswith(os.path.join(".ai-dlc", "governance", "lessons-learned", "candidates.md")))
        txt = open(p, encoding="utf-8").read()
        self.assertIn("generated_by: contracts_retro.py", txt)
        self.assertIn("không sửa tay", txt)

    def test_not_contracts_workspace(self):
        p = subprocess.run([sys.executable, SCRIPT, self.root], capture_output=True, text=True, env=clean_env())
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
