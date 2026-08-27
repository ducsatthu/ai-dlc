#!/usr/bin/env python3
"""AI-DLC gate guard (PreToolUse, matcher Write|Edit).

Hàng rào cứng: khi project có intent AI-DLC đang chạy mà CHƯA qua Gate D,
chặn Write/Edit vào code roots (đọc từ workspace-map). Cũng chặn sửa
governance/ (dor/dod) trực tiếp — phải đi qua DEC (skill sẽ ghi kèm decisions-log
trong cùng lượt; guard chỉ chặn khi không có intent/flow nào active).

6.2.0: code roots đọc từ `areas.*.path` (workspace-map v2) LẪN `code.*` (v1); `.ai-dlc/` được tìm
từ cwd đi lên tối đa 2 cấp (một đội nhiều repo đặt `.ai-dlc/` ở thư mục cha). Path trong map
tương đối với thư mục chứa `.ai-dlc/`.

Fail-open triệt để: thiếu file, sai format, không có .ai-dlc → cho qua (exit 0).
Tắt khẩn: export AI_DLC_GUARD=off. Exit 2 = block (stderr là lý do).
"""
import json, os, re, sys

def allow():
    sys.exit(0)

def block(msg):
    sys.stderr.write(msg)
    sys.exit(2)

def find_root(start, max_up=2):
    """Thư mục chứa `.ai-dlc/context-memory/`: cwd, rồi cha, rồi ông (tối đa 2 cấp)."""
    cur = os.path.abspath(start)
    for _ in range(max_up + 1):
        if os.path.isdir(os.path.join(cur, ".ai-dlc", "context-memory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    # tương thích 6.1: `.ai-dlc/` ngay tại cwd dù chưa có context-memory
    if os.path.isdir(os.path.join(os.path.abspath(start), ".ai-dlc")):
        return os.path.abspath(start)
    return None

def code_roots_from_map(wm_path, root):
    """Đọc code roots từ workspace-map. YAML đơn giản, không cần thư viện:
       v1:  code:\n  frontend: path
       v2:  areas:\n  api:\n    path: services/api\n    tests: …   (chỉ lấy `path:`)"""
    roots = []
    if not os.path.isfile(wm_path):
        return roots
    section = None      # "code" | "areas" | None
    for line in open(wm_path, encoding="utf-8", errors="replace"):
        s = line.rstrip("\n")
        if not s.strip() or s.lstrip().startswith("#"):
            continue
        if re.match(r"^\S", s):                       # key cấp 0
            m = re.match(r"^(\w+):\s*$", s)
            section = m.group(1) if m and m.group(1) in ("code", "areas") else None
            continue
        if section == "code":
            m = re.match(r"^\s+\w+:\s*(\S+)", s)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v and v != "null":
                    roots.append(v)
        elif section == "areas":
            m = re.match(r"^\s+path:\s*(\S+)", s)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v and v != "null":
                    roots.append(v)
    out = []
    for v in roots:
        p = os.path.abspath(os.path.join(root, v))
        if p == os.path.abspath(root):                # "." = cả workspace — không dùng làm code root
            continue
        if p not in out:
            out.append(p)
    return out

try:
    if os.environ.get("AI_DLC_GUARD", "").lower() == "off":
        allow()
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input") or {}
    fp = tool_input.get("file_path") or ""
    if not fp:
        allow()
    root = find_root(data.get("cwd") or os.getcwd())
    if not root:
        allow()
    aidlc = os.path.join(root, ".ai-dlc")
    fp_abs = os.path.abspath(fp)
    aidlc_abs = os.path.abspath(aidlc)
    gov = os.path.join(aidlc_abs, "context-memory", "governance")

    code_roots = code_roots_from_map(os.path.join(aidlc, "workspace-map.md"), root)

    # Trạng thái intents
    intents_dir = os.path.join(aidlc, "context-memory", "intents")
    active = []       # intents đang mở (stage < 8)
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

    # Rule 1: sửa governance (dor/dod) — cho qua, DEC do skill ghi trong cùng lượt
    if fp_abs.startswith(gov) and os.path.basename(fp_abs) in ("dor.md", "dod.md"):
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
