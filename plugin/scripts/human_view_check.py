#!/usr/bin/env python3
"""human_view_check.py — bản mô hình cho người xem KHÔNG được lệch bản chữ (protocol §2.4), stdlib.

Người quyết trên hình; AI làm theo chữ. Hai bản lệch nhau = người duyệt một thứ, AI làm thứ khác.
Bản chữ: intents/INT-NNN/<tài liệu gate>.md (agent chủ tài liệu viết).
Mô hình: intents/INT-NNN/views/<tài liệu gate>.view.json (dlc-modeler viết — người đọc độc lập).
Escalation đang mở: escalations/ESC-NNN.md ↔ escalations/views/ESC-NNN.view.json (đúng MỘT điểm cần chốt).
Chỉ ĐỌC. Thoát 1 khi có FIX.

  python3 human_view_check.py [<thư mục dự án>] [--json]
  python3 human_view_check.py --doc <tài liệu gate.md> --view <file.view.json> [--json]

Mã phát hiện:
  HV01 FIX   view không phải JSON hợp lệ
  HV08 FIX   MÔ HÌNH CŨ — bản chữ đã đổi sau khi vẽ (sha256 lệch): người đang quyết trên hình cũ
  HV09 WARN  modeler ghi `gaps` — bản chữ chưa đủ rõ để quyết (đây là phát hiện, không phải lỗi của view)
  HV02 FIX   mã trong mô hình không có trong bản chữ (UOW · O · D) hoặc trỏ chéo sai
  HV03 FIX   bản chữ có phần việc mà mô hình không vẽ — người thấy ít hơn cái AI sẽ làm
  HV04 WARN  tài liệu gate (A, D) chưa có view — người phải đọc toàn văn
  HV05 FIX   điểm cần chốt thiếu phương án/mặc định/đề xuất/người trả lời; `reversal`, `risk` sai giá trị
  HV06 WARN  mô hình cũng quá dài: > 7 điểm cần chốt · chuỗi > 160 ký tự · ô vượt trần
             (target/now ≤ 60 · short ≤ 70 · question ≤ 120 · tên phương án ≤ 60) — hình không cắt chữ
             nhưng cao thêm; hình mà như chữ thì người lại phải đọc
  HV07 FIX   phương án MẶC ĐỊNH là phương án đảo đắt, hoặc đảo "chưa rõ" ở câu rủi ro cao —
             không được tự áp khi im lặng (block #1): để `default: null` + `needs`
  HV10 FIX   `units[].condition` và `decisions[].blocks` không khớp hai chiều
  HV11 FIX   view của escalation không có đúng một điểm cần chốt

Giá đảo thuộc về TỪNG PHƯƠNG ÁN: `options[].reversal` (rẻ|đắt|chưa rõ, thiếu = rẻ). Rủi ro là chuyện khác:
`decisions[].risk` (cao|vừa|thấp). Một câu có thể đảo rẻ mà rủi ro cao — tower đưa nó lên đầu, không chặn.
"""
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import resolve  # noqa: E402

GATE_DOCS = {"A": "intent-plan.md", "D": "unit-plan.md"}
MAX_DECISIONS = 7
MAX_CHARS = 160


def view_path(doc_path):
    d, name = os.path.split(doc_path)
    return os.path.join(d, "views", os.path.splitext(name)[0] + ".view.json")


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, "%s[%d]" % (path, i))


def check_doc(text, view_text, where, single_decision=False):
    """text: bản chữ · view_text: nội dung file view (None = chưa có view).
    single_decision: view của escalation — phải có đúng một điểm cần chốt."""
    findings = []

    def add(level, code, msg):
        findings.append({"level": level, "code": code, "where": where, "msg": msg})

    if view_text is None:
        add("WARN", "HV04", "chưa có view — người duyệt phải đọc toàn văn (%d dòng)" % text.count("\n"))
        return findings
    try:
        model = json.loads(view_text)
        if not isinstance(model, dict):
            raise ValueError("view phải là một object JSON")
    except ValueError as e:
        add("FIX", "HV01", "view không đọc được: %s" % e)
        return findings
    prose = text
    want = model.get("source_sha256")
    if want != sha256(text):
        add("FIX", "HV08", "MÔ HÌNH CŨ: bản chữ đã đổi sau khi vẽ (view ghi source_version %s) — vẽ lại trước khi quyết"
            % model.get("source_version"))
    gaps = []
    for g in model.get("gaps") or []:                       # v2: chuỗi · v3: {text, ref, decision}
        if isinstance(g, str) and g.strip():
            gaps.append({"text": g})
        elif isinstance(g, dict) and str(g.get("text") or "").strip():
            gaps.append(g)
    if gaps:
        add("WARN", "HV09", "%d chỗ bản chữ chưa đủ rõ để quyết — vd: %s" % (len(gaps), gaps[0]["text"][:120]))

    text_units = set(re.findall(r"^\|\s*(UOW-\d+)\s*\|", prose, re.M))
    text_outcomes = set(re.findall(r"\*\*(O\d+)\*\*", prose))
    units = [u for u in model.get("units") or [] if isinstance(u, dict)]
    outcomes = [o for o in model.get("outcomes") or [] if isinstance(o, dict)]
    decisions = [d for d in model.get("decisions") or [] if isinstance(d, dict)]
    unit_ids = [u.get("id") for u in units]
    out_ids = {o.get("id") for o in outcomes}
    dec_ids = {d.get("id") for d in decisions}

    for uid in unit_ids:
        if text_units and uid not in text_units:
            add("FIX", "HV02", "%s có trong mô hình nhưng không có trong bảng phần việc của bản chữ" % uid)
    for oid in sorted(x for x in out_ids if x):
        if text_outcomes and oid not in text_outcomes:
            add("FIX", "HV02", "%s có trong mô hình nhưng không có trong bản chữ" % oid)
    for u in units:
        rv = u.get("review")
        if rv not in (None, "") and not re.match(r"^(none|peer|specialist\([a-z-]+\))$", str(rv)):
            add("FIX", "HV05", "%s.review phải là none | peer | specialist(<vai>), đang là %r" % (u.get("id"), rv))
        for o in u.get("serves") or []:
            if o not in out_ids:
                add("FIX", "HV02", "%s.serves trỏ %s — không có outcome đó trong mô hình" % (u.get("id"), o))
        cond = u.get("condition")
        if isinstance(cond, dict) and cond.get("decision") not in dec_ids:
            add("FIX", "HV02", "%s.condition trỏ %s — không có điểm cần chốt đó" % (u.get("id"), cond.get("decision")))
    for d in decisions:
        for b in d.get("blocks") or []:
            if b not in unit_ids:
                add("FIX", "HV02", "%s.blocks trỏ %s — không có phần việc đó trong mô hình" % (d.get("id"), b))

    text_sources = set(re.findall(r"^\|\s*(S-?\d+)\s*\|", prose, re.M))
    links = [("gaps", g.get("decision")) for g in gaps]
    links += [("risks", r.get("decision")) for r in model.get("risks") or [] if isinstance(r, dict)]
    links += [("scope.later", x.get("decision")) for x in (model.get("scope") or {}).get("later") or [] if isinstance(x, dict)]
    for where_, did in links:
        if did not in (None, "", "-") and did not in dec_ids:
            add("FIX", "HV02", "%s trỏ %s — không có điểm cần chốt đó" % (where_, did))
    for d in decisions:
        for sid in d.get("sources") or []:
            if text_sources and sid not in text_sources:
                add("FIX", "HV02", "%s.sources trỏ %s — không có nguồn đó trong bảng nguồn của bản chữ" % (d.get("id"), sid))

    for uid in sorted(text_units - set(unit_ids)):
        add("FIX", "HV03", "%s có trong bản chữ mà mô hình không vẽ — người thấy ít hơn cái AI sẽ làm" % uid)

    for d in decisions:
        did = d.get("id", "?")
        opts = [o for o in d.get("options") or [] if isinstance(o, dict)]
        keys = [o.get("key") for o in opts]
        if len(keys) < 2:
            add("FIX", "HV05", "%s có %d phương án — cần ít nhất 2 để là một lựa chọn" % (did, len(keys)))
        rec = d.get("recommended")
        if rec in (None, "", "-"):
            # bản chữ không có khuyến nghị thì modeler KHÔNG được bịa — nhưng phải nói ra bằng một dòng gaps
            if not any(g.get("decision") == did or did in g["text"] or "khuyến nghị" in g["text"] for g in gaps):
                add("FIX", "HV05", "%s không có đề xuất mà `gaps` không ghi bản chữ thiếu khuyến nghị" % did)
        elif rec not in keys:
            add("FIX", "HV05", "%s: đề xuất của AI '%s' không nằm trong các phương án" % (did, rec))
        for o in opts:
            if o.get("reversal", "rẻ") not in ("rẻ", "đắt", "chưa rõ"):
                add("FIX", "HV05", "%s.%s: reversal phải là rẻ|đắt|chưa rõ, đang là %r" % (did, o.get("key"), o.get("reversal")))
        if d.get("risk", "thấp") not in ("cao", "vừa", "thấp"):
            add("FIX", "HV05", "%s: risk phải là cao|vừa|thấp, đang là %r" % (did, d.get("risk")))
        dflt = d.get("default")
        if dflt in (None, "", "-"):
            if not d.get("needs"):
                add("FIX", "HV05", "%s không có mặc định mà cũng không ghi `needs` (cần người làm rõ gì)" % did)
        elif dflt not in keys:
            add("FIX", "HV05", "%s: mặc định khi im lặng '%s' không nằm trong các phương án" % (did, dflt))
        elif any(o.get("key") == dflt and o.get("reversal") == "đắt" for o in opts):
            add("FIX", "HV07", "%s: mặc định '%s' là phương án đảo đắt — phải chờ người, không tự áp" % (did, dflt))
        elif d.get("risk") == "cao" and any(o.get("key") == dflt and o.get("reversal") == "chưa rõ" for o in opts):
            add("FIX", "HV07", "%s: rủi ro cao mà giá đảo của mặc định '%s' chưa rõ — phải chờ người" % (did, dflt))
        for t_ in d.get("touches") or []:
            if t_ not in unit_ids:
                add("FIX", "HV02", "%s.touches trỏ %s — không có phần việc đó trong mô hình" % (did, t_))
        for u in d.get("unlocks") or []:
            if u == did:
                add("FIX", "HV02", "%s.unlocks trỏ chính nó" % did)
        if not d.get("who"):
            add("FIX", "HV05", "%s thiếu người trả lời" % did)

    for u in units:
        cond = u.get("condition")
        if isinstance(cond, dict):
            d = next((x for x in decisions if x.get("id") == cond.get("decision")), None)
            if d is not None and u.get("id") not in (d.get("blocks") or []):
                add("FIX", "HV10", "%s chờ %s nhưng %s.blocks không ghi %s" % (u.get("id"), d.get("id"), d.get("id"), u.get("id")))
    for d in decisions:
        for b in d.get("blocks") or []:
            u = next((x for x in units if x.get("id") == b), None)
            if u is not None and not (isinstance(u.get("condition"), dict) and u["condition"].get("decision") == d.get("id")):
                add("FIX", "HV10", "%s.blocks ghi %s nhưng %s không có condition trỏ %s" % (d.get("id"), b, b, d.get("id")))

    limits = []
    for o in outcomes:
        limits += [("%s.target" % o.get("id"), o.get("target"), 60), ("%s.now" % o.get("id"), o.get("now"), 60)]
    for u in units:
        limits.append(("%s.short" % u.get("id"), u.get("short"), 70))
    for d in decisions:
        limits.append(("%s.question" % d.get("id"), d.get("question"), 120))
        for o in d.get("options") or []:
            if isinstance(o, dict):
                limits.append(("%s.%s.name" % (d.get("id"), o.get("key")), o.get("name"), 60))
    over = [(k, len(v), n) for k, v, n in limits if isinstance(v, str) and len(v) > n]
    if over:
        add("WARN", "HV06", "%d ô vượt trần — hình sẽ cao thêm: %s" % (
            len(over), ", ".join("%s %d>%d" % x for x in over[:4])))

    if single_decision and len(decisions) != 1:
        add("FIX", "HV11", "escalation phải có đúng một điểm cần chốt, view có %d" % len(decisions))

    if len(decisions) > MAX_DECISIONS:
        add("WARN", "HV06", "%d điểm cần chốt trên hình (> %d) — đẩy bớt xuống decisions_minor" % (len(decisions), MAX_DECISIONS))
    long = [(p, len(s)) for p, s in _strings(model)                      # gaps là lời giải thích, được dài
            if len(s) > MAX_CHARS and not p.startswith("gaps")]
    if long:
        add("WARN", "HV06", "%d chuỗi dài hơn %d ký tự (vd %s: %d) — hình mà như chữ" % (
            len(long), MAX_CHARS, long[0][0], long[0][1]))
    return findings


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def check_project(project_dir):
    lay = resolve(project_dir)
    cm = lay.get("context_memory")
    findings = []
    if lay.get("engine") != "ai-dlc" or not cm:
        return findings
    for idir in sorted(glob.glob(os.path.join(cm, "intents", "INT-*"))):
        for gate, rel in sorted(GATE_DOCS.items()):
            p = os.path.join(idir, rel)
            text = _read(p)
            if text is not None:
                findings += check_doc(text, _read(view_path(p)), "%s/%s" % (os.path.basename(idir), rel))
    for p in sorted(glob.glob(os.path.join(cm, "escalations", "ESC-*.md"))):
        text = _read(p) or ""
        m = re.search(r"^status:\s*([A-Za-z-]+)", text, re.M)
        if m and m.group(1) in ("claimed", "done", "wontfix"):
            continue                                        # đã có chủ hoặc đã đóng — không ai còn phải quyết
        findings += check_doc(text, _read(view_path(p)), "escalations/" + os.path.basename(p), single_decision=True)
    return findings


def main(argv):
    if "--doc" in argv:
        doc = argv[argv.index("--doc") + 1]
        view = argv[argv.index("--view") + 1] if "--view" in argv else view_path(doc)
        findings = check_doc(_read(doc) or "", _read(view), os.path.basename(doc))
    else:
        args = [a for a in argv if not a.startswith("--")]
        findings = check_project(args[0] if args else os.getcwd())
    if "--json" in argv:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=1))
    else:
        for f in findings:
            print("%-4s %s  %s — %s" % (f["level"], f["code"], f["where"], f["msg"]))
        if not findings:
            print("human-view: OK — không có phát hiện")
    return 1 if any(f["level"] == "FIX" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
