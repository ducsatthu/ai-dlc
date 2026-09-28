"""Bản mô hình cho người xem không được lệch bản chữ (protocol §2.4) — ca sạch + mỗi ca một đột biến."""
import copy
import hashlib
import json
import os
import tempfile
import unittest

from helpers import PAD, build, read, run_py, write

DOC = """---
type: intent-plan
id: INT-001
version: 1
---
# INT-001 · Kế hoạch Intent

### 1.2 Outcome
- [ ] **O1** — người ngoài danh sách không huỷ được
- [ ] **O2** — mỗi lượt huỷ biết ai, lúc nào, vì sao

### 3.2 Bảng tổng quan Unit

| Unit | Tên | Est (h) |
|---|---|---|
| UOW-01 | Giới hạn vai được huỷ | 2.75 |
| UOW-02 | Bắt buộc lý do | 3.5 |

### 2.1 Bảng nguồn

| # | Nguồn | Ưu tiên | Trạng thái |
|---|---|---|---|
| S13 | nơi lưu dữ liệu thật | P0 | missing |

""" + PAD

VIEW = {
    "version": 2, "source": "intent-plan.md", "source_version": 1, "by": "dlc-modeler", "gaps": [],
    "headline": "Huỷ đơn có kiểm soát",
    "outcomes": [{"id": "O1", "text": "a", "now": "x", "target": "0", "from_request": True},
                 {"id": "O2", "text": "b", "now": "0%", "target": "100%", "from_request": True}],
    "units": [{"id": "UOW-01", "short": "Giới hạn vai", "serves": ["O1"], "condition": None},
              {"id": "UOW-02", "short": "Bắt buộc lý do", "serves": ["O2"], "condition": {"decision": "D1", "when": "chốt A"}}],
    "decisions": [{"id": "D1", "question": "Ai được huỷ đơn?", "who": "chị Lan", "risk": "vừa",
                   "options": [{"key": "A", "name": "Quản lý + trưởng ca", "cost": "0h", "reversal": "rẻ"},
                               {"key": "B", "name": "Cho khách tự huỷ", "cost": "?", "reversal": "đắt"}],
                   "recommended": "A", "default": "A", "blocks": ["UOW-02"]}],
    "risks": [{"text": "mất dữ liệu khi khởi động lại", "level": "cao", "owner": "chưa có"}],
}


class HumanViewCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = build(self.tmp.name)
        self.doc = os.path.join(self.p["intent"], "intent-plan.md")
        self.view = os.path.join(self.p["intent"], "views", "intent-plan.view.json")
        write(self.doc, DOC)
        os.remove(os.path.join(self.p["intent"], "unit-plan.md"))      # chỉ thử một tài liệu gate
        self.put(VIEW)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, model, stamp=True):
        m = copy.deepcopy(model)
        if stamp:
            m["source_sha256"] = hashlib.sha256(read(self.doc).encode("utf-8")).hexdigest()
        write(self.view, json.dumps(m, ensure_ascii=False, indent=1))

    def run_check(self):
        rc, out, err = run_py("human_view_check.py", self.p["root"], "--json")
        return rc, json.loads(out)["findings"]

    def expect(self, code, level="FIX"):
        rc, f = self.run_check()
        self.assertEqual(sorted({x["code"] for x in f}), [code], f)
        self.assertTrue(all(x["level"] == level for x in f), f)
        self.assertEqual(rc, 1 if level == "FIX" else 0)
        return f

    def mutate(self, fn):
        m = copy.deepcopy(VIEW)
        fn(m)
        self.put(m)

    def test_clean(self):
        self.assertEqual(self.run_check(), (0, []))

    def test_no_view_yet(self):
        os.remove(self.view)
        self.assertIn("toàn văn", self.expect("HV04", "WARN")[0]["msg"])

    def test_broken_json(self):
        write(self.view, '{"version": 2, "units": [')
        self.expect("HV01")

    def test_stale_view_after_doc_changed(self):
        write(self.doc, DOC.replace("| UOW-02 | Bắt buộc lý do | 3.5 |", "| UOW-02 | Bắt buộc lý do | 6.0 |"))
        self.assertIn("MÔ HÌNH CŨ", self.expect("HV08")[0]["msg"])

    def test_view_without_fingerprint_is_stale(self):
        self.put(VIEW, stamp=False)
        self.expect("HV08")

    def test_unit_not_in_text(self):
        self.mutate(lambda m: m["units"].append({"id": "UOW-09", "short": "bịa", "serves": ["O1"], "condition": None}))
        self.expect("HV02")

    def test_outcome_not_in_text(self):
        self.mutate(lambda m: m["outcomes"].append({"id": "O9", "text": "bịa", "now": "", "target": ""}))
        self.expect("HV02")

    def test_dangling_cross_references(self):
        for name, fn in (("serves", lambda m: m["units"][0].__setitem__("serves", ["O7"])),
                         ("condition", lambda m: (m["units"][1]["condition"].__setitem__("decision", "D9"),
                                                  m["decisions"][0].__setitem__("blocks", []))),
                         ("blocks", lambda m: m["decisions"][0].__setitem__("blocks", ["UOW-02", "UOW-08"]))):
            with self.subTest(ref=name):
                self.mutate(fn)
                self.expect("HV02")

    def test_view_hides_a_unit(self):
        self.mutate(lambda m: (m["units"].pop(), m["decisions"][0].__setitem__("blocks", [])))
        self.assertIn("UOW-02", self.expect("HV03")[0]["msg"])

    def test_decision_missing_fields(self):
        for name, fn in (("một phương án", lambda m: m["decisions"][0]["options"].pop()),
                         ("đề xuất lạ", lambda m: m["decisions"][0].__setitem__("recommended", "Z")),
                         ("mặc định lạ", lambda m: m["decisions"][0].__setitem__("default", "Z")),
                         ("không ai trả lời", lambda m: m["decisions"][0].__setitem__("who", "")),
                         ("reversal lạ", lambda m: m["decisions"][0]["options"][0].__setitem__("reversal", "vừa")),
                         ("risk lạ", lambda m: m["decisions"][0].__setitem__("risk", "khủng")),
                         ("không mặc định, không needs", lambda m: m["decisions"][0].__setitem__("default", None))):
            with self.subTest(case=name):
                self.mutate(fn)
                self.expect("HV05")

    def test_no_recommendation_is_allowed_only_when_said_so(self):
        self.mutate(lambda m: m["decisions"][0].__setitem__("recommended", None))
        self.expect("HV05")                                           # im lặng bỏ đề xuất: không được
        def honest(m):
            m["decisions"][0]["recommended"] = None
            m["gaps"] = [{"text": "bản chữ không đưa khuyến nghị giữa hai phương án", "decision": "D1"}]
        self.mutate(honest)
        self.expect("HV09", "WARN")                                   # nói ra: được, chỉ còn cảnh báo có gaps

    def test_long_gap_text_is_not_wordiness(self):
        self.mutate(lambda m: m.__setitem__("gaps", ["bản chữ thiếu " + "rất nhiều thứ " * 20]))
        self.expect("HV09", "WARN")

    def test_no_default_but_says_what_is_needed(self):
        self.mutate(lambda m: m["decisions"][0].update(default=None, needs="chị Lan xác nhận danh sách vai"))
        self.assertEqual(self.run_check(), (0, []))

    def test_default_is_the_costly_option(self):
        self.mutate(lambda m: m["decisions"][0].update(default="B", recommended="B"))
        self.assertIn("đảo đắt", self.expect("HV07")[0]["msg"])

    def test_costly_option_that_is_not_default_is_fine(self):
        self.assertEqual(self.run_check(), (0, []))          # ca sạch có phương án B đảo đắt, mặc định là A

    def test_condition_and_blocks_must_agree(self):
        self.mutate(lambda m: m["decisions"][0].__setitem__("blocks", []))            # unit chờ D1, D1 không ghi
        self.expect("HV10")
        self.mutate(lambda m: m["units"][1].__setitem__("condition", None))           # D1 giữ UOW-02, unit không biết
        self.expect("HV10")

    def test_unknown_reversal_on_high_risk_default(self):
        def fn(m):
            m["decisions"][0]["risk"] = "cao"
            m["decisions"][0]["options"][0]["reversal"] = "chưa rõ"
        self.mutate(fn)
        self.assertIn("chưa rõ", self.expect("HV07")[0]["msg"])
        self.mutate(lambda m: m["decisions"][0]["options"][0].__setitem__("reversal", "chưa rõ"))   # rủi ro vừa: được
        self.assertEqual(self.run_check(), (0, []))

    def test_short_cells_over_limit(self):
        self.mutate(lambda m: m["outcomes"][0].__setitem__("target", "0 lượt huỷ bởi người ngoài danh sách, đối chiếu sổ ghi huỷ với danh sách mỗi tuần"))
        self.assertIn("O1.target", self.expect("HV06", "WARN")[0]["msg"])

    def test_links_between_pieces_of_one_issue(self):
        def ok(m):
            m["gaps"] = [{"text": "không nói giá đảo của mặc định", "ref": "1.7", "decision": "D1"}]
            m["risks"][0]["decision"] = "D1"
        self.mutate(ok)
        self.expect("HV09", "WARN")                                  # nối đúng: chỉ còn cảnh báo có gaps
        for name, fn in (("risk", lambda m: m["risks"][0].__setitem__("decision", "D9")),
                         ("gap", lambda m: m.__setitem__("gaps", [{"text": "x" * 20, "decision": "D9"}])),
                         ("source", lambda m: m["decisions"][0].__setitem__("sources", ["S99"]))):
            with self.subTest(link=name):
                self.mutate(fn)
                rc, f = self.run_check()
                self.assertIn("HV02", {x["code"] for x in f if x["level"] == "FIX"}, f)

    def test_review_tier_and_touches(self):
        def ok(m):
            m["units"][0].update(review="specialist(security)", review_why="chạm phân quyền")
            m["units"][1].update(review="peer")
            m["decisions"][0]["touches"] = ["UOW-01", "UOW-02"]
        self.mutate(ok)
        self.assertEqual(self.run_check(), (0, []))
        self.mutate(lambda m: m["units"][0].__setitem__("review", "chuyên gia"))
        self.expect("HV05")
        self.mutate(lambda m: m["decisions"][0].__setitem__("touches", ["UOW-07"]))
        self.expect("HV02")

    def test_gaps_are_reported_not_failed(self):
        self.mutate(lambda m: m.__setitem__("gaps", ["mục 1.7 không ghi ai trả lời câu về nơi lưu dữ liệu"]))
        self.assertIn("nơi lưu", self.expect("HV09", "WARN")[0]["msg"])

    def test_model_as_wordy_as_the_text(self):
        self.mutate(lambda m: m.__setitem__("headline", "rất dài " * 40))
        self.expect("HV06", "WARN")
        def many(m):
            base = m["decisions"][0]
            m["decisions"] = [dict(base, id="D%d" % i, blocks=["UOW-02"] if i == 1 else []) for i in range(1, 10)]
            m["units"][1]["condition"]["decision"] = "D1"
        self.mutate(many)
        self.expect("HV06", "WARN")

    # ---- escalation -------------------------------------------------------------------------
    def put_esc(self, status="open", decisions=1, stamp=True):
        esc = os.path.join(self.p["cm"], "escalations", "ESC-001.md")
        write(esc, "---\nid: ESC-001\nseverity: high\nowner:\nstatus: %s\n---\n# ESC-001 · đăng nhập yếu\n%s" % (status, PAD))
        d = copy.deepcopy(VIEW["decisions"][0]); d["blocks"] = []
        m = {"version": 3, "source": "ESC-001.md", "by": "dlc-modeler", "gaps": [], "headline": "đăng nhập yếu",
             "decisions": [dict(d, id="D%d" % i) for i in range(1, decisions + 1)]}
        if stamp:
            m["source_sha256"] = hashlib.sha256(read(esc).encode("utf-8")).hexdigest()
        write(os.path.join(self.p["cm"], "escalations", "views", "ESC-001.view.json"), json.dumps(m, ensure_ascii=False))
        return esc

    def test_escalation_view_clean(self):
        self.put_esc()
        self.assertEqual(self.run_check(), (0, []))

    def test_open_escalation_without_view(self):
        esc = self.put_esc()
        os.remove(os.path.join(self.p["cm"], "escalations", "views", "ESC-001.view.json"))
        f = self.expect("HV04", "WARN")
        self.assertIn("ESC-001", f[0]["where"])

    def test_escalation_must_have_exactly_one_decision(self):
        self.put_esc(decisions=2)
        self.expect("HV11")

    def test_escalation_view_goes_stale_too(self):
        esc = self.put_esc()
        write(esc, read(esc) + "\nthêm một dòng sau khi vẽ\n")
        self.expect("HV08")

    def test_closed_escalation_is_ignored(self):
        for status in ("claimed", "done", "wontfix"):
            with self.subTest(status=status):
                self.put_esc(status=status, decisions=2, stamp=False)
                self.assertEqual(self.run_check(), (0, []))

    def test_not_an_ai_dlc_project(self):
        with tempfile.TemporaryDirectory() as t:
            rc, out, err = run_py("human_view_check.py", t, "--json")
            self.assertEqual((rc, json.loads(out)["findings"]), (0, []))


if __name__ == "__main__":
    unittest.main()
