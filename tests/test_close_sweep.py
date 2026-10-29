"""close_sweep.py (protocol §2.5) — đóng intent theo sự thật đo được; mỗi điều kiện C1–C3 có ca đột biến riêng."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import SCRIPTS, clean_env, read, write  # noqa: E402

SWEEP = os.path.join(SCRIPTS, "close_sweep.py")
BRIEF = os.path.join(SCRIPTS, "session_brief.py")


def sh(cwd, *a):
    subprocess.run(list(a), cwd=cwd, check=True, capture_output=True, env=clean_env())


def status(iid, gate_open="null", phase="construction", extra=""):
    return ("---\nintent: %s\nstage: 6\nphase: %s\ngates_passed: [A]\ngate_open: %s   # chú thích\n%s---\n# %s\n"
            % (iid, phase, gate_open, extra, iid))


class CloseSweep(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        cm = os.path.join(self.d, ".ai-dlc", "context-memory")
        self.cm = cm
        write(os.path.join(cm, "governance", "decisions-log.md"), "# Decisions\n\n## DEC-0041 · x · Gate A · INT-001\n")
        for iid, kw in (("INT-001", {}), ("INT-002", {}), ("INT-003", {"gate_open": "A"}), ("INT-004", {}),
                        ("INT-005", {}), ("INT-006", {"phase": "closed"})):
            write(os.path.join(cm, "intents", iid, "status.md"), status(iid, **kw))
        write(os.path.join(cm, "escalations", "ESC-0401.md"),
              "---\nid: ESC-0401\nintent: INT-004\nseverity: high\nstatus: open\n---\n# x\n")
        write(os.path.join(cm, "escalations", "ESC-0101.md"),
              "---\nid: ESC-0101\nintent: INT-001\nseverity: medium\nstatus: open\n---\n# không chặn\n")
        sh(self.d, "git", "init", "-q", "-b", "main")
        sh(self.d, "git", "config", "user.email", "t@example.com")
        sh(self.d, "git", "config", "user.name", "t")
        write(os.path.join(self.d, ".gitignore"), ".ai-dlc/\n")
        for iid in ("INT-001", "INT-003", "INT-004"):
            sh(self.d, "git", "commit", "-q", "--allow-empty", "-m", "%s: làm xong" % iid)
        sh(self.d, "git", "checkout", "-q", "-b", "feat")
        sh(self.d, "git", "commit", "-q", "--allow-empty", "-m", "INT-002 chưa merge")
        sh(self.d, "git", "commit", "-q", "--allow-empty", "-m", "INT-0010 là intent khác, không được đếm")
        sh(self.d, "git", "checkout", "-q", "main")

    def run_sweep(self, *flags):
        r = subprocess.run([sys.executable, SWEEP, self.d, "--json"] + list(flags), capture_output=True, text=True,
                           env=clean_env())
        return r.returncode, (json.loads(r.stdout) if r.stdout.startswith("{") else r.stdout)

    def rows(self, out):
        return {r["intent"]: r for r in out["intents"]}

    def test_measure_only(self):
        rc, out = self.run_sweep()
        self.assertEqual(rc, 0)
        rows = self.rows(out)
        self.assertNotIn("INT-006", rows)                       # đã đóng thì bỏ qua
        self.assertTrue(rows["INT-001"]["closable"])            # ESC medium không chặn
        self.assertEqual(rows["INT-001"]["commits"], 1)         # INT-0010 không bị đếm nhầm
        self.assertIn("C1", rows["INT-002"]["why_not"][0])      # commit chưa vào main
        self.assertTrue(any("C2" in w for w in rows["INT-003"]["why_not"]))
        self.assertTrue(any("C3" in w for w in rows["INT-004"]["why_not"]))
        self.assertIn("không có commit", rows["INT-005"]["why_not"][0])
        self.assertIn("gate_open: null   # chú thích", read(os.path.join(self.cm, "intents", "INT-001", "status.md")))

    def test_apply_closes_only_closable(self):
        rc, out = self.run_sweep("--apply")
        self.assertEqual(out["dec"], "DEC-0042")
        st = read(os.path.join(self.cm, "intents", "INT-001", "status.md"))
        self.assertIn("phase: closed", st)
        self.assertIn("closed_by: DEC-0042", st)
        self.assertIn("gates_passed: [A]", st)                  # không tự ký bù gate
        self.assertIn("## Đóng tự động", st)
        self.assertIn("phase: construction", read(os.path.join(self.cm, "intents", "INT-002", "status.md")))
        log = read(os.path.join(self.cm, "governance", "decisions-log.md"))
        self.assertIn("## DEC-0042", log)
        self.assertIn("Đảo bằng", log)
        rc2, out2 = self.run_sweep("--apply")                   # chạy lại: không đóng gì thêm, không DEC mới
        self.assertIsNone(out2["dec"])
        self.assertEqual(log, read(os.path.join(self.cm, "governance", "decisions-log.md")))

    def test_closure_ask_refuses_apply(self):
        write(os.path.join(self.cm, "governance", "autopilot.md"), "---\nmode: lead\nclosure: ask\n---\n")
        rc, _ = self.run_sweep("--apply")
        self.assertEqual(rc, 3)
        self.assertIn("phase: construction", read(os.path.join(self.cm, "intents", "INT-001", "status.md")))

    def test_explicit_dec(self):
        _, out = self.run_sweep("--apply", "--dec", "DEC-1805")
        self.assertEqual(out["dec"], "DEC-1805")


class SessionNumbering(unittest.TestCase):
    def test_gap_in_logs_creates_next_after_max(self):
        d = tempfile.mkdtemp()
        log = os.path.join(d, ".ai-dlc", "context-memory", "session", "log")
        write(os.path.join(log, "SES-001.md"), "---\nid: SES-001\n---\n")
        write(os.path.join(log, "SES-003.md"), "---\nid: SES-003\n---\n")
        write(os.path.join(d, ".ai-dlc", "context-memory", "intents", ".keep"), "")
        subprocess.run([sys.executable, BRIEF, d, "--open-session"], capture_output=True, env=clean_env())
        self.assertTrue(os.path.isfile(os.path.join(log, "SES-004.md")))
        self.assertEqual(read(os.path.join(log, "SES-003.md")), "---\nid: SES-003\n---\n")


if __name__ == "__main__":
    unittest.main()
