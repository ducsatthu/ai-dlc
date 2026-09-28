"""tower_generate.py — data.js nạp được, SVG có mặt, chữ từ markdown được escape, dự án lead không đổi."""
import json
import os
import re
import tempfile
import unittest

from helpers import build, read, run_py, write

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


if __name__ == "__main__":
    unittest.main()
