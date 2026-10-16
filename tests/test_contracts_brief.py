"""contracts_brief.py — brief/doctor đọc-only cho engine `contracts` (template đội, docs/intents/ bốn file).

Fixture tự dựng theo đúng template của đội (intent.md · plan.md · approvals.json · evidence.md); một ca SẠCH làm đối
chứng rồi đột biến (protocol §4.15). Không có validator trong fixture ⇒ `validator.available == False` — đó là một ca.
Đặt AI_DLC_TEMPLATE_PATH=<checkout project-starter-template-ai> để chạy thêm ca thật (có validator + git)."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import SCRIPTS, clean_env, write

INTENT = """# Intent: Sample change

- **Scope**: %(scope)s
- **Owner**: Lan (ops)
- **Implementation repository**: .
- **Backlog**: none
- **Security triggers**: none

## Problem

Users cannot see status.

## Proposed outcome

They can.

## Affected users and systems

Portal.

## Constraints

Existing auth only.

## Open questions

%(oq)s

## Success criteria

| ID | Criterion | How to verify |
| --- | --- | --- |
| AC-001 | Status is visible | `pytest tests/test_status.py` |

## Knowledge impact

%(ki)s
"""

PLAN = """# Plan: Sample change

- **Scope**: %(scope)s
- **Owner**: Minh
- **Implementation repository**: .
- **Branch**: feat/0001-sample

## Files that change

- `src/status.py` (new)
%(files)s
## Order of work

1. U-001 — Add status endpoint (AC-001) [owner: Minh]
%(units)s
## Risks

None.

## Proof

| AC | Check |
| --- | --- |
| AC-001 | `pytest tests/test_status.py` |
"""

EVIDENCE = """# Evidence: Sample change

## Work Units

| Unit | AC | Result | Check | Commit | Evidence |
| --- | --- | --- | --- | --- | --- |
%(rows)s
## Acceptance evidence

| AC | Result | Commit | Evidence |
| --- | --- | --- | --- |

## Outcome

- **Implementation commit**: [FULL_COMMIT_SHA]
- **Quality**: [PASS_OR_FAIL]

### Summary

[RESULT]

### Limitations

[NONE]
"""


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build(root, scope="feature", oq="None.", ki="None.", units="", files="", rows="", events=None):
    write(os.path.join(root, ".agents", "skills", "aidlc", "SKILL.md"), "---\nname: aidlc\n---\n")
    write(os.path.join(root, "docs", "memory", "project.md"), "# project\n")
    write(os.path.join(root, "docs", "intents", "_templates", "intent.md"), "# Intent: [CHANGE_NAME]\n")
    d = os.path.join(root, "docs", "intents", "0001-sample")
    write(os.path.join(d, "intent.md"), INTENT % {"scope": scope, "oq": oq, "ki": ki})
    write(os.path.join(d, "plan.md"), PLAN % {"scope": scope, "units": units, "files": files})
    write(os.path.join(d, "evidence.md"), EVIDENCE % {"rows": rows})
    write(os.path.join(d, "approvals.json"), json.dumps({"version": 1, "events": events or []}, indent=1))
    return d


def approve(d, gate, by="Lan"):
    """Ghi event đúng như approvals.py của đội: băm toàn bộ byte của các file gate ràng."""
    bind = {"intent": ["intent.md"], "plan": ["intent.md", "plan.md"], "contract": ["intent.md", "plan.md"],
            "outcome": ["intent.md", "plan.md", "evidence.md"]}[gate]
    p = os.path.join(d, "approvals.json")
    data = json.load(open(p))
    data["events"].append({"gate": gate, "decision": "approve", "by": by, "at": "2026-10-16T00:00:00Z",
                           "source": "chat", "files": {f: sha(os.path.join(d, f)) for f in bind}})
    json.dump(data, open(p, "w"), indent=1)


def run(root, *flags):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "contracts_brief.py"), root] + list(flags),
                       capture_output=True, text=True, env=clean_env(), cwd=root)
    return p.returncode, p.stdout, p.stderr


def brief(root, *flags):
    code, out, err = run(root, "--json", *flags)
    assert out, err
    return code, json.loads(out)


class ContractsBrief(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_not_a_contracts_workspace(self):
        code, out, err = run(self.root)
        self.assertEqual(code, 2)
        self.assertIn("contracts", err)

    def test_clean_feature_waits_for_intent(self):
        build(self.root)
        code, j = brief(self.root)
        self.assertEqual(code, 0)
        ch = j["changes"][0]
        self.assertEqual((ch["id"], ch["scope"], ch["gates"]), ("0001-sample", "feature", ["intent", "plan", "outcome"]))
        self.assertEqual((ch["pending"], ch["stage"], ch["say"]), ("intent", "draft", "approve intent"))
        self.assertEqual(ch["approvals"]["intent"]["state"], "none")
        self.assertEqual([u["id"] for u in ch["units"]], ["U-001"])
        self.assertEqual(ch["units"][0]["owner"], "Minh")
        self.assertFalse(ch["open_questions"])
        self.assertFalse(ch["validator"]["available"], "fixture không có validator của đội")

    def test_approval_advances_pending_gate(self):
        d = build(self.root)
        approve(d, "intent")
        _, j = brief(self.root)
        ch = j["changes"][0]
        self.assertEqual(ch["approvals"]["intent"]["state"], "current")
        self.assertEqual((ch["pending"], ch["stage"]), ("plan", "draft"))
        approve(d, "plan")
        _, j = brief(self.root)
        ch = j["changes"][0]
        self.assertEqual((ch["pending"], ch["stage"], ch["say"]), ("outcome", "execute", "approve outcome"))

    def test_changed_bytes_make_approval_stale(self):
        d = build(self.root)
        approve(d, "intent")
        with open(os.path.join(d, "intent.md"), "a") as f:
            f.write("\nedited after approval\n")
        code, j = brief(self.root, "--doctor")
        ch = j["changes"][0]
        self.assertEqual(ch["approvals"]["intent"]["state"], "stale")
        self.assertEqual(ch["approvals"]["intent"]["stale_files"], ["intent.md"])
        self.assertEqual(ch["pending"], "intent", "duyệt cũ không còn giá trị — quay lại gate đó")
        self.assertIn("D12", [f["code"] for f in j["doctor"]])
        self.assertEqual(code, 1, "doctor có FIX ⇒ exit 1")

    def test_bugfix_uses_combined_contract_gate(self):
        build(self.root, scope="bugfix")
        _, j = brief(self.root)
        ch = j["changes"][0]
        self.assertEqual(ch["gates"], ["contract", "outcome"])
        self.assertIn("Intent + Plan", ch["say"])

    def test_request_changes_is_revision_not_approval(self):
        d = build(self.root)
        p = os.path.join(d, "approvals.json")
        json.dump({"version": 1, "events": [{"gate": "intent", "decision": "request-changes", "by": "Lan",
                                             "at": "2026-10-16T00:00:00Z", "source": "chat", "files": {}}]}, open(p, "w"))
        _, j = brief(self.root, "--doctor")
        self.assertEqual(j["changes"][0]["approvals"]["intent"]["state"], "revision")
        self.assertIn("D13", [f["code"] for f in j["doctor"]])

    def test_doctor_flags_second_source_of_truth(self):
        build(self.root)
        os.makedirs(os.path.join(self.root, ".ai-dlc", "context-memory"))
        code, j = brief(self.root, "--doctor")
        d01 = [f for f in j["doctor"] if f["code"] == "D01"]
        self.assertEqual(len(d01), 1)
        self.assertEqual(d01[0]["level"], "FIX")
        self.assertEqual(code, 1)

    def test_doctor_notes_extra_unlisted_file(self):
        d = build(self.root)
        write(os.path.join(d, "sources.md"), "# S\n")
        _, j = brief(self.root, "--doctor")
        ch = j["changes"][0]
        self.assertEqual(ch["extra_files"], ["sources.md"])
        self.assertEqual(ch["extra_unlisted"], ["sources.md"])
        self.assertIn("D16", [f["code"] for f in j["doctor"]])
        self.assertEqual([f["level"] for f in j["doctor"] if f["code"] == "D16"], ["INFO"])

    def test_extra_file_listed_in_plan_is_fine(self):
        d = build(self.root, files="- `docs/intents/0001-sample/sources.md`\n")
        write(os.path.join(d, "sources.md"), "# S\n")
        _, j = brief(self.root, "--doctor")
        self.assertEqual(j["changes"][0]["extra_unlisted"], [])
        self.assertNotIn("D16", [f["code"] for f in j["doctor"]])

    def test_knowledge_impact_needs_knowledge_unit(self):
        build(self.root, ki="| Target | Change |\n| --- | --- |\n| `CHANGELOG.md` | add line |\n")
        _, j = brief(self.root, "--doctor")
        self.assertTrue(j["changes"][0]["knowledge_impact"])
        self.assertIn("D15", [f["code"] for f in j["doctor"]])
        build(self.root, ki="| Target | Change |\n| --- | --- |\n| `CHANGELOG.md` | add line |\n",
              units="2. U-002 — Reconcile knowledge impact [knowledge]\n")
        _, j = brief(self.root, "--doctor")
        self.assertNotIn("D15", [f["code"] for f in j["doctor"]])

    def test_last_evidence_row_per_unit_wins(self):
        d = build(self.root, rows="| U-001 | AC-001 | Fail | pytest | abc | log |\n| U-001 | AC-001 | Pass | pytest | def | log |\n")
        approve(d, "intent"); approve(d, "plan")
        _, j = brief(self.root)
        ch = j["changes"][0]
        self.assertEqual((ch["units_pass"], ch["units_fail"]), (1, []))

    def test_open_questions_flagged_in_text_brief(self):
        build(self.root, oq="Do adjusters need access too?")
        code, out, err = run(self.root)
        self.assertEqual(code, 0)
        self.assertIn("Open questions", out)
        self.assertIn("approve intent", out)
        self.assertIn("never infer approval", out)

    def test_short_brief_is_one_line_per_change(self):
        build(self.root)
        _, out, _ = run(self.root, "--short")
        self.assertIn("0001-sample · feature", out)
        self.assertNotIn("owner Lan", out)

    def test_missing_file_is_fix(self):
        d = build(self.root)
        os.remove(os.path.join(d, "evidence.md"))
        code, j = brief(self.root, "--doctor")
        self.assertIn("D10", [f["code"] for f in j["doctor"]])
        self.assertEqual(code, 1)

    def test_ideation_and_templates_dirs_are_not_changes(self):
        build(self.root)
        os.makedirs(os.path.join(self.root, "docs", "intents", "ideation", "x-2026"))
        os.makedirs(os.path.join(self.root, "docs", "intents", "legacy-draft"))
        _, j = brief(self.root, "--doctor")
        self.assertEqual([c["id"] for c in j["changes"]], ["0001-sample"])
        self.assertIn("D03", [f["code"] for f in j["doctor"]])


@unittest.skipUnless(os.environ.get("AI_DLC_TEMPLATE_PATH"), "đặt AI_DLC_TEMPLATE_PATH để chạy trên template thật")
class RealTemplate(unittest.TestCase):
    def test_runs_on_real_template(self):
        root = os.environ["AI_DLC_TEMPLATE_PATH"]
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "layout.py"), root, "--json"],
                           capture_output=True, text=True, env=clean_env())
        self.assertEqual(json.loads(p.stdout)["engine"], "contracts")
        code, out, err = run(root, "--doctor")
        self.assertIn(code, (0, 1), err)
        self.assertIn("engine contracts", out)


if __name__ == "__main__":
    unittest.main()
