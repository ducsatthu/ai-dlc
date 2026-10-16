"""tower_contracts.py — tower cho engine `contracts`: thẻ "Cần tôi quyết" và nút gọi approvals.py của đội.

Server thật trên port tự chọn, fixture bốn file dựng lại từ test_contracts_brief. approvals.py của đội được thay bằng
một stub ghi lại tham số (ca xanh) để test không phụ thuộc checkout template; ca thật chạy khi đặt AI_DLC_TEMPLATE_PATH.
Mọi ca chặn đi theo đúng một đột biến so với ca xanh (protocol §4.15)."""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from helpers import SCRIPTS, write
from test_contracts_brief import approve, build

sys.path.insert(0, SCRIPTS)
import tower_contracts as tc  # noqa: E402

STUB_APPROVALS = r'''#!/usr/bin/env python3
"""Stub approvals.py: ghi tham số ra called.json rồi thêm event như script của đội (băm toàn bộ byte)."""
import argparse, hashlib, json, os, sys
BIND = {"intent": ["intent.md"], "plan": ["intent.md", "plan.md"], "contract": ["intent.md", "plan.md"],
        "outcome": ["intent.md", "plan.md", "evidence.md"]}
ap = argparse.ArgumentParser()
ap.add_argument("spec_dir"); ap.add_argument("--gate", required=True); ap.add_argument("--decision", required=True)
ap.add_argument("--by", required=True)
a = ap.parse_args()
if not a.by.strip() or a.by.strip().lower() == "ai" or "[" in a.by:
    print("a confirmed human name is required", file=sys.stderr); sys.exit(1)
json.dump(vars(a), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "called.json"), "w"))
p = os.path.join(a.spec_dir, "approvals.json")
d = json.load(open(p))
d["events"].append({"gate": a.gate, "decision": a.decision, "by": a.by, "at": "2026-10-16T00:00:00Z", "source": "chat",
                    "files": {f: hashlib.sha256(open(os.path.join(a.spec_dir, f), "rb").read()).hexdigest() for f in BIND[a.gate]}})
json.dump(d, open(p, "w"), indent=1)
print("Recorded %s for %s; no contract file changed." % (a.decision, a.gate))
'''

STUB_VALIDATOR_RED = "import sys\nprint('ERROR plan.md: Branch missing')\nprint('Result: 1 error, 0 warning')\nsys.exit(1)\n"
STUB_VALIDATOR_GREEN = "print('Result: 0 errors, 0 warnings')\n"


class Tower(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.change = build(self.root)
        self.scripts = os.path.join(self.root, ".agents", "skills", "aidlc", "scripts")
        write(os.path.join(self.scripts, "approvals.py"), STUB_APPROVALS)
        self.srv = tc.make_server(self.root, 0, token="t0ken")
        self.port = self.srv.server_address[1]
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    # ---- helpers ----
    def get(self, path, token="t0ken"):
        url = "http://127.0.0.1:%d%s%stoken=%s" % (self.port, path, "&" if "?" in path else "?", token)
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.status, json.loads(r.read().decode("utf-8")), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read().decode("utf-8")), ""

    def post(self, body, token="t0ken"):
        req = urllib.request.Request("http://127.0.0.1:%d/approve?token=%s" % (self.port, token),
                                     data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read().decode("utf-8"))

    def good(self, **over):
        body = {"change": "0001-sample", "gate": "intent", "decision": "approve", "by": "Lan", "previewed": True}
        body.update(over)
        return body

    def called(self):
        p = os.path.join(self.scripts, "called.json")
        return json.load(open(p)) if os.path.isfile(p) else None

    def log_events(self):
        d = os.path.join(self.root, ".ai-dlc", "log")
        out = []
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                out += [json.loads(l) for l in f if l.strip()]
        return out

    # ---- đọc ----
    def test_page_is_html_and_state_needs_token(self):
        url = "http://127.0.0.1:%d/" % self.port
        with urllib.request.urlopen(url, timeout=10) as r:
            self.assertIn("text/html", r.headers.get("Content-Type", ""))
            self.assertIn("Cần tôi quyết", r.read().decode("utf-8"))
        code, j, _ = self.get("/state", token="sai")
        self.assertEqual(code, 403)
        code, j, _ = self.get("/state")
        self.assertEqual(code, 200)
        self.assertEqual(j["engine"], "contracts")
        self.assertEqual([c["id"] for c in j["need"]], ["0001-sample"])
        self.assertEqual(j["need"][0]["pending"], "intent")
        self.assertEqual(j["need"][0]["bind"], ["intent.md"])
        self.assertTrue(j["approvals_py"])

    def test_doc_serves_only_the_four_files_of_a_change(self):
        code, j, _ = self.get("/doc?change=0001-sample&file=intent.md")
        self.assertEqual(code, 200)
        self.assertIn("# Intent: Sample change", j["text"])
        for bad in ("/doc?change=0001-sample&file=../../memory/project.md", "/doc?change=..&file=intent.md",
                    "/doc?change=0001-sample&file=notes.md"):
            code, j, _ = self.get(bad)
            self.assertEqual(code, 404, bad)

    # ---- ca xanh ----
    def test_approve_calls_team_script_with_human_name_and_logs_without_name(self):
        code, j = self.post(self.good())
        self.assertEqual(code, 200, j)
        self.assertTrue(j["ok"])
        c = self.called()
        self.assertEqual((c["gate"], c["decision"], c["by"]), ("intent", "approve", "Lan"))
        self.assertEqual(c["spec_dir"], os.path.join("docs", "intents", "0001-sample"))
        self.assertEqual(j["pending"], "plan", "sau khi duyệt intent, gate chờ là plan")
        self.assertIn("không commit trên main", j["next"])
        ev = [e for e in self.log_events() if e["ev"] == "approve"]
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["change"], ev[0]["gate"], ev[0]["decision"], ev[0]["ok"], ev[0]["via"]),
                         ("0001-sample", "intent", "approve", True, "tower"))
        self.assertNotIn("Lan", json.dumps(ev), "log không ghi tên người")
        _, j, _ = self.get("/state")
        self.assertEqual(j["need"][0]["approvals"]["intent"]["state"], "current")

    def test_request_changes_does_not_need_preview_or_clean_validator(self):
        write(os.path.join(self.scripts, "validate_workflow.py"), STUB_VALIDATOR_RED)
        code, j = self.post(self.good(decision="request-changes", previewed=False))
        self.assertEqual(code, 200, j)
        self.assertEqual(self.called()["decision"], "request-changes")
        _, s, _ = self.get("/state")
        self.assertEqual(s["need"][0]["approvals"]["intent"]["state"], "revision")

    # ---- mỗi ca một đột biến ----
    def test_ai_name_is_refused_before_calling(self):
        for name in ("ai", "AI", "", "  ", "[OWNER]", "Claude"):
            code, j = self.post(self.good(by=name))
            self.assertEqual(code, 400, name)
        self.assertIsNone(self.called(), "không được gọi approvals.py")
        self.assertEqual(self.log_events(), [])

    def test_approve_without_preview_is_refused(self):
        code, j = self.post(self.good(previewed=False))
        self.assertEqual(code, 400)
        self.assertIn("previewed", j["error"])
        self.assertIsNone(self.called())

    def test_gate_must_be_the_pending_one(self):
        code, j = self.post(self.good(gate="plan"))
        self.assertEqual(code, 409)
        self.assertIn("`intent`", j["error"])
        self.assertIsNone(self.called())
        approve(self.change, "intent"); approve(self.change, "plan")
        code, j = self.post(self.good(gate="intent"))
        self.assertEqual(code, 409)
        self.assertIn("`outcome`", j["error"])

    def test_fully_approved_change_has_nothing_to_decide(self):
        approve(self.change, "intent"); approve(self.change, "plan"); approve(self.change, "outcome")
        _, s, _ = self.get("/state")
        self.assertEqual(s["need"], [])
        code, j = self.post(self.good(gate="outcome"))
        self.assertEqual(code, 409)
        self.assertIn("không còn gate", j["error"])

    def test_red_validator_blocks_approve(self):
        write(os.path.join(self.scripts, "validate_workflow.py"), STUB_VALIDATOR_RED)
        code, j = self.post(self.good())
        self.assertEqual(code, 409)
        self.assertIn("1 error", j["error"])
        self.assertIsNone(self.called())
        write(os.path.join(self.scripts, "validate_workflow.py"), STUB_VALIDATOR_GREEN)
        code, j = self.post(self.good())
        self.assertEqual(code, 200, j)

    def test_missing_team_script_means_no_write(self):
        os.remove(os.path.join(self.scripts, "approvals.py"))
        _, s, _ = self.get("/state")
        self.assertFalse(s["approvals_py"])
        code, j = self.post(self.good())
        self.assertEqual(code, 501)
        self.assertEqual(json.load(open(os.path.join(self.change, "approvals.json")))["events"], [])

    def test_unknown_change_and_bad_body(self):
        code, j = self.post(self.good(change="0002-nope"))
        self.assertEqual(code, 404)
        code, j = self.post(self.good(change="../x"))
        self.assertEqual(code, 400)
        code, j = self.post(["not", "an", "object"])
        self.assertEqual(code, 400)
        code, j = self.post(self.good(), token="sai")
        self.assertEqual(code, 403)

    def test_team_script_refusal_is_reported_not_hidden(self):
        write(os.path.join(self.scripts, "approvals.py"), "import sys\nprint('Plan approval requires the matching prior Intent approval', file=sys.stderr)\nsys.exit(1)\n")
        code, j = self.post(self.good())
        self.assertEqual(code, 409)
        self.assertIn("approvals.py từ chối", j["error"])
        ev = [e for e in self.log_events() if e["ev"] == "approve"]
        self.assertEqual([e["ok"] for e in ev], [False])

    def test_not_a_contracts_workspace_exits_2(self):
        with tempfile.TemporaryDirectory() as other:
            self.assertEqual(tc.main([other]), 2)


@unittest.skipUnless(os.environ.get("AI_DLC_TEMPLATE_PATH"), "đặt AI_DLC_TEMPLATE_PATH để chạy với approvals.py thật của đội")
class RealApprovals(unittest.TestCase):
    """Clone template thật, tạo change bằng start_change.py của đội, rồi đi qua tower → approvals.py thật.
    Change mới toàn placeholder nên validator của đội chưa sạch: duyệt phải bị chặn và sổ không đổi; yêu cầu sửa (không
    validate) phải được script của đội ghi đúng dạng (source chat, băm intent.md)."""

    def test_real_team_script_through_the_tower(self):
        import subprocess
        tpl = os.environ["AI_DLC_TEMPLATE_PATH"]
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(os.path.realpath(tmp), "ws")
            subprocess.run(["git", "clone", "-q", "--local", tpl, root], check=True, capture_output=True)
            scripts = os.path.join(root, ".agents", "skills", "aidlc", "scripts")
            p = subprocess.run([sys.executable, os.path.join(scripts, "start_change.py"), "tower-check",
                                "--workspace-root", root, "--branch", "feat/tower-check"],
                               cwd=root, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            changes = [n for n in os.listdir(os.path.join(root, "docs", "intents")) if n.endswith("-tower-check")]
            self.assertEqual(len(changes), 1)
            cid = changes[0]
            d = os.path.join(root, "docs", "intents", cid)
            code, j = tc.record_decision(root, {"change": cid, "gate": "intent", "decision": "approve",
                                                "by": "Lan", "previewed": True})
            self.assertEqual(code, 409, j)
            # validator của đội ở stage draft cho qua, nhưng approvals.py validate strict file gate ràng và từ chối:
            # lời từ chối của script đội phải lên tới thẻ nguyên văn
            self.assertIn("approvals.py từ chối", j["error"])
            self.assertIn("placeholders", j["error"])
            with open(os.path.join(d, "approvals.json")) as f:
                self.assertEqual(json.load(f)["events"], [], "duyệt bị chặn, sổ không đổi")
            code, j = tc.record_decision(root, {"change": cid, "gate": "intent", "decision": "request-changes", "by": "Lan"})
            self.assertEqual(code, 200, j)
            ev = json.load(open(os.path.join(d, "approvals.json")))["events"]
            self.assertEqual(len(ev), 1)
            self.assertEqual((ev[0]["gate"], ev[0]["decision"], ev[0]["by"], ev[0]["source"]),
                             ("intent", "request-changes", "Lan", "chat"))
            self.assertEqual(set(ev[0]["files"]), {"intent.md"})
            self.assertEqual(cb_state(root, cid), "revision")
            code, j = tc.record_decision(root, {"change": cid, "gate": "intent", "decision": "approve", "by": "ai", "previewed": True})
            self.assertEqual(code, 400, "tên ai bị chặn trước khi tới script của đội")


def cb_state(root, cid):
    return tc.cb.read_change(root, os.path.join(root, "docs", "intents", cid))["approvals"]["intent"]["state"]


if __name__ == "__main__":
    unittest.main()
