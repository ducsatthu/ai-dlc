"""Dựng dự án .ai-dlc/ mẫu cho test — một ca SẠCH làm đối chứng, test tự đột biến từ đó (protocol §4.15)."""
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "plugin", "scripts")
HOOKS = os.path.join(REPO, "plugin", "hooks")
PAD = "Nội dung đủ dài để không bị coi là rỗng. " * 8


def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("AI_DLC_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def dec(n, gate, intent="INT-001", shown="intent-plan.md#3", autopilot=True, extra=""):
    if not autopilot:
        return ("## DEC-%04d · 2026-09-27 · Gate %s · %s\n"
                "- Quyết định: chốt   - Người quyết: HUMAN\n- Căn cứ: RV-001   - Ảnh hưởng: không\n\n" % (n, gate, intent))
    return ("## DEC-%04d · 2026-09-27 · Gate %s · %s · autopilot\n"
            "- Quyết định: duyệt   - Người quyết: autopilot (mode: autopilot, governance/autopilot.md)\n"
            "- Căn cứ: %s   - Ảnh hưởng: stage kế chạy\n"
            "- Chọn: phương án A — giá: 2h · rủi ro thấp\n"
            "- Bỏ: phương án B — vì: tốn thêm 6h\n"
            "- Đảo bằng: viết lại mục đó rồi chạy lại stage kế — khoảng 2h   - Hiện ở: %s\n"
            "- Block check: #1 pass · #2 pass · #3 pass · #4 pass · #5 pass · #6 pass\n%s\n"
            % (n, gate, intent, shown, shown, extra))


QUESTIONS = """---
intent: INT-001
doc: open-questions-business
version: 1
---
# Câu hỏi cần người nghiệp vụ quyết — INT-001

## 0. Bảng điều phối — ai phải trả lời gì

| Mã | Câu hỏi | Ai trả lời | Hạn | Nếu im lặng | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|---|---|
| OQB-01 | Ai được huỷ đơn? | PO · chị Lan | 30/09 | chỉ quản lý kho | CHẶN UOW-02 | open |
| OQB-02 | Đơn cũ có hiện không? | BA · anh Minh | 02/10 | ẩn | không chặn | open |

### OQB-01 · Ai được huỷ đơn?

**Chọn một:**

| | Phương án | Nghĩa là gì với người dùng | Cái giá |
|---|---|---|---|
| ☐ | **A.** Chỉ quản lý kho | Nhân viên nhờ quản lý | không tốn thêm |
| ☐ | **B.** Quản lý và trưởng ca | Trưởng ca huỷ được | +2h |

- **AI đề xuất**: B — trưởng ca có mặt khi khách gọi.
- **Nếu không trả lời trước hạn**: đi theo phương án A, ghi `[ASSUMED]`.
"""

LEDGER = """---
title: Source ledger
---
## 0. Sổ cái
| # | Nguồn | Thông tin cần lấy | Trạng thái | Evidence |
|---|---|---|---|---|
| S-01 | docs/orders.md | luồng đơn | read | mục 2 |
| S-02 | docs/roles.md | vai trò | read | mục 1 |

""" + PAD


def build(root, mode="autopilot", gates_auto=("A", "B", "C", "D"), gate_open="null", blocked_by=None):
    """Dự án sạch: intent stage 6, bốn gate tự đóng có DEC đủ dòng, artefact đủ, 2 Unit đủ 4 file."""
    cm = os.path.join(root, ".ai-dlc", "context-memory")
    gov = os.path.join(cm, "governance")
    idir = os.path.join(cm, "intents", "INT-001")
    os.makedirs(os.path.join(root, ".ai-dlc", "inbox"), exist_ok=True)
    os.makedirs(os.path.join(root, "src", "api"), exist_ok=True)
    if mode:
        write(os.path.join(gov, "autopilot.md"),
              "---\ndoc: autopilot\nversion: 1\nmode: %s\nwait_hours: 0\nmax_units_per_intent: 8\nmax_self_fix: 2\n---\n" % mode)
    shown = {"A": "intent-plan.md#3", "B": "as-is/source-ledger.md#0",
             "C": "open-questions-business.md#0", "D": "unit-plan.md#2"}
    log = "# Decisions log\n\n"
    for i, g in enumerate(gates_auto, 1):
        log += dec(i, g, shown=shown.get(g, "intent-plan.md#3"), autopilot=(mode == "autopilot"))
    write(os.path.join(gov, "decisions-log.md"), log)
    passed = ", ".join(gates_auto)
    st = ("---\nintent: INT-001\nstage: 6\nphase: construction\ngates_passed: [%s]\ngate_open: %s\n"
          "gate_doc: null\nplan_version: 1\nplugin_version: 6.4.0\n" % (passed, gate_open))
    if mode == "autopilot":
        st += "gates_auto: [%s]          # 6.4.0\n" % passed
    if blocked_by:
        st += 'blocked_by: "%s"\n' % blocked_by
    st += "updated: 2026-09-28\n---\n"
    write(os.path.join(idir, "status.md"), st)
    write(os.path.join(idir, "intent.md"), "# INT-001 · Quản lý đơn\n" + PAD)
    write(os.path.join(idir, "intent-plan.md"), "---\nversion: 1\n---\n# Intent plan\n## 3. Unit map\n" + PAD)
    write(os.path.join(idir, "as-is", "source-ledger.md"), LEDGER)
    write(os.path.join(idir, "open-questions-business.md"), QUESTIONS)
    write(os.path.join(idir, "unit-plan.md"), "---\nversion: 1\n---\n# Unit plan\n## 2. Bảng Unit\n" + PAD)
    for u in ("UOW-01", "UOW-02"):
        write(os.path.join(idir, "units", u, "spec.md"),
              "---\nid: %s\nstatus: todo\nreleasable: yes\nsession_fit: 3 file, 1 endpoint\nestimate_hours: 3\nreview: none\n---\n# %s\n" % (u, u))
        for f in ("user-stories.md", "nfr.md", "risks.md"):
            write(os.path.join(idir, "units", u, f), "# %s\n%s" % (f, PAD))
    write(os.path.join(root, ".ai-dlc", "workspace-map.md"),
          "---\ntype: workspace-map\nversion: 2\n---\n```yaml\nrepos:\n  - id: main\n    path: .\nareas:\n  backend:\n"
          "    repo: main\n    path: src/api\n    tests: null\ncode:\n  backend: src/api\n```\n")
    return {"root": root, "cm": cm, "gov": gov, "intent": idir, "inbox": os.path.join(root, ".ai-dlc", "inbox")}


def run_py(script, *args, stdin=None, cwd=None):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args), input=stdin,
                       capture_output=True, text=True, env=clean_env(), cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def autopilot_check(root):
    code, out, err = run_py("autopilot_check.py", root, "--json")
    data = json.loads(out)
    return code, data["info"], data["findings"]


def codes(findings, level=None):
    return sorted({f["code"] for f in findings if level is None or f["level"] == level})


def have(cmd):
    return shutil.which(cmd) is not None
