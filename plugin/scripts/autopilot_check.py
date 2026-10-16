#!/usr/bin/env python3
"""autopilot_check.py — kiểm luật autopilot (protocol §2.3) bằng máy, stdlib.

Luật không kiểm được là luật sẽ trượt: `dlc-doctor` mục 3b gọi script này thay vì đọc bằng mắt.
Chỉ ĐỌC. Thoát 1 khi có FIX, 0 khi sạch hoặc chỉ WARN.

  python3 autopilot_check.py [<thư mục dự án>] [--json]

Mã phát hiện:
  AP01 FIX   DEC autopilot thiếu dòng bắt buộc (Chọn · Bỏ · Đảo bằng · Hiện ở · Block check)
  AP02 FIX   "Hiện ở" trỏ file không tồn tại trong intent
  AP03 FIX   Block check không đủ #1–#6, hoặc có `hit` mà vẫn tự quyết
  AP04 FIX   gate nằm trong gates_auto nhưng không có DEC autopilot nào cho gate đó
  AP05 FIX   BỎ BƯỚC — gate đã tự đóng mà artefact của stage thiếu hoặc rỗng
  AP06 FIX   TỰ QUYẾT QUA BLOCK — dấu vết nói có block mà gate vẫn tự đóng
  AP07 FIX   inbox còn steer-*.json chưa xử lý (người đã Đảo mà AI vẫn chạy hướng cũ)
  AP08 WARN  gate đang block quá 24h
  AP09 WARN  tỷ lệ đảo ngoài 10–30% (khi đã có ≥ 10 DEC autopilot)
  AP10 WARN  mode autopilot mà gate mở không có blocked_by/wait_until (dừng không lý do)
  AP11 WARN  có DEC autopilot trong khi mode là lead / không có autopilot.md
  AP12 FIX   DEC autopilot đã quyết một escalation mà file ESC vẫn `status: open` / chưa có `owner`
  AP13 FIX   DEC autopilot thiếu dòng `Áp` (mã = phương án từng mặc định đã áp; không áp gì thì `không có`)
  AP14 FIX   hai DEC autopilot áp hai phương án khác nhau cho cùng một mã mà DEC sau không ghi `(thay DEC-NNNN)`
"""
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import resolve  # noqa: E402

REQUIRED = ["Chọn", "Bỏ", "Đảo bằng", "Hiện ở", "Block check"]
APPLY_RE = re.compile(r"\b((?:OQB|OQT|ESC|D|T)-?\d+)\s*(?:=|:|→)\s*([A-Z])\b(?:\s*\(\s*thay\s+(DEC-\d+)\s*\))?")
# artefact tối thiểu mỗi gate phải có TRƯỚC khi được tự đóng (tương đối thư mục intent)
GATE_ARTEFACTS = {
    "A": ["intent-plan.md"],
    "B": ["as-is/source-ledger.md"],
    "C": ["open-questions-business.md"],
    "D": ["unit-plan.md"],
    "F": ["acceptance.md"],
}
MIN_BYTES = 200          # file ngắn hơn thế này coi như rỗng (chỉ có frontmatter)
HEAD_RE = re.compile(r"^## (DEC-\d+)\s*·\s*([^·\n]+?)\s*·\s*([^·\n]+?)\s*·\s*(INT-\d+)(?:\s*·\s*(\S+))?\s*$", re.M)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith('"'):                       # chuỗi có nháy: giữ nguyên tới nháy đóng
            mm = re.match(r'"((?:[^"\\]|\\.)*)"', v)
            v = mm.group(1) if mm else v.strip('"')
        else:
            v = re.sub(r"\s+#.*$", "", v).strip()
        out[k.strip()] = v
    return out


def as_list(v):
    v = (v or "").strip()
    if v in ("", "[]", "null", "-"):
        return []
    return [x.strip() for x in v.strip("[]").split(",") if x.strip()]


def parse_decs(text):
    """Trả list dict: id, gate, intent, by_autopilot, fields{}, body."""
    out = []
    heads = list(HEAD_RE.finditer(text))
    for i, h in enumerate(heads):
        body = text[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        gate = re.sub(r"(?i)^gate\s+", "", h.group(3).strip())
        fields = {}
        # một dòng có thể chứa nhiều "- Khoá: giá trị" cách nhau bởi ≥ 2 khoảng trắng
        for seg in re.split(r"\n|\s{2,}(?=- )", body):
            m = re.match(r"\s*-\s*([^:]+?):\s*(.*)$", seg.strip())
            if m:
                fields.setdefault(m.group(1).strip(), []).append(m.group(2).strip())
        who = " ".join(fields.get("Người quyết", []))
        out.append({
            "id": h.group(1), "gate": gate, "intent": h.group(4),
            "autopilot": (h.group(5) or "").lower() == "autopilot" or who.lower().startswith("autopilot"),
            "fields": fields,
        })
    return out


def table_rows(text, must_have):
    """Hàng của bảng markdown đầu tiên có đủ các cột `must_have` → list dict theo tên cột."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if not all(any(m.lower() == c.lower() for c in cols) for m in must_have):
            continue
        rows = []
        for r in lines[i + 2:]:
            if not r.strip().startswith("|"):
                break
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            rows.append(dict(zip(cols, cells)))
        return rows
    return []


def check(project_dir):
    lay = resolve(project_dir)
    findings, info = [], {"engine": lay.get("engine"), "mode": "off"}

    def add(level, code, where, msg):
        findings.append({"level": level, "code": code, "where": where, "msg": msg})

    cm = lay.get("context_memory")
    if lay.get("engine") != "ai-dlc" or not cm or not os.path.isdir(cm):
        info["note"] = "không phải engine ai-dlc — autopilot_check chỉ kiểm state .ai-dlc/"
        return info, findings

    gov = lay.get("governance") or os.path.join(cm, "governance")
    ap = frontmatter(read(os.path.join(gov, "autopilot.md")))
    mode = (ap.get("mode") or "lead").lower()
    info["mode"] = mode
    decs = parse_decs(read(os.path.join(gov, "decisions-log.md")))
    auto = [d for d in decs if d["autopilot"]]
    info["decisions"] = len(auto)
    info["reversed"] = sum(1 for d in decs if d["fields"].get("reverses"))

    if mode != "autopilot":
        if auto:
            add("WARN", "AP11", "governance/decisions-log.md",
                "%d DEC autopilot trong khi mode là '%s' — ai đã tự quyết?" % (len(auto), mode))
        return info, findings

    intents = sorted(glob.glob(os.path.join(cm, "intents", "INT-*")))
    for d in auto:
        idir = os.path.join(cm, "intents", d["intent"])
        f = d["fields"]
        missing = [k for k in REQUIRED if not any(v for v in f.get(k, []))]
        if missing:
            add("FIX", "AP01", d["id"], "thiếu dòng: " + " · ".join(missing) +
                " — quyết định không đảo được là quyết định không được tự ra")
        for shown in f.get("Hiện ở", []):
            path = shown.split("#", 1)[0].strip().strip("`")
            if path and not os.path.exists(os.path.join(idir, path)):
                add("FIX", "AP02", d["id"], "'Hiện ở' trỏ %s — không có trong %s" % (path, d["intent"]))
        bc = " ".join(f.get("Block check", []))
        if bc:
            seen = set(re.findall(r"#([1-6])", bc))
            if len(seen) < 6:
                add("FIX", "AP03", d["id"], "Block check chỉ ghi %d/6 điều kiện" % len(seen))
            if re.search(r"\bhit\b", bc, re.I):
                add("FIX", "AP03", d["id"], "Block check có 'hit' mà vẫn tự quyết: " + bc)

    for idir in intents:
        iid = os.path.basename(idir)
        st_path = os.path.join(idir, "status.md")
        st = frontmatter(read(st_path))
        gates_auto = as_list(st.get("gates_auto"))
        for g in gates_auto:
            if not any(d["intent"] == iid and d["gate"].upper().startswith(g.upper()) for d in auto):
                add("FIX", "AP04", "%s gate %s" % (iid, g), "nằm trong gates_auto nhưng không có DEC autopilot")
            for rel in GATE_ARTEFACTS.get(g.upper(), []):
                p = os.path.join(idir, rel)
                if not os.path.isfile(p):
                    add("FIX", "AP05", "%s gate %s" % (iid, g),
                        "BỎ BƯỚC: thiếu %s — ghi khoảng trống vào LL, không dựng bù" % rel)
                elif os.path.getsize(p) < MIN_BYTES:
                    add("FIX", "AP05", "%s gate %s" % (iid, g), "BỎ BƯỚC: %s gần như rỗng" % rel)
        if "D" in [g.upper() for g in gates_auto]:
            units = [u for u in glob.glob(os.path.join(idir, "units", "UOW-*")) if os.path.isdir(u)]
            for u in units:
                for need in ("spec.md", "user-stories.md", "nfr.md", "risks.md"):
                    if not os.path.isfile(os.path.join(u, need)):
                        add("FIX", "AP05", "%s/%s" % (iid, os.path.basename(u)), "BỎ BƯỚC: thiếu " + need)
            if not units:
                add("FIX", "AP05", iid + " gate D", "BỎ BƯỚC: Gate D tự đóng mà không có Unit nào")
            # tự quyết qua block #1: câu CHẶN còn mở mà không có mặc định
            for qf in ("open-questions-business.md", "open-questions-tech.md"):
                for r in table_rows(read(os.path.join(idir, qf)), ["Mã", "Ảnh hưởng", "Trạng thái"]):
                    if "CHẶN" in r.get("Ảnh hưởng", "").upper() and r.get("Trạng thái", "").lower() == "open":
                        dflt = r.get("Nếu im lặng", "").strip()
                        if dflt in ("", "-", "—", "TBD"):
                            add("FIX", "AP06", "%s %s" % (iid, r.get("Mã", "?")),
                                "TỰ QUYẾT QUA BLOCK #1: câu CHẶN còn mở, không có mặc định, mà Gate D đã tự đóng")
        if any(g.upper() in ("B", "D") for g in gates_auto):
            # bảng NGUỒN (có cột "Nguồn"), không phải bảng tổng hợp đếm trạng thái (`| planned | 0 |`)
            for r in table_rows(read(os.path.join(idir, "as-is", "source-ledger.md")), ["Nguồn", "Trạng thái"]):
                if re.search(r"\bplanned\b|⬜", r.get("Trạng thái", ""), re.I):
                    add("FIX", "AP06", "%s ledger %s" % (iid, r.get("#", r.get("Nguồn", "?"))),
                        "TỰ QUYẾT QUA BLOCK #3: nguồn còn 'planned' mà gate đã tự đóng")
        gate_open = (st.get("gate_open") or "null").strip()
        if gate_open not in ("null", "", "-"):
            if st.get("blocked_by", "null") not in ("null", "", "-"):
                age_h = (time.time() - os.path.getmtime(st_path)) / 3600.0
                if age_h > 24:
                    add("WARN", "AP08", "%s gate %s" % (iid, gate_open),
                        "block %.0f giờ chưa ai trả lời: %s" % (age_h, st.get("blocked_by")))
            elif not st.get("wait_until"):
                add("WARN", "AP10", "%s gate %s" % (iid, gate_open),
                    "gate mở mà không có blocked_by/wait_until — autopilot dừng không lý do")

    # AP13 / AP14 — mặc định đã áp phải đọc được bằng máy, và không được tự mâu thuẫn
    applied = {}                                            # (intent, mã) → [(DEC, phương án, thay DEC nào)]
    for d in auto:
        lines = d["fields"].get("Áp")
        if not lines or not any(x.strip() for x in lines):
            add("FIX", "AP13", d["id"], "thiếu dòng `Áp` — ghi từng mặc định đã áp dạng `OQB-01 = A`, không áp gì thì `không có`")
            continue
        for code, opt, repl in APPLY_RE.findall(" ".join(lines)):
            applied.setdefault((d["intent"], code), []).append((d["id"], opt, repl))
    for (iid, code), picks in sorted(applied.items()):
        replaced = {repl for _, _, repl in picks if repl}                 # DEC đã bị một DEC sau ghi `thay`
        live = [(dec, opt) for dec, opt, _ in picks if dec not in replaced]
        if len({opt for _, opt in live}) > 1:
            add("FIX", "AP14", "%s %s" % (iid, code),
                "%s — DEC sau phải ghi `%s = <phương án> (thay DEC-NNNN)` hoặc sửa cho khớp" % (
                    " ≠ ".join("%s áp %s" % x for x in live), code))

    # AP12 — quyết bằng DEC mà không đổi file ESC: tower vẫn báo "đang đứng — cần bạn" cho việc đã xong
    for d in auto:
        refs = " ".join(sum((d["fields"].get(k, []) for k in ("Quyết định", "Căn cứ", "Hiện ở")), []))
        for esc in sorted(set(re.findall(r"ESC-\d+", refs))):
            fm = frontmatter(read(os.path.join(cm, "escalations", esc + ".md")))
            if not fm:
                continue
            if (fm.get("status") or "open") == "open" or not (fm.get("owner") or "").strip():
                add("FIX", "AP12", "%s → %s" % (d["id"], esc),
                    "đã quyết bằng DEC nhưng %s vẫn status=%s, owner=%r — đổi trạng thái + ghi mục Chỉ đạo" % (
                        esc, fm.get("status") or "open", fm.get("owner") or ""))

    inbox = lay.get("inbox") or ""
    for p in sorted(glob.glob(os.path.join(inbox, "steer-*.json"))):
        add("FIX", "AP07", os.path.basename(p), "người đã Đảo — xử lý trước mọi thứ (protocol §2.3.6)")

    if len(auto) >= 10:
        rate = info["reversed"] / float(len(auto))
        if rate < 0.10:
            add("WARN", "AP09", "KPI", "tỷ lệ đảo %.0f%% < 10%% — có thể không ai nhìn" % (rate * 100))
        elif rate > 0.30:
            add("WARN", "AP09", "KPI", "tỷ lệ đảo %.0f%% > 30%% — giả định của AI kém, cân nhắc wait_hours" % (rate * 100))
    return info, findings


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    info, findings = check(args[0] if args else os.getcwd())
    fixes = [f for f in findings if f["level"] == "FIX"]
    if "--json" in argv:
        print(json.dumps({"info": info, "findings": findings}, ensure_ascii=False, indent=1))
    else:
        print("autopilot: mode=%s · DEC tự quyết=%s · đã đảo=%s" % (
            info.get("mode"), info.get("decisions", 0), info.get("reversed", 0)))
        if info.get("note"):
            print("  (" + info["note"] + ")")
        for f in findings:
            print("  %-4s %s  %s — %s" % (f["level"], f["code"], f["where"], f["msg"]))
        if not findings and info.get("mode") == "autopilot":
            print("  OK — không có phát hiện")
    return 1 if fixes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
