"""tower_generate.py — data.js nạp được, SVG có mặt, chữ từ markdown được escape, dự án lead không đổi."""
import copy
import hashlib
import json
import os
import re
import tempfile
import unittest

from helpers import PAD, build, dec, read, run_py, write

PAYLOAD = '<script>alert(1)</script><img src=x onerror=alert(2)></text><foreignObject>'


def generate(root):
    rc, out, err = run_py("tower_generate.py", root)
    assert rc == 0, err
    js = read(os.path.join(root, ".ai-dlc", "tower", "data.js"))
    return json.loads(js[js.index("window.CT_DATA = ") + len("window.CT_DATA = "):].rstrip().rstrip(";"))


def svgs(node, path="", out=None):
    out = [] if out is None else out
    if isinstance(node, str):
        if re.search(r"<svg[\s>]", node):
            out.append((path, node))
    elif isinstance(node, dict):
        for k, v in node.items():
            svgs(v, path + "." + k, out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            svgs(v, "%s[%d]" % (path, i), out)
    return out


class TowerGenerate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_autopilot_project(self):
        build(self.root, gates_auto=("A", "B", "C"), gate_open="D", blocked_by="#1 · OQB-01 cần chị Lan chọn")
        d = generate(self.root)
        self.assertEqual(d["autopilot"]["mode"], "autopilot")
        self.assertEqual(len(d["autopilot"]["decisions"]), 3)
        figs = svgs(d)
        self.assertGreaterEqual(len(figs), 3, "thiếu hình: flow intent + cây câu hỏi + thẻ tự quyết")
        for path, s in figs:
            self.assertEqual(s.count("<svg"), s.count("</svg>"), path)
        flow = "".join(s for _, s in figs)
        self.assertIn("OQB-01 cần chị Lan chọn", flow, "lý do block phải hiện trong hình")

    def test_markdown_text_is_escaped_in_svg(self):
        p = build(self.root, gates_auto=("A", "B", "C"), gate_open="D", blocked_by="#1 · X")
        q = os.path.join(p["intent"], "open-questions-business.md")
        write(q, read(q).replace("### OQB-01 · Ai được huỷ đơn?", "### OQB-01 · " + PAYLOAD + " Ai được huỷ đơn?")
                        .replace("**A.** Chỉ quản lý kho", "**A.** " + PAYLOAD))
        log = os.path.join(p["gov"], "decisions-log.md")
        write(log, read(log).replace("- Chọn: phương án A", "- Chọn: " + PAYLOAD, 1)
                            .replace("- Đảo bằng: viết lại", "- Đảo bằng: " + PAYLOAD + " viết lại", 1))
        st = os.path.join(p["intent"], "status.md")
        write(st, read(st).replace('blocked_by: "#1 · X"', 'blocked_by: "#1 · ' + PAYLOAD.replace('"', "") + '"'))
        all_svg = "".join(s for _, s in svgs(generate(self.root)))
        self.assertIn("&lt;script&gt;", all_svg, "payload phải CÓ MẶT ở dạng escape — nếu không, test không thử gì")
        for raw in ("<script", "<img", "<foreignObject", "onerror=alert(2)>"):
            self.assertNotIn(raw, all_svg)

    def test_lead_project_has_no_autopilot_cards(self):
        for mode in ("lead", None):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as t:
                    build(t, mode=mode, gates_auto=("A", "B", "C"), gate_open="D")
                    d = generate(os.path.realpath(t))
                    self.assertEqual(d["autopilot"]["mode"], "lead")
                    self.assertEqual(d["autopilot"]["decisions"], [])

    def test_does_not_litter_outside_state(self):
        build(self.root)
        generate(self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, "src", ".ai-dlc")))
        self.assertEqual(sorted(os.listdir(self.root)), [".ai-dlc", "src"])


# ---------- trang mô hình (protocol §2.4): views/<tài liệu>.view.json → sáu hình ----------
HV_DOC = """---
type: intent-plan
id: INT-001
gate: A
version: 1
---
# INT-001 · Kế hoạch Intent

### 1.2 Outcome
- [ ] **O1** — người ngoài danh sách không huỷ được
- [ ] **O2** — mỗi lượt huỷ biết ai, lúc nào, vì sao

### 2.1 Bảng nguồn

| # | Nguồn | Thông tin cụ thể phải lấy ra | Ai sở hữu | Ưu tiên | Rủi ro nếu bỏ qua | Trạng thái |
|---|---|---|---|---|---|---|
| S1 | docs/orders.md | luồng đơn | không ghi | P0 | hiểu sai luật | planned |
| S2 | Nơi lưu dữ liệu đơn thật | lưu ở đâu | người phụ trách kỹ thuật | P0 | O2 không đạt trong thực tế | missing |
| S3 | Anh Tuấn — trưởng ca | số cuộc gọi tối | anh Tuấn | P1 | chọn sai phạm vi ca | missing |

### 3.2 Bảng tổng quan Unit

| Unit | Tên | Est (h) |
|---|---|---|
| UOW-01 | Giới hạn vai được huỷ | 2.75 |
| UOW-02 | Bắt buộc lý do | 3.5 |

""" + PAD

HV_VIEW = {
    "version": 2, "source": "intent-plan.md", "source_version": 1, "by": "dlc-modeler", "gaps": ["1.7 không nói giá đảo"],
    "headline": "Huỷ đơn có kiểm soát",
    "pain": {"text": "Ai đăng nhập cũng huỷ được đơn.", "numbers": ["3 đơn huỷ nhầm / tháng"], "ref": "1.1"},
    "outcomes": [{"id": "O1", "text": "Người ngoài danh sách không huỷ được", "now": "ai cũng huỷ", "target": "0 lượt", "from_request": True},
                 {"id": "O2", "text": "Biết ai huỷ", "now": "0%", "target": "100%", "from_request": False}],
    "scope": {"now": ["Giới hạn vai"], "later": [{"what": "Nơi lưu bền", "cost": "GIÁ CAO NHẤT: mất khi khởi động lại"}],
              "never": ["Đổi cách đăng nhập"], "ref": "1.3"},
    "units": [{"id": "UOW-01", "short": "Giới hạn vai", "serves": ["O1"], "condition": None},
              {"id": "UOW-02", "short": "Bắt buộc lý do", "serves": ["O2"], "condition": {"decision": "D2", "when": "chốt A"}}],
    "decisions": [{"id": "D1", "kind": "CONFLICT", "question": "Ai được huỷ đơn?", "who": "chị Lan", "risk": "thấp",
                   "options": [{"key": "A", "name": "Quản lý + trưởng ca", "effect": "nhân viên phải nhờ", "cost": "0h", "reversal": "rẻ"},
                               {"key": "B", "name": "Chỉ quản lý kho", "effect": "tối không ai huỷ", "cost": "0h", "reversal": "rẻ"}],
                   "recommended": "A", "default": "A", "reverse_by": "đổi danh sách vai", "blocks": []},
                  {"id": "D2", "kind": "OPEN", "question": "Dữ liệu lưu ở đâu?", "who": "người phụ trách kỹ thuật", "risk": "cao",
                   "options": [{"key": "A", "name": "Cùng chỗ hiện tại", "effect": "mất khi khởi động lại", "cost": "0h", "reversal": "rẻ"},
                               {"key": "B", "name": "Dựng nơi lưu bền", "effect": "chạm dữ liệu", "cost": "một đợt riêng", "reversal": "đắt"}],
                   "recommended": "A", "default": "A", "reverse_by": "chuyển dữ liệu", "blocks": ["UOW-02"]}],
    "decisions_minor": ["D4 đơn cũ không bổ sung lý do (1.7 mục 4)"],
    "risks": [{"text": "Mất dữ liệu khi khởi động lại", "level": "cao", "owner": "chưa có"}],
}
SIX = ["goal", "scope", "roadmap", "sources", "decisions", "risks"]


class HumanView(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.p = build(self.root, gates_auto=("A",))
        self.doc = os.path.join(self.p["intent"], "intent-plan.md")
        self.view = os.path.join(self.p["intent"], "views", "intent-plan.view.json")
        write(self.doc, HV_DOC)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, view, stamp=True):
        v = copy.deepcopy(view)
        if stamp:
            v["source_sha256"] = hashlib.sha256(read(self.doc).encode("utf-8")).hexdigest()
        write(self.view, json.dumps(v, ensure_ascii=False, indent=1))

    def model(self, d=None):
        d = d or generate(self.root)
        hv = d["humanView"]["INT-001"]
        return hv["docs"][hv["primary"]], hv, d

    def test_view_draws_six_figures(self):
        self.put(HV_VIEW)
        m, hv, d = self.model()
        self.assertEqual([f["key"] for f in m["figures"]], SIX)
        for f in m["figures"]:
            if f["key"] != "decisions":
                self.assertRegex(f["svg"], r"^<svg[\s>]", f["key"])
                self.assertEqual(f["svg"].count("<svg"), f["svg"].count("</svg>"), f["key"])
        self.assertEqual((m["stale"], m["error"], m["gate"]), (False, "", "A"))
        self.assertFalse(hv["stale"])
        self.assertEqual(hv["warnings"], [], "ca sạch không được có cảnh báo — nếu có, các ca đột biến không thử gì")
        # giờ và thứ tự lấy từ BẢNG UNIT của bản chữ, không từ view
        self.assertIn("2 phần việc · 6,25 giờ", m["summary"])
        self.assertIn("3 nguồn (2 không đọc được)", m["summary"])
        self.assertIn("3 điểm cần chốt: 0 cần bạn · 3 AI tự lo", m["summary"])
        road = next(f for f in m["figures"] if f["key"] == "roadmap")
        self.assertIn("tổng 6,25h", road["svg"])
        self.assertIn("còn 1 phần việc · 2,75 giờ", road["note"])
        # rủi ro cao mà ĐÃ CÓ mặc định ⇒ vẫn "AI tự lo", nhưng đứng đầu nhóm (quyết định chủ gói 2026-09-28)
        self.assertEqual([(x["id"], x["group"], x["risk"]) for x in m["decisions"]],
                         [("D2", "auto", "cao"), ("D1", "auto", "thấp")])
        self.assertEqual(m["decisions"][1]["line"], "A. Quản lý + trưởng ca · 0h · đảo rẻ")
        # nhãn điều kiện bằng lời, mã quyết định trong ngoặc — không lộ số mục của bản chữ
        self.assertIn("chỉ làm nếu chốt: A (D2)", road["svg"])
        for x in m["decisions"]:
            self.assertIn('data-nav="pick:A"', x["svg"])
            self.assertIn('data-nav="pick:B"', x["svg"])
        self.assertIn("đảo đắt", m["decisions"][0]["svg"])
        self.assertEqual(m["gaps"], [{"text": "1.7 không nói giá đảo", "ref": "", "decision": ""}], "gaps dạng chuỗi (v2) vẫn đọc được")
        src = next(f for f in m["figures"] if f["key"] == "sources")["svg"]
        self.assertNotIn("chưa ai hỏi", src, "view schema 2 không khai được nguồn nào được thay — không kết luận thay nó")
        self.assertIsNone(m["stats"]["p0Unasked"])
        # dòng "nếu bạn không làm gì": tự tính từ default
        self.assertEqual(m["idle"], {"defaults": [{"id": "D2", "key": "A"}, {"id": "D1", "key": "A"}],
                                     "standing": [], "applied": [], "confirm": [], "minor": 1})
        self.assertTrue(all("resolved" not in x for x in m["decisions"]), "không có gì để khớp thì không phủ")
        # thẻ AI đã tự quyết của Gate A biết có mô hình để mở
        self.assertEqual([x.get("modelDoc") for x in d["autopilot"]["decisions"]], [m["doc"]])
        self.assertEqual(m["dec"], "DEC-0001")

    def test_broken_json_does_not_crash_and_warns(self):
        write(self.view, '{"version": 2, "headline": "thiếu ngoặc"')
        m, hv, d = self.model()
        self.assertIn("human-view không đọc được", m["error"])
        self.assertEqual(m["figures"], [])
        self.assertTrue(any("human-view không đọc được" in w for w in hv["warnings"]))
        self.assertTrue(d["intents"], "phần còn lại của tower vẫn phải sinh ra")
        self.assertNotIn("modelDoc", d["autopilot"]["decisions"][0], "mô hình hỏng thì không mời người mở")
        write(self.view, "[1, 2]")
        self.assertIn("object JSON", self.model()[0]["error"])

    def test_mismatched_codes_are_flagged_not_hidden(self):
        v = copy.deepcopy(HV_VIEW)
        v["units"].append({"id": "UOW-09", "short": "Phần việc ma", "serves": ["O9"],
                           "condition": {"decision": "D9", "when": "x"}})
        v["decisions"][0]["blocks"] = ["UOW-77"]
        v["decisions"][0]["recommended"] = "Z"
        self.put(v)
        m, hv, _ = self.model()
        joined = " | ".join(hv["warnings"])
        for needle in ("UOW-09 có trong human-view.units nhưng không có trong bảng phần việc",
                       "UOW-09.serves trỏ O9", "UOW-09.condition trỏ D9", "D1.blocks trỏ UOW-77",
                       "D1.recommended = Z"):
            self.assertIn(needle, joined)
        self.assertEqual([f["key"] for f in m["figures"]], SIX, "mã lệch vẫn phải vẽ đủ hình")
        road = next(f for f in m["figures"] if f["key"] == "roadmap")["svg"]
        for mark in ("UOW-09?", "O9?", "D9?"):
            self.assertIn(mark, road)
        self.assertIn("UOW-77?", next(x for x in m["decisions"] if x["id"] == "D1")["svg"])

    def test_view_text_is_escaped_in_svg(self):
        v = copy.deepcopy(HV_VIEW)
        v["pain"]["text"] = PAYLOAD
        v["pain"]["numbers"] = [PAYLOAD]
        v["outcomes"][0].update(text=PAYLOAD, now=PAYLOAD, target=PAYLOAD)
        v["scope"]["now"] = [PAYLOAD]
        v["scope"]["later"][0].update(what=PAYLOAD, cost=PAYLOAD)
        v["units"][0]["short"] = PAYLOAD
        v["units"][1]["condition"]["when"] = PAYLOAD
        v["decisions"][0].update(question=PAYLOAD, who=PAYLOAD, reverse_by=PAYLOAD)
        v["decisions"][0]["options"][0].update(name=PAYLOAD, effect=PAYLOAD, cost=PAYLOAD)
        v["risks"][0].update(text=PAYLOAD, owner=PAYLOAD)
        self.put(v)
        m, _, d = self.model()
        all_svg = "".join(s for _, s in svgs(d["humanView"]))
        self.assertGreaterEqual(all_svg.count("&lt;script&gt;"), 8, "payload phải CÓ MẶT ở dạng escape trong nhiều hình")
        for raw in ("<script", "<img", "<foreignObject", "onerror=alert(2)>"):
            self.assertNotIn(raw, all_svg)

    def test_order_puts_undecided_first(self):
        v = copy.deepcopy(HV_VIEW)
        v["units"][1]["condition"]["when"] = '1.7 mục 2 chốt "có chặn"'
        v["decisions"].append({"id": "D3", "kind": "OPEN", "question": "Khách có được xem?", "who": "chị Lan",
                               "risk": "thấp", "default": None, "needs": "chưa ai nói khách cần xem gì",
                               "recommended": "A",
                               "options": [{"key": "A", "name": "Không", "cost": "0h"},
                                           {"key": "B", "name": "Có", "cost": "?", "reversal": "đắt"}]})
        self.put(v)
        m, hv, _ = self.model()
        self.assertEqual([(x["id"], x["group"]) for x in m["decisions"]],
                         [("D3", "need"), ("D2", "auto"), ("D1", "auto")], "cần bạn CHỈ khi chưa có mặc định")
        self.assertIn("1 cần bạn · 3 AI tự lo", m["summary"])
        self.assertIn("Chưa có mặc định", m["decisions"][0]["svg"])
        self.assertIn("chưa ai nói khách cần xem gì", m["decisions"][0]["svg"])
        self.assertEqual(hv["warnings"], [])
        road = next(f for f in m["figures"] if f["key"] == "roadmap")["svg"]
        self.assertIn("chỉ làm nếu chốt: có chặn (D2)", road)
        self.assertNotIn("1.7 mục 2", road.split("<title>")[0] + "".join(
            re.findall(r"<text[^>]*>([^<]*)</text>", road)), "số mục của bản chữ không nằm trong chữ trên hình")

    def test_gaps_alone_still_open_the_decision_figure(self):
        self.put({"version": 2, "headline": "x", "gaps": ["bản chữ không nói ai chốt"]})
        m, hv, _ = self.model()
        self.assertEqual([f["key"] for f in m["figures"]], ["sources", "decisions"])
        self.assertEqual(([g["text"] for g in m["gaps"]], hv["gaps"]), (["bản chữ không nói ai chốt"], 1))

    def v3(self):
        v = copy.deepcopy(HV_VIEW)
        v["version"] = 3
        v["gaps"] = [{"text": "không nói giá đảo của A", "ref": "1.7 mục 7", "decision": "D2"},
                     {"text": "không nói ai trả lời khách", "ref": "1.7 mục 5", "decision": None}]
        v["scope"]["later"][0]["decision"] = "D2"
        v["decisions"][1]["sources"] = ["S2"]
        v["risks"][0].update(decision="D2", ref="ESC-001")
        v["approach"] = {"axis": "Cắt theo năng lực người dùng thấy được", "why": "mỗi phần tự ra được sản phẩm",
                         "rejected": [{"what": "Cắt theo vai", "why": "ba phần cùng sửa một chỗ"}], "ref": "3.1 · 3.4"}
        return v

    def test_v3_links_one_story_across_figures(self):
        write(self.doc, HV_DOC.replace("| Unit | Tên | Est (h) |\n|---|---|---|", "| Unit | Tên | Est (h) | Phụ thuộc |\n|---|---|---|---|")
                              .replace("| UOW-01 | Giới hạn vai được huỷ | 2.75 |", "| UOW-01 | Giới hạn vai được huỷ | 2.75 | — |")
                              .replace("| UOW-02 | Bắt buộc lý do | 3.5 |", "| UOW-02 | Bắt buộc lý do | 3.5 | UOW-01 |"))
        write(os.path.join(self.p["cm"], "escalations", "ESC-001.md"), "---\nid: ESC-001\nstatus: open\n---\n# ESC-001 · x\n")
        self.put(self.v3())
        m, hv, _ = self.model()
        self.assertEqual(hv["warnings"], [])
        fig = {f["key"]: f["svg"] for f in m["figures"]}
        self.assertEqual(list(fig), ["goal", "scope", "approach", "roadmap", "sources", "decisions", "risks"])
        for key in ("scope", "sources", "risks"):
            self.assertIn('data-nav="goto:D2"', fig[key], "hình %s phải có chip → D2" % key)
        self.assertIn("được thay bằng:", fig["sources"])
        self.assertNotIn("chưa ai hỏi", fig["sources"])
        self.assertIn("Cắt theo năng lực", fig["approach"])
        self.assertIn("Cắt theo vai", fig["approach"])
        self.assertIn("↳ sau UOW-01", fig["roadmap"])
        self.assertIn('data-nav="esc:ESC-001"', fig["risks"], "rủi ro chưa có chủ + có ESC còn mở ⇒ có nút nhận/giao")
        d2 = next(x for x in m["decisions"] if x["id"] == "D2")
        self.assertEqual(d2["also"], [{"fig": "scope", "label": "Phạm vi"}, {"fig": "sources", "label": "Nguồn S2"},
                                      {"fig": "risks", "label": "Rủi ro"}])
        self.assertEqual([g["text"] for g in d2["gaps"]], ["không nói giá đảo của A"])
        self.assertEqual(next(x for x in m["decisions"] if x["id"] == "D1")["also"], [])

    def test_v3_unasked_source_and_bad_links_are_loud(self):
        v = self.v3()
        v["decisions"][1]["sources"] = ["S99"]          # S2 (P0, không đọc được) không còn điểm nào thay
        v["risks"][0].update(decision="D9", ref="ESC-404")
        v["scope"]["later"][0]["decision"] = "D8"
        v["gaps"][0]["decision"] = "D7"
        self.put(v)
        m, hv, _ = self.model()
        fig = {f["key"]: f["svg"] for f in m["figures"]}
        self.assertIn("chưa ai hỏi", fig["sources"])
        self.assertNotIn('data-nav="esc:', fig["risks"], "ESC không tồn tại thì không có nút — chỉ tô đỏ")
        self.assertIn("D9?", fig["risks"])
        self.assertIn("D8?", fig["scope"])
        joined = " | ".join(hv["warnings"])
        for needle in ("D2.sources trỏ S99", "trỏ D9", "trỏ D8", "gaps trỏ D7"):
            self.assertIn(needle, joined)
        self.assertEqual(m["stats"]["p0Unasked"], 1)

    # ---- phủ trạng thái của gate sau lên cây của gate trước (phát hiện #25) ----
    OQ_LATER = """---
intent: INT-001
doc: open-questions-business
gate: C
version: 1
---
# Câu hỏi

## 0. Bảng điều phối — ai phải trả lời gì

| Mã | Câu hỏi | Ai trả lời | Hạn | Nếu im lặng | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|---|---|
| OQB-06 | Ghi chép huỷ có thể mất — chấp nhận không? | chị Lan | 30/09 | A — chấp nhận, ghi rõ giới hạn | làm lại nếu đổi muộn | open |
| OQB-03 | Những ai được huỷ đơn? | chị Lan | 30/09 | B — quản lý kho và trưởng ca | làm lại nếu đổi muộn | %s |

## Nhóm B4

### OQB-06 · Ghi chép huỷ có thể mất — chấp nhận không?

**Chọn một:**

| | Phương án | Nghĩa là gì với người dùng | Cái giá |
|---|---|---|---|
| ☐ | **A.** Chấp nhận trong đợt này | giới hạn ghi rõ | 0 giờ · Đảo: rẻ tới trước phát hành |
| ☐ | **B.** Không chấp nhận | hai phần việc dừng chờ | trên 14 giờ · Đảo: đắt |

- **AI đề xuất**: A — làm luật trước.
- **Nếu không trả lời trước hạn**: đi theo phương án A, ghi `[ASSUMED]`.
- **Trạng thái**: open

## Đối chiếu gộp câu — câu cũ đi đâu

| Nguồn | Về đâu | Ghi chú |
|---|---|---|
| 1.7 mục 7 · Q6 | OQB-06 ↔ OQT-01 | |
| 1.7 mục 1 · Q1 | OQB-03 | |
| 1.7 mục 5 · Q8 | không hỏi | đã để sang đợt sau |
"""

    def later_gate(self, status="open", gates=("A", "C"), view=None, apply="- Áp: OQB-06 = A · OQB-03 = B"):
        v = copy.deepcopy(view or HV_VIEW)
        v["decisions"][0].update(ref="1.7 mục 1")                                  # D1 — có mặc định A
        v["decisions"][1].update(ref="1.7 mục 7", default=None, needs="ai xác nhận nơi lưu")   # D2 — đội đang đứng
        write(os.path.join(self.p["intent"], "open-questions-business.md"), self.OQ_LATER % status)
        # DEC của Gate C khai bằng dòng `Áp` (mẫu DEC 6.5.1) nó đã áp phương án nào cho mã nào
        log = "# Decisions log\n\n" + "".join(
            dec(i, g, shown={"A": "intent-plan.md#3", "C": "open-questions-business.md#0"}[g]).replace(
                "- Áp: không có", apply if g == "C" else "- Áp: không có")
            for i, g in enumerate(gates, 1))
        write(os.path.join(self.p["gov"], "decisions-log.md"), log)
        self.put(v)
        return self.model()

    def test_later_gate_default_is_overlaid(self):
        m, hv, _ = self.later_gate()
        d2 = next(x for x in m["decisions"] if x["id"] == "D2")
        r = d2["resolved"]
        self.assertEqual((r["dec"], r["gate"], r["oq"], r["option"], r["until"]),
                         ("DEC-0002", "C", "OQB-06", "A — Chấp nhận trong đợt này", "trước phát hành"))
        self.assertEqual(r["parts"][0]["via"], "dòng Áp")
        self.assertEqual(r["parts"][0]["also"], [], "OQT-01 không có trong bảng điều phối thì không kể")
        self.assertEqual(d2["group"], "confirm", "gate sau đã áp ⇒ rời nhóm cần bạn; có hạn đảo ⇒ xác nhận trước mốc")
        self.assertFalse(d2["confirmed"])
        self.assertNotIn("Chưa có mặc định", d2["svg"])
        self.assertEqual(d2["line"], "đã áp ở Gate C: A — Chấp nhận trong đợt này · đảo rẻ tới: trước phát hành")
        self.assertEqual(m["idle"]["standing"], [])
        self.assertEqual(m["idle"]["applied"], [{"id": "D2", "gate": "C", "dec": "DEC-0002"}])
        self.assertEqual(m["idle"]["confirm"], [{"id": "D2", "until": "trước phát hành"}])
        self.assertIn("3 điểm cần chốt: 0 cần bạn · 1 xác nhận trước phát hành · 2 AI tự lo", m["summary"])
        self.assertEqual([x["id"] for x in m["decisions"]], ["D2", "D1"], "nhóm xác nhận đứng trước nhóm AI tự lo")
        self.assertEqual(hv["warnings"], [])
        # điểm đã có mặc định trong view cũng được phủ: người xem thấy gate sau áp gì
        d1 = next(x for x in m["decisions"] if x["id"] == "D1")
        self.assertEqual(d1["resolved"]["option"], "B — quản lý kho và trưởng ca")

    def test_overlay_points_at_the_dec_that_decided_not_the_latest(self):
        # Gate D (duyệt unit-plan) đến SAU Gate C nhưng không phải nơi quyết câu hỏi — đảo phải nhắm DEC của Gate C
        m, _, _ = self.later_gate()
        log = os.path.join(self.p["gov"], "decisions-log.md")
        write(log, read(log) + dec(3, "D", shown="unit-plan.md#2"))
        m, _, _ = self.model()
        r = next(x for x in m["decisions"] if x["id"] == "D2")["resolved"]
        self.assertEqual((r["dec"], r["gate"]), ("DEC-0002", "C"))
        # ---- đường lùi: DEC viết TRƯỚC 6.5.1, không có dòng Áp ----
        old = lambda *a, **k: dec(*a, **k).replace("- Áp: không có\n", "")      # noqa: E731
        write(log, "# Decisions log\n\n" + old(1, "A") + old(2, "C", shown="open-questions-business.md#0")
              + old(3, "D", shown="unit-plan.md#2"))
        m, _, _ = self.model()
        r = next(x for x in m["decisions"] if x["id"] == "D2")["resolved"]
        self.assertEqual((r["dec"], r["gate"], r["parts"][0]["via"]), ("DEC-0002", "C", "Căn cứ · Hiện ở"))
        # không DEC nào nêu đích danh file câu hỏi ⇒ lấy gate ĐẦU TIÊN đi qua câu hỏi, không lấy gate mới nhất
        write(log, "# Decisions log\n\n" + old(1, "A") + old(2, "C", shown="as-is/source-ledger.md#0")
              + old(3, "D", shown="unit-plan.md#2"))
        m, _, _ = self.model()
        r = next(x for x in m["decisions"] if x["id"] == "D2")["resolved"]
        self.assertEqual((r["dec"], r["gate"]), ("DEC-0002", "C"))

    def test_apply_line_is_authoritative(self):
        # DEC có dòng Áp mà KHÔNG liệt kê mã ⇒ nó không áp mã đó, dù Căn cứ có trỏ file câu hỏi
        m, _, _ = self.later_gate(apply="- Áp: OQB-03 = B")
        self.assertNotIn("resolved", next(x for x in m["decisions"] if x["id"] == "D2"))
        # Gate D áp LẠI mã đó bằng phương án khác và ghi `thay` ⇒ phủ theo DEC của Gate D, nêu rõ nó thay DEC nào
        m, _, _ = self.later_gate()
        log = os.path.join(self.p["gov"], "decisions-log.md")
        write(log, read(log) + dec(3, "D", shown="unit-plan.md#2").replace("- Áp: không có", "- Áp: OQB-06 = B (thay DEC-0002)"))
        m, hv, d = self.model()
        r = next(x for x in m["decisions"] if x["id"] == "D2")["resolved"]
        self.assertEqual((r["dec"], r["gate"], r["option"], r["until"], r["parts"][0]["replaces"]),
                         ("DEC-0003", "D", "B — Không chấp nhận", "", ["DEC-0002"]))
        self.assertEqual(d["autopilot"]["warnings"], [], "đã ghi `thay` thì hai DEC không còn mâu thuẫn")
        # thẻ AI đã tự quyết của DEC-0002: OQB-06 đã bị DEC-0003 thay, OQB-03 vẫn còn của nó
        codes = {x["code"]: x["replacedBy"] for x in next(a for a in d["autopilot"]["decisions"] if a["id"] == "DEC-0002")["appliedCodes"]}
        self.assertEqual(codes, {"OQB-06": "DEC-0003", "OQB-03": ""})

    def test_apply_line_on_the_views_own_decision_id(self):
        v = copy.deepcopy(HV_VIEW)
        self.put(v)
        log = os.path.join(self.p["gov"], "decisions-log.md")
        ap = lambda n, g, line, **k: dec(n, g, **k).replace("- Áp: không có", "- Áp: " + line)      # noqa: E731
        # DEC của chính gate này áp đúng mặc định hình đang vẽ ⇒ không có gì mới, không phủ
        write(log, "# Decisions log\n\n" + ap(1, "A", "D1 = A · D2 = A"))
        m, _, d = self.model()
        self.assertTrue(all("resolved" not in x for x in m["decisions"]))
        self.assertEqual(d["autopilot"]["applied"]["INT-001"]["D1"], {"option": "A", "dec": "DEC-0001", "gate": "A", "replaces": []})
        # sau một lần đảo, DEC mới áp D1 = B và ghi `thay` ⇒ hình (chưa vẽ lại) phải nói ra điều đó
        write(log, read(log) + ap(2, "A", "D1 = B (thay DEC-0001)"))
        m, _, d = self.model()
        r = next(x for x in m["decisions"] if x["id"] == "D1")["resolved"]
        self.assertEqual((r["dec"], r["option"], r["parts"][0]["direct"], r["parts"][0]["replaces"]),
                         ("DEC-0002", "B — Chỉ quản lý kho", True, ["DEC-0001"]))
        self.assertNotIn("resolved", next(x for x in m["decisions"] if x["id"] == "D2"))
        self.assertEqual(d["autopilot"]["applied"]["INT-001"]["D1"]["replaces"], ["DEC-0001"])

    def test_human_confirmation_clears_the_deadline_group(self):
        self.later_gate()
        log = os.path.join(self.p["gov"], "decisions-log.md")
        # (1) DEC do NGƯỜI ghi, nêu đích danh mã câu hỏi ⇒ đã xác nhận
        write(log, read(log) + "## DEC-0009 · 2026-09-29 · thay đổi · INT-001\n"
              "- Quyết định: chấp nhận OQB-06 theo mặc định   - Người quyết: HUMAN\n- Căn cứ: MSG-0009   - Ảnh hưởng: không\n\n")
        m, _, _ = self.model()
        d2 = next(x for x in m["decisions"] if x["id"] == "D2")
        self.assertEqual((d2["group"], d2["confirmed"], d2["resolved"]["confirmedBy"]), ("auto", True, "DEC-0009"))
        self.assertEqual(m["idle"]["confirm"], [])
        self.assertNotIn("xác nhận", m["summary"])
        # (2) DEC autopilot nêu mã thì KHÔNG tính là người xác nhận
        self.later_gate()
        write(log, read(log) + dec(9, "D", shown="unit-plan.md#2").replace("- Quyết định: duyệt", "- Quyết định: giữ OQB-06"))
        m, _, _ = self.model()
        self.assertEqual(next(x for x in m["decisions"] if x["id"] == "D2")["group"], "confirm")

    def test_default_with_deadline_in_the_view_needs_confirmation_too(self):
        v = copy.deepcopy(HV_VIEW)
        v["decisions"][0]["options"][0]["reversal_until"] = "trước phát hành"       # D1, mặc định A, rủi ro thấp
        self.put(v)
        m, _, _ = self.model()
        self.assertEqual([(x["id"], x["group"]) for x in m["decisions"]], [("D1", "confirm"), ("D2", "auto")])
        self.assertIn("0 cần bạn · 1 xác nhận trước phát hành · 2 AI tự lo", m["summary"])

    def test_no_match_means_no_overlay_no_guess(self):
        # (1) không có DEC nào áp lên file câu hỏi: câu còn mở ⇒ vẫn là chuyện đang treo
        m, _, _ = self.later_gate(gates=("A",))
        d2 = next(x for x in m["decisions"] if x["id"] == "D2")
        self.assertNotIn("resolved", d2)
        self.assertEqual((d2["group"], [x["id"] for x in m["idle"]["standing"]]), ("need", ["D2"]))
        self.assertIn("Chưa có mặc định", d2["svg"])
        # (2) mục không có trong bảng đối chiếu, hoặc bảng ghi "không hỏi": không khớp, không đoán theo lời câu hỏi
        v = copy.deepcopy(HV_VIEW)
        v["decisions"].append({"id": "D5", "ref": "1.7 mục 5", "question": "Ghi chép huỷ có thể mất — chấp nhận không?",
                               "who": "chị Lan", "default": None, "needs": "x", "recommended": "A",
                               "options": [{"key": "A", "name": "a"}, {"key": "B", "name": "b"}]})
        v["decisions"].append({"id": "D9", "ref": "1.7 mục 70", "question": "Khác?", "who": "chị Lan",
                               "default": None, "needs": "y", "recommended": "A",
                               "options": [{"key": "A", "name": "a"}, {"key": "B", "name": "b"}]})
        m, _, _ = self.later_gate(view=v)
        for did in ("D5", "D9"):
            self.assertNotIn("resolved", next(x for x in m["decisions"] if x["id"] == did), did)
        self.assertEqual(sorted(x["id"] for x in m["idle"]["standing"]), ["D5", "D9"])

    def test_reversed_dec_no_longer_overlays(self):
        self.later_gate()
        write(os.path.join(self.p["inbox"], "steer-1.json"),
              json.dumps({"type": "steer", "dec": "DEC-0002", "intent": "INT-001", "note": "đổi", "previewed": True}))
        m, _, _ = self.model()
        self.assertNotIn("resolved", next(x for x in m["decisions"] if x["id"] == "D2"),
                         "DEC đã bị người đảo thì mặc định của nó không còn là trạng thái mới nhất")

    def test_answered_question_overlays_as_closed(self):
        m, _, _ = self.later_gate(status="đã chốt", gates=("A",))
        r = next(x for x in m["decisions"] if x["id"] == "D1")["resolved"]
        self.assertEqual((r["closed"], r["dec"], r["oq"]), (True, "", "OQB-03"))

    def test_review_tier_is_visible_on_the_roadmap(self):
        v = copy.deepcopy(HV_VIEW)
        v["units"][0].update(review="specialist(security)", review_why="chạm phân quyền")
        v["units"][1].update(review="none", review_why="chỉ đổi nhãn")
        v["risks"][0]["level"] = "high"
        v["decisions"][1]["risk"] = "high"
        self.put(v)
        m, hv, _ = self.model()
        road = next(f for f in m["figures"] if f["key"] == "roadmap")
        self.assertIn("soát: specialist(security)", road["svg"])
        self.assertIn("chạm phân quyền", road["svg"])
        self.assertIn("không ai soát thứ hai", road["svg"])
        self.assertIn("1 phần việc không ai soát thứ hai: UOW-02.", road["note"])
        # #35 — view ghi high thì hình vẫn nói "cao"
        self.assertIn("MỨC CAO", next(f for f in m["figures"] if f["key"] == "risks")["svg"])
        self.assertEqual(next(x for x in m["decisions"] if x["id"] == "D2")["risk"], "cao")
        self.assertEqual(hv["warnings"], [])

    def test_recommended_null_is_not_an_error(self):
        v = copy.deepcopy(HV_VIEW)
        v["decisions"][0]["recommended"] = None
        v["gaps"] = [{"text": "bản chữ không có khuyến nghị cho D1", "ref": "1.7", "decision": "D1"}]
        self.put(v)
        m, hv, _ = self.model()
        self.assertEqual(hv["warnings"], [])
        d1 = next(x for x in m["decisions"] if x["id"] == "D1")
        self.assertNotIn("AI đề xuất", d1["svg"])
        self.assertIn("nếu im lặng", d1["svg"])
        self.assertEqual((d1["recommended"], d1["default"]), ("", "A"))

    def test_reversal_deadline_and_unlocks(self):
        v = self.v3()
        v["decisions"][0]["options"][0]["reversal_until"] = "trước phát hành"
        v["decisions"][0]["unlocks"] = ["D2", "D4"]
        v["decisions"][1]["unlocks"] = ["D77"]
        self.put(v)
        m, hv, _ = self.model()
        d1 = next(x for x in m["decisions"] if x["id"] == "D1")
        self.assertIn("đảo rẻ tới: trước phát hành", d1["svg"])
        self.assertEqual(d1["defaultUntil"], "trước phát hành")
        self.assertEqual(d1["line"], "A. Quản lý + trưởng ca · 0h · đảo rẻ tới: trước phát hành")
        self.assertIn("gỡ 2 điểm khác", d1["svg"])
        self.assertEqual(m["early"], ["D1"], "gỡ ≥ 2 điểm mới lên tầng Nên nhìn sớm")
        self.assertEqual(d1["group"], "confirm")
        self.assertIn("D2.unlocks trỏ D77", " | ".join(hv["warnings"]))

    def test_idle_line_names_where_the_team_stands(self):
        v = self.v3()
        v["decisions"][1].update(default=None, needs="ai xác nhận nơi lưu")
        self.put(v)
        m, _, _ = self.model()
        self.assertEqual(m["idle"]["standing"], [{"id": "D2", "needs": "ai xác nhận nơi lưu", "question": "Dữ liệu lưu ở đâu?"}])
        self.assertEqual(m["idle"]["defaults"], [{"id": "D1", "key": "A"}])

    def test_stale_view_is_marked(self):
        self.put(HV_VIEW)
        write(self.doc, read(self.doc).replace("version: 1", "version: 2", 1) + "\n- v2: bản chữ đổi sau khi vẽ\n")
        m, hv, _ = self.model()
        self.assertTrue(m["stale"])
        self.assertTrue(hv["stale"], "data.humanView[intent].stale phải bật")
        self.assertEqual((m["staleFrom"], m["staleTo"]), ("1", "2"))
        self.assertTrue(any("MÔ HÌNH CŨ" in w for w in hv["warnings"]))
        self.assertEqual([f["key"] for f in m["figures"]], SIX, "mô hình cũ vẫn vẽ — tower treo cảnh báo, không giấu hình")

    def test_missing_keys_drop_only_their_figure(self):
        v = {k: HV_VIEW[k] for k in ("version", "headline", "units", "risks")}
        self.put(v)
        m, _, _ = self.model()
        self.assertEqual([f["key"] for f in m["figures"]], ["roadmap", "sources", "risks"])

    def test_fence_in_document_is_not_a_source(self):
        """Mô hình phải do agent KHÁC viết thành file riêng — khối nhúng trong tài liệu không được đọc."""
        write(self.doc, HV_DOC + "\n```human-view\n" + json.dumps(HV_VIEW, ensure_ascii=False) + "\n```\n")
        self.assertEqual(generate(self.root)["humanView"], {})

    def test_no_view_changes_nothing(self):
        before = generate(self.root)
        self.assertEqual(before["humanView"], {})
        self.assertTrue(all("modelDoc" not in x for x in before["autopilot"]["decisions"]))
        self.put(HV_VIEW)
        after = generate(self.root)
        skip = {"humanView", "autopilot", "project", "activity"}
        for k in before:
            if k not in skip:
                self.assertEqual(before[k], after[k], "thêm mô hình không được đổi khoá `%s`" % k)
        strip = lambda ds: [{k: v for k, v in x.items() if k != "modelDoc"} for x in ds]   # noqa: E731
        self.assertEqual(strip(before["autopilot"]["decisions"]), strip(after["autopilot"]["decisions"]))


ESC = """---
id: ESC-001
found_by: dlc-intent-analyst
found_in: HOF-0001
severity: high
scope_impact: scope
owner:
status: open
---
# ESC-001 · Đăng nhập bằng chuỗi cố định
"""
ESC_VIEW = {"version": 2, "source": "ESC-001.md",
            "decisions": [{"id": "ESC-001", "question": "Xử lý đăng nhập chuỗi cố định thế nào?", "who": "tech lead",
                           "risk": "cao", "recommended": "A", "default": None, "needs": "ai phụ trách đăng nhập",
                           "options": [{"key": "A", "name": "Tách thành intent riêng", "cost": "một đợt"},
                                       {"key": "B", "name": "Sửa luôn đợt này", "cost": "+6h", "reversal": "đắt"}]}]}


class TowerDetails(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.p = build(self.root, gates_auto=("A",))

    def tearDown(self):
        self.tmp.cleanup()

    def test_escalation_names_its_intent_not_the_handoff(self):
        write(os.path.join(self.p["cm"], "handoffs", "HOF-0001.md"),
              "---\nid: HOF-0001\nfrom: HUMAN\nto: dlc-intent-analyst\nre: INT-001\nstatus: done\n---\n## Nhiệm vụ\n")
        write(os.path.join(self.p["cm"], "escalations", "ESC-001.md"), ESC)
        d = generate(self.root)
        e = d["escalations"][0]
        self.assertEqual((e["id"], e["foundIn"], e["intent"]), ("ESC-001", "HOF-0001", "INT-001"))
        self.assertEqual(d["svg"]["escalations"], {}, "chưa có view thì thẻ như cũ")

    def test_escalation_view_draws_a_tree(self):
        write(os.path.join(self.p["cm"], "escalations", "ESC-001.md"), ESC)
        vp = os.path.join(self.p["cm"], "escalations", "views", "ESC-001.view.json")
        write(vp, json.dumps(ESC_VIEW, ensure_ascii=False))
        t = generate(self.root)["svg"]["escalations"]["ESC-001"]
        self.assertRegex(t["svg"], r"^<svg[\s>]")
        self.assertEqual([o["key"] for o in t["options"]], ["A", "B"])
        self.assertIn("đảo đắt", t["svg"])
        self.assertIn("ai phụ trách đăng nhập", t["svg"])
        write(vp, json.dumps(ESC_VIEW["decisions"][0], ensure_ascii=False))      # để thẳng object quyết định
        self.assertEqual(len(generate(self.root)["svg"]["escalations"]["ESC-001"]["options"]), 2)
        write(vp, "{hỏng")
        t = generate(self.root)["svg"]["escalations"]["ESC-001"]
        self.assertEqual(t["svg"], "")
        self.assertIn("không đọc được", t["error"])

    def test_question_unlocks_and_reversal_deadline(self):
        q = os.path.join(self.p["intent"], "open-questions-business.md")
        before = generate(self.root)["svg"]["questions"]["INT-001:OQB-01"]
        self.assertNotIn("unlocks", before)
        self.assertNotIn("đảo rẻ", before["svg"], "thẻ không ghi giá đảo thì hình như cũ")
        write(q, read(q).replace("| ☐ | **A.** Chỉ quản lý kho | Nhân viên nhờ quản lý | không tốn thêm |",
                                 "| ☐ | **A.** Chỉ quản lý kho | Nhân viên nhờ quản lý | không tốn thêm · Đảo: rẻ tới trước phát hành |")
                        .replace("- **Nếu không trả lời trước hạn**",
                                 "- **Gỡ được**: OQB-02, OQT-01, OQT-03\n- **Nếu không trả lời trước hạn**"))
        t = generate(self.root)["svg"]["questions"]["INT-001:OQB-01"]
        self.assertEqual(t["unlocks"], ["OQB-02", "OQT-01", "OQT-03"])
        self.assertEqual(t["silentUntil"], "trước phát hành")
        self.assertIn("đảo rẻ tới: trước phát hành", t["svg"])
        self.assertIn("gỡ 3 câu khác", t["svg"])

    def test_decided_escalation_still_open_is_flagged(self):
        write(os.path.join(self.p["cm"], "escalations", "ESC-002.md"), ESC.replace("ESC-001", "ESC-002"))
        log = os.path.join(self.p["gov"], "decisions-log.md")
        write(log, read(log).replace("- Căn cứ: intent-plan.md#3", "- Căn cứ: ESC-002 · intent-plan.md#3", 1))
        d = generate(self.root)
        self.assertEqual([w["text"] for w in d["autopilot"]["warnings"]], ["DEC-0001 đã quyết ESC-002 nhưng ESC-002 vẫn open"])
        self.assertIn("DEC-0001 đã quyết ESC-002 nhưng ESC-002 vẫn open",
                      d["metricsByIntent"]["INT-001"]["autopilot.decisions"]["warnings"])
        esc = os.path.join(self.p["cm"], "escalations", "ESC-002.md")
        write(esc, read(esc).replace("status: open", "status: resolved"))
        self.assertEqual(generate(self.root)["autopilot"]["warnings"], [], "ESC đã đóng thì hết cảnh báo")

    PLAN = """---
version: 1
---
# Unit plan

## 1. Đã đổi gì so với provisional (đọc trước tiên)

| Unit provisional | Sau khi đọc AS-IS | Vì sao đổi |
|---|---|---|
| UOW-01 | giữ · 9.0h | tên SAI nếu đọc nhầm bảng này |
| UOW-01 (2.75h) | giữ · **3.0h (+0.25h)** | hàm lấy danh sách là bản rút gọn |

## 3. Bảng Unit

| Unit | Capability | Areas | Est (h) | Bolt | Phụ thuộc | Risk |
|---|---|---|---|---|---|---|
| UOW-00 | Bài kiểm máy chủ chạy được | api | 0.75h | 1 | — | 2 |
| UOW-01 | Chỉ quản lý kho và trưởng ca huỷ được đơn | api, web | 3.0 | 1 | UOW-00 | 5 |
| UOW-02 | Huỷ phải nêu lý do | api, web | **3,75** | 1 | UOW-00, UOW-01 | 6 |
| | **Tổng** | | **7.5** | | | |

""" + PAD

    def plan_only(self, text):
        import shutil
        shutil.rmtree(os.path.join(self.p["intent"], "units"))
        write(os.path.join(self.p["intent"], "unit-plan.md"), text)
        return generate(self.root)

    def test_unit_table_is_found_by_its_columns(self):
        u = self.plan_only(self.PLAN)["unitsByIntent"]["INT-001"]
        self.assertEqual([(x["id"], x["name"], x["estimate"]) for x in u],
                         [("UOW-00", "Bài kiểm máy chủ chạy được", 0.75),
                          ("UOW-01", "Chỉ quản lý kho và trưởng ca huỷ được đơn", 3.0),
                          ("UOW-02", "Huỷ phải nêu lý do", 3.75)],
                         "bảng 'đã đổi gì' đứng trước không được lấn bảng Unit; giờ nhận cả 3.0 lẫn 0.75h lẫn 3,75")

    def test_unit_plan_without_known_header_still_reads_the_old_way(self):
        u = self.plan_only("---\nversion: 1\n---\n# Unit plan\n\n| Mục | Việc | Ghi chú |\n|---|---|---|\n"
                           "| UOW-01 | Danh sách đơn | 4h |\n| UOW-02 | Đổi trạng thái | 6.5h |\n\n" + PAD)["unitsByIntent"]["INT-001"]
        self.assertEqual([(x["id"], x["name"], x["estimate"]) for x in u],
                         [("UOW-01", "Danh sách đơn", 4.0), ("UOW-02", "Đổi trạng thái", 6.5)])

    def test_risk_levels_are_shown_in_one_vocabulary(self):
        write(os.path.join(self.p["cm"], "escalations", "ESC-001.md"), ESC)            # severity: high
        write(os.path.join(self.p["gov"], "risks.md"),
              "# Risks\n- R-01 · high · mất dữ liệu · chủ: dev\n- R-02 · vừa · chậm · chủ: qa\n- R-03 · low · nhãn sai · chủ: ba\n")
        d = generate(self.root)
        self.assertEqual((d["escalations"][0]["severity"], d["escalations"][0]["level"]), ("high", "cao"))
        self.assertEqual([(r["sev"], r["level"]) for r in d["risks"]], [("high", "cao"), ("med", "vừa"), ("low", "thấp")])

    def test_two_decs_disagreeing_on_one_question_are_flagged(self):
        from helpers import autopilot_check, codes
        log = os.path.join(self.p["gov"], "decisions-log.md")
        ap = lambda n, g, line, **k: dec(n, g, **k).replace("- Áp: không có", "- Áp: " + line)      # noqa: E731

        def both():
            tower = [x["text"] for x in generate(self.root)["autopilot"]["warnings"]]
            ap14 = [f for f in autopilot_check(self.root)[2] if f["code"] == "AP14"]
            self.assertEqual(len(tower), len(ap14), "tower và autopilot_check (AP14) phải cùng kết luận: %r vs %r" % (tower, ap14))
            return tower

        # dòng Áp: khác phương án cho OQT-03, cùng phương án cho OQT-01
        write(log, "# Decisions log\n\n" + dec(1, "A")
              + ap(2, "C", "OQT-03 = A · OQT-01 = B") + ap(3, "D", "OQT-03 = C · OQT-01 = B"))
        self.assertEqual(both(), ["DEC-0002 và DEC-0003 cùng quyết OQT-03 nhưng khác phương án (A ≠ C)"])
        # DEC sau ghi `thay` ⇒ DEC trước hết hiệu lực Ở MÃ ĐÓ
        write(log, "# Decisions log\n\n" + dec(1, "A")
              + ap(2, "C", "OQT-03 = A · OQT-01 = B") + ap(3, "D", "OQT-03 = C (thay DEC-0002) · OQT-01 = A"))
        self.assertEqual(both(), ["DEC-0002 và DEC-0003 cùng quyết OQT-01 nhưng khác phương án (B ≠ A)"],
                         "`thay` chỉ có hiệu lực ở mã nó đứng cạnh — OQT-01 của DEC-0002 vẫn còn")
        # ca thật của demo: ba DEC, DEC giữa cùng phương án với DEC cuối, DEC cuối thay DEC đầu
        write(log, "# Decisions log\n\n" + ap(1, "C", "OQT-03 = A") + ap(2, "D", "OQT-03 = C")
              + ap(3, "D", "OQT-03 = C (thay DEC-0001)"))
        self.assertEqual(both(), [])
        # dòng Áp đọc TRƯỚC: DEC có `Áp: không có` thì câu văn "OQT-03 = A" trong Quyết định không được tính
        write(log, "# Decisions log\n\n" + dec(1, "C").replace("- Quyết định: duyệt", "- Quyết định: áp OQT-03 = A")
              + ap(2, "D", "OQT-03 = C"))
        self.assertEqual(both(), [])

    def test_prose_is_the_fallback_when_there_is_no_apply_line(self):
        log = os.path.join(self.p["gov"], "decisions-log.md")
        old = lambda n, g, **k: dec(n, g, **k).replace("- Áp: không có\n", "")      # noqa: E731
        write(log, "# Decisions log\n\n" + old(1, "A")
              + old(2, "C", shown="open-questions-tech.md#0").replace("- Quyết định: duyệt", "- Quyết định: áp mặc định OQT-03 = A, OQT-01 (B)")
              + old(3, "D", shown="unit-plan.md#2").replace("- Chọn: phương án A", "- Chọn: gộp việc thuộc phương án C của OQT-03; OQT-01 chọn B"))
        w = [x["text"] for x in generate(self.root)["autopilot"]["warnings"]]
        self.assertEqual(w, ["DEC-0002 và DEC-0003 cùng quyết OQT-03 nhưng khác phương án (A ≠ C)"])
        # đọc không rõ phương án ở một bên ⇒ im, không đoán
        write(log, "# Decisions log\n\n" + old(1, "A")
              + old(2, "C").replace("- Quyết định: duyệt", "- Quyết định: áp mặc định OQT-03 = A")
              + old(3, "D").replace("- Chọn: phương án A", "- Chọn: làm thêm việc liên quan OQT-03: Anh Tuấn xác nhận sau"))
        self.assertEqual(generate(self.root)["autopilot"]["warnings"], [])
        # DEC sau sinh từ một lần người đảo DEC trước ⇒ khác nhau là chủ đích
        write(log, "# Decisions log\n\n" + old(1, "A")
              + old(2, "C").replace("- Quyết định: duyệt", "- Quyết định: áp mặc định OQT-03 = A")
              + old(3, "C", extra="- reverses: DEC-0002\n").replace("- Quyết định: duyệt", "- Quyết định: đổi OQT-03 = C"))
        self.assertEqual(generate(self.root)["autopilot"]["warnings"], [])

    def test_tower_reads_the_apply_line_with_the_checkers_pattern(self):
        import subprocess
        import sys
        from helpers import SCRIPTS, clean_env
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0, %r)\nimport tower_generate as t, autopilot_check as a\n"
                            "print(t.APPLY_RE is a.APPLY_RE)" % SCRIPTS],
                           capture_output=True, text=True, env=clean_env())
        self.assertEqual(r.stdout.strip(), "True", r.stderr)

    def test_conflicts_counted_once_per_code(self):
        led = os.path.join(self.p["intent"], "as-is", "source-ledger.md")
        write(led, read(led) + """
## 3. Mâu thuẫn giữa các nguồn

| # | Nguồn A nói | Nguồn B nói | Trạng thái |
|---|---|---|---|
| C1 | nhân viên kho huỷ được [CONFLICT] | chỉ người có thẩm quyền | open |
| C2 | đơn đã giao đi hoàn hàng | đơn đã giao vẫn huỷ được | open |

## 4. Ghi chú

- Luật huỷ [CONFLICT] xem C2 ở trên.
- Giờ của ca tối [CONFLICT] giữa biên bản và tài liệu ca. [CONFLICT]
""")
        s = generate(self.root)["sourcesByIntent"]["INT-001"]
        self.assertEqual([c["id"] for c in s["conflicts"]], ["C1", "C2", "[CONFLICT]"],
                         "dấu trên dòng bảng và dấu nhắc lại mã C2 là cùng mâu thuẫn đã đếm")
        self.assertEqual(s["counts"]["conflicts"], 3)

    def test_no_five_hour_ceiling_left(self):
        write(os.path.join(self.p["intent"], "intent-plan.md"),
              "---\nversion: 1\n---\n# Intent plan\n### 3.2 Bảng Unit\n\n| Unit | Tên | Est (h) |\n|---|---|---|\n"
              "| UOW-07 | Phần việc dài | 9.5 |\n\n" + PAD)
        import shutil
        shutil.rmtree(os.path.join(self.p["intent"], "units"))
        os.remove(os.path.join(self.p["intent"], "unit-plan.md"))
        u = generate(self.root)["unitsByIntent"]["INT-001"]
        self.assertEqual([(x["id"], x["estimate"], x["problems"]) for x in u], [("UOW-07", 9.5, [])])


    def test_closed_intent_closes_its_units_and_bolts(self):
        """§2.5 (6.6.0): intent `phase: closed` ⇒ unit/bolt còn lại hiện "đã đóng", không còn "chờ" ai."""
        write(os.path.join(self.p["intent"], "units", "UOW-01", "bolts", "BOLT-01", "tasks.md"), "# tasks\n")
        u = {x["id"]: x for x in generate(self.root)["unitsByIntent"]["INT-001"]}
        self.assertNotEqual(u["UOW-01"]["status"], "done")          # đối chứng: intent còn chạy thì unit vẫn mở
        self.assertFalse(u["UOW-01"]["boltDetails"][0]["closed"])
        st = os.path.join(self.p["intent"], "status.md")
        write(st, read(st).replace("phase: construction", "phase: closed   # đóng\nclosed_by: DEC-0099   # x"))
        spec = os.path.join(self.p["intent"], "units", "UOW-02", "spec.md")
        write(spec, read(spec).replace("status: todo", "status: closed\nclosed_by: DEC-0098"))
        u = {x["id"]: x for x in generate(self.root)["unitsByIntent"]["INT-001"]}
        self.assertEqual((u["UOW-01"]["status"], u["UOW-01"]["closedBy"], u["UOW-01"]["problems"]),
                         ("done", "DEC-0099", []))
        self.assertEqual(u["UOW-01"]["boltDetails"][0]["closedBy"], "DEC-0099")
        self.assertEqual(u["UOW-02"]["closedBy"], "DEC-0098", "DEC riêng của unit thắng DEC của intent")


class ImportIsSafe(unittest.TestCase):
    """Hai agent trong lần chạy thử đã vô tình sinh lại tower khi chỉ muốn kiểm một parser (phát hiện #22)."""

    def test_import_writes_nothing_and_parsers_work(self):
        import subprocess
        import sys
        from helpers import SCRIPTS, clean_env
        with tempfile.TemporaryDirectory() as t:
            root = os.path.realpath(t)
            p = build(root)
            code = (
                "import json, os, sys\n"
                "sys.path.insert(0, %r)\n"
                "import tower_generate as tg\n"
                "qs = tg.parse_questions(%r)\n"
                "tg.use_project(%r)\n"
                "units = tg.parse_units(%r, 'INT-001', 6)\n"
                "print(json.dumps({'q': [q['code'] for q in qs], 'u': [u['id'] for u in units],\n"
                "                  'main': callable(tg.main), 'tower': os.path.exists(os.path.join(%r, '.ai-dlc', 'tower'))}))\n"
            ) % (SCRIPTS, p["intent"], root, p["intent"], root)
            r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=clean_env(), cwd=root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout), {"q": ["OQB-01", "OQB-02"], "u": ["UOW-01", "UOW-02"],
                                                    "main": True, "tower": False})
            self.assertEqual(sorted(os.listdir(os.path.join(root, ".ai-dlc"))),
                             ["context-memory", "inbox", "workspace-map.md"], "import + parser không được ghi gì")

    def test_main_twice_in_one_process_does_not_accumulate(self):
        import subprocess
        import sys
        from helpers import SCRIPTS, clean_env
        with tempfile.TemporaryDirectory() as t:
            root = os.path.realpath(t)
            p = build(root)
            write(os.path.join(p["cm"], "escalations", "ESC-001.md"), ESC)
            write(os.path.join(p["cm"], "lessons-learned", "LL-001.md"), "---\nstatus: proposed\n---\n# LL-001 · bài học\n")
            code = ("import sys\nsys.path.insert(0, %r)\nimport tower_generate as tg\n"
                    "tg.main(['x', %r])\ntg.main(['x', %r])\n" % (SCRIPTS, root, root))
            r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=clean_env())
            self.assertEqual(r.returncode, 0, r.stderr)
            js = read(os.path.join(root, ".ai-dlc", "tower", "data.js"))
            d = json.loads(js[js.index("window.CT_DATA = ") + len("window.CT_DATA = "):].rstrip().rstrip(";"))
            self.assertEqual([len(d["escalations"]), len(d["lessons"]), len(d["autopilot"]["decisions"]),
                              len(d["intents"])], [1, 1, 4, 1])

    def test_cli_behaviour_is_unchanged(self):
        rc, out, err = run_py("tower_generate.py", "/nonexistent-dir-for-test")
        self.assertEqual(rc, 1)
        self.assertIn("Không tìm thấy dự án AI-DLC", err)
        with tempfile.TemporaryDirectory() as t:
            root = os.path.realpath(t)
            build(root)
            rc, out, err = run_py("tower_generate.py", os.path.join(root, ".ai-dlc", "context-memory"))
            self.assertEqual(rc, 0, err)
            self.assertEqual(out.strip(), os.path.join(root, ".ai-dlc", "tower", "index.html"))
            self.assertIn("gốc dự án", err)


class TowerServe(unittest.TestCase):
    def test_tower_exists_before_first_request(self):
        import socket
        import subprocess
        import sys
        import time
        import urllib.request
        from helpers import SCRIPTS, clean_env
        with tempfile.TemporaryDirectory() as t:
            root = os.path.realpath(t)
            build(root)
            with socket.socket() as sk:
                sk.bind(("127.0.0.1", 0))
                port = sk.getsockname()[1]
            self.assertFalse(os.path.exists(os.path.join(root, ".ai-dlc", "tower", "index.html")))
            proc = subprocess.Popen([sys.executable, os.path.join(SCRIPTS, "tower_serve.py"), root, str(port)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env())
            try:
                code = None
                for _ in range(80):
                    try:
                        with urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=2) as r:
                            code = r.status
                        break
                    except urllib.error.HTTPError as e:
                        code = e.code
                        break
                    except OSError:
                        time.sleep(0.1)
                self.assertEqual(code, 200, "trang đầu phải có ngay ở lần gọi đầu tiên, không 404")
            finally:
                proc.terminate()
                proc.wait(timeout=5)
                proc.stdout.close()
                proc.stderr.close()


if __name__ == "__main__":
    unittest.main()
