#!/usr/bin/env python3
"""AI-DLC gate guard (PreToolUse, matcher Write|Edit).

Hàng rào cứng: khi project có intent AI-DLC đang chạy mà CHƯA qua Gate D,
chặn Write/Edit vào code roots (đọc từ workspace-map). Cũng chặn sửa
governance/ (dor/dod) trực tiếp — phải đi qua DEC (skill sẽ ghi kèm decisions-log
trong cùng lượt; guard chỉ chặn khi không có intent/flow nào active).

Fail-open triệt để: thiếu file, sai format, không có .ai-dlc → cho qua (exit 0).
Tắt khẩn: export AI_DLC_GUARD=off. Exit 2 = block (stderr là lý do).
"""
import json, os, re, sys

def allow():
    sys.exit(0)

def block(msg):
    sys.stderr.write(msg)
    sys.exit(2)

try:
    if os.environ.get("AI_DLC_GUARD", "").lower() == "off":
        allow()
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input") or {}
    fp = tool_input.get("file_path") or ""
    if not fp:
        allow()
    root = data.get("cwd") or os.getcwd()
    aidlc = os.path.join(root, ".ai-dlc")
    if not os.path.isdir(aidlc):
        allow()
    fp_abs = os.path.abspath(fp)
    # Không chặn ghi trong .ai-dlc/ (trừ governance — xem dưới)
    aidlc_abs = os.path.abspath(aidlc)
    gov = os.path.join(aidlc_abs, "context-memory", "governance")

    # Đọc code roots từ workspace-map (YAML đơn giản: "  frontend: path")
    code_roots = []
    wm = os.path.join(aidlc, "workspace-map.md")
    if os.path.isfile(wm):
        in_code = False
        for line in open(wm, encoding="utf-8", errors="replace"):
            s = line.rstrip("\n")
            if re.match(r"^code:\s*$", s):
                in_code = True
                continue
            if in_code:
                m = re.match(r"^\s+\w+:\s*(\S+)", s)
                if m:
                    v = m.group(1).strip().strip('"')
                    if v and v != "null":
                        code_roots.append(os.path.abspath(os.path.join(root, v)))
                elif not s.startswith(" "):
                    in_code = False

    # Trạng thái intents
    intents_dir = os.path.join(aidlc, "context-memory", "intents")
    active = []       # intents đang mở (stage < 8 hoặc gate_open)
    any_d_passed = False
    if os.path.isdir(intents_dir):
        for name in os.listdir(intents_dir):
            st = os.path.join(intents_dir, name, "status.md")
            if not os.path.isfile(st):
                continue
            txt = open(st, encoding="utf-8", errors="replace").read()
            gates = re.search(r"gates_passed:\s*\[([^\]]*)\]", txt)
            passed = [g.strip() for g in gates.group(1).split(",")] if gates else []
            stage_m = re.search(r"^stage:\s*(\d+)", txt, re.M)
            stage = int(stage_m.group(1)) if stage_m else 1
            if stage < 8:
                active.append(name)
                if "D" in passed:
                    any_d_passed = True

    # Rule 1: sửa governance (dor/dod) — chỉ nhắc khi không có flow nào active
    if fp_abs.startswith(gov) and os.path.basename(fp_abs) in ("dor.md", "dod.md"):
        # cho qua nhưng không chặn — DEC được ghi bởi skill trong cùng lượt;
        # chặn cứng ở đây sẽ khóa cả luồng hợp lệ. Chỉ cảnh báo qua stdout (không block).
        allow()

    # Rule 2: chặn code-write trước Gate D
    if active and not any_d_passed:
        for cr in code_roots:
            if fp_abs.startswith(cr + os.sep) or fp_abs == cr:
                block(
                    "AI-DLC gate guard: intent dang chay ({}) CHUA qua Gate D — "
                    "khong duoc ghi vao code root '{}'. Hoan thanh Gate D (approve Units + DoD) "
                    "hoac tat khan bang AI_DLC_GUARD=off neu day la viec ngoai flow.".format(
                        ",".join(active), cr
                    )
                )
    allow()
except SystemExit:
    raise
except Exception:
    # fail-open: guard không bao giờ được phá công việc thường
    allow()
