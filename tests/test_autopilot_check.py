"""Luật autopilot (protocol §2.3) — ca sạch làm đối chứng, mỗi test đột biến MỘT thứ và đòi đúng MỘT mã."""
import os
import re
import tempfile
import time
import unittest

from helpers import PAD, autopilot_check, build, codes, dec, read, write


class AutopilotCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = build(self.tmp.name)
        self.log = os.path.join(self.p["gov"], "decisions-log.md")
        self.status = os.path.join(self.p["intent"], "status.md")

    def tearDown(self):
        self.tmp.cleanup()

    def sub(self, path, pattern, repl, count=1):
        s = read(path)
        new, n = re.subn(pattern, repl, s, count=count, flags=re.S)   # re.S: xoá được cả khối DEC
        self.assertGreater(n, 0, "đột biến không trúng gì: %r trong %s" % (pattern, path))
        write(path, new)

    def expect(self, code, level="FIX"):
        rc, info, findings = autopilot_check(self.p["root"])
        self.assertEqual(codes(findings), [code], findings)
        self.assertTrue(all(f["level"] == level for f in findings), findings)
        self.assertEqual(rc, 1 if level == "FIX" else 0)
        return findings

    # ---- đối chứng -------------------------------------------------------------------------
    def test_clean_project_has_no_findings(self):
        rc, info, findings = autopilot_check(self.p["root"])
        self.assertEqual(findings, [])
        self.assertEqual((rc, info["mode"], info["decisions"]), (0, "autopilot", 4))

    # ---- AP01–AP03: DEC phải đảo được ------------------------------------------------------
    def test_dec_missing_each_required_line(self):
        for line in ("Chọn", "Bỏ", "Block check"):
            with self.subTest(line=line):
                build(self.tmp.name)
                self.sub(self.log, r"- %s: [^\n]*\n" % line, "")
                f = self.expect("AP01")
                self.assertIn(line, f[0]["msg"])

    def test_dec_missing_inline_fields(self):
        self.sub(self.log, r"- Đảo bằng: [^\n]*?(?=   - Hiện ở)", "")
        self.assertIn("Đảo bằng", self.expect("AP01")[0]["msg"])

    def test_shown_at_points_to_missing_file(self):
        self.sub(self.log, r"- Hiện ở: intent-plan\.md#3", "- Hiện ở: khong-co.md#1")
        self.expect("AP02")

    def test_block_check_incomplete(self):
        self.sub(self.log, r" · #6 pass", "")
        self.expect("AP03")

    def test_block_check_hit_but_decided(self):
        self.sub(self.log, r"#4 pass", "#4 hit: migration xoá cột")
        self.expect("AP03")

    # ---- AP04: gates_auto phải có DEC ------------------------------------------------------
    def test_gate_auto_without_dec(self):
        self.sub(self.log, r"## DEC-0003 .*?(?=## DEC-0004)", "")
        self.expect("AP04")

    # ---- AP05: KHÔNG BỎ BƯỚC ---------------------------------------------------------------
    def test_skipped_step_missing_artefact(self):
        for rel in ("intent-plan.md", "as-is/source-ledger.md", "open-questions-business.md", "unit-plan.md"):
            with self.subTest(artefact=rel):
                build(self.tmp.name)
                os.remove(os.path.join(self.p["intent"], rel))
                rc, info, findings = autopilot_check(self.p["root"])
                self.assertIn("AP05", codes(findings, "FIX"))
                self.assertEqual(rc, 1)

    def test_skipped_step_stub_artefact(self):
        write(os.path.join(self.p["intent"], "unit-plan.md"), "---\nversion: 1\n---\n# Unit plan\n")
        self.expect("AP05")

    def test_skipped_step_unit_missing_file(self):
        os.remove(os.path.join(self.p["intent"], "units", "UOW-02", "nfr.md"))
        self.expect("AP05")

    def test_short_artefact_for_small_scope_is_fine(self):
        # phạm vi nhỏ ⇒ tài liệu ngắn là ĐÚNG; chỉ vỏ rỗng mới là bỏ bước
        write(os.path.join(self.p["intent"], "unit-plan.md"),
              "---\nversion: 1\n---\n# Unit plan\n## 2. Bảng Unit\n" + PAD[:260])
        rc, info, findings = autopilot_check(self.p["root"])
        self.assertEqual(findings, [])

    # ---- AP06: tự quyết qua block ----------------------------------------------------------
    def test_decided_through_blocking_question_without_default(self):
        q = os.path.join(self.p["intent"], "open-questions-business.md")
        self.sub(q, r"\| chỉ quản lý kho \| CHẶN UOW-02", "|  | CHẶN UOW-02")
        self.expect("AP06")

    def test_blocking_question_with_default_is_not_a_block(self):
        rc, info, findings = autopilot_check(self.p["root"])          # ca sạch có câu CHẶN + mặc định
        self.assertNotIn("AP06", codes(findings))

    def test_decided_with_planned_source(self):
        led = os.path.join(self.p["intent"], "as-is", "source-ledger.md")
        self.sub(led, r"\| S-02 \| docs/roles\.md \| vai trò \| read \|", "| S-02 | docs/roles.md | vai trò | planned |")
        self.expect("AP06")

    # ---- AP07: người đã Đảo ----------------------------------------------------------------
    def test_pending_steer(self):
        write(os.path.join(self.p["inbox"], "steer-20260928T101500.json"),
              '{"type":"steer","dec":"DEC-0002","intent":"INT-001","note":"Đảo sang: chờ nguồn 6"}')
        self.expect("AP07")

    # ---- WARN ------------------------------------------------------------------------------
    def test_block_older_than_24h(self):
        build(self.tmp.name, gates_auto=("A", "B", "C"), gate_open="D", blocked_by="#1 · OQB-01 cần chị Lan chọn")
        old = time.time() - 30 * 3600
        os.utime(self.status, (old, old))
        self.expect("AP08", level="WARN")

    def test_fresh_block_is_silent(self):
        build(self.tmp.name, gates_auto=("A", "B", "C"), gate_open="D", blocked_by="#1 · OQB-01 cần chị Lan chọn")
        rc, info, findings = autopilot_check(self.p["root"])
        self.assertEqual(findings, [])

    def test_stop_without_reason(self):
        build(self.tmp.name, gates_auto=("A", "B", "C"), gate_open="D")
        self.expect("AP10", level="WARN")

    def test_reversal_rate(self):
        log = "# Decisions log\n\n" + "".join(
            dec(i, "A" if i == 1 else "B" if i == 2 else "C" if i == 3 else "D",
                shown="intent-plan.md#3") for i in range(1, 13))
        write(self.log, log)
        self.expect("AP09", level="WARN")                               # 0/12 đảo — không ai nhìn
        write(self.log, "# Decisions log\n\n" + "".join(
            dec(i, "ABCD"[min(i - 1, 3)], shown="intent-plan.md#3",
                extra="- reverses: DEC-0001\n" if i > 7 else "") for i in range(1, 13)))
        f = self.expect("AP09", level="WARN")                           # 5/12 đảo — giả định kém
        self.assertIn("> 30%", f[0]["msg"])

    # ---- mode lead: hành vi 6.3.0 ----------------------------------------------------------
    def test_lead_mode_is_untouched(self):
        for mode in ("lead", None):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as t:
                    p = build(t, mode=mode)
                    os.remove(os.path.join(p["intent"], "unit-plan.md"))   # lỗi autopilot sẽ bắt — lead thì không
                    rc, info, findings = autopilot_check(t)
                    self.assertEqual((rc, findings), (0, []))

    def test_autopilot_dec_under_lead_mode(self):
        self.sub(os.path.join(self.p["gov"], "autopilot.md"), r"mode: autopilot", "mode: lead")
        self.expect("AP11", level="WARN")

    def test_not_an_ai_dlc_project(self):
        with tempfile.TemporaryDirectory() as t:
            rc, info, findings = autopilot_check(t)
            self.assertEqual((rc, findings, info["mode"]), (0, [], "off"))


if __name__ == "__main__":
    unittest.main()
