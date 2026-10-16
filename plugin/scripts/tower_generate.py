#!/usr/bin/env python3
"""AI-DLC Control Tower generator (v3 — gate doc preview + dòng chảy 3 pha).

Usage: python3 tower_generate.py [project_root]

`import tower_generate` KHÔNG chạy gì (6.5.0): mọi việc đọc state và ghi file nằm trong `main()`. Muốn thử một
parser: hàm nhận `base`/`text` (fm · md_tables · parse_questions · parse_question_details · parse_sources…) gọi được
ngay; hàm cần biết gốc dự án (parse_units · load_doc…) thì gọi `use_project(<gốc>)` trước — nó chỉ gán đường dẫn.

1) Copy runtime UI (React ui-kit của Control Tower Design System, đã flatten trong
   plugin/tower-ui/) vào <root>/.ai-dlc/tower/
2) Sinh <root>/.ai-dlc/tower/data.js (window.CT_DATA) từ state .ai-dlc/ thật.

Mới ở v3 (theo protocol v2):
- Mỗi gate mang theo `doc`: TOÀN VĂN markdown của gate_doc (intent-plan.md, source-ledger.md,
  open-questions-business.md, unit-plan.md…) để tower render preview — approve mù bị chặn.
- `sourcesByIntent`: coverage nguồn đọc từ Source Reading Plan + source-ledger.
- `flowByIntent`: Inception · Construction · Operations, mỗi Unit là một mạch chạy xuyên suốt.
- Unit mang estimate_hours, số US/NFR/risk, nguồn — đủ để UI bắt lỗi >5h hoặc thiếu khối.

Mở tĩnh (file://) xem được (cần internet cho React CDN); nút Approve/Reject cần
tower_serve.py. Regenerate sau mỗi sự kiện — data.js là phần duy nhất đổi.
"""
import datetime
import glob as globmod
import hashlib
import json
import os
import re
import shutil
import sys

def _layout(start):
    """7.0.0: scripts/layout.py là nơi duy nhất trả lời state ở đâu (config file · fence CLAUDE.md · env · tự dò)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from layout import resolve
    return resolve(start)


def resolve_root(start):
    """(giữ làm fallback khi layout.py lỗi) Tìm gốc dự án AI-DLC thật. TRƯỚC 4.0.0 script nhận bừa cwd làm gốc và tạo `.ai-dlc/tower/`
    ở bất cứ đâu — chạy nhầm từ `app-fe/` hay từ trong `.ai-dlc/context-memory/` là đẻ ra một
    thư mục `.ai-dlc` rác với dashboard rỗng, trông y như một dự án thật. Nay:
      1. đường dẫn nằm TRONG một cây `.ai-dlc` → nhảy ngược ra gốc của cây đó;
      2. không có `.ai-dlc/context-memory` → đi lên cha tìm; tìm không ra thì DỪNG, không tạo gì.
    """
    p = os.path.abspath(start)
    parts = p.split(os.sep)
    if ".ai-dlc" in parts:                                  # (1) đang đứng bên trong .ai-dlc/
        p = os.sep.join(parts[:parts.index(".ai-dlc")]) or os.sep
    cur = p
    while True:                                             # (2) đi lên tìm gốc thật
        if os.path.isdir(os.path.join(cur, ".ai-dlc", "context-memory")):
            return cur, p
        nxt = os.path.dirname(cur)
        if nxt == cur:
            return None, p
        cur = nxt

MAX_DOC_BYTES = 400_000  # trần an toàn cho một tài liệu nhúng vào data.js

STAGE_HOLDER = {1: "intent-analyst", 2: "context-archaeologist", 3: "context-validator",
                4: "context-validator", 5: "unit-planner", 6: "bolt-coordinator",
                7: "acceptance-recorder", 8: "acceptance-recorder"}
BROWNFIELD = {"add-feature": "Add feature", "optimize-nfr": "Optimize NFR",
              "tech-debt": "Technical debt", "fix-defect": "Fix defect", "green-field": "Green-field"}
GATE_TITLE = {"A": "Duyệt Intent Plan — outcome · nguồn sẽ đọc · phân rã Unit",
              "B": "Xác nhận AS-IS + coverage nguồn (Validation Mob)",
              "C": "Chốt câu hỏi NGHIỆP VỤ (file business — câu kỹ thuật đi lối khác)", "D": "Approve Unit Plan + Bolt plan + DoD/DoR",
              "E": "Checkpoint trong Bolt", "F": "UAT / approve deploy", "G": "Duyệt lesson + patch"}
# gate_doc mặc định khi status.md chưa khai báo (intent tạo bằng plugin 1.x)
GATE_DOC_DEFAULT = {"A": "intent-plan.md", "B": "as-is/source-ledger.md",
                    "C": "open-questions-business.md", "D": "unit-plan.md"}
# fallback khi intent cũ (≤2.2) còn dùng một file gộp
GATE_DOC_LEGACY = {"C": "open-questions.md"}
PHASE_OF_STAGE = {1: "inception", 2: "inception", 3: "inception", 4: "inception", 5: "inception",
                  6: "construction", 7: "operations", 8: "operations"}


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


LEVEL_WORDS = (("cao", r"^(cao|high|critical|nghiêm\s*trọng|h)$"),
               ("vừa", r"^(vừa|vua|trung\s*bình|medium|med|moderate|m)$"),
               ("thấp", r"^(thấp|thap|low|minor|l)$"))


def norm_level(v):
    """Template Unit và ESC ghi `high/medium/low`, sổ rủi ro và view ghi `cao/vừa/thấp` — cùng một thang.
    Tower NHẬN cả hai, HIỂN THỊ một bộ: cao · vừa · thấp (phát hiện #35). Không nhận ra thì trả nguyên văn."""
    t = re.sub(r"[`*\"']", "", str(v or "")).strip().lower()
    for word, pat in LEVEL_WORDS:
        if re.match(pat, t):
            return word
    return t


def fm(text):
    """Frontmatter → dict. Cắt chú thích cuối dòng kiểu YAML (` # …`) trên giá trị KHÔNG nằm trong
    dấu nháy — người viết state hay ghi `gate_open: null  # A đã đóng bằng DEC-0031`, và nếu giữ
    nguyên cả dòng thì tower đọc thành "có gate tên là 'null # A đã đóng…' đang mở": một gate ma,
    kèm nhãn dài 300px làm vỡ cả sidebar. Giá trị trong nháy giữ nguyên (`note: "… # …"`)."""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if not mm:
                continue
            v = mm.group(2).strip()
            if v[:1] not in ('"', "'"):
                v = re.sub(r"\s+#.*$", "", v).strip()
            d[mm.group(1)] = v
    return d


def num(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def mtime_hm(p):
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H:%M")
    except OSError:
        return ""


def section(text, header):
    """Nội dung sau '**header:**' tới dòng trống kế hoặc '**' kế."""
    m = re.search(r"\*\*" + re.escape(header) + r":?\*\*\s*(.*?)(?=\n\s*\n|\n\*\*|\Z)", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def md_section(text, pattern):
    """Trả nội dung một mục markdown theo regex tiêu đề (## / ###)."""
    m = re.search(r"^#{2,3}\s*" + pattern + r".*?$\n(.*?)(?=^#{2,3}\s|\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def table_rows(block):
    """Parse bảng markdown → list các list ô (bỏ header + dòng ngăn)."""
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def load_doc(rel_path):
    """Đọc toàn văn một artifact trong intent → dict cho preview."""
    p = os.path.join(A, rel_path) if not os.path.isabs(rel_path) else rel_path
    if not os.path.isfile(p):
        return None
    raw = read(p)
    truncated = False
    if len(raw.encode("utf-8")) > MAX_DOC_BYTES:
        raw = raw.encode("utf-8")[:MAX_DOC_BYTES].decode("utf-8", "ignore")
        truncated = True
    d = fm(raw)
    changelog = md_section(raw, r"Changelog")
    return {
        "path": os.path.relpath(p, A),
        "name": os.path.basename(p),
        "title": d.get("title", os.path.basename(p)),
        "version": d.get("version", ""),
        "type": d.get("type", ""),
        "updated": mtime_hm(p),
        "markdown": raw,
        "truncated": truncated,
        "changelog": [l.strip("- ").strip() for l in changelog.splitlines() if l.strip().startswith("-")][:6],
    }
metrics_by_intent = {}


def md_tables(text):
    """Mọi bảng markdown trong text → [(heading gần nhất phía trên, header cells, [row cells])].

    Không bám số mục: dự án viết `## 3. Nguồn code` hay `## 3. Mâu thuẫn` đều đọc được, vì
    ta phân loại bằng TÊN CỘT và TÊN TIÊU ĐỀ, không bằng vị trí.
    """
    out, heading, header, rows = [], "", None, []

    def flush():
        if header and rows:
            out.append((heading, header, list(rows)))

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            flush()
            header, rows = None, []
            heading = s.lstrip("#").strip()
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells if c != ""):
                continue                              # dòng ngăn
            if header is None:
                header = [re.sub(r"[*`]", "", c).strip().lower() for c in cells]
            else:
                rows.append(cells)
            continue
        if not s:                                     # dòng trống kết thúc bảng
            flush()
            header, rows = None, []
    flush()
    return out


def col_of(header, *patterns):
    """Vị trí cột đầu tiên khớp một trong các pattern tên cột. -1 nếu không có."""
    for i, h in enumerate(header):
        for p in patterns:
            if re.search(p, h):
                return i
    return -1


SRC_STATUS = [
    ("read", r"✅|\bread\b|đã\s*đọc|đọc\s*xong|\bdone\b|\bxong\b"),
    ("missing", r"❌|\bmissing\b|không\s*tồn\s*tại|không\s*tìm\s*thấy|không\s*truy\s*cập"),
    ("superseded", r"\bsuperseded\b|bị\s*thay\s*thế|thay\s*bằng"),
    ("deferred", r"\bdeferred\b|hoãn|để\s*sau"),
    ("planned", r"⬜|\bplanned\b|chưa\s*đọc|\bchưa\b|đang\s*chờ|\btodo\b"),
]


def norm_src_status(raw):
    """Chuẩn hoá ô trạng thái người viết tay → từ khoá máy đếm được.

    Trả về (status, added). `unknown` khi không nhận ra — KHÔNG đoán bừa thành 0/read,
    vì đếm sai âm thầm nguy hiểm hơn là nói thẳng 'không đọc được'.
    """
    t = re.sub(r"[`*]", "", raw or "").strip()
    added = bool(re.search(r"\[?ADDED\]?", t, re.I))
    low = t.lower()
    if not low:
        return "unknown", added
    for name, pat in SRC_STATUS:
        if re.search(pat, low):
            return name, added
    return "unknown", added


def parse_sources(base, intent_id):
    """Coverage nguồn — đọc MỌI bảng nguồn trong source-ledger (+ kế hoạch ở intent-plan).

    Nguyên tắc: nhận bảng bằng tên cột (`#`/`Nguồn`/`Trạng thái`), nhận mục mâu thuẫn bằng
    tên tiêu đề. Ô trạng thái viết tay được chuẩn hoá; ô không hiểu được đánh `unknown` và
    báo lên UI thay vì âm thầm tính là 0.
    """
    plan_p = os.path.join(base, "intent-plan.md")
    ledger_p = os.path.join(base, "as-is", "source-ledger.md")
    plan, ledger = read(plan_p), read(ledger_p)
    rows, by_id, used, warns = [], {}, [], []

    def take(text, origin, default_status):
        for heading, header, trs in md_tables(text):
            i_id = col_of(header, r"^#$", r"^id$", r"^stt$")
            i_src = col_of(header, r"nguồn", r"source", r"tài\s*liệu")
            if i_id < 0 or i_src < 0:
                continue
            i_st = col_of(header, r"trạng\s*thái", r"status")
            i_ev = col_of(header, r"evidence", r"vùng\s*đã\s*đọc", r"phát\s*hiện", r"trả\s*lời\s*được")
            i_un = col_of(header, r"^dùng\s*cho", r"unit")
            i_need = col_of(header, r"thông\s*tin", r"phải\s*lấy", r"vì\s*sao")
            i_prio = col_of(header, r"ưu\s*tiên", r"prio")
            n_taken = 0
            for c in trs:
                sid = re.sub(r"[*`~]", "", c[i_id] if i_id < len(c) else "").strip()
                if not re.match(r"^S\d+$", sid):
                    continue
                raw_st = c[i_st] if 0 <= i_st < len(c) else ""
                st, added = norm_src_status(raw_st) if i_st >= 0 else (default_status, False)
                if st == "unknown" and i_st >= 0:
                    # ô bị lệch (thường do dấu `|` nằm trong inline code) — dò ngược từ ô cuối
                    for c2 in reversed(c[i_st:]):
                        st2, added2 = norm_src_status(c2)
                        if st2 != "unknown":
                            st, added, raw_st = st2, added or added2, c2
                            break
                row = by_id.get(sid)
                if not row:
                    row = {"id": sid, "source": "", "kind": "", "need": "", "prio": "",
                           "units": "", "evidence": "", "status": default_status, "added": False,
                           "rawStatus": "", "from": origin}
                    rows.append(row)
                    by_id[sid] = row
                row["source"] = (c[i_src] if i_src < len(c) else row["source"])[:200]
                if i_st >= 0:
                    row["status"], row["rawStatus"] = st, raw_st.strip()[:60]
                    row["added"] = row["added"] or added
                    row["from"] = origin
                for key, idx, lim in (("evidence", i_ev, 220), ("units", i_un, 60),
                                      ("need", i_need, 160), ("prio", i_prio, 24)):
                    if 0 <= idx < len(c) and c[idx] and not row.get(key):
                        row[key] = c[idx][:lim]
                if st == "unknown" and i_st >= 0 and raw_st.strip():
                    warns.append("%s: trạng thái \"%s\" không hiểu được" % (sid, raw_st.strip()[:40]))
                n_taken += 1
            if n_taken:
                used.append({"file": origin, "section": heading or "(đầu file)", "rows": n_taken})

    take(plan, "intent-plan.md", "planned")
    take(ledger, "as-is/source-ledger.md", "read")

    # mâu thuẫn: bắt bằng TÊN mục, không bằng số mục — cộng thêm mọi dấu [CONFLICT] trong file
    conflicts = []
    for heading, header, trs in md_tables(ledger):
        if not re.search(r"mâu\s*thuẫn|conflict|xung\s*đột", heading or "", re.I):
            continue
        for c in trs:
            if not any(x for x in c):
                continue
            conflicts.append({"id": c[0][:20], "a": c[1][:120] if len(c) > 1 else "",
                              "b": c[2][:120] if len(c) > 2 else "", "status": c[-1][:60],
                              "from": "as-is/source-ledger.md · " + (heading or "")})
    # dấu [CONFLICT] rải trong sổ cái — bỏ mục Changelog (kể chuyện) và câu phủ định ("không có [CONFLICT]")
    body = re.split(r"^#{1,3}\s*changelog", ledger, flags=re.I | re.M)[0]
    # Một mâu thuẫn = một mã. Dấu [CONFLICT] nằm trên chính dòng bảng đã đếm, hoặc nhắc lại một mã đã có
    # trong bảng ("… [CONFLICT] xem C2"), là CÙNG mâu thuẫn đó — trước đây bị đếm thành hai.
    seen_ids = {re.sub(r"[*`~\s]", "", c["id"]) for c in conflicts if c["id"]}
    seen_lines = set()
    for m in list(re.finditer(r"\[CONFLICT\]", body))[:40]:
        before = re.sub(r"\s+", " ", body[max(0, m.start() - 70):m.start()])
        if re.search(r"không\s+(có|phải|gặp)\s*$|chưa\s+có\s*$", before, re.I):
            continue
        line = re.sub(r"\s+", " ", body[body.rfind("\n", 0, m.start()) + 1:
                                        (body.find("\n", m.end()) + 1 or len(body))]).strip()
        if line in seen_lines or any(re.search(r"(?<![\w-])" + re.escape(i) + r"(?![\w-])", line)
                                     for i in seen_ids if i):
            continue
        seen_lines.add(line)
        if len(seen_lines) > 10:
            break
        conflicts.append({"id": "[CONFLICT]", "a": line[:160], "b": "",
                          "status": "dấu trong sổ cái", "from": "as-is/source-ledger.md · dấu [CONFLICT]"})

    counts = {"planned": 0, "read": 0, "missing": 0, "deferred": 0, "superseded": 0,
              "unknown": 0, "added": 0}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        if r.get("added"):
            counts["added"] += 1
    counts["total"] = len(rows)
    counts["conflicts"] = len(conflicts)
    counts["ledger_exists"] = os.path.isfile(ledger_p)
    if not counts["ledger_exists"]:
        warns.append("chưa có as-is/source-ledger.md — không có gì để đếm")
    elif not rows:
        warns.append("đọc được sổ cái nhưng KHÔNG thấy bảng nguồn nào (cần cột `#` + `Nguồn`)")
    return {"counts": counts, "rows": rows[:80], "conflicts": conflicts[:20],
            "sources_used": used, "warnings": warns[:8],
            "blocking": counts.get("planned", 0) > 0}


def _plan_rows_by_line(txt):
    """Cách đọc cũ (≤6.4): mọi dòng `| UOW-NN |`, ô giờ là ô đầu tiên dạng `4.5h`. Giữ làm đường lùi cho
    unit-plan có bảng mà tiêu đề cột không nhận ra được — để dự án cũ không mất Unit sau khi nâng gói."""
    rows = {}
    for line in txt.splitlines():
        m = re.match(r"^\|\s*(UOW-\d+)\s*\|(.*)$", line.strip())
        if not m or m.group(1) in rows:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        est = 0.0
        for c in cells:
            mm = re.search(r"(\d+(?:[.,]\d+)?)\s*h\b", c)
            if mm:
                est = num(mm.group(1).replace(",", "."), 0.0)
                break
        rows[m.group(1)] = {"id": m.group(1),
                            "name": re.sub(r"\*", "", cells[0]).strip() if cells else m.group(1),
                            "est": est}
    return rows


def parse_plan_rows(base):
    """Unit đang được ĐỀ XUẤT trong unit-plan.md — đọc từ BẢNG UNIT, nhận bảng bằng tên cột (mã + tên + giờ),
    không bằng vị trí trong file (phát hiện #30).

    Unit-plan thật có bảng "Đã đổi gì so với provisional" đứng TRƯỚC bảng Unit và hàng của nó cũng mở đầu bằng
    mã UOW; lấy dòng đầu tiên chứa mã là lấy nhầm tên và giờ. Ô giờ nhận cả `4.0h` lẫn số trần `4.0` (đúng như
    template ghi). Không bảng nào nhận ra được ⇒ rơi về cách đọc cũ theo dòng."""
    txt = read(os.path.join(base, "unit-plan.md"))
    rows = {}
    for _heading, header, trs in md_tables(txt):
        i_id = col_of(header, r"^unit$", r"^uow$", r"^mã(?:\s*unit)?$", r"^id$")
        i_name = col_of(header, r"capability", r"^tên", r"năng\s*lực", r"^name", r"phần\s*việc")
        i_est = col_of(header, r"\best\b", r"\(h\)", r"^giờ", r"ước\s*lượng", r"estimate")
        if i_id < 0 or i_name < 0 or i_est < 0:
            continue
        for c in trs:
            uid = re.sub(r"[*`~]", "", c[i_id] if i_id < len(c) else "").strip()
            if not re.match(r"^UOW-\d+$", uid) or uid in rows:
                continue
            mm = re.search(r"(\d+(?:[.,]\d+)?)", re.sub(r"[*`~]", "", c[i_est] if i_est < len(c) else ""))
            rows[uid] = {"id": uid,
                         "name": re.sub(r"[*`]", "", c[i_name] if i_name < len(c) else uid).strip() or uid,
                         "est": num(mm.group(1).replace(",", "."), 0.0) if mm else 0.0}
    return rows or _plan_rows_by_line(txt)


def parse_descoped(base):
    """ID bị descope (units/DESCOPED.md) — giữ thư mục để truy vết nhưng KHÔNG tính vào gate."""
    d = fm(read(os.path.join(base, "units", "DESCOPED.md")))
    return {x.strip() for x in (d.get("units") or "").strip("[]").split(",") if x.strip()}


OQ_FILES = [("business", "open-questions-business.md", "Nghiệp vụ"),
            ("tech", "open-questions-tech.md", "Kỹ thuật"),
            ("legacy", "open-questions.md", "Chưa tách")]
OQ_COLS = {"mã": "code", "ma": "code", "câu hỏi": "q", "cau hoi": "q", "ai trả lời": "who",
           "ai tra loi": "who", "hạn": "due", "han": "due", "deadline": "due",
           "nếu im lặng": "fallback", "neu im lang": "fallback",
           "ảnh hưởng": "impact", "anh huong": "impact", "trạng thái": "status", "trang thai": "status",
           # bảng đã chốt: cột câu trả lời + người quyết thay cho cột trạng thái
           "chốt là gì": "answer", "chot la gi": "answer", "câu trả lời": "answer", "chốt": "answer",
           "ai quyết": "who", "ai quyet": "who", "việc phải làm": "todo", "viec phai lam": "todo"}


def oq_headers(block):
    """Map vị trí cột → tên trường, đọc từ dòng header của bảng điều phối."""
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [re.sub(r"[*`]", "", c).strip().lower() for c in s.strip("|").split("|")]
        hit = {i: OQ_COLS[c] for i, c in enumerate(cells) if c in OQ_COLS}
        if "q" in hit.values() or "code" in hit.values():
            return hit
        return {}
    return {}


def parse_questions(base):
    """Open questions tách theo đối tượng trả lời (protocol §4.10).

    Đọc bảng điều phối mục 0 theo TÊN CỘT (không theo vị trí) nên file thêm/bớt cột vẫn đọc được.
    File cũ gộp một bản (≤2.2) vẫn đọc được, gắn nhãn `legacy`.
    """
    out, seen, seen_rows = [], set(), set()
    for audience, fname, label in OQ_FILES:
        txt = read(os.path.join(base, fname))
        if not txt.strip():
            continue
        if audience == "legacy" and seen:
            continue                      # đã có bản tách → bỏ qua bản gộp cũ
        # chỉ đọc BẢNG ĐIỀU PHỐI (mục 0) — bảng phương án và bảng "Đã trả lời" không phải câu hỏi
        # Mục 0 kết thúc ở tiêu đề kế BẤT KỲ cấp nào (## hoặc ###) hoặc cuối file. Trước đây chỉ nhận `## `:
        # file đi thẳng từ bảng điều phối sang `### OQB-01` làm cả file bị coi là bảng, và dòng tiêu đề của
        # bảng "Chọn một" thành một câu hỏi ma tên "Phương án".
        m = re.search(r"^##+[^\n]*(?:Bảng điều phối|Bang dieu phoi)[^\n]*$(.*?)(?=^#{2,6}\s|\Z)", txt, re.M | re.S)
        table = m.group(1) if m else txt
        cols = oq_headers(table)
        # mã → tên nhóm: quét tài liệu theo thứ tự, mỗi `### OQB-01` thuộc `## Nhóm B1 — …` gần nhất phía trên
        groups, cur = {}, ""
        for m in re.finditer(r"^##+\s*(?:Nhóm\s+([BT]\d)\s*[—:–-]\s*(.+)|(OQ[BT]?-\d+)\b.*)$", txt, re.M):
            if m.group(1):
                cur = "%s · %s" % (m.group(1), m.group(2).strip())
            elif m.group(3):
                groups[m.group(3)] = cur
        for cells in table_rows(table):
            if not cells or len(cells) < 3:
                continue
            row = {}
            if cols:
                for i, key in cols.items():
                    row[key] = cells[i] if i < len(cells) else ""
            else:                          # bảng không có header chuẩn: rơi về thứ tự cũ
                row = {"q": cells[0], "who": cells[1], "due": cells[2],
                       "impact": cells[3] if len(cells) > 3 else "",
                       "status": cells[-1] if len(cells) > 4 else "open"}
            code = re.sub(r"[*`]", "", row.get("code", "")).strip()
            if code and not re.match(r"^OQ[BT]?-\d+$", code):
                continue                   # dòng của bảng khác (Đã trả lời, phương án…)
            q = row.get("q", "").strip()
            if not q or q.startswith("#") or q.startswith("<"):
                continue
            impact = row.get("impact", "")
            if (audience, code, q[:40]) in seen_rows:
                continue
            seen_rows.add((audience, code, q[:40]))
            answer = re.sub(r"[*`~]", "", row.get("answer", "")).strip()
            if "status" not in row and answer and answer not in ("—", "-", "chưa", "?"):
                row["status"] = "đã chốt"          # bảng chỉ có cột "Chốt là gì" = bảng đã trả lời xong
            closed = bool(re.search(r"closed|đã chốt|da chot|đóng|descoped", row.get("status", ""), re.I))
            if closed:
                row["status"] = row.get("status") or "đã chốt"
            out.append({"code": code, "q": q[:200], "who": row.get("who", ""),
                        "due": row.get("due", ""), "fallback": row.get("fallback", ""),
                        "impact": impact[:140], "status": (row.get("status") or "open").strip(),
                        "answer": answer[:160],
                        "audience": audience, "audienceLabel": label,
                        "blocking": bool(re.search(r"chặn|chan\b|blocking", impact, re.I)) and
                                    not re.search(r"không\s*chặn|ko\s*chặn|khong\s*chan", impact, re.I) and
                                    not closed,
                        "group": groups.get(code, "")})
            seen.add(fname)
    return out


UNIT_DONE = r"^(done|approved|accepted|completed|closed|delivered|xong|đã xong|đã nghiệm thu|nghiệm thu)$"
UNIT_WIP = r"^(in-bolt|in-progress|wip|doing|đang làm|đang chạy)$"


def norm_unit_status(raw, has_bolts):
    """Từ vựng `status:` của spec.md mỗi dự án viết một kiểu — chuẩn hoá thay vì chỉ nhận đúng chữ `done`.

    Trả (status, raw). Trước 3.1.1 chỉ `done` mới tính là xong, nên 21 unit ghi `approved` của PILOT
    hiện thành "chưa xong" trong khi intent đã ở Operations.
    """
    t = re.sub(r"[`*\"']", "", raw or "").strip().lower()
    if re.match(UNIT_DONE, t):
        return "done", t
    if re.match(UNIT_WIP, t):
        return "in-bolt", t
    return ("in-bolt" if has_bolts else "pending-gate"), t


def unit_max_hours():
    """Trần giờ/Unit là núm của TỪNG DỰ ÁN, không phải hằng số của gói (protocol §4.9 v5).
    Mặc định `null` = không trần: cắt Unit theo đường ra sản phẩm và sức chứa một phiên, không theo đồng hồ.
    Override thắng bản gốc, cùng luật với mọi governance khác."""
    for p in (os.path.join(A, "overrides", "governance", "sizing.md"),
              os.path.join(CM, "governance", "sizing.md")):
        m = re.search(r"^\s*unit_max_hours:\s*(\S+)", read(p), re.M)
        if m:
            v = m.group(1).strip().strip('"\'')
            return None if v.lower() in ("null", "none", "-", "0") else num(v, None)
    return None
_HOF_CACHE = []


def hof_rows():
    """Frontmatter của mọi HOF — quét một lần, dùng cho phép đo "unit có gọn trong một phiên không".
    Tách riêng khỏi phần dựng `handoffs` phía dưới vì build_metrics chạy TRƯỚC phần đó."""
    if _HOF_CACHE:
        return _HOF_CACHE
    hdir_m = os.path.join(CM, "handoffs")
    for f in sorted(os.listdir(hdir_m)) if os.path.isdir(hdir_m) else []:
        if not f.startswith("HOF-"):
            continue
        d = fm(read(os.path.join(hdir_m, f)))
        if d:
            _HOF_CACHE.append({"id": d.get("id", f.replace(".md", "")), "re": d.get("re", ""),
                               "status": (d.get("status") or "").strip()})
    return _HOF_CACHE


def sizing_problems(est, us=None, descoped=False):
    """Kích thước Unit: hai điều kiện thay cho một con số (§4.9 v5).

    Trần 5h cũ bắt tách theo đồng hồ nên đẻ ra unit vụn không tự release được (`DEC-0052` của PILOT tách
    3.5h + 2.75h chỉ để lọt trần). Nay chặn theo: **ra được sản phẩm một mình** và **một phiên ôm nổi**."""
    out = []
    if descoped:
        return out
    if est <= 0:
        out.append("thiếu ước lượng")
    elif UNIT_MAX_H and est > UNIT_MAX_H:
        out.append("est %.1fh > trần %.1fh của dự án" % (est, UNIT_MAX_H))
    if us is None:                       # unit mới có trong unit-plan, chưa có spec.md để soi
        return out
    rel = (us.get("releasable") or "").strip().strip('"\'').lower()
    if rel not in ("yes", "no", "true", "false"):
        out.append("thiếu `releasable`")
    elif rel in ("no", "false") and not (us.get("released_with") or "").strip():
        out.append("`releasable: no` mà không nói ra chung với unit nào")
    fit = (us.get("session_fit") or "").strip().strip('"\'')
    if not fit:
        out.append("thiếu `session_fit`")
    elif not re.search(r"\d", fit):
        out.append("`session_fit` không có con số")
    return out


def unit_stub(uid, name, est, provisional=True):
    return {"id": uid, "name": name, "status": "proposed", "provisional": provisional,
            "descoped": False, "bolt": "—", "bolts": [], "done": 0, "estimate": est,
            "stories": 0, "nfrs": 0, "risks": [], "riskCount": 0, "sources": [],
            "problems": sizing_problems(est) or ([] if est > 0 else ["thiếu ước lượng trong unit-plan"]),
            "tasks": [0, 0], "evidence": 0, "specPath": None, "boltDetails": [],
            "rawStatus": "", "reviewedBy": "", "rv": "", "reviewWaivedBy": "",
            "releasable": "", "releasedWith": "", "sessionFit": "", "hofCount": 0}


def parse_provisional_units(base):
    """Unit dự kiến ở phần 3.2 của intent-plan.md — có từ stage 1, trước khi units/ tồn tại."""
    plan = read(os.path.join(base, "intent-plan.md"))
    out = []
    for cells in table_rows(md_section(plan, r"3\.2")):
        if len(cells) < 3 or not re.match(r"^UOW-\d+$", cells[0]):
            continue
        est = num(re.sub(r"[^\d.]", "", cells[2] or "0"), 0.0)
        out.append({
            "id": cells[0], "name": cells[1], "status": "proposed", "provisional": True,
            "bolt": "—", "bolts": [], "done": 0, "estimate": est,
            "stories": 0, "nfrs": 0, "risks": [], "riskCount": 0,
            "sources": [s.strip() for s in (cells[5] if len(cells) > 5 else "").split(",") if s.strip()],
            "problems": [],
            "tasks": [0, 0], "evidence": 0, "specPath": None,
        })
    return out


def parse_tasks_md(text):
    out = []
    for blk in re.findall(r"## (TSK-\d+)[ ·]*([^\n]*)\n(.*?)(?=\n## TSK-|\Z)", text, re.S):
        t = dict(re.findall(r"^(\w+):\s*(.+)$", blk[2], re.M))
        out.append({"id": blk[0], "title": blk[1].strip() or blk[0], "status": t.get("status", "todo"),
                    **({"claimedBy": t["claimed_by"].replace("dlc-", "")} if t.get("claimed_by", "-") not in ("-", "") else {}),
                    "approver": t.get("approver", "—").replace("dlc-", ""),
                    **({"dependsOn": t["depends_on"].strip("[]")} if t.get("depends_on", "[]").strip("[]") else {}),
                    "msgCount": len(t.get("comms", "").strip("[]").split(",")) if t.get("comms", "[]").strip("[]") else 0})
    return out


# Các chặng BÊN TRONG một Bolt, đúng thứ tự white paper: Domain Design → Logical Design + ADR →
# Code + Unit Test. Bolt là nơi bốn chặng đó xảy ra, và nó phải nằm TRONG unit — một Unit chạy qua
# một hoặc nhiều Bolt (song song hoặc tuần tự). Tower đo SỰ TỒN TẠI của từng chặng: chặng thiếu là
# chặng đã bị bỏ qua, và sự vắng mặt đó im lặng (LL-003).
BOLT_STEPS = [("domain-design.md", "Domain Design", "mô hình nghiệp vụ, độc lập hạ tầng"),
              ("logical-design.md", "Logical Design", "áp NFR + pattern"),
              ("adr/", "ADR", "mỗi quyết định kiến trúc một file"),
              ("contract.md", "Contract", "freeze trước khi FE/BE chạy song song"),
              ("tasks.md", "Task board", "TSK-NN có approver + depends_on"),
              ("evidence/", "Evidence", "bằng chứng AC đã pass — nguồn của Gate F")]


def parse_bolts(upath, unit_id):
    """Liệt kê bolt TỪ THƯ MỤC UNIT — không suy từ chỗ khác. Unit không có bolt nào thì trả [],
    và đó là một sự thật cần hiện ra, không phải chỗ để mượn số của unit khác."""
    bdir = os.path.join(upath, "bolts")
    if not os.path.isdir(bdir):
        return []
    out = []
    for bn in sorted(d for d in os.listdir(bdir) if os.path.isdir(os.path.join(bdir, d))):
        bb = os.path.join(bdir, bn)
        steps, done_steps = [], 0
        for rel, label, hint in BOLT_STEPS:
            p = os.path.join(bb, rel.rstrip("/"))
            if rel.endswith("/"):
                n = len(os.listdir(p)) if os.path.isdir(p) else 0
                exists, meta = n > 0, ("%d file" % n if n else "")
            else:
                exists, meta = os.path.isfile(p), ""
            done_steps += 1 if exists else 0
            steps.append({"key": rel, "label": label, "hint": hint, "exists": exists, "meta": meta,
                          "doc": os.path.relpath(p, A) if exists and not rel.endswith("/") else None})
        tasks = parse_tasks_md(read(os.path.join(bb, "tasks.md")))
        out.append({"id": bn, "unit": unit_id, "path": os.path.relpath(bb, A),
                    "steps": steps, "stepsDone": done_steps, "stepsTotal": len(BOLT_STEPS),
                    "tasks": tasks, "tasksFile": os.path.relpath(os.path.join(bb, "tasks.md"), A)
                    if os.path.isfile(os.path.join(bb, "tasks.md")) else None})
    return out


def parse_units(base, intent_id, stage):
    units = []
    proposal = parse_plan_rows(base)
    descoped_ids = parse_descoped(base)
    udir = os.path.join(base, "units")
    if not os.path.isdir(udir):
        return ([unit_stub(r["id"], r["name"], r["est"]) for r in proposal.values()]
                if proposal else parse_provisional_units(base))
    for un in sorted(os.listdir(udir)):
        upath = os.path.join(udir, un)
        # `units/_trash/` giữ unit lỗi thời có bia mộ (DoD "unit lỗi thời vào _trash", LL-002 P-6).
        # Nó là kho bằng chứng cho retro, KHÔNG phải unit đang chạy — đếm nó vào thống kê thì
        # mọi con số của intent sai. Mọi thư mục `_*` đều là kho nội bộ, bỏ qua như nhau.
        if not os.path.isdir(upath) or un.startswith("_"):
            continue
        spec_p = os.path.join(upath, "spec.md")
        us = fm(read(spec_p))
        bdir = os.path.join(upath, "bolts")
        bolts = sorted(os.listdir(bdir)) if os.path.isdir(bdir) else []
        nb = len(bolts)
        done_files, tasks_total, tasks_done, evidence = 0, 0, 0, 0
        for bn in bolts:
            bb = os.path.join(bdir, bn)
            done_files += sum(os.path.isfile(os.path.join(bb, f)) for f in
                              ("domain-design.md", "logical-design.md", "tasks.md"))
            tt = read(os.path.join(bb, "tasks.md"))
            statuses = re.findall(r"^status:\s*(\S+)", tt, re.M)
            tasks_total += len(statuses)
            tasks_done += sum(1 for s in statuses if s == "done")
            evidence += len(globmod.glob(os.path.join(bb, "evidence", "*")))
        pct = int(done_files / (nb * 3) * 100) if nb else 0

        def count_items(fname):
            """Đếm rộng tay: bullet, dòng bảng, heading con. Mỗi dự án viết một kiểu
            (bullet `- US-01:` cũng hợp lệ như bảng) — đếm hẹp sẽ báo 'thiếu' oan."""
            p = os.path.join(upath, fname)
            if not os.path.isfile(p):
                return 0, False
            txt = read(p)
            body = re.sub(r"^---.*?---\s*", "", txt, flags=re.S)
            body = re.sub(r"^#.*$", "", body, flags=re.M)
            bullets = len(re.findall(r"^\s*[-*+]\s+\S", body, re.M))
            trows = [l for l in body.splitlines()
                     if l.strip().startswith("|") and not re.fullmatch(r"[|\s:-]+", l.strip())]
            heads = len(re.findall(r"^#{2,4}\s*\S", txt, re.M))
            n = bullets + max(0, len(trows) - 1) + heads
            return n, len(body.strip()) > 40

        stories, has_us = count_items("user-stories.md")
        nfrs, has_nfr = count_items("nfr.md")
        risks, has_risk = count_items("risks.md")
        est = num(us.get("estimate_hours"), 0.0)
        # CHỈ `units/DESCOPED.md` (hoặc `status: descoped` trong spec) mới đưa unit ra ngoài phạm vi.
        # Trước 3.1.0 còn suy "không có trong unit-plan ⇒ descoped" — sai với unit sinh sau Gate D
        # (UOW-19..22 của PILOT là ví dụ: đã giao xong mà bị tính là ngoài phạm vi).
        descoped = un in descoped_ids or us.get("status") == "descoped"
        added_after_plan = bool(proposal) and un not in proposal and not descoped
        if not est and un in proposal:
            est = proposal[un]["est"]
        srcs = [s.strip() for s in us.get("sources", "").strip("[]").split(",") if s.strip()]
        ustatus, raw_status = norm_unit_status(us.get("status"), bool(nb))
        status = "descoped" if descoped else ustatus
        problems = sizing_problems(est, us, descoped)
        if not descoped:
            for label, ok in (("user-stories", has_us and stories), ("nfr", has_nfr and nfrs),
                              ("risks", has_risk and risks)):
                if not ok:
                    problems.append("thiếu " + label)
        units.append({
            "id": un, "name": us.get("title", un), "status": status,
            "bolt": bolts[-1] if bolts else "—", "bolts": bolts, "done": pct,
            "boltDetails": parse_bolts(upath, un),
            "estimate": est, "stories": stories, "nfrs": nfrs, "risks": [],
            "riskCount": risks, "sources": srcs, "problems": problems, "provisional": False,
            "descoped": descoped, "addedAfterPlan": added_after_plan, "rawStatus": raw_status,
            # protocol §4.12 + §4.17: `done` phải có bằng chứng soát ĐÚNG theo tầng review đã duyệt —
            # RV thật (peer/specialist) · self-verify thật (tier none) · DEC miễn (ngoại lệ).
            "reviewedBy": (us.get("reviewed_by") or "").strip(),
            "rv": (us.get("rv") or "").strip(),
            "reviewWaivedBy": (us.get("review_waived_by") or "").strip(),
            "review": (us.get("review") or "").strip().strip('"\''),
            "selfVerify": (us.get("self_verify") or "").strip(),
            "selfVerifyExists": bool((us.get("self_verify") or "").strip())
                and os.path.isfile(os.path.join(upath, (us.get("self_verify") or "").strip())),
            # §4.9 v5: kích thước Unit đo bằng đường ra sản phẩm + sức chứa một phiên, không bằng giờ
            "releasable": (us.get("releasable") or "").strip().strip('"\''),
            "releasedWith": (us.get("released_with") or "").strip(),
            "sessionFit": (us.get("session_fit") or "").strip().strip('"\''),
            "tasks": [tasks_done, tasks_total], "evidence": evidence,
            "specPath": os.path.relpath(spec_p, A) if os.path.isfile(spec_p) else None,
        })
    # Unit có trong unit-plan nhưng chưa có thư mục — vẫn phải hiện ở gate và tính trần 5h
    have = {u["id"] for u in units}
    for uid, r in proposal.items():
        if uid not in have:
            units.append(unit_stub(uid, r["name"], r["est"]))
    return units


SIZING_NEW = ("thiếu `releasable`", "thiếu `session_fit`", "`session_fit` không có con số",
              "`releasable: no` mà không nói ra chung với unit nào")


def build_metrics(intent_id, base, units, srcs, qs, gates_open, passed=()):
    """Mỗi con số hiện trên dashboard kèm CÁCH RA SỐ ĐÓ.

    Một metric = {value, label, rule (đếm gì, từ đâu), files (file · mục), rows (dòng thật đã đếm),
    warnings}. UI bấm vào con số là thấy đúng những dòng này — không có số nào không giải thích được.
    """
    rel = os.path.relpath(base, A)
    out = []
    c = srcs["counts"]
    live = [u for u in units if not u.get("descoped")]
    off = [u for u in units if u.get("descoped")]

    def add(key, value, label, rule, files, rows, warnings=(), tone="neutral"):
        out.append({"key": key, "value": value, "label": label, "rule": rule,
                    "files": files, "rows": rows[:80], "rowCount": len(rows),
                    "warnings": list(warnings), "tone": tone})

    src_files = [{"file": rel + "/" + u["file"], "section": u["section"], "rows": u["rows"]}
                 for u in srcs.get("sources_used", [])]
    src_rows = [{"Mã": r["id"], "Nguồn": r["source"], "Trạng thái": r["status"],
                 "Ô gốc trong file": r.get("rawStatus", ""), "Evidence": r.get("evidence", "")[:120]}
                for r in srcs["rows"]]
    add("sources.read", "%d/%d" % (c.get("read", 0), c.get("total", 0)), "nguồn đã đọc có evidence",
        "Đếm dòng có cột `Trạng thái` hiểu được là đã đọc (✅ · read · đã đọc · xong), trên MỌI bảng "
        "có cột `#` + `Nguồn` trong sổ cái. Nhận bảng bằng tên cột, không bằng số mục.",
        src_files, src_rows, srcs.get("warnings", []), "done" if not c.get("planned") else "gate")
    add("sources.planned", c.get("planned", 0), "nguồn còn treo (chặn Gate B/D)",
        "Dòng trạng thái là ⬜ / planned / chưa đọc. Còn dòng nào là cấm đóng Gate B (protocol §4.8).",
        src_files, [r for r in src_rows if r["Trạng thái"] == "planned"], (),
        "gate" if c.get("planned") else "done")
    conf_rows = [{"Ở đâu": x.get("from", ""), "Nội dung": x.get("a", ""), "Bên kia": x.get("b", ""),
                  "Trạng thái": x.get("status", "")} for x in srcs.get("conflicts", [])]
    add("sources.conflicts", c.get("conflicts", 0), "mâu thuẫn nguồn chưa chốt",
        "Hai nguồn nói khác nhau. Đếm: các dòng trong mục có tiêu đề chứa “mâu thuẫn”/“conflict” của sổ cái, "
        "cộng các dấu `[CONFLICT]` rải trong file (bỏ mục Changelog và câu phủ định “không có [CONFLICT]”).",
        [{"file": rel + "/as-is/source-ledger.md", "section": "mục có tiêu đề “Mâu thuẫn…” + dấu [CONFLICT]",
          "rows": len(conf_rows)}], conf_rows, (), "gate" if c.get("conflicts") else "done")
    if c.get("unknown"):
        add("sources.unknown", c["unknown"], "nguồn KHÔNG đọc được trạng thái",
            "Ô `Trạng thái` viết theo cách máy chưa hiểu. Những dòng này KHÔNG được tính là đã đọc — "
            "sửa ô đó trong sổ cái hoặc coi như chưa đọc.",
            src_files, [r for r in src_rows if r["Trạng thái"] == "unknown"], (), "gate")

    unit_rows = [{"Unit": u["id"], "Tên": u["name"][:70], "Giờ": u["estimate"], "Trạng thái": u["status"],
                  "US/NFR/Risk": "%d/%d/%d" % (u["stories"], u["nfrs"], u["riskCount"]),
                  "Bolt": len(u["bolts"]), "Task": "%d/%d" % tuple(u["tasks"]),
                  "Ghi chú": "thêm sau unit-plan" if u.get("addedAfterPlan") else
                             ("dự kiến" if u.get("provisional") else "")} for u in live]
    add("units.count", len(live), "unit trong phạm vi" + (" (+%d ngoài phạm vi)" % len(off) if off else ""),
        "Đếm thư mục `units/UOW-NN/` có `spec.md`, cộng unit mới có trong `unit-plan.md` mà chưa tạo thư mục. "
        "Chỉ `units/DESCOPED.md` (hoặc `status: descoped`) mới đưa unit ra ngoài phạm vi.",
        [{"file": rel + "/units/", "section": "mỗi thư mục UOW-NN/spec.md", "rows": len(units)},
         {"file": rel + "/units/DESCOPED.md", "section": "frontmatter `units:`", "rows": len(off)}],
        unit_rows + [{"Unit": u["id"], "Tên": u["name"][:70], "Giờ": u["estimate"],
                      "Trạng thái": "NGOÀI PHẠM VI", "US/NFR/Risk": "—", "Bolt": len(u["bolts"]),
                      "Task": "%d/%d" % tuple(u["tasks"]), "Ghi chú": "DESCOPED.md"} for u in off],
        (), "agent")
    add("units.estimate", "%.1fh" % sum(u["estimate"] for u in live), "tổng ước lượng (trong phạm vi)",
        "Cộng `estimate_hours` trong frontmatter `spec.md` của unit trong phạm vi; unit chưa có thư mục thì "
        "lấy ô giờ ở `unit-plan.md`. Unit ngoài phạm vi KHÔNG cộng.",
        [{"file": rel + "/units/UOW-NN/spec.md", "section": "frontmatter `estimate_hours`", "rows": len(live)}],
        [{"Unit": u["id"], "Giờ": u["estimate"]} for u in live], (), "agent")
    # Intent đã qua Gate D được lập kế hoạch dưới luật cũ (trần 5h). Không bắt khai lại `releasable`/
    # `session_fit` cho chúng — đó là dựng bù hồ sơ. Áp §4.9 v5 từ intent kế; ở đây chỉ WARN.
    legacy = "D" in (passed or ())
    if legacy:
        for _u in live:
            _u["problemsLegacy"] = [p for p in _u["problems"] if p in SIZING_NEW]
            _u["problems"] = [p for p in _u["problems"] if p not in SIZING_NEW]
    bad = [u for u in live if u["problems"]]
    legacy_n = sum(1 for u in live if u.get("problemsLegacy"))
    add("units.problems", len(bad),
        "unit chưa đủ điều kiện kích thước hoặc thiếu US/NFR/risk",
        "Kích thước Unit đo bằng ĐƯỜNG RA SẢN PHẨM + SỨC CHỨA MỘT PHIÊN, không bằng giờ (§4.9 v5 — trần 5h "
        "đã bỏ): mỗi unit phải khai `releasable` (nếu `no` thì kèm `released_with`) và `session_fit` có con "
        "số; `estimate_hours` vẫn bắt buộc >0 và có breakdown"
        + (", vượt trần %.1fh mà dự án tự đặt là WARN" % UNIT_MAX_H if UNIT_MAX_H else ", dự án không đặt trần giờ")
        + ". Cộng ba file `user-stories.md` · `nfr.md` · `risks.md` phải có nội dung "
          "(đếm gạch đầu dòng + dòng bảng + heading con).",
        [{"file": rel + "/units/UOW-NN/", "section": "spec.md · user-stories.md · nfr.md · risks.md",
          "rows": len(live)}],
        [{"Unit": u["id"], "Vấn đề": ", ".join(u["problems"])} for u in bad],
        (["%d unit lập kế hoạch dưới luật cũ (trần 5h, chưa có `releasable`/`session_fit`) — đã qua Gate D "
          "nên KHÔNG bắt khai lại; §4.9 v5 áp từ intent kế" % legacy_n] if legacy_n else []),
        "gate" if bad else "done")

    t_rows = [{"Unit": u["id"], "Bolt": ", ".join(u["bolts"]) or "—", "Task done/tổng": "%d/%d" % tuple(u["tasks"])}
              for u in live if u["bolts"] or u["tasks"][1]]
    t_done, t_all = sum(u["tasks"][0] for u in live), sum(u["tasks"][1] for u in live)
    add("tasks.done", "%d/%d" % (t_done, t_all), "task done (unit trong phạm vi)",
        "Đếm dòng `## TSK-NN` trong `units/UOW-NN/bolts/BOLT-NN/tasks.md`; done = dòng có `status: done`. "
        "Không có file `tasks.md` nào thì bằng 0 — nghĩa là chưa lập task, KHÔNG phải chưa làm gì.",
        [{"file": rel + "/units/*/bolts/*/tasks.md", "section": "mục `## TSK-NN`",
          "rows": sum(1 for u in live if u["tasks"][1])}], t_rows,
        (["Không unit nào trong phạm vi có `tasks.md` — số task bằng 0 là do chưa lập file, "
          "không phải do chưa làm việc."] if not t_all else []), "agent")

    st_rows = [{"Unit": u["id"], "Tower hiểu là": u["status"],
                "Chữ trong spec.md": u.get("rawStatus") or "(không khai báo)",
                "Bolt": len(u["bolts"])} for u in live]
    nodecl = sum(1 for u in live if not u.get("rawStatus"))
    add("units.done", sum(1 for u in live if u["status"] == "done"), "unit đã xong",
        "Đọc `status:` trong frontmatter `spec.md` của từng unit và chuẩn hoá: "
        "`done` · `approved` · `accepted` · `completed` · `closed` · `xong` · `đã nghiệm thu` đều tính là xong. "
        "Đây là số liệu KHAI BÁO trong tài liệu, KHÔNG phải đo từ code — unit làm xong mà quên sửa dòng này "
        "vẫn hiện là chưa xong.",
        [{"file": rel + "/units/UOW-NN/spec.md", "section": "frontmatter `status`", "rows": len(live)}],
        st_rows, (["%d unit không khai `status` — đang tính là chưa xong" % nodecl] if nodecl else []), "done")

    # Kích thước Unit đo bằng ĐƯỜNG RA (§4.9 v5) — khai lúc lập kế hoạch, kiểm được ngay.
    rel_rows, rel_ok = [], []
    for u in live:
        v = (u.get("releasable") or "").lower()
        if v in ("yes", "true"):
            verdict = "ra được một mình"
        elif v in ("no", "false"):
            verdict = ("ra chung " + u["releasedWith"]) if u.get("releasedWith") else "KHÔNG có đường ra nào"
        else:
            verdict = "chưa khai"
        if verdict not in ("chưa khai", "KHÔNG có đường ra nào"):
            rel_ok.append(u)
        rel_rows.append({"Unit": u["id"], "releasable": u.get("releasable") or "—",
                         "released_with": u.get("releasedWith") or "—",
                         "session_fit": (u.get("sessionFit") or "—")[:60], "Kết luận": verdict})
    if live:
        add("units.releasable", "%d/%d" % (len(rel_ok), len(live)), "unit có đường ra sản phẩm rõ ràng",
            "Đọc `releasable:` trong `spec.md`. `yes` = xong là ra được (có thể sau cờ tính năng); `no` thì "
            "BẮT BUỘC kèm `released_with:` nói ra chung với unit nào. Không khai được đường ra nghĩa là unit "
            "đó không tự có nghĩa với người dùng — pseudo-unit kỹ thuật, phải gộp hoặc cắt theo trục khác "
            "(§4.9 v5, thay cho trần 5h cũ).",
            [{"file": rel + "/units/UOW-NN/spec.md", "section": "frontmatter `releasable` · `released_with`",
              "rows": len(live)}], rel_rows,
            ([] if len(rel_ok) == len(live) else
             ["%d unit chưa khai đường ra%s" % (len(live) - len(rel_ok),
              " — kế hoạch cũ, không bắt khai lại (§4.9 v5 áp từ intent kế)" if legacy else " — chặn Gate D")]),
            "done" if len(rel_ok) == len(live) else ("agent" if legacy else "gate"))

    # ... và kiểm SAU bằng dấu vết: thực tế nó có gọn trong một phiên không (lời khai lúc lập kế hoạch
    # luôn lạc quan — §9.4 đã dạy một lần). Một unit cần nhiều lượt giao việc là một unit cắt quá to.
    hof_per_unit = {}
    for h in hof_rows():
        m = re.search(r"(UOW-\d+)", h.get("re") or "")
        if m:
            hof_per_unit.setdefault(m.group(1), []).append(h)
    closed_now = [u for u in live if u["status"] == "done"]
    if closed_now and hof_per_unit:
        rows_1s, ok_1s = [], []
        for u in closed_now:
            hs = hof_per_unit.get(u["id"], [])
            returned = [h for h in hs if h["status"] == "returned"]
            if not hs:
                verdict = "không HOF nào — không đo được"
            elif len(hs) == 1 and not returned:
                verdict = "một phiên"
                ok_1s.append(u)
            else:
                verdict = "%d lượt giao việc%s" % (len(hs), " (có trả lại)" if returned else "")
            rows_1s.append({"Unit": u["id"], "Số HOF": len(hs), "Ước lượng": "%.1fh" % u["estimate"],
                            "session_fit đã khai": (u.get("sessionFit") or "—")[:50], "Thực tế": verdict})
        add("units.oneSession", "%d/%d" % (len(ok_1s), len(closed_now)), "unit thật sự gọn trong một phiên",
            "Đếm số `handoffs/HOF-*.md` có `re:` trỏ vào unit đó. Một chuỗi HOF = một phiên làm trọn; cần "
            "nhiều lượt hoặc có lượt `returned` nghĩa là **thực tế** unit to hơn `session_fit` đã khai. Đây "
            "KHÔNG phải để phạt: đó là dữ liệu để intent sau cắt unit sát hơn (§4.9 v5).",
            [{"file": ".ai-dlc/context-memory/handoffs/HOF-*.md", "section": "frontmatter `re` · `status`",
              "rows": len(hof_rows())}],
            rows_1s, ([] if len(ok_1s) == len(closed_now) else
                      ["%d unit cần nhiều hơn một lượt — lời khai `session_fit` lạc quan hơn thực tế"
                       % (len(closed_now) - len(ok_1s))]),
            "done" if len(ok_1s) == len(closed_now) else "agent")

    # Review có địa chỉ hay không (protocol §4.12). `approved` do chính agent làm unit tự đặt không chứng
    # minh được gì; chỉ `rv:` trỏ một RV có thật, hoặc `review_waived_by:` trỏ một DEC, mới là bằng chứng.
    rv_ids = set()
    rdir_all = os.path.join(CM, "reviews")
    if os.path.isdir(rdir_all):
        rv_ids = {f.replace(".md", "") for f in os.listdir(rdir_all) if f.startswith("RV-")}
    closed = [u for u in live if u["status"] == "done"]
    if closed:
        OK_STATES = ("RV có thật", "miễn review có DEC", "self-verify có thật (tier none)")

        def rv_state(u):
            if u.get("rv"):
                return "RV có thật" if u["rv"].strip() in rv_ids else "rv trỏ RV KHÔNG tồn tại"
            if u.get("selfVerify"):
                tier = (u.get("review") or "none").lower()
                if not tier.startswith("none"):
                    return "self-verify nhưng tier khai `%s` — cần RV" % (u.get("review") or "?")
                return ("self-verify có thật (tier none)" if u.get("selfVerifyExists")
                        else "self_verify trỏ file KHÔNG tồn tại")
            if u.get("reviewWaivedBy"):
                return "miễn review có DEC"
            return "TỰ KHAI — không RV, không self-verify, không DEC miễn"
        rows = [{"Unit": u["id"], "Trạng thái": u.get("rawStatus") or u["status"],
                 "review (tầng)": u.get("review") or "— (chưa khai, kế hoạch trước v6)",
                 "reviewed_by": u.get("reviewedBy") or "—", "rv": u.get("rv") or "—",
                 "self_verify": u.get("selfVerify") or "—",
                 "review_waived_by": u.get("reviewWaivedBy") or "—", "Kết luận": rv_state(u)}
                for u in closed]
        ok = [r for r in rows if r["Kết luận"] in OK_STATES]
        add("units.reviewed", "%d/%d" % (len(ok), len(closed)),
            "unit đã xong CÓ bằng chứng soát đúng tầng",
            "Với mỗi unit đã đóng, đọc bằng chứng ĐÚNG theo tầng `review:` đã duyệt ở Gate D (§4.17): "
            "`rv:` (file `reviews/RV-NNN.md` phải tồn tại thật — tier peer/specialist) · `self_verify:` "
            "(file evidence phải tồn tại thật — CHỈ tier none) · `review_waived_by:` (DEC ngoại lệ). "
            "Thiếu cả ba thì `approved` chỉ là TỰ KHAI của chính agent làm unit (protocol §4.12).",
            [{"file": rel + "/units/UOW-NN/spec.md",
              "section": "frontmatter `review` · `rv` · `self_verify` · `review_waived_by`",
              "rows": len(closed)},
             {"file": "context-memory/reviews/", "section": "RV-NNN.md có thật", "rows": len(rv_ids)}],
            rows,
            (["%d/%d unit đóng mà không có bằng chứng soát nào — con số “unit đã xong” ở trên là TỰ KHAI."
              % (len(closed) - len(ok), len(closed))] if len(ok) < len(closed) else []),
            "done" if len(ok) == len(closed) else "gate")

    # Artifact bắt buộc mà không ai kiểm sự TỒN TẠI thì nó sẽ không tồn tại (LL-003).
    # Đo sự vắng mặt, đừng đo nội dung: thiếu bolt/tasks/evidence là im lặng — code vẫn ra, test vẫn xanh,
    # chỉ khả năng truy vết là mất.
    if closed:
        miss = []
        for u in closed:
            gaps = []
            if not u["bolts"]:
                gaps.append("không có `bolts/`")
            elif not u["tasks"][1]:
                gaps.append("bolt không có `tasks.md`")
            if not u["evidence"]:
                gaps.append("không có `evidence/`")
            if gaps:
                miss.append({"Unit": u["id"], "Bolt": ", ".join(u["bolts"]) or "—",
                             "Thiếu": " · ".join(gaps)})
        add("units.artifacts", "%d/%d" % (len(closed) - len(miss), len(closed)),
            "unit đã xong có đủ hồ sơ bolt",
            "Với mỗi unit đã đóng, kiểm SỰ TỒN TẠI của `bolts/BOLT-NN/` · `tasks.md` · `evidence/`. "
            "Đây là phép đo có/không, không đo nội dung: artifact bắt buộc mà không ai kiểm sự tồn tại "
            "thì nó sẽ không tồn tại, và sự vắng mặt đó im lặng — sản phẩm vẫn chạy, chỉ mất truy vết. "
            "KHÔNG dựng bù hồ sơ sau khi code xong: design viết ngược từ code là mô tả code đội lốt "
            "quyết định thiết kế; hồ sơ trống trung thực hơn hồ sơ dựng lại.",
            [{"file": rel + "/units/UOW-NN/bolts/", "section": "thư mục BOLT-NN + tasks.md + evidence/",
              "rows": len(closed)}],
            miss,
            (["%d/%d unit đóng mà thiếu hồ sơ bolt — HOF vẫn khai `scope: …/BOLT-01` cho những unit này, "
              "tên bolt trong HOF là chuỗi tự do, không có gì đối chiếu nó với thư mục thật."
              % (len(miss), len(closed))] if miss else []),
            "done" if not miss else "gate")

    # đối chiếu pha ↔ unit: `stage` là MỘT con số do orchestrator ghi, unit là 22 file riêng.
    # Không ai ràng buộc hai thứ đó, nên phải nói ra khi chúng lệch nhau.
    stage_now = int(num(fm(read(os.path.join(base, "status.md"))).get("stage", 1), 1))
    unfinished = [u for u in live if u["status"] != "done"]
    if stage_now >= 6 and unfinished:
        add("phase.consistency", "%d/%d" % (len(live) - len(unfinished), len(live)),
            "unit đã đóng, so với pha đang hiện",
            "So `stage:` trong `status.md` (một con số do orchestrator ghi, quyết định pha hiển thị) với "
            "`status:` của từng unit. Hai thứ này KHÔNG tự ràng buộc nhau: intent có thể bị đẩy sang "
            "Construction/Operations trong khi hồ sơ unit chưa đóng.",
            [{"file": rel + "/status.md", "section": "frontmatter `stage` (đang là %d)" % stage_now, "rows": 1},
             {"file": rel + "/units/UOW-NN/spec.md", "section": "frontmatter `status`", "rows": len(live)}],
            [{"Unit": u["id"], "Chữ trong spec.md": u.get("rawStatus") or "(không khai báo)",
              "Bolt": len(u["bolts"]), "Evidence": u["evidence"]} for u in unfinished],
            ["Intent đang ở stage %d (%s) nhưng %d/%d unit chưa đóng hồ sơ. Hoặc unit đã xong mà chưa cập nhật "
             "`status:`, hoặc pha bị đẩy sớm — hai khả năng này tower không tự phân biệt được, phải người xem."
             % (stage_now, PHASE_OF_STAGE.get(stage_now, "?"), len(unfinished), len(live))], "gate")

    for aud, label, fname in (("business", "câu hỏi chờ người nghiệp vụ", "open-questions-business.md"),
                              ("tech", "câu hỏi chờ người kỹ thuật", "open-questions-tech.md")):
        qq = [q for q in qs if q["audience"] == aud and
              not re.search(r"closed|đã chốt|đóng", q["status"], re.I)]
        if not qq and not any(q["audience"] == aud for q in qs):
            continue
        add("questions." + aud, len(qq), label,
            "Đếm dòng bảng điều phối (mục 0) có mã OQ và trạng thái chưa đóng. Nhận cột theo TÊN "
            "(`Mã` · `Ai trả lời` · `Ảnh hưởng` · `Trạng thái`).",
            [{"file": rel + "/" + fname, "section": "mục 0 · Bảng điều phối", "rows": len(qq)}],
            [{"Mã": q["code"], "Câu hỏi": q["q"][:90], "Ai trả lời": q["who"],
              "Ảnh hưởng": q["impact"], "Trạng thái": q["status"]} for q in qq], (),
            "gate" if any(q["blocking"] for q in qq) else "done")

    add("gates.open", len(gates_open), "gate đang chờ người quyết",
        "Đọc `gate_open` trong `status.md` của từng intent. Mỗi gate mở phải có `gate_doc` là một markdown "
        "tự đủ; thiếu file đó thì tower chặn approve.",
        [{"file": rel + "/status.md", "section": "frontmatter `gate_open` · `gate_doc`",
          "rows": len(gates_open)}],
        [{"Gate": g, "Tài liệu": "xem màn duyệt"} for g in gates_open], (), "gate")
    return {m["key"]: m for m in out}


def build_flow(intent_id, base, stage, passed, gate_open, units, srcs, qs=(), brownfield=False):
    """Ba khối pha; mỗi khối có các chặng + trạng thái, và mạch của từng Unit."""
    def gate_state(g):
        if g in passed:
            return "passed"
        if gate_open and gate_open.startswith(g):
            return "open"
        return "pending"

    def artifact(rel, label, min_stage, extra=None):
        p = os.path.join(base, rel)
        exists = os.path.isfile(p)
        return {"key": rel, "label": label, "doc": os.path.relpath(p, A) if exists else None,
                "status": "done" if exists else ("active" if stage == min_stage else "pending"),
                "meta": extra or ""}

    def oq_open(aud):
        return [q for q in qs if q["audience"] == aud and
                not re.search(r"closed|đã chốt|da chot|descoped", q["status"], re.I)]

    oq_n = {"business": len(oq_open("business")), "tech": len(oq_open("tech")),
            "techBlocking": len([q for q in oq_open("tech") if q["blocking"]]),
            "legacy": len(oq_open("legacy"))}
    c = srcs["counts"]
    split_exists = any(os.path.isfile(os.path.join(base, f))
                       for f in ("open-questions-business.md", "open-questions-tech.md"))
    if not split_exists and os.path.isfile(os.path.join(base, "open-questions.md")):
        oq_steps = [artifact("open-questions.md", "Open Questions (bản gộp cũ)", 4,
                             "%d câu · chưa tách business/tech (§4.10)" % oq_n["legacy"])]
    else:
        oq_steps = [
            artifact("open-questions-business.md", "OQ · Nghiệp vụ", 4,
                     ("%d câu chờ người nghiệp vụ" % oq_n["business"]) if oq_n["business"] else
                     ("%d mâu thuẫn nguồn" % c["conflicts"] if c.get("conflicts") else "")),
            artifact("open-questions-tech.md", "OQ · Kỹ thuật", 4,
                     ("%d câu chờ · %d chặn Unit" % (oq_n["tech"], oq_n["techBlocking"]))
                     if oq_n["tech"] else ""),
        ]
    live = [u for u in units if not u.get("descoped")]
    prov = [u for u in live if u.get("provisional")]
    real = [u for u in live if not u.get("provisional")]
    inception = {
        "label": "Inception", "stages": "stage 1–5",
        "steps": [
            artifact("intent-plan.md", "Intent Plan", 1,
                     "%d nguồn · %d unit dự kiến · %.1fh" % (
                         c.get("total", 0), len(prov or real),
                         sum(u["estimate"] for u in (prov or real)))),
            {"key": "gate-A", "label": "Gate A", "gate": "A", "status": gate_state("A"),
             "meta": GATE_TITLE["A"]},
            artifact("as-is/source-ledger.md", "Source Ledger", 2,
                     "%d/%d nguồn đã đọc%s" % (c.get("read", 0), c.get("total", 0),
                                               " · %d còn planned" % c["planned"] if c.get("planned") else "")),
            # Brownfield: đầu pha có thêm chặng NÂNG MÃ LÊN MÔ HÌNH — code hiện có phải được đọc
            # thành mô hình tĩnh (cấu trúc) và mô hình động (luồng chạy) trước khi bàn tới thay đổi.
            # Greenfield không có chặng này; hiện nhầm cho greenfield là bịa việc.
            *([artifact("as-is/static-model.md", "Mô hình tĩnh (as-is)", 3,
                        "brownfield: nâng mã hiện có thành cấu trúc đọc được"),
               artifact("as-is/dynamic-model.md", "Mô hình động (as-is)", 3,
                        "brownfield: luồng chạy thật, không phải luồng trong tài liệu")]
              if brownfield else []),
            {"key": "gate-B", "label": "Gate B", "gate": "B", "status": gate_state("B"),
             "meta": GATE_TITLE["B"], "blocked": srcs["blocking"]},
            *oq_steps,
            {"key": "gate-C", "label": "Gate C", "gate": "C", "status": gate_state("C"),
             "meta": GATE_TITLE["C"]},
            artifact("unit-plan.md", "Unit Plan", 5,
                     "%d unit chốt · %.1fh" % (len(real), sum(u["estimate"] for u in real))),
            {"key": "gate-D", "label": "Gate D", "gate": "D", "status": gate_state("D"),
             "meta": GATE_TITLE["D"]},
        ]}
    n_bolts = sum(len(u["bolts"]) for u in live)
    t_done = sum(u["tasks"][0] for u in live)
    t_all = sum(u["tasks"][1] for u in live)
    construction = {
        "label": "Construction", "stages": "stage 6",
        "steps": [
            {"key": "bolts", "label": "Bolts đang chạy", "status": "active" if stage == 6 else (
                "done" if stage > 6 else "pending"),
             "meta": "%d bolt / %d unit · %d/%d task done%s" % (
                 n_bolts, len(live), t_done, t_all,
                 " · %d unit CHƯA có bolt nào" % sum(1 for u in live if not u["bolts"])
                 if any(not u["bolts"] for u in live) else "")},
            {"key": "gate-E", "label": "Gate E", "gate": "E", "status": gate_state("E"),
             "meta": GATE_TITLE["E"]},
        ]}
    ev = sum(u["evidence"] for u in live)
    operations = {
        "label": "Operations", "stages": "stage 7–8",
        "steps": [
            {"key": "acceptance", "label": "Acceptance evidence", "status": "active" if stage == 7 else (
                "done" if stage > 7 else "pending"), "meta": "%d evidence" % ev},
            {"key": "gate-F", "label": "Gate F", "gate": "F", "status": gate_state("F"),
             "meta": GATE_TITLE["F"]},
            {"key": "release", "label": "Release / Deployment Unit",
             "status": "done" if stage >= 8 and not gate_open else ("active" if stage == 8 else "pending"), "meta": ""},
            {"key": "gate-G", "label": "Gate G", "gate": "G", "status": gate_state("G"),
             "meta": GATE_TITLE["G"]},
        ]}

    # mạch từng Unit xuyên ba khối
    lanes = []
    for u in live:
        prov_u = u.get("provisional")
        stops = u.get("stops", [])
        waiting = [s for s in stops if s["state"] == "waiting"]
        skipped = [s for s in stops if s["state"] == "skipped"]
        lanes.append({
            "id": u["id"], "name": u["name"], "estimate": u["estimate"], "problems": u["problems"],
            "provisional": bool(prov_u),
            "inception": {"state": "warn" if u["problems"] else (
                              "active" if prov_u else (
                                  "done" if u["stories"] and u["nfrs"] and u["riskCount"] else "warn")),
                          "meta": ("dự kiến · %.1fh · %d nguồn" % (u["estimate"], len(u["sources"])))
                                  if prov_u else
                                  ("%d US · %d NFR · %d risk · %.1fh" % (u["stories"], u["nfrs"], u["riskCount"], u["estimate"])),
                          "sources": u["sources"]},
            # Mạch Construction phải nói ĐANG DỪNG Ở ĐÂU và AI GIỮ — đó là câu hỏi thật của người xem,
            # không phải "bao nhiêu phần trăm". Điểm dừng bị bỏ qua cũng hiện ở đây, vì nó im lặng.
            "construction": {"state": ("returned" if any(s["state"] == "returned" for s in stops) else
                                       "warn" if skipped else
                                       "done" if u["done"] == 100 else
                                       "active" if u["bolts"] else "pending"),
                             "meta": ((waiting[0]["label"] + " · " +
                                       ("CHỜ NGƯỜI" if waiting[0]["holder"] == "human" else "chờ agent"))
                                      if waiting else
                                      ("%d điểm dừng bị đi qua" % len(skipped) if skipped else
                                       ("%s · %d/%d task" % (u["bolt"], u["tasks"][0], u["tasks"][1])
                                        if u["bolts"] else "chưa vào bolt"))),
                             "stops": stops, "holder": (waiting[0]["holder"] if waiting else None),
                             "pct": u["done"]},
            "operations": {"state": "done" if u["status"] == "done" else ("active" if u["evidence"] else "pending"),
                           "meta": "%d evidence" % u["evidence"] if u["evidence"] else "chưa có evidence"},
        })
    return {"phases": [inception, construction, operations], "lanes": lanes,
            "current": PHASE_OF_STAGE.get(stage, "inception")}


def scan_records(sub, keep):
    """Đọc TOÀN BỘ một thư mục bản ghi (comms/ reviews/ escalations/) thành chỉ mục tra được.
    Điểm dừng trong Bolt được suy ra từ chính những file này — không suy từ trạng thái tự khai."""
    out = []
    d = os.path.join(CM, sub)
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"):
            continue
        p = os.path.join(d, f)
        d0 = fm(read(p))
        if not d0:
            continue
        body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S).strip()
        rec = {k: (d0.get(k) or "").strip() for k in keep}
        rec.update({"id": f.replace(".md", ""), "path": os.path.relpath(p, A),
                    "time": mtime_hm(p), "body": re.sub(r"\s+", " ", body)[:200]})
        out.append(rec)
    return out

# Điểm dừng trong một Bolt (protocol §1.0c). Mỗi điểm ghi rõ AI GIỮ: agent hay người.
# `after` = chặng phải xong trước khi tới điểm dừng này; `evidence` = dấu vết chứng minh đã dừng thật.
BOLT_STOPS = [
    ("design-review", "Review thiết kế", "agent", "logical-design.md",
     "tech-lead + security ký TRƯỚC khi có dòng code nào"),
    ("contract-freeze", "Freeze contract", "agent", "contract.md",
     "BE ↔ FE chốt shape; sau freeze đổi contract = DEC + mở lại task phụ thuộc"),
    ("gate-E-a", "Gate E(a) — checkpoint design", "human", "logical-design.md",
     "người duyệt design + ADR + contract trước khi code chạy"),
    ("code-review", "Review code", "agent", "tasks.md",
     "reviewer theo góc nhìn ký từng task; 2× request-changes cùng điểm → escalation"),
    ("gate-E-b", "Gate E(b) — demo", "human", "tasks.md",
     "người xem demo trước khi Unit bàn giao sang Acceptance"),
]


def _refs(text, unit_id):
    return unit_id and unit_id in (text or "")


def unit_stops(intent_id, u, passed, gate_open, qs):
    """Vẽ mạch dừng của một Unit: mỗi điểm dừng ở một trong năm trạng thái —
    chưa tới · đang chờ (ai giữ) · đã qua · trả lại · **đã đi qua mà không dừng**.
    Trạng thái cuối là thứ đắt nhất và im lặng nhất: unit xong xuôi mà không ai ký."""
    uid = u["id"]
    bolts = u.get("boltDetails", [])
    have = {s["key"]: any(st["exists"] for b in bolts for st in b["steps"] if st["key"] == s["key"])
            for s in [{"key": k} for k, *_ in
                      (("logical-design.md",), ("contract.md",), ("tasks.md",))]}
    coded = bool(u["tasks"][1]) or u["status"] == "done" or u["evidence"]

    rvs = [r for r in RV_IDX if _refs(r.get("target"), uid) or _refs(r.get("re"), uid)]
    design_rv = [r for r in rvs if re.search(r"tech-lead|security|architect", r.get("reviewer", ""), re.I)
                 or re.search(r"design|adr|contract", r.get("target", ""), re.I)]
    code_rv = [r for r in rvs if r not in design_rv]
    reqs = [m for m in MSG_IDX if m.get("type") == "review-request" and _refs(m.get("re"), uid)]
    open_reqs = [m for m in reqs if m.get("status", "open") not in ("closed", "answered")]
    escs = [e for e in ESC_IDX if (_refs(e.get("where"), uid) or _refs(e.get("found_in"), uid))
            and e.get("status", "open") == "open"]
    esc_msgs = [m for m in MSG_IDX if m.get("type") == "escalation" and _refs(m.get("re"), uid)
                and m.get("status", "open") == "open"]
    blocking_q = [q for q in qs if q.get("blocking") and uid in (q.get("impact") or "")
                  and not re.search(r"closed|đã chốt|đóng", q.get("status", ""), re.I)]

    def verdict_state(group):
        if not group:
            return None
        last = group[-1]
        if re.search(r"request-changes", last.get("verdict", ""), re.I):
            return ("returned", "bị trả lại · " + last["id"], [last])
        if re.search(r"approve", last.get("verdict", ""), re.I):
            return ("passed", last["id"] + " · " + last.get("verdict", ""), [last])
        return ("waiting", last["id"] + " · chưa có verdict rõ ràng", [last])

    out = []
    for key, label, holder, after, why in BOLT_STOPS:
        reached = have.get(after, False) or (after == "tasks.md" and coded)
        state, meta, ev = "pending", "chưa tới", []

        if key in ("design-review", "code-review"):
            v = verdict_state(design_rv if key == "design-review" else code_rv)
            if v:
                state, meta, ev = v
            elif open_reqs:
                state, meta, ev = "waiting", "đã gửi review-request, chưa có verdict", open_reqs[-1:]
            elif reached and (coded if key == "design-review" else u["status"] == "done"):
                state, meta = "skipped", "đi qua mà KHÔNG dừng — không RV nào ký"
            elif reached:
                state, meta = "waiting", "tới điểm dừng, chưa thấy review-request nào"
            elif key == "design-review" and coded:
                # Không có chặng thiết kế thì điểm dừng này không bao giờ TỚI — code đi thẳng.
                # Đây là "bỏ qua" nặng hơn, không phải "chưa tới".
                state, meta = "skipped", "không có chặng thiết kế nên không có gì để review — code đi thẳng"
        elif key == "contract-freeze":
            frozen = any(b for b in bolts for st in b["steps"]
                         if st["key"] == "contract.md" and st["exists"])
            if frozen:
                state, meta = "passed", "contract.md có trên đĩa"
            elif reached or coded:
                state, meta = ("skipped", "code chạy mà không có contract.md") if coded else ("waiting", "chờ chốt shape")
        else:  # hai checkpoint của người
            if gate_open and gate_open.startswith("E"):
                state, meta = "waiting", "Gate E đang mở — chờ NGƯỜI quyết"
            elif "E" in passed:
                state, meta = "passed", "Gate E đã qua"
            elif u["status"] == "done":
                state, meta = "skipped", "Unit đóng mà Gate E chưa từng mở"
            elif reached:
                state, meta = "waiting", "tới checkpoint, gate chưa được mở"

        if u.get("provisional"):
            state, meta = "pending", "unit chưa có thư mục — chưa vào Bolt"
        out.append({"key": key, "label": label, "holder": holder, "why": why,
                    "state": state, "meta": meta,
                    "evidence": [{"id": e["id"], "path": e["path"]} for e in ev]})

    if escs or esc_msgs:
        ev = escs + esc_msgs
        out.append({"key": "escalation", "label": "Escalation — agent không tự quyết được",
                    "holder": "human", "why": "bất đồng 2 lần cùng một điểm, hoặc phát hiện sai từ gốc",
                    "state": "waiting", "meta": "%d mục đang chờ người" % len(ev),
                    "evidence": [{"id": e.get("id") or e["id"], "path": e["path"]} for e in ev]})
    if blocking_q:
        out.append({"key": "open-question", "label": "Câu hỏi CHẶN unit này",
                    "holder": "human", "why": "câu `CHẶN UOW-NN` còn mở thì Unit không được đi tiếp (§4.10.4)",
                    "state": "waiting", "meta": "%d câu chưa chốt" % len(blocking_q),
                    "evidence": [{"id": q["code"], "path": ""} for q in blocking_q]})
    return out


# ---------- SVG: mô hình hoá thay cho chữ (6.4.0 — yêu cầu chủ gói 2026-09-28) ----------
# Sinh server-side thành CHUỖI, nhúng vào data.js: không thư viện JS, không CDN. Màu đi bằng biến CSS
# của tower (`var(--ok)`…) nên cùng một chuỗi đọc được ở cả dark lẫn light. Mọi chữ lấy từ hồ sơ đều
# đi qua `_x()` trước khi vào SVG — UI chèn chuỗi này bằng innerHTML.
SVG_CSS = """
.ct-svg{display:block;max-width:100%;overflow-x:auto}
.ct-svg svg{display:block;width:100%;height:auto;font-family:var(--sans)}
.ct-svg text{fill:var(--ink)}
.ct-svg .mono{font-family:var(--mono)}
.ct-svg .cap{font-family:var(--mono);letter-spacing:.12em}
.ct-svg .t-muted{fill:var(--muted)}
.ct-svg .t-done{fill:var(--ok)}
.ct-svg .t-open{fill:var(--accent)}
.ct-svg .t-blocked{fill:var(--danger)}
.ct-svg .t-active{fill:var(--blue)}
.ct-svg .sh{fill:var(--surface);stroke:var(--line);stroke-width:1.4}
.ct-svg .sh.pending{fill:transparent;stroke:var(--line)}
.ct-svg .sh.done{fill:var(--ok-bg);stroke:var(--ok)}
.ct-svg .sh.auto{fill:var(--ok-bg);stroke:var(--ok);stroke-dasharray:4 3}
.ct-svg .sh.active{fill:var(--blue-bg);stroke:var(--blue);stroke-width:1.9}
.ct-svg .sh.open{fill:var(--accent-bg);stroke:var(--accent);stroke-width:2;animation:cts-pulse 1800ms ease-in-out infinite}
.ct-svg .sh.lg-open{fill:var(--accent-bg);stroke:var(--accent)}
.ct-svg .sh.blocked{fill:var(--danger-bg);stroke:var(--danger);stroke-width:2.3}
.ct-svg .sh.rec{fill:var(--blue-bg);stroke:var(--blue);stroke-width:2.6}
.ct-svg .sh.silent{stroke-dasharray:6 4}
.ct-svg .sh.undo{fill:var(--accent-bg);stroke:var(--accent);stroke-dasharray:6 4}
.ct-svg .sh.band{fill:transparent;stroke:var(--line);stroke-dasharray:2 4}
.ct-svg .sh.later{fill:var(--accent-bg);stroke:var(--accent)}
.ct-svg .pill.later{fill:var(--accent-bg);stroke:var(--accent)}
.ct-svg .pill.blue{fill:var(--blue-bg);stroke:var(--blue)}
.ct-svg .seg{stroke:var(--bg);stroke-width:1}
.ct-svg .seg.done{fill:var(--ok)}
.ct-svg .seg.active{fill:var(--blue)}
.ct-svg .seg.blocked{fill:var(--danger)}
.ct-svg .seg.pending{fill:var(--muted)}
.ct-svg .t-on{fill:var(--on-accent)}
.ct-svg .pill{fill:var(--surface-2);stroke:none}
.ct-svg .pill.rec{fill:var(--blue)}
.ct-svg .pill.ok{fill:var(--ok-bg);stroke:var(--ok)}
.ct-svg .pill.bad{fill:var(--danger-bg);stroke:var(--danger)}
.ct-svg .pill.silent{fill:transparent;stroke:var(--muted);stroke-dasharray:4 3}
.ct-svg .t-on-rec{fill:var(--on-accent)}
.ct-svg .ln{stroke:var(--line);stroke-width:1.4;fill:none}
.ct-svg .ln.done{stroke:var(--ok)}
.ct-svg .ln.rec{stroke:var(--blue);stroke-width:2.2}
.ct-svg .ln.silent{stroke-dasharray:6 4}
.ct-svg .ah{fill:var(--line);stroke:none}
.ct-svg .ah.done{fill:var(--ok)}
.ct-svg .nav{cursor:pointer}
.ct-svg .nav:hover .sh,.ct-svg .nav:focus-visible .sh{stroke-width:3}
.ct-svg .nav:focus{outline:none}
@keyframes cts-pulse{0%,100%{opacity:1}50%{opacity:.5}}
@media (prefers-reduced-motion:reduce){.ct-svg .sh.open{animation:none}}
"""

STAGE_NAMES = ["Inception", "Discovery", "Validation", "Clarify", "Units",
               "Construction", "Acceptance", "Operations"]
# Gate nằm SAU stage nào (protocol §2). Gate E không nằm giữa hai stage: nó ở TRONG mỗi Bolt của stage 6.
GATE_AFTER_STAGE = {1: "A", 3: "B", 4: "C", 5: "D", 7: "F", 8: "G"}
STAGE_DOCS = {1: ("intent-plan.md", "intent.md"), 2: ("as-is/static-model.md", "as-is/source-ledger.md"),
              3: ("as-is/source-ledger.md",), 4: ("open-questions-business.md", "open-questions.md"),
              5: ("unit-plan.md",), 7: ("acceptance.md",)}
STAGE_SCREEN = {6: "bolt", 8: "gov"}
GATE_CAPTION = {"auto": "tự quyết", "open": "chờ bạn", "blocked": "đang đứng"}


def _x(s):
    return (str("" if s is None else s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def _n(v):
    s = "%.1f" % float(v)
    return s[:-2] if s.endswith(".0") else s


def _plain(s):
    """Bỏ markdown inline — SVG không render markdown, để nguyên thì người đọc thấy dấu sao."""
    s = re.sub(r"<!--.*?-->", "", str(s or ""), flags=re.S)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[*`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _tw(s, size, mono=False):
    """Ước lượng bề rộng chữ (px). Python không đo được font thật nên ước DƯ một chút: thà xuống dòng
    sớm còn hơn chữ tràn khỏi hộp."""
    if mono:
        return len(s) * size * 0.62
    w = 0.0
    for ch in s:
        if ch in "iljtfrI.,:;'|!·()[] ":
            w += 0.32
        elif ch in "mwMW@—…%":
            w += 0.9
        elif ch.isupper() or ch.isdigit():
            w += 0.66
        else:
            w += 0.56
    return w * size


def _clip(s, max_px, size, mono=False):
    s = _plain(s)
    if _tw(s, size, mono) <= max_px:
        return s
    while s and _tw(s + "…", size, mono) > max_px:
        s = s[:-1]
    return s.rstrip() + "…"


def _wrap(text, max_px, size, max_lines=2):
    """Xuống dòng theo từ; quá `max_lines` thì cắt bằng dấu ba chấm (chữ đầy đủ vẫn nằm trong <title>
    của hình và trong khối gấp bên dưới thẻ)."""
    lines, cur = [], ""
    for w in _plain(text).split(" "):
        if not w:
            continue
        trial = (cur + " " + w).strip()
        if not cur or _tw(trial, size) <= max_px:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    cut = len(lines) > max_lines
    lines = [_clip(l, max_px, size) for l in lines[:max_lines]]
    if cut and lines and not lines[-1].endswith("…"):
        lines[-1] = _clip(lines[-1] + " …", max_px, size) if _tw(lines[-1] + " …", size) <= max_px \
            else _clip(lines[-1] + "……", max_px, size)
    return lines


def _text(x, y, s, size=12, cls="", anchor="start", weight=None):
    return '<text x="%s" y="%s" font-size="%s"%s%s%s>%s</text>' % (
        _n(x), _n(y), _n(size),
        ' text-anchor="%s"' % anchor if anchor != "start" else "",
        ' font-weight="%s"' % weight if weight else "",
        ' class="%s"' % cls if cls else "", _x(s))


def _rect(x, y, w, h, cls, rx=6):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" class="%s"/>' % (
        _n(x), _n(y), _n(w), _n(h), _n(rx), cls)


def _nav(target, title, inner):
    """Nhóm bấm được. `data-nav` là địa chỉ để UI nhảy tới (doc: · gate: · unit: · dec: · screen: · pick:)."""
    if not target:
        return "<g><title>%s</title>%s</g>" % (_x(title), inner)
    return '<g class="nav" data-nav="%s" tabindex="0" role="link"><title>%s</title>%s</g>' % (
        _x(target), _x(title), inner)


def _svg(w, h, body, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img" aria-label="%s">%s</svg>'
            % (_n(w), _n(h), _x(label), "".join(body)))


def svg_intent_flow(intent_id, base, stage, passed, gate_open, gates_auto, blocked_by, units,
                    dec_of_gate=None, show_auto_legend=False):
    """Một hình cho một intent: 8 stage theo hàng ngang, gate là hình thoi ĐÚNG chỗ protocol §2 đặt nó
    (A sau 1 · B sau 3 · C sau 4 · D sau 5 · E trong stage 6 · F sau 7 · G sau 8), dưới stage 6 là hàng Unit."""
    W, BW, BH, GAP, X0, R = 960, 80, 46, 38, 8, 14
    dec_of_gate = dec_of_gate or {}
    passed_l = {p.strip()[:1].upper() for p in passed if p.strip()}
    auto_l = {p.strip()[:1].upper() for p in gates_auto if p.strip()}
    open_l = gate_open[:1] if gate_open and gate_open != "escalation" else ""

    def stage_state(s):
        if s < stage:
            return "done"
        if s == stage:
            return "done" if (stage >= 8 and not gate_open and "G" in passed_l) else "active"
        return "pending"

    def gate_state(g):
        if open_l == g:
            return "blocked" if blocked_by else "open"
        if g in auto_l:
            return "auto"
        if g in passed_l or (g == "E" and stage > 6):
            return "done"
        return "pending"

    def gate_nav(g, state):
        if state in ("open", "blocked"):
            return "gate:g-%s-%s" % (intent_id, g)
        if state in ("done", "auto") and dec_of_gate.get(g):
            return "dec:" + dec_of_gate[g]
        return None

    def diamond(cx, cy, g):
        state = gate_state(g)
        tip = {"done": "đã qua", "auto": "AI đã tự quyết — bấm để xem và đảo nếu cần",
               "open": "đang chờ bạn quyết", "blocked": "đang đứng: " + _plain(blocked_by),
               "pending": "chưa tới"}[state]
        pts = "%s,%s %s,%s %s,%s %s,%s" % (_n(cx), _n(cy - R), _n(cx + R), _n(cy), _n(cx), _n(cy + R),
                                          _n(cx - R), _n(cy))
        inner = '<polygon points="%s" class="sh %s"/>' % (pts, state)
        inner += _text(cx, cy + 4, g, 11, "mono" + ("" if state != "pending" else " t-muted"), "middle", 700)
        return state, _nav(gate_nav(g, state), "Gate %s — %s" % (g, tip), inner)

    body, y = [], 0
    if blocked_by and open_l:
        body.append(_rect(X0, 4, W - 2 * X0, 26, "sh blocked", 5))
        body.append(_text(X0 + 12, 21, _clip("■ Đang đứng ở Gate %s — %s" % (open_l, _plain(blocked_by)),
                                             W - 2 * X0 - 24, 12), 12, "t-blocked", weight=650))
        y = 34
    # băng ba pha
    xs = [X0 + i * (BW + GAP) for i in range(8)]
    for label, a, b in (("INCEPTION", 0, 4), ("CONSTRUCTION", 5, 5), ("OPERATIONS", 6, 7)):
        body.append(_text((xs[a] + xs[b] + BW) / 2, y + 12, label, 9, "cap t-muted", "middle"))
        body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (
            _n(xs[a]), _n(y + 17), _n(xs[b] + BW), _n(y + 17)))
    top = y + 26
    cy = top + BH / 2
    for i in range(8):
        s = i + 1
        state = stage_state(s)
        x = xs[i]
        target = None
        for rel in STAGE_DOCS.get(s, ()):
            if os.path.isfile(os.path.join(base, rel)):
                target = "doc:" + os.path.relpath(os.path.join(base, rel), A)
                break
        if not target and s in STAGE_SCREEN:
            target = "screen:%s:%s" % (STAGE_SCREEN[s], intent_id)
        inner = _rect(x, top, BW, BH, "sh " + state, 7)
        inner += _text(x + 8, top + 14, str(s), 9.5, "mono t-muted")
        if state == "done":
            inner += _text(x + BW - 8, top + 14, "✓", 10, "t-done", "end", 700)
        inner += _text(x + BW / 2, top + 32, STAGE_NAMES[i], 11.5,
                       "t-muted" if state == "pending" else "", "middle", 650 if state == "active" else 500)
        tip = {"done": "đã xong", "active": "đang ở đây", "pending": "chưa tới"}[state]
        body.append(_nav(target, "Stage %d · %s — %s" % (s, STAGE_NAMES[i], tip), inner))
        # đoạn nối sang stage kế (hoặc tới gate G sau stage 8)
        g = GATE_AFTER_STAGE.get(s)
        x1, x2 = x + BW, x + BW + GAP
        ln = "ln done" if s < stage else "ln"
        ah = "ah done" if s < stage else "ah"
        if g:
            gx = x1 + GAP / 2
            gstate, gsvg = diamond(gx, cy, g)
            body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>' % (
                _n(x1), _n(cy), _n(gx - R), _n(cy), ln))
            if s < 8:
                body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>' % (
                    _n(gx + R), _n(cy), _n(x2 - 4), _n(cy), ln))
            body.append(gsvg)
            if gstate in GATE_CAPTION:
                body.append(_text(gx, top + BH + 12, GATE_CAPTION[gstate], 9,
                                  {"auto": "t-done", "open": "t-open", "blocked": "t-blocked"}[gstate],
                                  "middle", 650))
        elif s < 8:
            body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>' % (
                _n(x1), _n(cy), _n(x2 - 4), _n(cy), ln))
        if s < 8:
            body.append('<polygon points="%s,%s %s,%s %s,%s" class="%s"/>' % (
                _n(x2 - 5), _n(cy - 3.5), _n(x2), _n(cy), _n(x2 - 5), _n(cy + 3.5), ah))
    # gate E + hàng Unit dưới stage 6
    ex, ey = xs[5] + BW / 2, top + BH + 30
    estate, esvg = diamond(ex, ey, "E")
    body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(ex), _n(top + BH), _n(ex), _n(ey - R)))
    body.append(esvg)
    body.append(_text(ex + R + 7, ey + 3.5, "trong mỗi vòng xây" +
                      (" · " + GATE_CAPTION[estate] if estate in GATE_CAPTION else ""), 9,
                      {"auto": "t-done", "open": "t-open", "blocked": "t-blocked"}.get(estate, "t-muted")))
    live = [u for u in units if not u.get("descoped")]
    n_done = sum(1 for u in live if u["status"] == "done")
    by = ey + R + 12
    body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(ex), _n(ey + R), _n(ex), _n(by)))
    PW, PH, PG = 66, 20, 8
    per_row = max(1, int((W - 2 * X0 - 20 + PG) // (PW + PG)))
    rows = (len(live) + per_row - 1) // per_row
    bh = 28 + max(1, rows) * (PH + 6) + 4
    body.append(_rect(X0, by, W - 2 * X0, bh, "sh band", 8))
    body.append(_text(X0 + 12, by + 17, "PHẦN VIỆC (UNIT) · %d/%d XONG" % (n_done, len(live)) if live
                      else "PHẦN VIỆC (UNIT)", 9, "cap t-muted"))
    if not live:
        body.append(_text(X0 + 12, by + 40, "Chưa có phần việc nào — chia ở stage 5, duyệt tại Gate D.",
                          11.5, "t-muted"))
    for i, u in enumerate(live):
        ust = "done" if u["status"] == "done" else ("active" if u["status"] == "in-bolt" else "pending")
        px = X0 + 12 + (i % per_row) * (PW + PG)
        py = by + 26 + (i // per_row) * (PH + 6)
        inner = _rect(px, py, PW, PH, "sh " + ust, 10)
        inner += _text(px + PW / 2, py + 14, u["id"], 10, "mono" + (" t-muted" if ust == "pending" else ""),
                       "middle")
        word = {"done": "đã xong", "active": "đang xây", "pending": "chưa làm"}[ust]
        body.append(_nav("unit:%s:%s" % (intent_id, u["id"]),
                         "%s · %s — %s" % (u["id"], _plain(u.get("name") or ""), word), inner))
    # chú giải — mục "tự quyết" chỉ hiện khi dự án thật sự có autopilot
    ly = by + bh + 18
    legend = [("done", "đã xong")] + ([("auto", "AI tự quyết")] if show_auto_legend or auto_l else []) + \
             [("open", "chờ bạn"), ("blocked", "đang đứng"), ("active", "đang làm"), ("pending", "chưa tới")]
    lx = X0 + 2
    for cls, label in legend:
        # ô chú giải của "chờ bạn" dùng lớp riêng: cùng màu nhưng KHÔNG nhấp nháy
        body.append(_rect(lx, ly - 9, 14, 10, "sh " + ("lg-open" if cls == "open" else cls), 2))
        body.append(_text(lx + 19, ly, label, 10, "t-muted"))
        lx += 19 + _tw(label, 10) + 22
    words = "stage %d/8 (%s)" % (stage, STAGE_NAMES[max(1, min(8, stage)) - 1])
    if open_l:
        words += ", gate %s %s" % (open_l, "đang đứng: " + _plain(blocked_by) if blocked_by else "đang chờ bạn")
    return _svg(W, ly + 10, body, "Sơ đồ các bước của %s — %s, %d/%d phần việc xong"
                % (intent_id, words, n_done, len(live)))


# ----- cây lựa chọn của một câu hỏi -----
def parse_question_details(base):
    """Thẻ `### OQB-NN` / `### OQT-NN` của hai file câu hỏi → {mã: chi tiết}.

    `parse_questions` chỉ đọc bảng điều phối (mục 0) nên không biết các phương án. Ở đây đọc phần thẻ:
    bảng "Chọn một" (nhận cột theo TÊN, dùng lại `md_tables` + `col_of`), dòng "AI đề xuất" và
    "Nếu không trả lời trước hạn"."""
    out = {}
    for _aud, fname, _label in OQ_FILES:
        txt = read(os.path.join(base, fname))
        if not txt.strip():
            continue
        for m in re.finditer(r"^###\s*(OQ[BT]?-\d+)\s*[·:—–-]?\s*([^\n]*)\n(.*?)(?=^#{1,3}\s|^---\s*$|\Z)",
                             txt, re.S | re.M):
            code, title, blk = m.group(1), _plain(m.group(2)), m.group(3)
            if code in out:
                continue

            def field(label, _blk=blk):
                mm = re.search(r"\*\*" + label + r"\*\*\s*(?:\([^)]*\))?\s*:\s*(.+?)"
                               r"(?=\s+·\s+\*\*|\n\s*-\s+\*\*|\n\s*\n|\n\*\*|\Z)", _blk, re.S)
                return _plain(mm.group(1)) if mm else ""

            options = []
            for _h, header, rows in md_tables(blk):
                ci = col_of(header, r"phương án|phuong an")
                if ci < 0:
                    continue
                c_mean = col_of(header, r"nghĩa là|nghia la|hệ quả|he qua")
                c_cost = col_of(header, r"cái giá|cai gia|chi phí|chi phi|giá\b")
                c_risk = col_of(header, r"rủi ro|rui ro")
                for cells in rows:
                    raw = _plain(cells[ci]) if ci < len(cells) else ""
                    if not raw or raw.startswith("<") or raw in ("…", "..."):
                        continue
                    km = re.match(r"^([A-Z])[.):]\s*(.*)$", raw)

                    def cell(i, _c=cells):
                        return _plain(_c[i]) if 0 <= i < len(_c) else ""
                    opt = {"key": km.group(1) if km else "",
                           "name": (km.group(2) if km else raw).strip(),
                           "meaning": cell(c_mean), "cost": cell(c_cost), "risk": cell(c_risk)}
                    rv, until = parse_reversal(cell(c_cost))
                    if rv:                       # chỉ khi bản chữ GHI giá đảo — thẻ cũ không có thì hình như cũ
                        opt.update(reversal=rv, reversal_until=until)
                    options.append(opt)
                break
            rec = field("AI đề xuất")
            silent = field("Nếu không trả lời trước hạn")
            out[code] = {"code": code, "title": title, "who": field("Ai trả lời"), "due": field("Hạn"),
                         "impact": field("Ảnh hưởng"), "context": field("Bối cảnh"),
                         "options": options[:6], "recommend": rec, "silent": silent,
                         "checked": field("Đã soát mà không thấy đáp án"),
                         "xref": field("Soi chiếu"),
                         # §4.10.14 — câu này có trả lời thì những câu nào tự hết mở
                         "unlocks": [u for u in dict.fromkeys(re.findall(r"\b(?:OQ[BT]?-\d+|D\d+)\b", field("Gỡ được")))
                                     if u != code]}
    return out


def _pick_option(text, options, lead_only=False):
    """Câu "AI đề xuất: B — …" / "đi theo phương án A, ghi [ASSUMED]" trỏ vào phương án nào.
    Không đoán: không nhận ra thì trả "" và hình không tô phương án nào."""
    t = _plain(text)
    if not t or not options:
        return ""
    keys = {o["key"] for o in options if o["key"]}
    m = re.match(r"^([A-Z])(?![\w])", t)
    if m and m.group(1) in keys:
        return m.group(1)
    if not lead_only:
        m = re.search(r"(?:phương án|phuong an|theo|chọn|chon|áp|giữ)\s+(?:phương án\s+)?([A-Z])(?![\w])", t)
        if m and m.group(1) in keys:
            return m.group(1)
    low = t.lower()
    hits = [o for o in options if len(o["name"]) >= 4 and o["name"].lower() in low]
    if len(hits) == 1:
        return hits[0]["key"] or hits[0]["name"]
    return ""


def _rev_badge(o):
    """Huy hiệu giá đảo của MỘT phương án → (nhãn, lớp viên, lớp chữ, bề rộng). Đảo rẻ mà có hạn
    (`reversal_until`, §4.10.16) thì không còn là "rẻ" vô điều kiện: hổ phách, ghi rõ mốc."""
    if o.get("reversal") == "đắt":
        return "đảo đắt", "bad", "t-blocked", 64
    until = _plain(o.get("reversal_until") or "")
    if until:
        lab = _clip("đảo rẻ tới: " + until, 210, 9.5)
        return lab, "later", "t-open", _tw(lab, 9.5) * 1.08 + 18
    return "đảo rẻ", "", "t-muted", 64


def parse_reversal(text):
    """`… · Đảo: rẻ tới trước phát hành` trong ô giá của một phương án → ("rẻ", "trước phát hành").
    Không có chữ `Đảo:` ⇒ ("", "") — không suy diễn."""
    m = re.search(r"đảo\s*:\s*(rẻ|đắt|re|dat)\b(?:\s*(?:tới|đến|toi|den)\s*:?\s*([^·;|]+))?", _plain(text), re.I)
    if not m:
        return "", ""
    kind = "đắt" if m.group(1).lower() in ("đắt", "dat") else "rẻ"
    return kind, (m.group(2) or "").strip().rstrip(".") if kind == "rẻ" else ""


def svg_question_tree(q, d, width=760, extras=None):
    """Nút gốc = câu hỏi rút gọn; mỗi nhánh = một phương án kèm cái giá; phương án AI đề xuất tô đậm;
    phương án áp khi im lặng viền nét đứt; hạn + người trả lời ở góc phải trên.

    Dùng cho HAI nguồn: thẻ câu hỏi trong open-questions (mặc định — chuỗi ra y như trước) và `decisions`
    của human-view (`width=1000`, `extras` = {kind, reversal, reverse_by, blocks[(mã, có thật?)], q_lines,
    tip}): thêm huy hiệu loại + "đảo đắt/rẻ" ở đầu, và hàng "đảo bằng · chặn UOW" ở chân cây."""
    opts = d.get("options") or []
    if len(opts) < 2:
        return None, {}
    ex = extras or {}
    W, RX = width, 10
    RW = 232 if width <= 760 else 300
    OX = RX + RW + 58
    OW = W - OX - 10
    rec = _pick_option(d.get("recommend"), opts, lead_only=False)
    fallback_txt = d.get("silent") or q.get("fallback") or ""
    sil = _pick_option(fallback_txt, opts)

    def okey(o):
        return o["key"] or o["name"]

    body = []
    head = q.get("code") or d.get("code") or ""
    impact = _plain(q.get("impact") or d.get("impact") or "")
    body.append(_text(RX, 15, head, 11, "mono", weight=700))
    hx = RX + _tw(head, 11, True) + 10
    for label, cls, tcls in ex.get("badges") or ():
        bw = _tw(label, 9.5) * 1.1 + 18           # chữ đậm rộng hơn ước lượng — chừa lề cho khỏi tràn viên
        body.append(_rect(hx, 2.5, bw, 18, "pill " + cls, 9))
        body.append(_text(hx + bw / 2, 15, label, 9.5, tcls, "middle", 700))
        hx += bw + 6
    if impact:
        body.append(_text(hx, 15, _clip(impact, 190, 10.5), 10.5,
                          "t-blocked" if q.get("blocking") else "t-muted", weight=650 if q.get("blocking") else None))
    who = _plain(q.get("who") or d.get("who") or "")
    due = _plain(q.get("due") or d.get("due") or "")
    corner = " · ".join(x for x in (("Hạn: " + due) if due else "", ("Trả lời: " + who) if who else "") if x)
    if corner:
        body.append(_text(W - 10, 15, _clip(corner, 440, 10.5), 10.5, "t-muted", "end"))

    # đo từng nhánh trước, rồi mới đặt nút gốc vào giữa
    y, boxes = 28, []
    for o in opts:
        is_rec, is_sil = okey(o) == rec and bool(rec), okey(o) == sil and bool(sil)
        badge_w = (74 if is_rec else 0) + (82 if is_sil else 0) + (6 if is_rec and is_sil else 0)
        if o.get("reversal"):
            badge_w += _rev_badge(o)[3] + (6 if badge_w else 0)
        name_l = _wrap(o["name"], OW - 52 - badge_w - (10 if badge_w else 0), 12.5, 2)
        mean_l = _wrap(o["meaning"], OW - 56, 11.5, 2) if o["meaning"] else []
        cost = " · ".join(x for x in (("giá: " + o["cost"]) if o["cost"] else "",
                                       ("rủi ro: " + o["risk"]) if o["risk"] else "") if x)
        h = 14 + 16 * len(name_l) + 15 * len(mean_l) + (17 if cost else 0) + 6
        boxes.append((o, y, max(h, 40), name_l, mean_l, cost, is_rec, is_sil))
        y += max(h, 40) + 10
    note = None
    if ex.get("note"):
        note_l = _wrap(ex["note"], OW - 28, 11.5, 3)
        note = (y, 14 + 15 * len(note_l), note_l)
        y += note[1] + 10
    elif fallback_txt and not sil:
        note_l = _wrap("Nếu im lặng: " + fallback_txt, OW - 28, 11.5, 2)
        note = (y, 14 + 15 * len(note_l), note_l)
        y += note[1] + 10
    bottom = y - 10
    q_lines = _wrap(d.get("title") or q.get("q") or "", RW - 24, 12.5, ex.get("q_lines", 5))
    rh = 30 + 17 * len(q_lines)
    total = max(bottom, 28 + rh)
    ry = 28 + (total - 28 - rh) / 2
    rcy = ry + rh / 2
    inner = _rect(RX, ry, RW, rh, "sh active", 8)
    inner += _text(RX + 12, ry + 16, "CÂU HỎI", 9, "cap t-muted")
    for i, l in enumerate(q_lines):
        inner += _text(RX + 12, ry + 34 + 17 * i, l, 12.5, weight=600)
    body.append(_nav(None, d.get("title") or q.get("q") or "", inner))

    def branch(y_mid, cls):
        x1, x2 = RX + RW, OX
        xm = (x1 + x2) / 2
        return '<path d="M%s %s C%s %s %s %s %s %s" class="%s"/>' % (
            _n(x1), _n(rcy), _n(xm), _n(rcy), _n(xm), _n(y_mid), _n(x2), _n(y_mid), cls)

    for o, oy, oh, name_l, mean_l, cost, is_rec, is_sil in boxes:
        body.append(branch(oy + oh / 2, "ln" + (" rec" if is_rec else "") + (" silent" if is_sil else "")))
        cls = "sh" + (" rec" if is_rec else "") + (" silent" if is_sil else "")
        inner = _rect(OX, oy, OW, oh, cls, 8)
        if o["key"]:
            inner += '<circle cx="%s" cy="%s" r="11" class="%s"/>' % (
                _n(OX + 22), _n(oy + 21), "pill rec" if is_rec else "pill")
            inner += _text(OX + 22, oy + 25, o["key"], 11.5, "mono" + (" t-on-rec" if is_rec else ""), "middle", 700)
        tx = OX + (44 if o["key"] else 14)
        ty = oy + 22
        for l in name_l:
            inner += _text(tx, ty, l, 12.5, weight=700 if is_rec else 600)
            ty += 16
        for l in mean_l:
            inner += _text(tx, ty, l, 11.5, "t-muted")
            ty += 15
        if cost:
            inner += _text(tx, ty + 1, _clip(cost, OW - 56, 11, True), 11, "mono t-open")
        bx = OX + OW - 10
        if is_sil:
            inner += _rect(bx - 82, oy + 9, 82, 18, "pill silent", 9)
            inner += _text(bx - 41, oy + 21.5, "nếu im lặng", 9.5, "t-muted", "middle", 650)
            bx -= 88
        if is_rec:
            inner += _rect(bx - 74, oy + 9, 74, 18, "pill rec", 9)
            inner += _text(bx - 37, oy + 21.5, "AI đề xuất", 9.5, "t-on-rec", "middle", 700)
            bx -= 80
        if o.get("reversal"):
            rlab, rcls, rtcls, rw = _rev_badge(o)
            inner += _rect(bx - rw, oy + 9, rw, 18, "pill " + rcls, 9)
            inner += _text(bx - rw / 2, oy + 21.5, rlab, 9.5, rtcls, "middle", 700)
        tip = "%s%s%s%s — %s" % (
            (o["key"] + ". ") if o["key"] else "", o["name"],
            (" · giá: " + o["cost"]) if o["cost"] else "",
            (" · AI đề xuất" if is_rec else "") + (" · áp khi bạn im lặng" if is_sil else ""),
            ex.get("tip") or "bấm để điền vào ô trả lời")
        body.append(_nav("pick:" + okey(o), tip, inner))
    if note:
        ny, nh, note_l = note
        body.append(branch(ny + nh / 2, "ln silent"))
        inner = _rect(OX, ny, OW, nh, "sh silent" if not ex.get("note") else "sh blocked silent", 8)
        for i, l in enumerate(note_l):
            inner += _text(OX + 14, ny + 19 + 15 * i, l, 11.5, "t-muted" if not ex.get("note") else "t-blocked")
        body.append(_nav(None, ex.get("note") or ("Nếu im lặng: " + _plain(fallback_txt)), inner))
    if ex.get("reverse_by") or ex.get("blocks"):
        fy = total + 10
        undo_l = _wrap("↺ đảo bằng: " + ex["reverse_by"], W - 2 * RX - 28, 11.5, 2) if ex.get("reverse_by") else []
        fh = 10 + 15 * len(undo_l) + (24 if ex.get("blocks") else 0) + 6
        inner = _rect(RX, fy, W - 2 * RX, fh, "sh undo" if ex.get("reversal") != "đắt" else "sh blocked", 8)
        ty = fy + 19
        for l in undo_l:
            inner += _text(RX + 14, ty, l, 11.5, "t-open" if ex.get("reversal") != "đắt" else "t-blocked", weight=600)
            ty += 15
        body.append(_nav(None, "Đảo bằng: " + (ex.get("reverse_by") or ""), inner))
        if ex.get("blocks"):
            bx = RX + 14
            body.append(_text(bx, ty + 5, "quyết định này giữ:", 10.5, "t-muted"))
            bx += _tw("quyết định này giữ:", 10.5) + 8
            for uid, known in ex["blocks"]:
                lab = uid + ("" if known else "?")
                bw = _tw(lab, 10, True) + 14
                body.append(_nav(None, uid + (" — phần việc chỉ làm khi điểm này chốt đúng hướng" if known
                                              else " — mã này KHÔNG có trong bảng phần việc"),
                                 _rect(bx, ty - 8, bw, 18, "pill " + ("later" if known else "bad"), 9) +
                                 _text(bx + bw / 2, ty + 4.5, lab, 10, "mono" + ("" if known else " t-blocked"),
                                       "middle", 700)))
                bx += bw + 6
        total = fy + fh
    label = "Cây lựa chọn cho %s: %s. %d phương án%s%s" % (
        head, _plain(d.get("title") or q.get("q") or ""), len(opts),
        ("; AI đề xuất " + rec) if rec else "", ("; im lặng thì áp " + sil) if sil else "")
    meta = {"options": [{"key": okey(o), "label": ((o["key"] + ". ") if o["key"] else "") + o["name"],
                         "cost": o["cost"]} for o in opts],
            "recommend": rec, "silent": sil,
            "recommendWhy": d.get("recommend", ""), "silentText": fallback_txt,
            "context": d.get("context", ""), "checked": d.get("checked", "")}
    return _svg(W, total + 8, body, label), meta


# ----- quyết định (DEC) — đọc TRƯỚC vòng intent để flow biết gate nào đóng bằng DEC nào -----
def dec_fields(body):
    """Dòng `- Nhãn: giá trị` của một DEC. Mẫu protocol §5 đặt hai nhãn trên một dòng, cách nhau bằng
    nhiều khoảng trắng — tách cả hai. Một nhãn lặp nhiều lần (`Bỏ:`) thì giữ đủ mọi lần."""
    out = {}
    for line in body.splitlines():
        for part in re.split(r"\s{2,}(?=-\s)", line.strip()):
            mm = re.match(r"^-\s*\**([^:*\n]{2,32}?)\**\s*:\s*(.*)$", part.strip())
            if mm:
                out.setdefault(mm.group(1).strip().lower(), []).append(mm.group(2).strip())
    return out


def _split_cost(v, word):
    """`<phương án> — giá: <…>` / `<phương án> — vì: <…>` → (phương án, phần sau)."""
    parts = re.split(r"\s+[—–-]\s+" + word + r"\s*:\s*", v, maxsplit=1, flags=re.I)
    return (_plain(parts[0]), _plain(parts[1]) if len(parts) > 1 else "")


# Dòng `- Áp: OQB-01 = A · OQT-03 = C (thay DEC-0003)` (mẫu DEC 6.5.1) là nguồn MÁY ĐỌC của "DEC này áp phương án
# nào cho mã nào". Mẫu nhận dạng dùng chung với `autopilot_check.py` (AP13/AP14) — import, không chép, để tower và
# checker không bao giờ đọc cùng một dòng ra hai kết quả.
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from autopilot_check import APPLY_RE
except Exception:  # noqa: BLE001 — gói cài thiếu checker: tower vẫn phải chạy, chỉ không đọc được dòng Áp
    APPLY_RE = None


def applied_index():
    """(intent, mã) → [{dec, gate, opt, repl}] theo thứ tự DEC — từ dòng `Áp`; DEC không có dòng `Áp` thì rơi về
    bốn mẫu câu văn (`dec_picks`). Cùng cách gom với AP14 của autopilot_check."""
    out = {}
    for d in decisions:
        if not d.get("autopilot"):
            continue
        for code, opt, repl in d.get("applied") or []:
            out.setdefault((d["intent"], code), []).append(
                {"dec": d["id"], "gate": (d.get("gate") or "")[:1].upper(), "opt": opt, "repl": repl})
    return out


def live_applied(intent_id, code, index=None):
    """Các lần áp CÒN HIỆU LỰC cho một mã. Luật của AP14: DEC bị một DEC sau ghi `(thay DEC-NNNN)` cho mã đó thì
    hết hiệu lực Ở MÃ ĐÓ — các mã khác của nó vẫn còn. Thêm một điều tower biết mà checker không: DEC đã bị NGƯỜI
    đảo (steer / `reverses:`) thì cũng không còn là trạng thái đang áp."""
    picks = (index if index is not None else applied_index()).get((intent_id, code), [])
    replaced = {p["repl"] for p in picks if p["repl"]}
    return [p for p in picks if p["dec"] not in replaced
            and not _reversed_by.get(p["dec"]) and not STEERS.get(p["dec"])]


_CODE = r"(?:OQ[BT]?-\d+|[DT]\d+)"
PICK_PATTERNS = [
    re.compile(r"(?<![\w-])(" + _CODE + r")\s*(?:=|:|→|->|⇒|—|–)\s*(?:phương\s*án\s*)?\**([A-E])\**(?![\w])"),
    re.compile(r"(?<![\w-])(" + _CODE + r")\s*\(\s*(?:phương\s*án\s*)?([A-E])\s*\)"),
    re.compile(r"(?<![\w-])(" + _CODE + r")\s+(?:chọn|áp|theo|lấy)\s+(?:phương\s*án\s*)?\**([A-E])\**(?![\w])"),
]
PICK_REVERSED = re.compile(r"phương\s*án\s*\**([A-E])\**\s*(?:của|cho)\s*(?:câu\s*(?:hỏi\s*)?)?(" + _CODE + r")(?![\w-])")


def dec_picks(text):
    """Một DEC chọn phương án nào cho mã câu hỏi nào — CHỈ khi viết rõ (`OQT-03 = A` · `OQT-03 (A)` ·
    `OQT-03 chọn A` · `phương án C của OQT-03`). Cùng một mã mà đọc ra hai chữ cái thì bỏ mã đó: không đoán."""
    seen = {}
    for pat in PICK_PATTERNS:
        for m in pat.finditer(text or ""):
            seen.setdefault(m.group(1), set()).add(m.group(2))
    for m in PICK_REVERSED.finditer(text or ""):
        seen.setdefault(m.group(2), set()).add(m.group(1))
    return {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}


def parse_decisions():
    out = []
    txt = read(os.path.join(CM, "governance", "decisions-log.md"))
    # Nhóm thứ năm (`· autopilot`) là phần THÊM ở 6.4.0; tiêu đề bốn đoạn cũ khớp y như trước.
    for m in re.finditer(r"^## (DEC-\d+) · ([^·\n]+) · ([^·\n]+) · (\S+)(?: · ([^\n]+))?\n(.*?)(?=\n## |\Z)",
                         txt, re.S | re.M):
        body = m.group(6)
        what = re.search(r"Quyết định:\s*(.+)", body)
        basis = re.search(r"Căn cứ:\s*(.+)", body)
        d = {"id": m.group(1), "when": m.group(2).strip(), "gate": m.group(3).replace("Gate", "").strip(),
             "codes": sorted(set(re.findall(r"(?<![\w-])(?:OQ[BT]?-\d+|[DT]\d+)(?![\w-])", body))),
             "by": "Human supervisor", "what": (what.group(1).strip()[:180] if what else ""),
             "basis": (basis.group(1).strip()[:60] if basis else ""), "_to": m.group(4)}
        f = dec_fields(body)
        who = (f.get("người quyết") or [""])[0]
        rev = re.search(r"DEC-\d+", (f.get("reverses") or [""])[0])
        if rev:
            d["reverses"] = rev.group(0)
        if (m.group(5) or "").strip().lower().startswith("autopilot") or re.match(r"autopilot\b", who, re.I):
            chosen, cost = _split_cost((f.get("chọn") or [""])[0], "giá")
            shown = _plain((f.get("hiện ở") or [""])[0])
            checks = (f.get("block check") or [""])[0]
            hits = re.findall(r"#(\d)\s*hit\b[:\s]*([^·#]*)", checks, re.I)
            d.update({
                "by": "autopilot", "autopilot": True, "intent": m.group(4),
                "what": _plain((f.get("quyết định") or [""])[0])[:240] or d["what"],
                "basis": _plain((f.get("căn cứ") or [""])[0])[:120] or d["basis"],
                "impact": _plain((f.get("ảnh hưởng") or [""])[0])[:240],
                "chosen": chosen, "chosenCost": cost,
                "rejected": [dict(zip(("option", "why"), _split_cost(v, "vì"))) for v in f.get("bỏ", []) if v],
                "undo": _plain((f.get("đảo bằng") or [""])[0]),
                "shownAt": shown, "blockCheck": _plain(checks),
                "blockPass": len(re.findall(r"#\d\s*pass\b", checks, re.I)),
                "blockHits": [{"no": h[0], "why": _plain(h[1])} for h in hits],
                "reason": _plain((f.get("reason") or [""])[0]),
                "escRefs": sorted(set(re.findall(r"ESC-\d+", " ".join((f.get("căn cứ") or []) + (f.get("hiện ở") or []))))),
                "basisFull": _plain(" · ".join((f.get("căn cứ") or []) + (f.get("hiện ở") or []))),
                "picks": dec_picks(_plain(" · ".join((f.get("quyết định") or []) + (f.get("chọn") or []) +
                                                     (f.get("căn cứ") or [])))),
                "hasApply": bool(APPLY_RE) and any(x.strip() for x in f.get("áp") or []),
                "missing": [k for k, lbl in (("chọn", "Chọn"), ("bỏ", "Bỏ"), ("đảo bằng", "Đảo bằng"),
                                             ("hiện ở", "Hiện ở"), ("block check", "Block check"))
                            if not (f.get(k) or [""])[0]],
            })
        if d.get("autopilot"):
            # dòng Áp đọc TRƯỚC; không có thì mới dùng câu văn (khi đó `reverses:` đóng vai `thay` cho mọi mã)
            if d["hasApply"]:
                d["applied"] = [list(x) for x in APPLY_RE.findall(" ".join(f.get("áp") or []))]
            else:
                d["applied"] = [[c, o, d.get("reverses", "")] for c, o in sorted(d["picks"].items())]
        out.append(d)
    return out


def scan_steers():
    """`inbox/steer-*.json` — người bấm Đảo trên tower. Còn trong `inbox/` = chưa áp; trong
    `inbox/processed/` = đã áp. Trả {DEC: "pending"|"applied"} (applied thắng)."""
    out = {}
    for sub, state in (("", "pending"), ("processed", "applied")):
        d = os.path.join(A, "inbox", sub) if sub else os.path.join(A, "inbox")
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not (f.startswith("steer-") and f.endswith(".json")):
                continue
            try:
                with open(os.path.join(d, f), encoding="utf-8") as fh:
                    j = json.load(fh)
            except Exception:  # noqa: BLE001
                continue
            dec = str(j.get("dec") or "").strip()
            if re.match(r"^DEC-\d+$", dec) and (state == "applied" or dec not in out):
                out[dec] = state
    return out


def autopilot_config():
    """`governance/autopilot.md` — override thắng bản gốc, cùng luật với mọi governance khác.
    Không có file = `lead` (protocol §2.3): tower hiển thị y như trước 6.4.0."""
    for p in (os.path.join(A, "overrides", "governance", "autopilot.md"),
              os.path.join(CM, "governance", "autopilot.md")):
        if os.path.isfile(p):
            d = fm(read(p))
            mode = (d.get("mode") or "lead").strip().strip('"\'').lower()
            return {"present": True, "mode": mode if mode in ("autopilot", "lead") else "lead",
                    "waitHours": num(d.get("wait_hours"), 0.0), "path": os.path.relpath(p, A)}
    return {"present": False, "mode": "lead", "waitHours": 0.0, "path": None}


def resolve_shown_doc(intent_id, shown):
    """`Hiện ở: unit-plan.md#3` → đường dẫn tài liệu (tương đối `.ai-dlc/`) mà tower mở được."""
    rel = re.split(r"[#\s]", (shown or "").strip(), maxsplit=1)[0].strip("`")
    if not rel.endswith(".md"):
        return None
    for cand in (os.path.join(idir, intent_id, rel), os.path.join(CM, rel), os.path.join(A, rel)):
        real = os.path.realpath(cand)
        if os.path.isfile(real) and real.startswith(os.path.realpath(CM) + os.sep):
            return os.path.relpath(cand, A)
    return None


def svg_autopilot_decision(d):
    """Hai cột CHỌN vs BỎ, mỗi bên kèm cái giá / lý do; hàng dưới là cách đảo và nơi quyết định hiện hình."""
    W, X0, GAP = 760, 10, 28
    CW = (W - 2 * X0 - GAP) / 2
    body = []
    body.append(_text(X0, 15, d["id"], 11, "mono", weight=700))
    body.append(_text(X0 + _tw(d["id"], 11, True) + 10, 15,
                      _clip(" · ".join(x for x in ("Gate " + d["gate"] if re.match(r"^[A-G]", d["gate"] or "")
                                                   else d["gate"], d["when"]) if x), 300, 10.5),
                      10.5, "t-muted"))
    hits = d.get("blockHits") or []
    chip = ("block check: hit #" + ", #".join(h["no"] for h in hits)) if hits else \
           ("block check: %d/6 pass" % d["blockPass"] if d.get("blockPass") else "block check: chưa ghi")
    cw = _tw(chip, 10, True) + 18
    body.append(_rect(W - X0 - cw, 3, cw, 18, "pill " + ("bad" if hits or not d.get("blockPass") else "ok"), 9))
    body.append(_text(W - X0 - cw / 2, 15.5, chip, 10,
                      "mono " + ("t-blocked" if hits or not d.get("blockPass") else "t-done"), "middle"))
    top = 30
    ch_l = _wrap(d.get("chosen") or "(DEC không ghi dòng Chọn)", CW - 28, 13, 3)
    cost_l = _wrap("giá: " + d["chosenCost"], CW - 28, 11.5, 2) if d.get("chosenCost") else []
    lh = 30 + 17 * len(ch_l) + 15 * len(cost_l) + 10
    rej = d.get("rejected") or [{"option": "(DEC không ghi dòng Bỏ)", "why": ""}]
    rboxes, ry = [], top
    for r in rej[:4]:
        o_l = _wrap(r["option"], CW - 28, 12.5, 2)
        w_l = _wrap("vì: " + r["why"], CW - 28, 11.5, 2) if r.get("why") else []
        h = 30 + 16 * len(o_l) + 15 * len(w_l) + 8
        rboxes.append((ry, h, o_l, w_l, r))
        ry += h + 8
    rh_total = ry - 8 - top
    lh = max(lh, rh_total)
    lx, rx = X0, X0 + CW + GAP
    inner = _rect(lx, top, CW, lh, "sh done", 8)
    inner += _text(lx + 14, top + 17, "CHỌN", 9, "cap t-done", weight=700)
    ty = top + 37
    for l in ch_l:
        inner += _text(lx + 14, ty, l, 13, weight=700)
        ty += 17
    for l in cost_l:
        inner += _text(lx + 14, ty + 1, l, 11.5, "t-open")
        ty += 15
    body.append(_nav(None, "Chọn: %s%s" % (d.get("chosen") or "", (" — giá: " + d["chosenCost"])
                                           if d.get("chosenCost") else ""), inner))
    body.append(_text(lx + CW + GAP / 2, top + lh / 2 + 4, "≠", 15, "t-muted", "middle"))
    for by_, h, o_l, w_l, r in rboxes:
        inner = _rect(rx, by_, CW, h, "sh pending", 8)
        inner += _text(rx + 14, by_ + 17, "BỎ", 9, "cap t-muted", weight=700)
        ty = by_ + 36
        for l in o_l:
            inner += _text(rx + 14, ty, l, 12.5, "t-muted", weight=600)
            ty += 16
        for l in w_l:
            inner += _text(rx + 14, ty, l, 11.5, "t-muted")
            ty += 15
        body.append(_nav(None, "Bỏ: %s%s" % (r["option"], (" — vì: " + r["why"]) if r.get("why") else ""), inner))
    y = top + lh + 12
    undo_l = _wrap(d.get("undo") or "(DEC không ghi dòng Đảo bằng)", W - 2 * X0 - 28, 12, 2)
    uh = 28 + 16 * len(undo_l) + 6
    inner = _rect(X0, y, W - 2 * X0, uh, "sh undo", 8)
    inner += _text(X0 + 14, y + 17, "↺ ĐẢO BẰNG", 9, "cap t-open", weight=700)
    for i, l in enumerate(undo_l):
        inner += _text(X0 + 14, y + 35 + 16 * i, l, 12)
    body.append(_nav(None, "Đảo bằng: " + (d.get("undo") or ""), inner))
    y += uh + 16
    if d.get("shownAt"):
        inner = _text(X0, y, _clip("Hiện ở: " + d["shownAt"] + (" ↗" if d.get("shownDoc") else ""),
                                   W - 2 * X0, 11, True), 11, "mono t-active")
        body.append(_nav(("doc:" + d["shownDoc"]) if d.get("shownDoc") else None,
                         "Mở tài liệu nơi quyết định này hiện hình", inner))
        y += 8
    return _svg(W, y + 4, body, "%s — AI đã tự quyết. Chọn: %s. Bỏ: %s. Đảo bằng: %s" % (
        d["id"], d.get("chosen") or "?", "; ".join(r["option"] for r in rej), d.get("undo") or "?"))


# ---------- human-view: trang mô hình cho NGƯỜI xem (protocol §2.4 — yêu cầu chủ gói 2026-09-28) ----------
# Bản chữ (intent-plan.md…) là nguồn sự thật cho AI. Bản mô hình là file RIÊNG `views/<tên>.view.json` do
# một agent khác (dlc-modeler) viết — tower chỉ đọc file đó, KHÔNG đọc gì nhúng trong tài liệu: còn đường
# nhúng là còn cửa cho tác giả tự vẽ mô hình của chính mình. Số giờ + thứ tự phần việc lấy từ bảng Unit,
# nguồn lấy từ bảng nguồn — view không lặp lại số, nên hình không lệch bản chữ ở hai thứ dễ lệch nhất.
HV_W = 1000
HV_GATE_OF_DOC = {"intent-plan.md": "A", "unit-plan.md": "D"}
HV_LEVEL = {"cao": 0, "vừa": 1, "vua": 1, "thấp": 2, "thap": 2}
# "chưa có" · "chưa rõ (tạm: orchestrator)" · "—" đều là CHƯA có người chịu: tạm giữ không phải là chủ
HV_NO_OWNER = r"^(chưa|chua|không có|khong co|-|—|\?)"


def view_path_of(doc_path):
    """Cùng quy ước với `human_view_check.view_path`: `<thư mục tài liệu>/views/<tên>.view.json`."""
    d, name = os.path.split(doc_path)
    return os.path.join(d, "views", os.path.splitext(name)[0] + ".view.json")


def parse_human_view(doc_path):
    """→ (dict | None, lỗi | None). Không có file view ⇒ (None, None): tower hiển thị y như trước
    (toàn văn, phải đọc — §2.4.7)."""
    vp = view_path_of(doc_path)
    if not os.path.isfile(vp):
        return None, None
    try:
        hv = json.loads(read(vp))
    except ValueError as e:
        return None, str(e)
    if not isinstance(hv, dict):
        return None, "phải là một object JSON, đang là %s" % type(hv).__name__
    return hv, None


def _s(v):
    return "" if v is None or isinstance(v, (dict, list)) else _plain(str(v))


def _hours(v):
    """2.75 → `2,75` · 10.0 → `10` (dấu phẩy thập phân, như bản chữ viết)."""
    t = ("%.2f" % float(v)).rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _hv_list(hv, key, warns, of=(dict,)):
    v = hv.get(key)
    if v is None:
        return []
    if not isinstance(v, list):
        warns.append("`%s` phải là một danh sách — bỏ phần hình này" % key)
        return []
    ok = [x for x in v if isinstance(x, of)]
    if len(ok) != len(v):
        warns.append("`%s` có %d mục sai kiểu — bỏ các mục đó" % (key, len(v) - len(ok)))
    return ok


def _hv_dict(hv, key, warns):
    v = hv.get(key)
    if v is None:
        return {}
    if not isinstance(v, dict):
        warns.append("`%s` phải là một object — bỏ phần hình này" % key)
        return {}
    return v


def _strs(v):
    return [_s(x) for x in v if _s(x)] if isinstance(v, list) else []


def unit_table_for(base, doc_name):
    """Bảng Unit của CHÍNH tài liệu đó — nguồn của giờ và thứ tự. Dùng lại parser đã có."""
    if doc_name == "unit-plan.md":
        return [{"id": r["id"], "name": r["name"], "est": r["est"]} for r in parse_plan_rows(base).values()]
    return [{"id": u["id"], "name": u["name"], "est": u["estimate"]} for u in parse_provisional_units(base)]


def source_extras(text):
    """Người giữ nguồn + rủi ro nếu bỏ qua, theo mã nguồn. `parse_sources` không mang hai cột này và
    thêm vào đó sẽ đổi `sourcesByIntent` của mọi dự án — nên đọc riêng ở đây."""
    out = {}
    for _h, header, rows in md_tables(text):
        i_id = col_of(header, r"^#$", r"^id$", r"^stt$")
        i_own = col_of(header, r"ai\s*sở\s*hữu", r"ai\s*giữ", r"owner", r"chủ")
        i_risk = col_of(header, r"rủi\s*ro")
        if i_id < 0 or (i_own < 0 and i_risk < 0):
            continue
        for c in rows:
            sid = re.sub(r"[*`~]", "", c[i_id] if i_id < len(c) else "").strip()
            if re.match(r"^S\d+$", sid) and sid not in out:
                out[sid] = {"owner": _plain(c[i_own]) if 0 <= i_own < len(c) else "",
                            "risk": _plain(c[i_risk]) if 0 <= i_risk < len(c) else ""}
    return out


def _goto_chip(x_right, y, dec_id, decision_ids, warns, where):
    """Chip nhỏ "→ D6" đặt sát mép phải: phần tử này là một mặt của điểm cần chốt D6 — bấm để cuộn tới cây.
    Trả (svg, bề rộng). Mã không có trong `decisions` ⇒ "D6?" đỏ + cảnh báo, vẫn vẽ."""
    ok = dec_id in decision_ids
    if not ok:
        warns.append("%s trỏ %s — không có điểm cần chốt nào mang mã đó" % (where, dec_id))
    lab = "→ " + dec_id + ("" if ok else "?")
    w = _tw(lab, 10, True) + 14
    inner = _rect(x_right - w, y, w, 18, "pill " + ("blue" if ok else "bad"), 9)
    inner += _text(x_right - w / 2, y + 12.6, lab, 10, "mono " + ("t-active" if ok else "t-blocked"), "middle", 700)
    return _nav(("goto:" + dec_id) if ok else None,
                ("Cùng một chuyện với điểm cần chốt %s — bấm để tới cây lựa chọn" % dec_id) if ok
                else ("%s — KHÔNG có điểm cần chốt nào mang mã này" % dec_id), inner), w


def hv_gaps(hv):
    """`gaps[]` — schema 2 là chuỗi, schema 3 là {text, ref, decision}. Trả về một dạng duy nhất."""
    out = []
    for g in hv.get("gaps") if isinstance(hv.get("gaps"), list) else []:
        if isinstance(g, dict) and _s(g.get("text")):
            out.append({"text": _s(g.get("text")), "ref": _s(g.get("ref")), "decision": _s(g.get("decision"))})
        elif _s(g):
            out.append({"text": _s(g), "ref": "", "decision": ""})
    return out


def unit_deps(text):
    """Cột "Phụ thuộc" của bảng Unit trong bản chữ → {UOW: [UOW nó phải chờ]}. View không mang thông tin
    này (và không nên lặp lại): thứ tự và phụ thuộc là của bản chữ."""
    out = {}
    for _h, header, rows in md_tables(text):
        i_dep = col_of(header, r"phụ\s*thuộc", r"phu\s*thuoc", r"depends")
        if i_dep < 0:
            continue
        for c in rows:
            uid = re.sub(r"[*`~]", "", c[0] if c else "").strip()
            if re.match(r"^UOW-\d+$", uid) and uid not in out:
                out[uid] = [d for d in re.findall(r"UOW-\d+", c[i_dep] if i_dep < len(c) else "") if d != uid]
    return out


def _lines(x, y, lines, size, lh, cls="", weight=None, anchor="start"):
    return "".join(_text(x, y + i * lh, l, size, cls, anchor, weight) for i, l in enumerate(lines))


def _chip(x, y, label, cls="", tcls="", size=10, mono=True, h=18):
    """Viên nhãn nhỏ; trả (svg, bề rộng). `y` là mép trên."""
    w = _tw(label, size, mono) + 14
    return (_rect(x, y, w, h, "pill " + cls, h / 2) +
            _text(x + w / 2, y + h / 2 + size * 0.36, label, size, ("mono " if mono else "") + tcls, "middle", 700), w)


def hv_fig_goal(hv, warns):
    """ĐÍCH — trái: đang đau gì (kèm con số); phải: từng outcome với `hiện nay → đích`."""
    pain = _hv_dict(hv, "pain", warns)
    outs = _hv_list(hv, "outcomes", warns)
    if not pain and not outs:
        return None
    PX, PW, top = 10, 330, 6
    OX = PX + PW + 60 if pain else PX
    OW = HV_W - 10 - OX
    body = []
    # đo cột outcome trước
    y, strips = top, []
    for o in outs:
        t_l = _wrap(_s(o.get("text")) or "(outcome không có chữ)", OW - 54 - 326, 12.5, 5)
        n_l = _wrap(_s(o.get("now")) or "—", 124, 11.5, 3)
        g_l = _wrap(_s(o.get("target")) or "—", 158, 12.5, 3)
        added = o.get("from_request") is False
        h = max(42, 14 + 17 * max(len(t_l), len(n_l), len(g_l)) + (22 if added else 0) + 8)
        strips.append((o, y, h, t_l, n_l, g_l, added))
        y += h + 8
    o_bottom = y - 8 if strips else top
    p_lines = _wrap(_s(pain.get("text")), PW - 28, 13.5, 9) if pain else []
    nums = _strs(pain.get("numbers")) if pain else []
    p_h = 34 + 19 * len(p_lines) + (8 + 36 * len(nums) if nums else 0) + (20 if _s(pain.get("ref")) else 0) + 8
    total = max(o_bottom, top + p_h) if pain else o_bottom
    if pain:
        ph = total - top
        inner = _rect(PX, top, PW, ph, "sh blocked", 9)
        inner += _text(PX + 14, top + 20, "ĐANG ĐAU", 9.5, "cap t-blocked", weight=700)
        inner += _lines(PX + 14, top + 42, p_lines, 13.5, 19, weight=600)
        ny = top + 42 + 19 * len(p_lines) - 6
        for n in nums:
            inner += _rect(PX + 14, ny, PW - 28, 30, "pill bad", 7)
            inner += _text(PX + 26, ny + 20, _clip(n, PW - 52, 14.5), 14.5, "t-blocked", weight=750)
            ny += 36
        if _s(pain.get("ref")):
            inner += _text(PX + 14, top + ph - 10, "bản chữ: mục " + _s(pain.get("ref")), 10, "mono t-muted")
        body.append(_nav(None, "Đang đau: " + _s(pain.get("text")), inner))
    if pain and strips:
        jx, my = OX - 30, top + (total - top) / 2
        body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(PX + PW), _n(my), _n(jx), _n(my)))
        mids = [sy + sh / 2 for _o, sy, sh, *_r in strips]
        body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (
            _n(jx), _n(min(mids + [my])), _n(jx), _n(max(mids + [my]))))
        for m in mids:
            body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(jx), _n(m), _n(OX - 5), _n(m)))
            body.append('<polygon points="%s,%s %s,%s %s,%s" class="ah"/>' % (
                _n(OX - 6), _n(m - 3.5), _n(OX - 1), _n(m), _n(OX - 6), _n(m + 3.5)))
    for o, sy, sh, t_l, n_l, g_l, added in strips:
        inner = _rect(OX, sy, OW, sh, "sh later silent" if added else "sh", 8)
        chip, _w = _chip(OX + 10, sy + 9, _s(o.get("id")) or "O?", "blue", "t-active", 10.5)
        inner += chip
        inner += _lines(OX + 54, sy + 23, t_l, 12.5, 17, weight=600)
        if added:
            lab = "AI thêm — không có trong yêu cầu gốc"
            bw = _tw(lab, 9.5) + 16
            by = sy + 14 + 17 * len(t_l)
            inner += _rect(OX + 54, by, bw, 17, "pill later", 8.5)
            inner += _text(OX + 54 + bw / 2, by + 12, lab, 9.5, "t-open", "middle", 700)
        nx = OX + OW - 316
        inner += _lines(nx + 124, sy + 23, n_l, 11.5, 17, "t-muted", anchor="end")
        inner += _text(nx + 138, sy + 23, "→", 13, "t-muted", "middle")
        inner += _lines(nx + 152, sy + 23, g_l, 12.5, 17, "t-done", 750)
        body.append(_nav(None, "%s · %s — hiện nay: %s → đích: %s%s" % (
            _s(o.get("id")), _s(o.get("text")), _s(o.get("now")) or "—", _s(o.get("target")) or "—",
            " (AI thêm, không có trong yêu cầu gốc — bỏ được)" if added else ""), inner))
    n_added = sum(1 for x in strips if x[6])
    return {"key": "goal", "title": "Đích",
            "svg": _svg(HV_W, total + 6, body, "Đích: %s. %d kết quả cần đạt%s" % (
                _s(pain.get("text")) if pain else "", len(strips),
                ", trong đó %d do AI thêm" % n_added if n_added else "")),
            "note": ("%d kết quả do AI thêm, không có trong yêu cầu gốc — bạn bỏ được." % n_added) if n_added else ""}


def hv_fig_scope(hv, warns, decision_ids=()):
    """PHẠM VI — ba cột: làm đợt này · để đợt sau (kèm giá của việc để lại) · không làm."""
    sc = _hv_dict(hv, "scope", warns)
    now, never = _strs(sc.get("now")), _strs(sc.get("never"))
    later = []
    link_of = {}
    for x in sc.get("later") if isinstance(sc.get("later"), list) else []:
        if isinstance(x, dict) and _s(x.get("what")):
            later.append((_s(x.get("what")), _s(x.get("cost"))))
            if _s(x.get("decision")):
                link_of[_s(x.get("what"))] = _s(x.get("decision"))
        elif _s(x):
            later.append((_s(x), ""))
    if not (now or later or never):
        return None
    X0, GAP, top = 10, 13, 6
    CW = (HV_W - 2 * X0 - 2 * GAP) / 3
    body, bottoms = [], []
    cols = (("LÀM ĐỢT NÀY", "t-done", [(t, "") for t in now], "done"),
            ("ĐỂ ĐỢT SAU", "t-open", later, "later"),
            ("KHÔNG LÀM", "t-muted", [(t, "") for t in never], "pending"))
    for ci, (title, tcls, items, cls) in enumerate(cols):
        x = X0 + ci * (CW + GAP)
        body.append(_text(x + 2, top + 13, "%s · %d" % (title, len(items)), 9.5, "cap " + tcls, weight=700))
        y = top + 24
        for what, cost in items:
            dec_id = link_of.get(what) if cls == "later" else None
            w_l = _wrap(what, CW - 28 - (58 if dec_id else 0), 12.5, 3)
            c_l = _wrap("giá: " + cost, CW - 28, 11.5, 5) if cost else []
            h = 12 + 17 * len(w_l) + 15 * len(c_l) + 8
            worst = bool(re.search(r"giá\s*cao\s*nhất", cost, re.I))
            inner = _rect(x, y, CW, h, "sh blocked" if worst else "sh " + cls, 7)
            inner += _lines(x + 14, y + 22, w_l, 12.5, 17, "t-muted" if cls == "pending" else "", 600)
            inner += _lines(x + 14, y + 22 + 17 * len(w_l), c_l, 11.5, 15, "t-blocked" if worst else "t-open")
            body.append(_nav(None, what + ((" — giá: " + cost) if cost else ""), inner))
            if dec_id:
                body.append(_goto_chip(x + CW - 8, y + 8, dec_id, decision_ids, warns, "scope.later “%s”" % what[:30])[0])
            y += h + 7
        if not items:
            body.append(_text(x + 2, y + 14, "(không có)", 11.5, "t-muted"))
            y += 24
        bottoms.append(y)
    total = max(bottoms)
    if _s(sc.get("ref")):
        body.append(_text(HV_W - X0, total + 10, "bản chữ: mục " + _s(sc.get("ref")), 10, "mono t-muted", "end"))
        total += 14
    return {"key": "scope", "title": "Phạm vi",
            "svg": _svg(HV_W, total + 4, body, "Phạm vi: làm đợt này %d việc, để đợt sau %d việc, không làm %d việc"
                        % (len(now), len(later), len(never))), "note": ""}


def _when(v):
    """`1.7 mục 2 chốt "có chặn"` → `có chặn`. Số mục của bản chữ là mã nội bộ: nó vào tooltip, không nằm
    giữa câu người đọc."""
    t = _s(v)
    t = re.sub(r"^\s*(?:mục\s*)?\d+(?:\.\d+)*(?:\s*mục\s*\d+)?\s*[:·—–-]?\s*", "", t)
    t = re.sub(r"^(?:chốt|chot|=)\s*[:=]?\s*", "", t, flags=re.I)
    return t.strip().strip('"“”\'').strip()


def hv_fig_roadmap(hv, table, outcome_ids, decision_ids, warns, deps=None):
    """LỘ TRÌNH — mỗi phần việc một thanh, dài theo giờ, đặt nối tiếp theo thứ tự chạy của bảng Unit."""
    units = _hv_list(hv, "units", warns)
    if not units:
        return None, {}
    by_id = {}
    for u in units:
        by_id.setdefault(_s(u.get("id")), u)
    rows = []
    for t in table:
        if t["id"] in by_id:
            rows.append((t["id"], by_id[t["id"]], t, True))
        else:
            rows.append((t["id"], {}, t, True))
            warns.append("%s có trong bảng phần việc nhưng thiếu trong human-view.units" % t["id"])
    in_table = {t["id"] for t in table}
    for uid, u in by_id.items():
        if uid not in in_table:
            rows.append((uid or "UOW-?", u, {"name": "", "est": 0.0}, False))
            warns.append("%s có trong human-view.units nhưng không có trong bảng phần việc — không biết giờ"
                         % (uid or "(unit không có id)"))
    total_h = sum(t["est"] for _i, _u, t, _k in rows)
    X0, top, RH = 10, 4, 50
    CWD = HV_W - 2 * X0
    scale = CWD / total_h if total_h > 0 else 0
    body, cum, ticks = [], 0.0, [0.0]
    cond_n, cond_h = 0, 0.0
    unreviewed = []
    deps = deps or {}
    order = {r[0]: k for k, r in enumerate(rows)}
    for i, (uid, u, t, known) in enumerate(rows):
        y = top + i * RH
        est = t["est"]
        after = []
        for dep in deps.get(uid, []):
            if dep not in order:
                warns.append("%s phụ thuộc %s — không có trong bảng phần việc" % (uid, dep))
                after.append(dep + "?")
            else:
                if order[dep] > i:
                    warns.append("%s xếp chạy TRƯỚC %s mà nó phụ thuộc — thứ tự trong bảng phần việc sai" % (uid, dep))
                after.append(dep + ("" if order[dep] < i else "!"))
        cond = u.get("condition") if isinstance(u.get("condition"), dict) else None
        if cond:
            cond_n, cond_h = cond_n + 1, cond_h + est
        # chip outcome ở mép phải
        cx, chips = HV_W - X0, ""
        for oid in reversed(_strs(u.get("serves"))):
            ok = oid in outcome_ids
            if not ok:
                warns.append("%s.serves trỏ %s — không có outcome nào mang mã đó" % (uid, oid))
            w = _tw(oid + ("" if ok else "?"), 10, True) + 14
            cx -= w
            c, _w = _chip(cx, y + 1, oid + ("" if ok else "?"), "blue" if ok else "bad",
                          "t-active" if ok else "t-blocked")
            chips = _nav(None, (oid + " — kết quả mà phần việc này phục vụ") if ok
                         else (oid + " — KHÔNG có outcome nào mang mã này"), c) + chips
            cx -= 5
        # Tầng review của phần việc (§4.17) — Gate D duyệt cả bảng tầng này nên người phải THẤY nó trên hình
        rv = _s(u.get("review")).strip("`")
        if rv:
            none = bool(re.match(r"^(none|không)\b", rv, re.I))
            spec = bool(re.match(r"^specialist", rv, re.I))
            lab = "không ai soát thứ hai" if none else "soát: " + rv
            w = _tw(lab, 10, not none) + 14
            cx -= w
            c, _w = _chip(cx, y + 1, lab, "later" if none else ("blue" if spec else ""),
                          "t-open" if none else ("t-active" if spec else "t-muted"), 10, not none)
            chips = _nav(None, "Tầng review: %s%s" % (rv, (" — " + _s(u.get("review_why"))) if _s(u.get("review_why"))
                                                      else ""), c) + chips
            cx -= 6
            if none:
                unreviewed.append(uid)
        label_w = cx - X0 - 8
        id_txt = uid + ("" if known else "?")
        inner = _text(X0, y + 14, id_txt, 11.5, "mono" + ("" if known else " t-blocked"), weight=700)
        hrs = (_hours(est) + "h") if known and est > 0 else "?h"
        tx = X0 + _tw(id_txt, 11.5, True) + 8
        short = _s(u.get("short")) or _plain(t.get("name") or "")
        short_c = _clip("· " + short, label_w - (tx - X0) - _tw(" · " + hrs, 11.5, True) - 20, 12.5)
        inner += _text(tx, y + 14, short_c, 12.5, weight=600)
        tx2 = tx + _tw(short_c, 12.5) * 1.05 + 12          # chữ đậm rộng hơn ước lượng một chút
        inner += _text(tx2, y + 14, "· " + hrs, 11.5, "mono t-active" if not cond else "mono t-open", weight=700)
        if after:
            bad = any(a[-1] in "?!" for a in after)
            ax = tx2 + _tw("· " + hrs, 11.5, True) + 12
            inner += _text(ax, y + 14, _clip("↳ sau " + ", ".join(after), max(40, cx - ax - 8), 11), 11,
                           "mono " + ("t-blocked" if bad else "t-muted"))
        inner += chips
        # rãnh + thanh
        inner += _rect(X0, y + 22, CWD, 16, "pill", 4)
        bx = X0 + cum * scale
        bw = max(est * scale, 0)
        if known and est > 0:
            inner += _rect(bx, y + 22, bw, 16, "sh later silent" if cond else "sh active", 4)
        else:
            inner += _rect(min(bx, HV_W - X0 - 44), y + 22, 44, 16, "sh blocked silent", 4)
            bw = 44
        if cond:
            dec_id = _s(cond.get("decision"))
            ok = dec_id in decision_ids
            if not ok:
                warns.append("%s.condition trỏ %s — không có điểm cần chốt nào mang mã đó" % (uid, dec_id or "(rỗng)"))
            lab = "chỉ làm nếu chốt: %s (%s%s)" % (_when(cond.get("when")) or "?", dec_id or "?", "" if ok else "?")
            lw = _tw(lab, 10.5)
            right_room = HV_W - X0 - (bx + bw) - 10
            lx, anchor = (bx + bw + 8, "start") if right_room >= lw else (bx - 8, "end")
            inner += _text(lx, y + 34, _clip(lab, max(right_room, bx - X0 - 10), 10.5), 10.5,
                           "t-open" if ok else "t-blocked", anchor, 650)
        body.append(_nav("unit:%s:%s" % (hv.get("_intent", ""), uid) if known else None,
                         "%s · %s · %s%s%s" % (uid, short, hrs,
                                               (" — chỉ làm nếu %s chốt: %s" % (_s(cond.get("decision")), _s(cond.get("when"))))
                                               if cond else "",
                                               (" — phải chờ %s xong" % ", ".join(deps.get(uid, []))) if after else ""),
                         inner))
        cum += est
        ticks.append(cum)
    ay = top + len(rows) * RH + 4
    body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(X0), _n(ay), _n(HV_W - X0), _n(ay)))
    last_x = -99
    for k, tv in enumerate(ticks):
        x = X0 + tv * scale
        body.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="ln"/>' % (_n(x), _n(ay - 3), _n(x), _n(ay + 4)))
        is_last = k == len(ticks) - 1
        if is_last:
            body.append(_text(HV_W - X0, ay + 17, "tổng %sh" % _hours(total_h), 11.5, "mono", "end", 750))
        elif x - last_x >= 38 and (HV_W - X0 - x) >= 96:
            body.append(_text(x, ay + 16, _hours(tv) + ("h" if k == 0 else ""), 10, "mono t-muted",
                              "start" if k == 0 else "middle"))
            last_x = x
    note = ""
    if cond_n:
        note = "Bỏ cả %d phần việc có điều kiện ⇒ còn %d phần việc · %s giờ." % (
            cond_n, len(rows) - cond_n, _hours(total_h - cond_h))
    if unreviewed:
        note = (note + " " if note else "") + "%d phần việc không ai soát thứ hai: %s." % (
            len(unreviewed), ", ".join(unreviewed))
    stats = {"units": len(rows), "hours": total_h, "condUnits": cond_n, "condHours": cond_h,
             "unreviewed": len(unreviewed)}
    return {"key": "roadmap", "title": "Lộ trình phần việc",
            "svg": _svg(HV_W, ay + 24, body, "Lộ trình: %d phần việc chạy nối tiếp, tổng %s giờ%s" % (
                len(rows), _hours(total_h), (", %d phần việc có điều kiện" % cond_n) if cond_n else "")),
            "note": note}, stats


def hv_fig_sources(srcs, extras, replaced_by=None, decision_ids=(), warns=None):
    """NGUỒN — thanh chồng theo trạng thái, tách theo mức ưu tiên; dưới là nguồn P0 không đọc được."""
    rows = srcs.get("rows") or []
    if not rows:
        return None, {}
    # View schema 2 không có chỗ khai "điểm nào thay nguồn nào" — khi đó KHÔNG nói "chưa ai hỏi":
    # thiếu chỗ khai không phải là bằng chứng chưa ai hỏi.
    linked = replaced_by is not None
    replaced_by = replaced_by or {}
    KIND = (("read", "done", "đã đọc"), ("planned", "active", "sẽ đọc"),
            ("missing", "blocked", "không đọc được"), ("other", "pending", "khác"))

    def prio(r):
        m = re.search(r"P\s*([0-3])", r.get("prio") or "", re.I)
        return "P" + m.group(1) if m else "—"

    def kind(r):
        return r["status"] if r["status"] in ("read", "planned", "missing") else "other"
    groups = {}
    for r in rows:
        groups.setdefault(prio(r), {}).setdefault(kind(r), []).append(r)
    order = [p for p in ("P0", "P1", "P2", "P3", "—") if p in groups]
    biggest = max(sum(len(v) for v in groups[p].values()) for p in order)
    X0, LX, top = 10, 176, 22
    scale = (HV_W - X0 - LX) / biggest
    body = []
    lx = X0
    totals = {k: sum(1 for r in rows if kind(r) == k) for k, _c, _l in KIND}
    for k, cls, label in KIND:
        if not totals[k]:
            continue
        body.append(_rect(lx, 3, 12, 12, "seg " + cls, 2))
        t = "%s %d" % (label, totals[k])
        body.append(_text(lx + 17, 13.5, t, 11, "t-blocked" if k == "missing" else "t-muted",
                          weight=700 if k == "missing" else None))
        lx += 17 + _tw(t, 11) + 20
    for i, p in enumerate(order):
        y = top + i * 34 + 6
        n = sum(len(v) for v in groups[p].values())
        body.append(_text(X0, y + 17, "%s · %d nguồn" % (p if p != "—" else "chưa ghi mức", n), 11.5,
                          "mono", weight=700 if p == "P0" else None))
        x = LX
        for k, cls, label in KIND:
            c = len(groups[p].get(k, []))
            if not c:
                continue
            w = c * scale
            inner = _rect(x, y, w, 24, "seg " + cls, 3)
            if w >= 20:
                inner += _text(x + w / 2, y + 16.5, str(c), 11.5, "mono t-on", "middle", 700)
            body.append(_nav(None, "%s · %s: %d nguồn — %s" % (
                p, label, c, ", ".join(r["id"] for r in groups[p][k])), inner))
            x += w
    y = top + len(order) * 34 + 12
    p0_missing = groups.get("P0", {}).get("missing", [])
    if p0_missing:
        body.append(_text(X0, y + 10, "NGUỒN P0 KHÔNG ĐỌC ĐƯỢC — KẾT QUẢ CÓ THỂ CHỈ \"ĐẠT TRÊN GIẤY\"", 9.5,
                          "cap t-blocked", weight=700))
        y += 20
        for r in p0_missing:
            ex = extras.get(r["id"], {})
            s_l = _wrap(r["source"], HV_W - 2 * X0 - 78, 12.5, 2)
            own = "ai giữ: " + (ex.get("owner") or "chưa ghi")
            k_l = _wrap("bỏ qua thì: " + ex["risk"], HV_W - 2 * X0 - 78, 11.5, 2) if ex.get("risk") else []
            h = 12 + 17 * len(s_l) + 16 + 15 * len(k_l) + (24 if linked else 0) + 8
            inner = _rect(X0, y, HV_W - 2 * X0, h, "sh blocked", 7)
            # người xem không đọc thay nguồn được — cái họ làm được là trả lời điểm cần chốt đang THAY cho nguồn đó
            ry = y + 22 + 17 * len(s_l) + 16 + 15 * len(k_l) + 4
            by_dec = replaced_by.get(r["id"], [])
            if not linked:
                pass
            elif by_dec:
                inner += _text(X0 + 64, ry, "được thay bằng:", 11.5, "t-muted")
            else:
                inner += _text(X0 + 64, ry, "chưa ai hỏi — không điểm cần chốt nào thay cho nguồn này", 11.5,
                               "t-blocked", weight=700)
            inner += _text(X0 + 14, y + 22, r["id"], 11.5, "mono t-blocked", weight=700)
            inner += _lines(X0 + 64, y + 22, s_l, 12.5, 17, weight=600)
            inner += _text(X0 + 64, y + 22 + 17 * len(s_l), _clip(own, HV_W - 2 * X0 - 78, 11.5), 11.5, "t-muted")
            inner += _lines(X0 + 64, y + 22 + 17 * len(s_l) + 16, k_l, 11.5, 15, "t-blocked")
            body.append(_nav(None, "%s · %s — %s" % (r["id"], _plain(r["source"]), own), inner))
            cxr = X0 + 64 + _tw("được thay bằng:", 11.5) + 10
            for dec_id in by_dec:
                chip, w = _goto_chip(cxr + _tw("→ " + dec_id, 10, True) + 14, ry - 13, dec_id, decision_ids,
                                     warns if warns is not None else [], "nguồn %s" % r["id"])
                body.append(chip)
                cxr += w + 6
            y += h + 7
    stats = {"sources": len(rows), "unreadable": totals["missing"], "p0Unreadable": len(p0_missing),
             "p0Unasked": sum(1 for r in p0_missing if not replaced_by.get(r["id"])) if linked else None}
    return {"key": "sources", "title": "Nguồn",
            "svg": _svg(HV_W, y + 4, body, "Nguồn: %d nguồn, %d đã đọc, %d sẽ đọc, %d không đọc được; "
                        "%d nguồn P0 không đọc được" % (len(rows), totals["read"], totals["planned"],
                                                        totals["missing"], len(p0_missing))),
            "note": ""}, stats


def hv_fig_approach(hv, warns):
    """TRỤC PHÂN RÃ — Gate A duyệt cả cách cắt phần việc: trục đã chọn (xanh) cạnh những gì đã cân nhắc rồi bỏ."""
    ap = _hv_dict(hv, "approach", warns)
    axis = _s(ap.get("axis"))
    rej = [(_s(x.get("what")), _s(x.get("why"))) for x in ap.get("rejected") if isinstance(x, dict) and _s(x.get("what"))] \
        if isinstance(ap.get("rejected"), list) else []
    if not axis and not rej:
        return None
    X0, GAP, top = 10, 30, 4
    CW = (HV_W - 2 * X0 - GAP) / 2
    a_l = _wrap(axis or "(view không ghi trục đã chọn)", CW - 28, 13, 4)
    w_l = _wrap("vì: " + _s(ap.get("why")), CW - 28, 11.5, 5) if _s(ap.get("why")) else []
    lh = 30 + 18 * len(a_l) + 15 * len(w_l) + 10
    boxes, ry = [], top
    for what, why in rej[:5]:
        o_l = _wrap(what, CW - 28, 12.5, 3)
        y_l = _wrap("vì: " + why, CW - 28, 11.5, 4) if why else []
        bh = 30 + 16 * len(o_l) + 15 * len(y_l) + 8
        boxes.append((ry, bh, o_l, y_l, what, why))
        ry += bh + 8
    lh = max(lh, ry - 8 - top) if boxes else lh
    body = []
    inner = _rect(X0, top, CW, lh, "sh done", 8)
    inner += _text(X0 + 14, top + 18, "CẮT PHẦN VIỆC THEO", 9, "cap t-done", weight=700)
    inner += _lines(X0 + 14, top + 39, a_l, 13, 18, weight=700)
    inner += _lines(X0 + 14, top + 39 + 18 * len(a_l), w_l, 11.5, 15, "t-muted")
    body.append(_nav(None, "Trục đã chọn: %s%s" % (axis, (" — vì: " + _s(ap.get("why"))) if _s(ap.get("why")) else ""), inner))
    if boxes:
        body.append(_text(X0 + CW + GAP / 2, top + lh / 2 + 5, "≠", 15, "t-muted", "middle"))
    rx = X0 + CW + GAP
    for by_, bh, o_l, y_l, what, why in boxes:
        inner = _rect(rx, by_, CW, bh, "sh pending", 8)
        inner += _text(rx + 14, by_ + 17, "ĐÃ CÂN NHẮC RỒI BỎ", 9, "cap t-muted", weight=700)
        inner += _lines(rx + 14, by_ + 36, o_l, 12.5, 16, "t-muted", 600)
        inner += _lines(rx + 14, by_ + 36 + 16 * len(o_l), y_l, 11.5, 15, "t-muted")
        body.append(_nav(None, "Đã bỏ: %s%s" % (what, (" — vì: " + why) if why else ""), inner))
    total = top + lh
    if _s(ap.get("ref")):
        body.append(_text(HV_W - X0, total + 14, "bản chữ: mục " + _s(ap.get("ref")), 10, "mono t-muted", "end"))
        total += 16
    return {"key": "approach", "title": "Trục phân rã",
            "svg": _svg(HV_W, total + 6, body, "Trục phân rã đã chọn: %s. Đã cân nhắc rồi bỏ: %s" % (
                axis or "?", "; ".join(r[0] for r in rej) or "không ghi")),
            "note": ("%d hướng đã cân nhắc rồi bỏ" % len(rej)) if rej else ""}


def _open_esc(ref):
    """Mã ESC trong `ref` của rủi ro, nếu escalation đó có thật và còn mở — chỉ khi ấy mới có đường giao chủ."""
    m = re.search(r"ESC-\d+", ref or "")
    if not m:
        return ""
    d = fm(read(os.path.join(CM, "escalations", m.group(0) + ".md")))
    return m.group(0) if d and (d.get("status") or "open").strip() == "open" else ""


def hv_fig_risks(hv, warns, decision_ids=()):
    """RỦI RO — tối đa ba thẻ, nặng nhất trước. Rủi ro chưa có chủ thì chữ "chưa có" tô đỏ."""
    risks = _hv_list(hv, "risks", warns)
    risks = [r for r in risks if _s(r.get("text"))]
    if not risks:
        return None
    ranked = sorted(enumerate(risks), key=lambda x: (HV_LEVEL.get(norm_level(_s(x[1].get("level"))), 3), x[0]))
    shown = [r for _i, r in ranked[:3]]
    X0, GAP, top = 10, 13, 4
    CW = (HV_W - 2 * X0 - 2 * GAP) / 3
    cards, body = [], []
    for r in shown:
        t_l = _wrap(r.get("text"), CW - 28, 12.5, 7)
        cards.append((r, t_l, 38 + 17 * len(t_l) + 24 + (16 if _s(r.get("ref")) else 0) + 4))
    h = max(c[2] for c in cards)
    for i, (r, t_l, _h) in enumerate(cards):
        x = X0 + i * (CW + GAP)
        lv = norm_level(_s(r.get("level")))
        high = HV_LEVEL.get(lv) == 0
        inner = _rect(x, top, CW, h, "sh blocked" if high else ("sh later" if HV_LEVEL.get(lv) == 1 else "sh"), 8)
        chip, _w = _chip(x + 12, top + 10, "MỨC " + (lv.upper() or "?"),
                         "bad" if high else ("later" if HV_LEVEL.get(lv) == 1 else ""),
                         "t-blocked" if high else ("t-open" if HV_LEVEL.get(lv) == 1 else "t-muted"), 9.5, False)
        inner += chip
        inner += _lines(x + 14, top + 48, t_l, 12.5, 17, weight=600)
        oy = top + 48 + 17 * len(t_l) + 4
        owner = _s(r.get("owner"))
        no_owner = not owner or re.match(HV_NO_OWNER, owner, re.I)
        inner += _text(x + 14, oy, "người chịu:", 11, "t-muted")
        inner += _text(x + 14 + _tw("người chịu:", 11) + 6, oy, _clip(owner or "chưa có", CW - 110, 11.5), 11.5,
                       "t-blocked" if no_owner else "", weight=700)
        if _s(r.get("ref")):
            inner += _text(x + 14, oy + 16, _clip(_s(r.get("ref")), CW - 130, 10, True), 10, "mono t-muted")
        body.append(_nav(None, "Rủi ro mức %s: %s — người chịu: %s" % (lv or "?", _s(r.get("text")), owner or "chưa có"),
                         inner))
        if _s(r.get("decision")):
            body.append(_goto_chip(x + CW - 10, top + 10, _s(r.get("decision")), decision_ids, warns,
                                   "rủi ro “%s”" % _s(r.get("text"))[:30])[0])
        esc = _open_esc(_s(r.get("ref"))) if no_owner else ""
        if esc:
            lab = "nhận / giao ▸"
            bw = _tw(lab, 10.5) + 18
            body.append(_nav("esc:" + esc, "Giao người chịu rủi ro này — gửi chỉ đạo cho %s" % esc,
                             _rect(x + CW - 10 - bw, top + h - 28, bw, 20, "pill rec", 10) +
                             _text(x + CW - 10 - bw / 2, top + h - 14.5, lab, 10.5, "t-on-rec", "middle", 700)))
    more = len(risks) - len(shown)
    n_orphan = sum(1 for r in risks if not _s(r.get("owner")) or re.match(HV_NO_OWNER, _s(r.get("owner")), re.I))
    note = " · ".join(x for x in (("%d rủi ro chưa có người chịu." % n_orphan) if n_orphan else "",
                                   ("Còn %d rủi ro nữa trong bản chữ." % more) if more > 0 else "") if x)
    return {"key": "risks", "title": "Rủi ro",
            "svg": _svg(HV_W, top + h + 6, body, "Rủi ro: %d thẻ, %d chưa có người chịu" % (len(shown), n_orphan)),
            "note": note}


# ----- phủ trạng thái của gate SAU lên cây của gate TRƯỚC (phát hiện #25) -----
# View của Gate A vẽ lúc chưa có open-questions. Tới Gate C đội đã áp mặc định cho chính chuyện đó — trang mô
# hình mà vẫn ghi "đội đang ĐỨNG" là nói sai với người xem. Tower KHÔNG sửa view; nó tìm câu hỏi tương ứng và
# phủ trạng thái mới nhất lên cây. Không khớp được thì không phủ — không đoán.
GATE_ORDER = "ABCDEFG"
OQ_GATE = {"business": "C", "tech": "D", "legacy": "C"}


def _refkey(v):
    """`Intent-plan  1.7 mục 7` → `1.7 mục 7` — để so hai cách viết cùng một mục."""
    t = re.sub(r"\s+", " ", _s(v).lower()).strip(" .")
    return re.sub(r"^(?:intent-plan|unit-plan)(?:\.md)?\s*[#:·—–-]?\s*(?:mục\s+(?=\d+\.))?", "", t).strip()


def oq_crossmap(base):
    """Bảng "Đối chiếu …" validator viết ở cuối file câu hỏi (cột Nguồn → Về đâu): mục của tài liệu gate đã
    thành mã câu hỏi nào. Trả {mục: [[mã cùng một dòng], …]} — hai dòng cùng mục là hai câu hỏi riêng."""
    out = {}
    for _aud, fname, _label in OQ_FILES:
        for heading, header, rows in md_tables(read(os.path.join(base, fname))):
            if not re.search(r"đối\s*chiếu|doi\s*chieu|câu\s*cũ", heading or "", re.I):
                continue
            i_src = col_of(header, r"^nguồn", r"câu\s*cũ", r"^từ")
            i_to = col_of(header, r"về\s*đâu", r"mã\s*mới", r"^thành")
            if i_src < 0 or i_to < 0:
                continue
            for c in rows:
                codes = re.findall(r"\bOQ[BT]?-\d+\b", c[i_to] if i_to < len(c) else "")
                if not codes:
                    continue                          # "không hỏi" · ESC-NNN: không có câu hỏi nào để phủ
                for part in (c[i_src] if i_src < len(c) else "").split("·"):
                    k = _refkey(part)
                    if k and codes not in out.setdefault(k, []):
                        out[k].append(codes)
    return out


def applying_dec(intent_id, audience, fname, code):
    """DEC autopilot đã ÁP mặc định cho câu hỏi này, chưa bị đảo.

    Ưu tiên DEC nêu ĐÍCH DANH file hoặc mã câu hỏi trong Căn cứ · Hiện ở (mới nhất trong số đó) — đó là nơi điểm
    này thật sự được quyết. Không DEC nào nêu đích danh thì lấy DEC SỚM NHẤT có gate không đứng trước gate của
    file câu hỏi: gate đầu tiên đi qua câu hỏi là gate đã áp nó. DEC của gate sau nữa (vd Gate D duyệt unit-plan)
    chỉ xây trên mặc định ấy, không phải nơi quyết — nhắm đảo vào đó là đảo nhầm chỗ."""
    named, later = None, None
    for d in decisions:
        if not d.get("autopilot") or d.get("intent") != intent_id:
            continue
        if d.get("hasApply"):
            continue        # DEC có dòng `Áp` tự khai nó áp gì; mã không có trong dòng đó là mã nó KHÔNG áp
        if _reversed_by.get(d["id"]) or STEERS.get(d["id"]):
            continue
        basis = d.get("basisFull", "")
        if fname in basis or re.search(r"(?<![\w-])" + re.escape(code) + r"(?![\w-])", basis):
            named = d
            continue
        g = (d.get("gate") or "")[:1].upper()
        if later is None and re.match(r"^[A-G]\b", d.get("gate") or "") and \
                GATE_ORDER.index(g) >= GATE_ORDER.index(OQ_GATE.get(audience, "C")):
            later = d
    return named or later


def human_confirmed(intent_id, codes):
    """Đã có NGƯỜI xác nhận: một DEC không phải của autopilot, cùng intent, nêu đích danh một trong các mã đó."""
    want = {c for c in codes if c}
    for d in decisions:
        if d.get("autopilot") or (d.get("_to") or d.get("intent") or intent_id) != intent_id:
            continue
        hit = want & set(d.get("codes") or [])
        if hit:
            return d["id"]
    return ""


def make_resolver(intent_id, base, qs, own_dec="", own_gate=""):
    by_code = {q["code"]: q for q in qs if q.get("code")}
    details = parse_question_details(base)
    cross = oq_crossmap(base)
    applied = applied_index()
    file_of = {aud: fname for aud, fname, _l in OQ_FILES}

    def groups_for(dc):
        oq = _s(dc.get("oq"))
        if oq:
            return [[oq]], "view ghi `oq`"
        ref = _refkey(dc.get("ref"))
        if not ref:
            return [], ""
        hit = [[c] for c, dt in details.items()
               if any(_refkey(part) == ref for part in re.split(r"[·,;]", dt.get("xref") or ""))]
        if hit:
            return hit, "dòng Soi chiếu của câu hỏi"
        return cross.get(ref, []), "bảng đối chiếu"

    def direct(dc):
        """DEC ghi `Áp: D4 = B` — áp thẳng lên MÃ ĐIỂM của view, cùng bộ phương án với cây. Chỉ phủ khi điều đó
        là tin MỚI so với hình: DEC của gate khác, hoặc phương án khác mặc định hình đang vẽ (vd sau một lần người
        đảo: `D4 = B (thay DEC-0001)`). So theo GATE của tài liệu, không so một id DEC: gate A có thể có nhiều DEC
        (DEC-0001 áp mặc định, DEC-0002 đảo một điểm), và điểm chưa bị đảo vẫn là "đúng mặc định đang vẽ"."""
        did = _s(dc.get("id"))
        live = live_applied(intent_id, did, applied)
        if not live:
            return None
        last = live[-1]
        own = last["dec"] == own_dec or (own_gate and last["gate"] == own_gate)
        if own and last["opt"] == _s(dc.get("default")):
            return None
        o = next((x for x in dc.get("options") if isinstance(x, dict) and _s(x.get("key")) == last["opt"]), None) \
            if isinstance(dc.get("options"), list) else None
        until = _s(o.get("reversal_until")) if o and _reversal(o.get("reversal")) != "đắt" else ""
        part = {"oq": did, "file": "", "also": [], "closed": False, "direct": True, "key": last["opt"],
                "option": last["opt"] + ((" — " + _s(o.get("name"))) if o else ""), "until": until,
                "dec": last["dec"], "gate": last["gate"], "via": "dòng Áp",
                "replaces": [p["repl"] for p in applied.get((intent_id, did), []) if p["dec"] == last["dec"] and p["repl"]]}
        by_human = human_confirmed(intent_id, [did])
        return {"confirmed": bool(by_human), "confirmedBy": by_human, "dec": part["dec"], "gate": part["gate"],
                "option": part["option"], "until": until, "oq": did, "closed": False,
                "how": "dòng Áp của " + part["dec"], "parts": [part], "path": ""}

    def resolve(dc):
        groups, how = groups_for(dc)
        if not groups:
            return direct(dc)
        parts = []
        for codes in groups:
            known = [c for c in codes if c in by_code]
            if not known:
                return None                            # mã trỏ tới không có trong bảng điều phối: không phủ
            code = next((c for c in known if c.startswith("OQB")), known[0])
            q = by_code[code]
            fname = file_of.get(q["audience"], "open-questions.md")
            dt = details.get(code, {})
            closed = bool(re.search(r"closed|đã chốt|da chot|đóng", q.get("status") or "", re.I))
            key = _pick_option(dt.get("silent") or q.get("fallback"), dt.get("options") or [])
            opt = next((o for o in dt.get("options") or [] if (o["key"] or o["name"]) == key), None)
            label = (((opt["key"] + " — ") if opt["key"] else "") + opt["name"]) if opt else _s(q.get("fallback"))
            if closed:
                parts.append({"oq": code, "file": fname, "also": [c for c in known if c != code], "closed": True,
                              "option": _s(q.get("answer")) or label, "until": "", "dec": "", "gate": "",
                              "replaces": [], "via": ""})
                continue
            # (1) DEC ghi rõ `Áp: OQB-06 = A` — phương án và nơi quyết lấy thẳng từ đó, không suy
            live = live_applied(intent_id, code, applied)
            if live:
                last = live[-1]
                o2 = next((o for o in dt.get("options") or [] if o["key"] == last["opt"]), None)
                fb = _s(q.get("fallback"))             # thẻ không có bảng phương án: tên lấy từ cột "Nếu im lặng" nếu đúng chữ cái
                named_fb = fb if re.match(r"^%s(?![\w])" % re.escape(last["opt"]), fb) else ""
                parts.append({"oq": code, "file": fname, "also": [c for c in known if c != code], "closed": False,
                              "option": (last["opt"] + " — " + o2["name"]) if o2 else (named_fb or last["opt"]),
                              "key": last["opt"], "until": (o2 or {}).get("reversal_until", ""),
                              "dec": last["dec"], "gate": last["gate"],
                              "replaces": [p["repl"] for p in applied.get((intent_id, code), [])
                                           if p["dec"] == last["dec"] and p["repl"]],
                              "via": "dòng Áp"})
                continue
            if applied.get((intent_id, code)):
                return None                            # mọi lần áp cho mã này đều đã bị thay / bị đảo: đang treo
            # (2) đường lùi cho DEC viết trước 6.5.1: suy từ Căn cứ · Hiện ở + mặc định trong file câu hỏi
            dec = applying_dec(intent_id, q["audience"], fname, code) if label else None
            if not dec:
                return None                            # câu còn mở và chưa DEC nào áp mặc định: vẫn là chuyện đang treo
            parts.append({"oq": code, "file": fname, "also": [c for c in known if c != code], "closed": False,
                          "option": label, "key": key, "until": (opt or {}).get("reversal_until", ""),
                          "dec": dec["id"], "gate": (dec.get("gate") or "")[:1].upper(),
                          "replaces": [], "via": "Căn cứ · Hiện ở"})
        if not parts:
            return None
        first = parts[0]
        by_human = human_confirmed(intent_id, [_s(dc.get("id"))] + [c for p in parts for c in [p["oq"]] + p["also"]])
        return {"confirmed": all(p["closed"] for p in parts) or bool(by_human), "confirmedBy": by_human,
                "dec": first["dec"], "gate": first["gate"], "option": first["option"],
                "until": next((p["until"] for p in parts if p["until"]), ""), "oq": first["oq"],
                "closed": all(p["closed"] for p in parts), "how": how, "parts": parts,
                "path": os.path.relpath(os.path.join(base, first["file"]), A)}
    return resolve


def _reversal(v):
    t = _s(v).lower()
    return "đắt" if re.search(r"đắt|dat\b|expensive", t) else ("rẻ" if re.search(r"rẻ|re\b|cheap", t) else "")


def hv_decisions(hv, table_ids, qs, warns, width=None, resolver=None):
    """CẦN BẠN QUYẾT — mỗi điểm một cây lựa chọn, vẽ bằng CHÍNH `svg_question_tree` của thẻ câu hỏi.

    Giá đảo thuộc về TỪNG phương án (`options[].reversal`, thiếu = rẻ — §2.4.6).
    Xếp: chưa có mặc định (đang cần người) → rủi ro cao → mặc định có hạn đảo → có phương án đảo đắt → còn lại.
    `recommended: null` là hợp lệ (bản chữ không có khuyến nghị, modeler không được bịa): cây không có huy hiệu
    "AI đề xuất", không sinh cảnh báo."""
    out = []
    open_q = {q["code"]: q for q in qs if q.get("code") and
              not re.search(r"closed|đã chốt|da chot|đóng|descoped", q.get("status") or "", re.I)}
    by_text = {re.sub(r"\W+", "", q["q"].lower()): c for c, q in open_q.items()}
    for idx, dc in enumerate(_hv_list(hv, "decisions", warns)):
        did = _s(dc.get("id")) or "D?"
        dflt, rec = _s(dc.get("default")), _s(dc.get("recommended"))
        if dflt in ("-", "—"):
            dflt = ""
        resolved = resolver(dc) if resolver else None
        opts = []
        for o in dc.get("options") if isinstance(dc.get("options"), list) else []:
            if not isinstance(o, dict):
                continue
            rv = _reversal(o.get("reversal")) or "rẻ"
            until = _s(o.get("reversal_until")) if rv == "rẻ" else ""
            opts.append({"key": _s(o.get("key")), "name": _s(o.get("name")) or "(phương án không tên)",
                         "meaning": _s(o.get("effect")), "cost": _s(o.get("cost")), "risk": "", "reversal": rv,
                         "reversal_until": until})
        keys = {o["key"] for o in opts if o["key"]}
        for fld, val in (("recommended", rec), ("default", dflt)):
            if val and val not in keys:
                warns.append("%s.%s = %s — không có phương án nào mang khoá đó" % (did, fld, val))
        costly = [o["key"] for o in opts if o["reversal"] == "đắt"]
        if dflt and dflt in costly:
            warns.append("%s: mặc định khi im lặng (%s) là phương án đảo đắt — phải chờ người, không tự áp" % (did, dflt))
        needs = _s(dc.get("needs"))
        if not dflt and not needs and not resolved:
            warns.append("%s không có mặc định mà cũng không ghi cần người làm rõ gì" % did)
        risk = norm_level(_s(dc.get("risk")))
        kind = _s(dc.get("kind")).upper()
        blocks = []
        for uid in _strs(dc.get("blocks")):
            ok = uid in table_ids
            if not ok:
                warns.append("%s.blocks trỏ %s — không có trong bảng phần việc" % (did, uid))
            blocks.append((uid, ok))
        unlocks = [u for u in dict.fromkeys(_strs(dc.get("unlocks"))) if u != did]
        badges = []
        if len(unlocks) >= 1:
            badges.append(("gỡ %d điểm khác" % len(unlocks), "blue", "t-active"))
        if costly:
            badges.append(("có phương án đảo đắt", "bad", "t-blocked"))
        if HV_LEVEL.get(risk) == 0:
            badges.append(("rủi ro cao", "bad", "t-blocked"))
        elif HV_LEVEL.get(risk) == 1:
            badges.append(("rủi ro vừa", "later", "t-open"))
        if kind:
            badges.append((kind, "later" if kind == "CONFLICT" else "", "t-open" if kind == "CONFLICT" else "t-muted"))
        oq = _s(dc.get("oq"))
        if oq not in open_q:
            oq = did if did in open_q else by_text.get(re.sub(r"\W+", "", _s(dc.get("question")).lower()), "")
        q = {"code": did, "who": _s(dc.get("who")), "due": _s(dc.get("deadline")) or _s(dc.get("due")),
             "impact": "", "blocking": False, "q": _s(dc.get("question")), "fallback": ""}
        d = {"title": _s(dc.get("question")), "options": opts, "recommend": rec, "silent": dflt}
        dflt_costly = bool(dflt and dflt in costly)
        svg, meta = svg_question_tree(q, d, width=width or HV_W, extras={
            "badges": badges, "reversal": "đắt" if dflt_costly else "rẻ",
            "reverse_by": _s(dc.get("reverse_by")), "blocks": blocks, "q_lines": 9,
            "note": ("Chưa có mặc định — đội đứng chờ bạn. Cần làm rõ: " + needs)
            if (not dflt and needs and not resolved) else "",
            "tip": "bấm để chọn phương án này"})
        if not svg:
            warns.append("%s có dưới 2 phương án — không vẽ được cây lựa chọn" % did)
        chosen = next((o for o in opts if o["key"] == (dflt or rec)), None)
        until_now = resolved["until"] if resolved else ((chosen or {}).get("reversal_until", "") if dflt else "")
        confirmed = resolved["confirmed"] if resolved else bool(human_confirmed(hv.get("_intent", ""), [did]))
        if resolved:
            chosen_line = "đã áp ở Gate %s: %s" % (resolved["gate"], resolved["option"]) if not resolved["closed"] \
                else "đã chốt: " + resolved["option"]
            if len(resolved["parts"]) > 1:              # một điểm của view đã tách thành nhiều câu hỏi ở gate sau
                chosen_line += " (+%d câu nữa)" % (len(resolved["parts"]) - 1)
            if resolved["until"]:
                chosen_line += " · đảo rẻ tới: " + resolved["until"]
        line = chosen_line if resolved else " · ".join(x for x in (
            ((chosen["key"] + ". ") if chosen["key"] else "") + chosen["name"], chosen["cost"],
            ("đảo rẻ tới: " + chosen["reversal_until"]) if chosen.get("reversal_until")
            else "đảo " + (chosen["reversal"] or "rẻ")) if x) if chosen else ""
        out.append({"id": did, "kind": kind, "risk": risk, "costly": costly, "question": _s(dc.get("question")),
                    "sources": _strs(dc.get("sources")), "defaultLabel": (chosen["key"] or chosen["name"]) if (chosen and dflt) else "",
                    # Cần NGƯỜI chỉ khi CHƯA CÓ mặc định (thông tin chưa đủ rõ — đội đang đứng). Rủi ro cao mà đã
                    # có mặc định thì AI đi tiếp, người đảo nếu cần: nó đứng ĐẦU nhóm "AI tự lo", dòng có huy hiệu đỏ.
                    # Gate sau đã áp mặc định / đã chốt cho chính chuyện này ⇒ không còn là việc đang chờ người.
                    # Mặc định mang HẠN ĐẢO mà chưa người nào xác nhận: thứ duy nhất người còn nợ sau khi gate sau đã
                    # áp — nhóm riêng "xác nhận trước mốc", cây mở sẵn, không gấp.
                    "group": "need" if (not dflt and not resolved) else
                    ("confirm" if until_now and not confirmed else "auto"), "line": line,
                    "confirmed": confirmed,
                    **({"resolved": resolved} if resolved else {}),
                    "unlocks": unlocks,
                    "defaultUntil": resolved["until"] if resolved else
                    ((chosen or {}).get("reversal_until", "") if dflt else ""),
                    "who": _s(dc.get("who")), "deadline": q["due"], "needs": needs, "ref": _s(dc.get("ref")),
                    "reverseBy": _s(dc.get("reverse_by")), "blocks": [b[0] for b in blocks],
                    "options": [dict(m, reversal=o["reversal"], reversalUntil=o["reversal_until"])
                                for m, o in zip(meta.get("options", []), opts)],
                    "recommended": meta.get("recommend", ""), "default": meta.get("silent", ""),
                    "oq": oq, "svg": svg or "",
                    "_rank": (0 if (not dflt and not resolved) else (1 if (until_now and not confirmed) else 2),
                              0 if HV_LEVEL.get(risk) == 0 else 1,
                              0 if (chosen or {}).get("reversal_until") and dflt else 1,
                              0 if costly else 1, HV_LEVEL.get(risk, 3), idx)})
    out.sort(key=lambda x: x.pop("_rank"))
    return out


def build_human_view(intent_id, base, doc_rel, srcs, qs, dec_of_gate=None):
    """Một tài liệu gate → trang mô hình. None khi tài liệu không có fence human-view."""
    p = os.path.join(base, doc_rel)
    if not os.path.isfile(p):
        return None
    text = read(p)
    hv, err = parse_human_view(p)
    if hv is None and err is None:
        return None
    name = os.path.basename(doc_rel)
    dfm = fm(text)
    gate = (dfm.get("gate") or "").strip().strip('"\'')[:1].upper() or HV_GATE_OF_DOC.get(name, "")
    model = {"intent": intent_id, "doc": os.path.relpath(p, A), "docName": name, "gate": gate,
             "lines": text.count("\n") + 1, "headline": "", "summary": "", "stats": {}, "figures": [],
             "decisions": [], "minor": [], "gaps": [], "warnings": [], "error": "",
             "stale": False, "staleFrom": "", "staleTo": "",
             "view": os.path.relpath(view_path_of(p), A)}
    if err:
        model["error"] = "human-view không đọc được: " + err
        model["warnings"].append(model["error"])
        return model
    warns = []
    if "version" not in hv:
        warns.append("thiếu `version` — khoá bắt buộc duy nhất của human-view")
    # Mô hình vẽ từ bản chữ CŨ là lỗi nặng (§2.4.5): người quyết trên hình, AI làm theo chữ.
    want = _s(hv.get("source_sha256"))
    if want != hashlib.sha256(text.encode("utf-8")).hexdigest():
        model["stale"] = True
        model["staleFrom"] = _s(hv.get("source_version")) or "?"
        model["staleTo"] = (dfm.get("version") or "?").strip().strip('"\'')
        warns.append("MÔ HÌNH CŨ — bản chữ đã đổi sau khi vẽ (v%s → v%s)" % (model["staleFrom"], model["staleTo"]))
    model["gaps"] = hv_gaps(hv)
    model["by"], model["at"] = _s(hv.get("by")), _s(hv.get("at"))
    hv = dict(hv, _intent=intent_id)
    table = unit_table_for(base, name)
    table_ids = {t["id"] for t in table}
    outcome_ids = {_s(o.get("id")) for o in _hv_list(hv, "outcomes", []) if _s(o.get("id"))}
    minor = _strs(hv.get("decisions_minor"))
    decision_ids = {_s(d.get("id")) for d in _hv_list(hv, "decisions", []) if _s(d.get("id"))}
    decision_ids |= {m.group(1) for m in (re.match(r"^(D\d+)\b", x) for x in minor) if m}
    figs = []
    # chỉ mã có CÂY mới là đích cuộn tới được: điểm nhỏ (decisions_minor) không có cây
    tree_ids = {_s(d.get("id")) for d in _hv_list(hv, "decisions", []) if _s(d.get("id"))}
    source_ids = {r["id"] for r in srcs.get("rows") or []}
    replaced_by = {}
    links_known = num(hv.get("version"), 0) >= 3 or any("sources" in d for d in _hv_list(hv, "decisions", []))
    for d in _hv_list(hv, "decisions", []):
        for sid in _strs(d.get("sources")):
            if source_ids and sid not in source_ids:
                warns.append("%s.sources trỏ %s — không có trong bảng nguồn" % (_s(d.get("id")) or "D?", sid))
            replaced_by.setdefault(sid, []).append(_s(d.get("id")))
    goal = hv_fig_goal(hv, warns)
    scope = hv_fig_scope(hv, warns, tree_ids)
    approach = hv_fig_approach(hv, warns)
    road, ustats = hv_fig_roadmap(hv, table, outcome_ids, decision_ids, warns, unit_deps(text))
    src_fig, sstats = hv_fig_sources(srcs, source_extras(read(os.path.join(base, "intent-plan.md")) + "\n" +
                                                         read(os.path.join(base, "as-is", "source-ledger.md"))),
                                     replaced_by if links_known else None, tree_ids, warns)
    model["dec"] = (dec_of_gate or {}).get(gate, "")
    decs = hv_decisions(hv, table_ids, qs, warns, resolver=make_resolver(intent_id, base, qs, model["dec"], gate))
    risks = hv_fig_risks(hv, warns, tree_ids)
    for f in (goal, scope, approach, road, src_fig):
        if f:
            figs.append(f)
    # Một chuyện hay hiện ở nhiều hình (phạm vi · nguồn · rủi ro · chỗ bản chữ thiếu). Gom về đúng cây của nó
    # để người xem thấy đó là MỘT chuyện chứ không phải bốn cảnh báo rời.
    sc = hv.get("scope") if isinstance(hv.get("scope"), dict) else {}
    for d in decs:
        also = []
        if any(isinstance(x, dict) and _s(x.get("decision")) == d["id"] for x in sc.get("later") or []
               if isinstance(sc.get("later"), list)):
            also.append({"fig": "scope", "label": "Phạm vi"})
        if d["sources"]:
            also.append({"fig": "sources", "label": "Nguồn " + ", ".join(d["sources"])})
        if any(_s(r.get("decision")) == d["id"] for r in _hv_list(hv, "risks", [])):
            also.append({"fig": "risks", "label": "Rủi ro"})
        d["also"] = also
        d["gaps"] = [g for g in model["gaps"] if g["decision"] == d["id"]]
    known_q = {q["code"] for q in qs if q.get("code")}
    for d in decs:
        for u in d["unlocks"]:
            if u not in decision_ids and u not in known_q:
                warns.append("%s.unlocks trỏ %s — không có điểm cần chốt hay câu hỏi nào mang mã đó" % (d["id"], u))
    # §4.10.14 — trả lời MỘT điểm mà gỡ được ≥ 2 điểm khác: đáng nhìn sớm dù không chặn ai
    model["early"] = [d["id"] for d in decs if len(d["unlocks"]) >= 2]
    for g in model["gaps"]:
        if g["decision"] and g["decision"] not in tree_ids:
            warns.append("gaps trỏ %s — không có điểm cần chốt nào mang mã đó" % g["decision"])
    model["idle"] = {"defaults": [{"id": d["id"], "key": d["defaultLabel"]} for d in decs if d["defaultLabel"]],
                     "standing": [{"id": d["id"], "needs": d["needs"], "question": d["question"]}
                                  for d in decs if not d["defaultLabel"] and not d.get("resolved")],
                     # view không có mặc định nhưng gate sau đã áp: đội KHÔNG đứng ở đây nữa
                     "applied": [{"id": d["id"], "gate": d["resolved"]["gate"], "dec": d["resolved"]["dec"]}
                                 for d in decs if d.get("resolved") and not d["defaultLabel"]],
                     # mặc định đã áp mang hạn đảo: qua mốc đó là hết đảo rẻ — cần người xác nhận TRƯỚC mốc
                     "confirm": [{"id": d["id"], "until": d["defaultUntil"]} for d in decs if d["group"] == "confirm"],
                     "minor": len(minor)}
    n_need = sum(1 for d in decs if d["group"] == "need")
    confirm = [d for d in decs if d["group"] == "confirm"]
    untils = list(dict.fromkeys(d["defaultUntil"] for d in confirm))
    n_auto = len(decs) - n_need - len(confirm) + len(minor)
    if decs or minor or model["gaps"]:
        figs.append({"key": "decisions", "title": "Cần bạn quyết", "svg": "",
                     "note": " · ".join(x for x in (
                         "%d cần bạn" % n_need,
                         ("%d xác nhận %s" % (len(confirm), untils[0] if len(untils) == 1 else "trước mốc")) if confirm else "",
                         "%d đã có mặc định" % n_auto) if x)})
    if risks:
        figs.append(risks)
    n_units = ustats.get("units", len(table))
    hours = ustats.get("hours", sum(t["est"] for t in table))
    n_dec = len(decs) + len(minor)
    n_exp = sum(1 for d in decs if d["costly"])
    parts = []
    if n_units:
        parts.append("%d phần việc" % n_units)
    if hours:
        parts.append("%s giờ" % _hours(hours))
    if sstats.get("sources"):
        parts.append("%d nguồn (%d không đọc được)" % (sstats["sources"], sstats["unreadable"]))
    if n_dec:
        parts.append("%d điểm cần chốt: %d cần bạn%s · %d AI tự lo" % (
            n_dec, n_need,
            (" · %d xác nhận %s" % (len(confirm), untils[0] if len(untils) == 1 else "trước mốc")) if confirm else "",
            n_auto))
    seen = set()
    model.update({
        "version": hv.get("version") if isinstance(hv.get("version"), (int, float, str)) else "",
        "headline": _s(hv.get("headline")), "summary": " · ".join(parts),
        "stats": dict(ustats, **sstats, decisions=n_dec, expensive=n_exp, need=n_need, auto=n_auto,
                      confirm=len(confirm)),
        "figures": figs, "decisions": decs, "minor": minor,
        "warnings": [w for w in warns if not (w in seen or seen.add(w))][:40]})
    return model


def human_views_of(intent_id, base, gate_doc_rel, srcs, qs, dec_of_gate):
    """Mọi tài liệu gate của intent có human-view. `primary` = tài liệu của gate đang mở nếu nó có mô hình,
    không thì bản kế hoạch mới nhất (unit-plan trước intent-plan)."""
    docs = {}
    for rel in dict.fromkeys([x for x in (gate_doc_rel, "unit-plan.md", "intent-plan.md") if x]):
        m = build_human_view(intent_id, base, rel, srcs, qs, dec_of_gate)
        if m:
            m.setdefault("dec", dec_of_gate.get(m["gate"], ""))
            docs[m["doc"]] = m
    if not docs:
        return None
    primary = next(iter(docs))
    return {"primary": primary, "docs": docs, "stale": any(m["stale"] for m in docs.values()),
            "gaps": sum(len(m["gaps"]) for m in docs.values()),
            "warnings": [("%s: %s" % (m["docName"], w)) for m in docs.values() for w in m["warnings"]]}
human_view = {}
blocked_gates = []

# ---------- handoffs → vị trí đang làm việc ----------
HB_DRIFT_MIN = 30        # phút — lệch quá mức này giữa lời khai và mtime của chính file = số giả
HB_FUTURE_MIN = 5


def parse_iso_local(s):
    """ISO → datetime NAIVE theo giờ máy. Không đọc được thì None.

    Có offset (`+07:00`, `Z`) thì quy về giờ máy trước khi bỏ tzinfo: trừ một datetime aware cho một
    datetime naive là TypeError, và ca đó đã làm sập `session_brief.py` một lần rồi."""
    s = (s or "").strip().strip('"\'')
    if not s or s in ("-", "null", "none"):
        return None
    try:
        t = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t.astimezone().replace(tzinfo=None) if t.tzinfo is not None else t


def heartbeat_audit(hb_raw, hb_ts, file_ts, now):
    """Đối chiếu LỜI KHAI (`heartbeat:`) với DẤU VẾT (mtime của chính file HOF đó).

    Ca thật (PILOT · HOF-0039 · 13/08): agent ghi HOF lúc 18:13 nhưng khai `heartbeat: …T00:00:00Z`,
    và `progress` trễ 3 vòng so với việc nó đang làm. Tower vẫn hiện "im lặng 1099 phút" — người
    giám sát đọc ra "agent chết" trong khi nó đang chạy. Lời khai không kiểm chéo là lời khai sẽ lệch.
    Không đoán ý — chỉ so hai con số cùng nằm trên đĩa."""
    if hb_ts is None:
        return ("", "") if not hb_raw or hb_raw == "-" else (
            "unreadable", "heartbeat `%s` không đọc được như ISO — tower không tính được nhịp" % hb_raw[:32])
    if re.search(r"T00:00:00(\.0+)?(Z|[+-]\d{2}:?\d{2})?$", hb_raw):
        return ("placeholder", "heartbeat đúng nửa đêm (`%s`) — gần như chắc chắn là giá trị điền cho có"
                % hb_raw[:32])
    if (hb_ts - now).total_seconds() > HB_FUTURE_MIN * 60:
        return ("future", "heartbeat ở tương lai (`%s`) — đồng hồ sai hoặc số bịa" % hb_raw[:32])
    drift = int((file_ts - hb_ts).total_seconds() // 60)
    if drift > HB_DRIFT_MIN:
        return ("drift", "file HOF được ghi lúc %s nhưng heartbeat khai %s — lệch %d phút, tức là agent "
                         "có sửa file mà không cập nhật nhịp" % (file_ts.strftime("%H:%M"),
                                                                hb_ts.strftime("%H:%M"), drift))
    return ("", "")
LANE = {"be-dev": "pipeline", "fe-dev": "pipeline", "bolt-coordinator": "pipeline",
        "orchestrator": "pipeline", "intent-analyst": "pipeline", "source-planner": "pipeline",
        "context-archaeologist": "pipeline", "context-validator": "pipeline", "unit-planner": "pipeline",
        "acceptance-recorder": "pipeline", "retro-keeper": "pipeline"}
def scan_team():
    """Agent team của CHÍNH dự án này — chỉ đọc `~/.claude/teams/*/config.json` có `cwd` của lead trùng ROOT.

    Hai thứ cần thấy:
    1. Ai đang thật sự chạy như một phiên riêng (ghép pane với dòng trên board).
    2. **Tin chết** — hộp thư mang tên một teammate KHÔNG có trong `members`. Ca thật (PILOT · 13/08): 5 lần
       spawn teammate hỏng vì tmux (`respawn pane failed: fork failed: Device not configured`), nhưng
       `SendMessage` vẫn báo "đã gửi" — nó chỉ ghi file JSON, ghi được là coi như xong. Hai review-request
       và hai yêu cầu Review Board nằm im trong hộp thư của những agent chưa bao giờ tồn tại. Đúng
       `LL-002` ("13 lần xin review, 0 verdict") lặp lại ở tầng teams, lần này người xin còn tin là đã gửi.
    """
    base = os.path.expanduser(os.path.join("~", ".claude", "teams"))
    out = {"name": None, "members": [], "deadLetters": [], "zombies": []}
    if not os.path.isdir(base):
        return out
    root_real = os.path.realpath(ROOT)
    for name in sorted(os.listdir(base)):
        cfg = os.path.join(base, name, "config.json")
        try:
            with open(cfg, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        mem = d.get("members") or []
        lead_cwd = (mem[0].get("cwd") if mem else "") or ""
        if not lead_cwd:
            continue
        lead_real = os.path.realpath(lead_cwd)
        # Lead hay ngồi ở gốc monorepo trong khi dự án AI-DLC là một thư mục con (ca PILOT trong monorepo)
        # — nên nhận cả hai chiều lồng nhau, không chỉ trùng khít.
        if not (lead_real == root_real
                or root_real.startswith(lead_real + os.sep)
                or lead_real.startswith(root_real + os.sep)):
            continue
        out["name"] = d.get("name")
        # Ghép phiên đang sống với HOF nó giữ (qua `teammate:`). Không ghép được thì lead không có cách nào
        # biết phiên nào còn việc — và một phiên sống quá vòng đời HOF của nó là một nguồn sự thật thứ hai:
        # nó vẫn nhớ unit-plan v3 trong khi đĩa đã v4. §9.5.6.
        by_teammate = {r["teammate"]: r for r in handoffs if r.get("teammate")}
        out["members"] = []
        for m in mem:
            nm = m.get("name")
            row = {"name": nm, "type": m.get("agentType"), "backend": m.get("backendType"),
                   "pane": m.get("tmuxPaneId"), "hof": None, "state": "lead", "why": ""}
            if m.get("agentType") != "team-lead":
                h = by_teammate.get(nm)
                if h is None:
                    row.update(state="unknown",
                               why="không HOF nào khai `teammate: %s` — không biết phiên này đang giữ việc gì" % nm)
                elif h["status"] in ("done", "returned"):
                    row.update(hof=h["id"], state="zombie",
                               why="%s đã `%s` — phiên còn sống quá vòng đời HOF của nó, nên tắt" % (h["id"], h["status"]))
                else:
                    row.update(hof=h["id"], state="working",
                               why="đang giữ %s (%s)" % (h["id"], h["status"]))
            out["members"].append(row)
        out["zombies"] = [r for r in out["members"] if r["state"] in ("zombie", "unknown")]
        names = {m.get("name") for m in mem}
        ibox = os.path.join(base, name, "inboxes")
        for fn in sorted(os.listdir(ibox)) if os.path.isdir(ibox) else []:
            who = fn[:-5] if fn.endswith(".json") else fn
            if who in names:
                continue
            try:
                with open(os.path.join(ibox, fn), encoding="utf-8") as fh:
                    msgs = json.load(fh)
            except (OSError, ValueError):
                continue
            if not msgs:
                continue
            out["deadLetters"].append({
                "to": who, "count": len(msgs),
                "from": (msgs[0].get("from") if isinstance(msgs[0], dict) else "?") or "?",
                "text": re.sub(r"\s+", " ", (msgs[0].get("text") if isinstance(msgs[0], dict) else "") or "")[:160],
                "at": mtime_hm(os.path.join(ibox, fn)),
            })
    return out

# ---------- hoạt động thật trên đĩa ----------
# Agent quên cập nhật HOF thì board vẫn ghi "chờ nhận" dù nó đang chạy. File nó vừa ghi
# thì không nói dối được — quét mtime để luôn có tín hiệu sống, kể cả khi agent không kỷ luật.
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "out", "coverage", "venv",
             ".venv", "__pycache__", ".turbo", ".cache", "target", ".pytest_cache", "tower"}
ACTIVITY_WINDOW_MIN = 120
MAX_SCAN = 40000


def scan_activity():
    roots = [(A, ".ai-dlc")]
    wm = read(os.path.join(A, "workspace-map.md"))
    # v1 `code.frontend: path` và v2 `areas.<x>.path: path` đều là `  key: value` — bắt chung.
    # "." (repos.path của map v2) là cả workspace: bỏ, kẻo quét toàn repo thay vì code roots.
    for m in re.finditer(r"^\s{2,}\w+:\s*(\S+)\s*$", wm, re.M):
        v = m.group(1).strip().strip('"').strip("'")
        if v and v != "null":
            p = os.path.abspath(os.path.join(ROOT, v))
            if p == os.path.abspath(ROOT):
                continue
            if os.path.isdir(p) and not any(p == r[0] for r in roots):
                roots.append((p, v.rstrip("/")))
    now = datetime.datetime.now().timestamp()
    cutoff = now - ACTIVITY_WINDOW_MIN * 60
    seen, out = 0, []
    for root, label in roots:
        for dirpath, dirnames, files in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in SKIP_DIRS and (not d.startswith(".") or d == ".ai-dlc")]
            for f in files:
                seen += 1
                if seen > MAX_SCAN:
                    return sorted(out, key=lambda x: -x["ts"])[:25]
                if f.startswith("."):
                    continue
                fp = os.path.join(dirpath, f)
                try:
                    ts = os.path.getmtime(fp)
                except OSError:
                    continue
                if ts < cutoff:
                    continue
                rel = os.path.relpath(fp, ROOT)
                if rel.startswith(os.path.join(".ai-dlc", "tower")):
                    continue
                out.append({"path": rel, "ts": ts, "root": label,
                            "mins": int((now - ts) // 60),
                            "kind": "state" if rel.startswith(".ai-dlc") else "code"})
    return sorted(out, key=lambda x: -x["ts"])[:25]

# ---------- autopilot: thẻ "AI đã tự quyết" + KPI (6.4.0, protocol §2.3) ----------
# Không có DEC autopilot, không có autopilot.md, không gate nào block ⇒ khối này không sinh ra gì:
# dự án chạy `lead` thấy tower y như trước.
def esc_is_open(esc_id):
    d = fm(read(os.path.join(CM, "escalations", esc_id + ".md")))
    return bool(d) and (d.get("status") or "open").strip().strip('"\'').lower() == "open"


auto_decisions = []
auto_warnings = []


def parse_reg(path, kind):
    out = []
    for l in read(path).splitlines():
        m = re.match(r"^- (\S+) · (\w+) · (.+)", l)
        if m:
            rest = m.group(3)
            owner = re.search(r"chủ:\s*([^·]+)", rest)
            # `sev` là mã tô màu (high/med/low) mà UI đã dùng từ trước; `level` là chữ HIỂN THỊ (cao/vừa/thấp)
            out.append({"id": m.group(1),
                        "sev": {"cao": "high", "vừa": "med", "thấp": "low"}.get(norm_level(m.group(2)), m.group(2)),
                        "level": norm_level(m.group(2)),
                        "text": rest.split("·")[0].strip()[:160],
                        "owner": owner.group(1).strip() if owner else "—"})
    return out

lessons = []

# escalations/ — phát hiện NGOÀI phạm vi unit (protocol §4.13). Không có chỗ này thì phát hiện
# chìm theo HOF đóng lại; tower phải hiện nó cho tới khi có người nhận.
def esc_intent(d):
    """Escalation thuộc yêu cầu nào. `found_in` thường là một HOF — đi qua `re:` của HOF đó để ra INT.
    Không suy ra được thì trả "": thẻ hiện mã ESC, không hiện mã HOF như thể đó là tên yêu cầu."""
    for v in (d.get("intent"), d.get("re"), d.get("found_in")):
        m = re.search(r"INT-\d+", v or "")
        if m:
            return m.group(0)
    hof = re.search(r"HOF-\d+", d.get("found_in") or "")
    if hof:
        for h in hof_rows():
            if h["id"] == hof.group(0):
                m = re.search(r"INT-\d+", h.get("re") or "")
                return m.group(0) if m else ""
    return ""


def esc_view(esc_path, esc_id):
    """`escalations/views/ESC-NNN.view.json` — MỘT quyết định, cùng schema với `decisions[]` của human-view
    (nhận cả dạng `{decisions: [ {...} ]}` lẫn để thẳng object quyết định). Có thì thẻ đỏ vẽ cây lựa chọn
    thay cho ô chữ trống; chưa có thì thẻ như cũ."""
    hv, err = parse_human_view(esc_path)
    if hv is None and err is None:
        return None
    if err:
        return {"error": "mô hình của %s không đọc được: %s" % (esc_id, err), "svg": "", "options": []}
    one = hv["decisions"][0] if isinstance(hv.get("decisions"), list) and hv["decisions"] and \
        isinstance(hv["decisions"][0], dict) else hv
    warns = []
    # Cây mang mã của CHÍNH thẻ (ESC-NNN) — modeler hay đánh "D1", trùng với D1 của intent và làm người đọc
    # tưởng hai chuyện là một. Rộng 760 cho vừa thẻ ở màn "Cần tôi quyết".
    decs = hv_decisions({"decisions": [dict(one, id=esc_id)]}, set(), [], warns, width=760)
    if not decs or not decs[0]["svg"]:
        return {"error": "mô hình của %s chưa đủ phương án để vẽ" % esc_id, "svg": "", "options": []}
    d = decs[0]
    want = _s(hv.get("source_sha256"))
    stale = bool(want) and want != hashlib.sha256(read(esc_path).encode("utf-8")).hexdigest()
    return {"svg": d["svg"], "options": d["options"], "recommended": d["recommended"], "default": d["default"],
            "needs": d["needs"], "risk": d["risk"], "question": d["question"], "who": d["who"],
            "stale": stale, "error": "", "warnings": [w for w in warns if "blocks" not in w][:8],
            "gaps": [g["text"] for g in hv_gaps(hv)]}


escalations = []
svg_escalations = {}


def gov_doc(name):
    p = os.path.join(CM, "governance", name + ".md")
    d = fm(read(p))
    items = [m.strip() for m in re.findall(r"^- \[ \] (.+)$", read(p), re.M)][:10]
    return {"version": "v" + str(d.get("version", "1")), "items": items}

# inbox/ — việc người đã gửi từ tower (quyết định gate · câu trả lời · chỉ đạo) mà phiên Claude Code CHƯA áp
# (file còn nằm ngoài processed/). Tower dùng để chuyển thẻ sang "đã gửi, chờ áp" thay vì hỏi lại.
inbox_pending = []
# Bảng Decisions ở Tra cứu giữ đúng sáu trường cũ; phần trade-off + SVG của DEC autopilot đi riêng trong
# `autopilot.decisions` để không nhân đôi chuỗi SVG trong data.js.
_DEC_KEYS = ("id", "when", "gate", "by", "what", "basis")


def use_project(root):
    """Cho người IMPORT module để thử parser: gán đường dẫn của dự án (ROOT · A · CM · idir · OUT · UNIT_MAX_H) rồi thôi.
    Không sinh tower, không ghi file, không `exec` sang tower khác, không `sys.exit` — khác `main()` ở đúng những chỗ đó."""
    global ROOT, A, CM, idir, OUT, LAYOUT, UNIT_MAX_H
    ROOT = os.path.abspath(root)
    try:
        LAYOUT = _layout(ROOT)
    except Exception:  # noqa: BLE001
        LAYOUT = None
    ok = bool(LAYOUT) and LAYOUT.get("engine") == "ai-dlc"
    if ok:
        ROOT = LAYOUT["root"]
    A = LAYOUT["state"] if ok else os.path.join(ROOT, ".ai-dlc")
    CM = os.path.join(A, "context-memory")
    idir = os.path.join(CM, "intents")
    OUT = LAYOUT["tower"]["out"] if ok else os.path.join(A, "tower")
    UNIT_MAX_H = unit_max_hours()
    _HOF_CACHE.clear()
    return A


def main(argv=None):
    """Sinh tower. TOÀN BỘ việc đọc state và ghi file nằm ở đây — `import tower_generate` không chạy gì.

    Các biến dưới đây từng là biến cấp module (script chạy thẳng từ trên xuống); khai `global` để mọi hàm
    phía trên vẫn đọc được chúng đúng như trước."""
    global ASKED, LAYOUT, ROOT, A, CM, UI_SRC, _pf, PLUGIN_VERSION, OUT, intents, units_by_intent, gates, docs
    global questions_by_intent, questions, sources_by_intent, flow_by_intent, revisions_by_intent, idir
    global UNIT_MAX_H, MSG_IDX, RV_IDX, ESC_IDX, AUTOPILOT, decisions, STEERS, _reversed_by
    global svg_flow_by_intent, svg_questions, name, base, st, it_text, it, plan_fm, stage, raw_gate, gm
    global gate_open, passed, gates_auto, blocked_by, units, srcs, qs, _u, _dec_of_gate, _d, _details, _q, _dt
    global _unl, _svg_q, _meta, _sil, _gd, _hv, _bn, revs, rdir_i, rf, rd, body, trash_dir, obsolete
    global live_units, n_done, total_est, c, g, gate_doc_rel, doc, brief_p, btxt, options, checks, oq_block
    global stations, handoffs, hdir, f, p, d, agent, hb, status_v, now_dt, file_dt, hb_dt, silent, hb_kind
    global hb_why, ref, row, _acc, handoff_health, _done_all, team, _z, _r, activity, s, key, tag, feed
    global reviews, cdir, rdir, finding, _e, _m, _iid, _ms, _mine, _blk, _dl, _rev, _through, _short, _key
    global _val, _label, _rule, _files, _rows, _warn, _tone, risks, debt, ldir, lm, h1, text, edir, _ev
    global gov_changelog, tasks, work, tasks_from, cands, iid, us, u, b, live_cands, pick, _ib, _f, _fh, _j
    global first, decisions_out, data, ui, rel_root, dirs, files, rel, dst_dir
    argv = list(sys.argv if argv is None else argv)
    # Các bộ gom khởi tạo rỗng ở cấp module: xoá trước mỗi lần chạy, không thì gọi main() lần hai trong cùng
    # một tiến trình (người import để thử) sẽ cộng dồn kết quả của lần trước.
    for _acc in (_HOF_CACHE, metrics_by_intent, human_view, blocked_gates, auto_decisions, auto_warnings,
                 lessons, escalations, svg_escalations, inbox_pending):
        _acc.clear()
    ASKED = argv[1] if len(argv) > 1 else os.getcwd()
    try:
        LAYOUT = _layout(ASKED)
    except Exception:
        LAYOUT = None
    if LAYOUT and LAYOUT["engine"] == "aws-v2":
        # Workspace AWS aidlc v2 (phương án A): tower của gói là tower_aws_v2.py — chuyển tiếp, không tạo .ai-dlc/context-memory
        print("engine aws-v2 tại %s — dùng tower_aws_v2.py" % LAYOUT["root"], file=sys.stderr)
        os.execv(sys.executable, [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tower_aws_v2.py"),
                                  "--project-dir", LAYOUT["root"]] + argv[2:])
    if LAYOUT and LAYOUT["engine"] == "ai-dlc":
        ROOT, ASKED = LAYOUT["root"], os.path.abspath(ASKED)
    elif LAYOUT and LAYOUT["engine"] == "off":
        sys.exit("AI-DLC tắt (engine: off trong config) tại %s — không sinh tower." % LAYOUT["root"])
    else:
        ROOT, ASKED = resolve_root(ASKED)
    if ROOT is None:
        sys.exit("Không tìm thấy dự án AI-DLC nào từ '%s' (thiếu `.ai-dlc/context-memory/`).\n"
                 "Không tạo gì cả — chạy `/ai-dlc:dlc-init` nếu đây là dự án mới, hoặc truyền đúng gốc:\n"
                 "  python3 tower_generate.py <đường-dẫn-gốc-dự-án>" % ASKED)
    if os.path.abspath(ROOT) != os.path.abspath(ASKED):
        print("gốc dự án: %s (bạn đưa vào '%s')" % (ROOT, ASKED), file=sys.stderr)
    A = LAYOUT["state"] if LAYOUT and LAYOUT["engine"] == "ai-dlc" else os.path.join(ROOT, ".ai-dlc")
    CM = os.path.join(A, "context-memory")
    UI_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tower-ui")
    # Version thật của gói đang chạy — đọc từ plugin.json cạnh script, không hardcode
    # (bug tới 6.1.0: chuỗi "5.0.0" nằm chết trong code, tower khai sai version qua hai bản major).
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                               ".claude-plugin", "plugin.json"), encoding="utf-8") as _pf:
            PLUGIN_VERSION = json.load(_pf).get("version", "?")
    except Exception:  # noqa: BLE001
        PLUGIN_VERSION = "?"
    OUT = LAYOUT["tower"]["out"] if LAYOUT and LAYOUT["engine"] == "ai-dlc" else os.path.join(A, "tower")


    # ---------- intents ----------
    intents, units_by_intent, gates, docs = [], {}, [], {}
    questions_by_intent, questions = {}, []
    sources_by_intent, flow_by_intent, revisions_by_intent = {}, {}, {}
    idir = os.path.join(CM, "intents")


    UNIT_MAX_H = unit_max_hours()


    MSG_IDX = scan_records("comms", ("from", "to", "re", "type", "status"))
    RV_IDX = scan_records("reviews", ("reviewer", "target", "verdict", "checklist", "re"))
    ESC_IDX = scan_records("escalations", ("found_by", "found_in", "where", "severity",
                                           "scope_impact", "owner", "status", "created", "id"))


    AUTOPILOT = autopilot_config()
    decisions = parse_decisions()
    STEERS = scan_steers()
    _reversed_by = {d["reverses"]: d["id"] for d in decisions if d.get("reverses")}
    svg_flow_by_intent, svg_questions = {}, {}

    if os.path.isdir(idir):
        for name in sorted(os.listdir(idir)):
            base = os.path.join(idir, name)
            st = fm(read(os.path.join(base, "status.md")))
            if not st:
                continue
            it_text = read(os.path.join(base, "intent.md"))
            it = fm(it_text)
            plan_fm = fm(read(os.path.join(base, "intent-plan.md")))
            stage = int(num(st.get("stage", 1), 1))
            # `gate_open` chỉ có 8 giá trị hợp lệ. Bất cứ thứ gì khác là người viết tay ghi lạc —
            # nhận bừa thì tower dựng ra một gate ma và bắt người duyệt một thứ không tồn tại.
            raw_gate = (st.get("gate_open") or "null").strip().strip('"\'')
            gm = re.match(r"^(?:gate\s*)?([A-Ga-g])\b|^(escalation)$", raw_gate)
            gate_open = (gm.group(1).upper() if gm and gm.group(1) else
                         ("escalation" if gm else None))
            if raw_gate.lower() not in ("null", "none", "-", "") and not gate_open:
                print("cảnh báo: %s/status.md có `gate_open: %s` — không phải A–G hay escalation, "
                      "tower coi như KHÔNG có gate mở." % (name, raw_gate[:60]), file=sys.stderr)
            passed = [g.strip() for g in (st.get("gates_passed", "") or "").strip("[]").split(",") if g.strip()]
            # 6.4.0 (protocol §2.3) — hai trường tuỳ chọn; intent cũ không có thì cả hai rỗng, mọi thứ như trước.
            gates_auto = [g.strip() for g in (st.get("gates_auto", "") or "").strip("[]").split(",") if g.strip()]
            blocked_by = (st.get("blocked_by") or "").strip().strip('"\'').strip()
            if blocked_by.lower() in ("null", "none", "-", "—") or not gate_open:
                blocked_by = ""              # `blocked_by` chỉ có nghĩa khi có gate đang mở

            units = parse_units(base, name, stage)
            units_by_intent[name] = units
            srcs = parse_sources(base, name)
            sources_by_intent[name] = srcs
            qs = parse_questions(base)
            questions_by_intent[name] = qs
            questions += qs
            for _u in units:
                _u["stops"] = unit_stops(name, _u, passed, gate_open, qs)
            flow_by_intent[name] = build_flow(name, base, stage, passed, gate_open, units, srcs, qs,
                                              bool((it.get('brownfield_type') or '').strip()))
            metrics_by_intent[name] = build_metrics(name, base, units, srcs, qs,
                                                    [gate_open[:1]] if gate_open else [], passed)

            # ---- SVG: flow của intent + cây lựa chọn cho từng câu hỏi CÒN MỞ ----
            _dec_of_gate = {}
            for _d in decisions:                       # DEC mới nhất của mỗi gate thắng
                if _d.get("_to") == name and re.match(r"^[A-G]", _d.get("gate") or ""):
                    _dec_of_gate[_d["gate"][:1]] = _d["id"]
            svg_flow_by_intent[name] = svg_intent_flow(
                name, base, stage, passed, gate_open, gates_auto, blocked_by, units, _dec_of_gate,
                show_auto_legend=AUTOPILOT["mode"] == "autopilot")
            _details = parse_question_details(base)
            for _q in qs:
                if not _q["code"] or _q["code"] not in _details or \
                        re.search(r"closed|đã chốt|da chot|đóng|descoped", _q["status"], re.I):
                    continue
                _dt = _details[_q["code"]]
                _unl = _dt.get("unlocks") or []
                _svg_q, _meta = svg_question_tree(_q, _dt, extras={"badges": [
                    ("gỡ %d câu khác" % len(_unl), "blue", "t-active")]} if _unl else None)
                if _svg_q:
                    _sil = next((o for o in _dt["options"] if (o["key"] or o["name"]) == _meta.get("silent")), None)
                    svg_questions["%s:%s" % (name, _q["code"])] = dict(
                        _meta, svg=_svg_q,
                        **({"unlocks": _unl} if _unl else {}),
                        # mặc định mang HẠN ĐẢO: qua mốc đó thì đảo thành đắt — câu này phải được nhìn trước mốc
                        **({"silentUntil": _sil["reversal_until"]} if _sil and _sil.get("reversal_until") else {}))
            # ---- trang mô hình: tài liệu gate nào có fence human-view thì vẽ, không có thì không sinh gì ----
            _gd = (st.get("gate_doc") or "").strip().strip('"\'')
            _hv = human_views_of(name, base, "" if _gd.lower() in ("", "null", "none") else _gd,
                                 srcs, qs, _dec_of_gate)
            if _hv:
                human_view[name] = _hv
            if blocked_by:
                _bn = re.match(r"^#?(\d)\b", blocked_by)
                blocked_gates.append({"intent": name, "gate": gate_open[:1], "no": _bn.group(1) if _bn else "",
                                      "why": re.sub(r"^#?\d\s*[·:—–-]\s*", "", blocked_by)})

            revs = []
            rdir_i = os.path.join(base, "revisions")
            if os.path.isdir(rdir_i):
                for rf in sorted(os.listdir(rdir_i)):
                    rd = fm(read(os.path.join(rdir_i, rf)))
                    body = re.sub(r"^---.*?---\s*", "", read(os.path.join(rdir_i, rf)), flags=re.S).strip()
                    revs.append({"id": rf.replace(".md", ""), "gate": rd.get("gate", ""),
                                 "doc": rd.get("doc", ""), "version": rd.get("doc_version", ""),
                                 "status": rd.get("status", "open"), "at": rd.get("at", ""),
                                 "request": re.sub(r"\s+", " ", body)[:400]})
            revisions_by_intent[name] = revs

            trash_dir = os.path.join(base, "units", "_trash")
            obsolete = sorted(d for d in os.listdir(trash_dir)
                              if os.path.isdir(os.path.join(trash_dir, d))) if os.path.isdir(trash_dir) else []
            live_units = [u for u in units if not u.get("descoped")]
            n_done = sum(1 for u in live_units if u["status"] == "done")
            total_est = sum(u["estimate"] for u in live_units)
            c = srcs["counts"]
            intents.append({
                "id": name, "name": it.get("title", plan_fm.get("title", name)), "stage": stage,
                **({"gate": gate_open} if gate_open else {}),
                "phase": PHASE_OF_STAGE.get(stage, "inception"),
                "holder": STAGE_HOLDER.get(stage, "orchestrator"),
                "brownfield": BROWNFIELD.get(it.get("brownfield_type", ""), it.get("brownfield_type", "")),
                "doc": "intent-plan.md" if os.path.isfile(os.path.join(base, "intent-plan.md")) else "intent.md",
                "owner": "Human supervisor",
                "updated": mtime_hm(os.path.join(base, "status.md")) + " hôm nay",
                "units": [len(live_units), n_done], "estimate": round(total_est, 1),
                "descoped": len(units) - len(live_units),
                "obsolete": obsolete,
                "sources": [c.get("read", 0), c.get("total", 0)],
                "planVersion": st.get("plan_version", plan_fm.get("version", "")),
                "openRevisions": sum(1 for r in revs if r["status"] == "open"),
                "risk": None,
                **({"gatesAuto": gates_auto} if gates_auto else {}),
                **({"blockedBy": blocked_by} if blocked_by else {}),
            })

            # ---- gate đang mở: đính TOÀN VĂN gate_doc để preview ----
            if gate_open:
                g = gate_open[:1]
                gate_doc_rel = (st.get("gate_doc") or "").strip()
                if gate_doc_rel in ("", "null"):
                    gate_doc_rel = GATE_DOC_DEFAULT.get(g, "")
                if gate_doc_rel and not os.path.isfile(os.path.join(base, gate_doc_rel)) \
                        and g in GATE_DOC_LEGACY and os.path.isfile(os.path.join(base, GATE_DOC_LEGACY[g])):
                    gate_doc_rel = GATE_DOC_LEGACY[g]      # intent ≤2.2 còn dùng file gộp
                doc = load_doc(os.path.join(base, gate_doc_rel)) if gate_doc_rel else None
                if doc:
                    docs[doc["path"]] = doc
                brief_p = os.path.join(base, "decision-briefs", "brief-%s.md" % g)
                btxt = read(brief_p)
                options = re.findall(r"^- \(?\d?\)?\s*(.+)$", section(btxt, "Phương án"), re.M)
                if not options:
                    options = [s.strip() for s in re.split(r"\(\d\)", section(btxt, "Phương án")) if s.strip()][:3]
                checks = []
                if g == "A":
                    checks = ["Outcome đúng cái bạn muốn?",
                              "Bảng nguồn (phần 2) đã đủ chưa — có nguồn nào bạn biết mà agent chưa liệt kê?",
                              "Mâu thuẫn ở 1.7 chốt theo bên nào?",
                              "Trục phân rã + khối lượng ở phần 3 hợp lý?"]
                elif g == "B":
                    checks = ["AS-IS đúng thực tế?",
                              "Nguồn `missing`/`deferred` có chấp nhận được không?",
                              "Vùng chưa có nguồn phủ đã xử lý chưa?"]
                elif g == "C":
                    checks = ["Mỗi câu bạn trả lời được ngay, không phải hỏi lại kỹ thuật?",
                              "Phương án AI đề xuất có chấp nhận được không?",
                              "Câu nào bạn không quyết được thì ai quyết — đã ghi đúng người chưa?"]
                elif g == "D":
                    checks = ["Phân rã Unit cuối đúng?", "Mọi Unit có `releasable` + `session_fit` có con số, đủ US/NFR/risk?",
                              "Trade-off ở mục 7 chọn phương án nào?"]
                oq_block = [q for q in qs if q["blocking"]]
                gates.append({
                    "key": "g-%s-%s" % (name, g), "kind": "gate", "gate": g,
                    "target": name, "title": GATE_TITLE.get(g, "Chờ quyết định"),
                    "brief": section(btxt, "Bối cảnh") or (doc and doc["title"]) or
                             ("Xem " + gate_doc_rel if gate_doc_rel else "Chưa có decision brief."),
                    "options": options[:4],
                    "recommendation": section(btxt, "Khuyến nghị"),
                    "evidence": re.findall(r"\b(?:RV|MSG|DEC|REV)-\d+\b", btxt)[:5],
                    "doc": doc["path"] if doc else None,
                    "docTitle": doc["title"] if doc else None,
                    "docVersion": doc["version"] if doc else "",
                    "docMissing": doc is None,
                    "requiresPreview": True,
                    "checks": checks,
                    "blockers": (["Source ledger còn %d nguồn `planned` — chưa đủ điều kiện đóng gate này"
                                  % c["planned"]] if g in ("B", "D") and c.get("planned") else []) +
                                ([u["id"] + ": " + ", ".join(u["problems"]) for u in units if u["problems"]]
                                 if g == "D" else []) +
                                # protocol §4.10.4 — câu CHẶN còn treo thì không đóng được gate
                                # Gate C KHÔNG chặn vì câu hỏi còn mở — trả lời chính là việc của gate này.
                                (["%s còn treo (%s) — chốt, hoặc hạ [ASSUMED] + ghi rủi ro vào Unit: %s"
                                  % (q["code"] or "OQ", q["who"] or "chưa rõ người trả lời", q["q"][:70])
                                  for q in oq_block if q["audience"] == "tech"][:5] if g == "D" else []),
                    "revisions": [r for r in revs if r["status"] == "open"][:3],
                    # 6.4.0 — gate mở vì autopilot BLOCK (không phải vì chờ duyệt): thẻ đỏ, lý do lên đầu
                    **({"blockedBy": blocked_by} if blocked_by else {}),
                })


    stations, handoffs = [], []
    hdir = os.path.join(CM, "handoffs")
    if os.path.isdir(hdir):
        for f in sorted(os.listdir(hdir)):
            if not f.startswith("HOF-"):
                continue
            p = os.path.join(hdir, f)
            d = fm(read(p))
            if not d:
                continue
            body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S)
            agent = (d.get("to") or "?").replace("dlc-", "")
            hb = (d.get("heartbeat") or "-").strip()
            status_v = (d.get("status") or "").strip()
            now_dt = datetime.datetime.now()
            try:
                file_dt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
            except OSError:
                file_dt = now_dt
            hb_dt = parse_iso_local(hb)
            silent, hb_kind, hb_why = None, "", ""
            if status_v == "accepted":
                ref = hb_dt or parse_iso_local(d.get("accepted"))
                if ref is not None:
                    silent = int((now_dt - ref).total_seconds() // 60)
                hb_kind, hb_why = heartbeat_audit(hb, hb_dt, file_dt, now_dt)
                if hb_kind:
                    print("cảnh báo: %s (%s) — %s" % (d.get("id", f), agent, hb_why), file=sys.stderr)
            row = {
                "id": d.get("id", f.replace(".md", "")), "agent": agent,
                "from": (d.get("from") or "?").replace("dlc-", ""),
                "lane": LANE.get(agent, "review"), "status": (d.get("status") or "open").strip(),
                "re": d.get("re", "—"), "kind": d.get("kind", "assign"),
                "created": d.get("created", ""), "accepted": d.get("accepted", "-"),
                "closed": d.get("closed", "-"),
                "heartbeat": hb, "progress": (d.get("progress") or "-").strip(),
                # §9.6: người giao nghiệm kết quả — "pass · <ISO> · <đã kiểm gì>" | "returned · ..." | "-"
                "resultCheck": (d.get("result_check") or "").strip().lstrip("-").strip(),
                "silentMin": silent, "stale": bool(silent is not None and silent > 15 and not hb_kind),
                # lời khai vs dấu vết (protocol §9.4) — hbKind rỗng nghĩa là nhịp khai khớp với file
                "hbKind": hb_kind, "hbWhy": hb_why,
                "fileMin": int((now_dt - file_dt).total_seconds() // 60),
                # tên teammate (agent team) nếu lượt này chạy bằng phiên riêng — protocol §9.5
                "teammate": (d.get("teammate") or "").strip(),
                "blocked": [x.strip() for x in (d.get("blocked_by") or "").strip("[]").split(",") if x.strip() and x.strip() != "-"],
                "reads": len([x for x in (d.get("read_first") or "").strip("[]").split('", "') if x.strip(' "')]),
                "task": (re.search(r"^#\s*HOF-\S+\s*·\s*(.+)$", body, re.M) or
                         re.search(r"^##\s*Nhiệm vụ.*?\n+(.+)$", body, re.M | re.S) or [None, ""])[1].strip().split("\n")[0][:90],
                "pending": [l.strip("- ").strip()[:90] for l in
                            md_section(body, r"Còn treo").splitlines() if l.strip().startswith("-") and len(l.strip()) > 2][:3],
                "doc": os.path.relpath(p, A),
            }
            handoffs.append(row)
            if row["status"] in ("accepted", "open", "returned"):
                stations.append(row)
    stations.sort(key=lambda r: {"returned": 0, "accepted": 1, "open": 2}.get(r["status"], 3))
    handoffs = sorted(handoffs, key=lambda r: r["id"], reverse=True)[:40]

    # KPI nhịp sống: mỗi luật mới cần một trường để điền VÀ một con số để đối chiếu, nếu không nó sẽ trượt.
    # Trường = `heartbeat:`; con số = bao nhiêu vị trí đang chạy có nhịp khớp với dấu vết trên đĩa.
    _acc = [r for r in stations if r["status"] == "accepted"]
    handoff_health = {
        "accepted": len(_acc),
        "trusted": len([r for r in _acc if not r["hbKind"] and r["heartbeat"] not in ("-", "")]),
        "suspect": [{"id": r["id"], "agent": r["agent"], "kind": r["hbKind"], "why": r["hbWhy"]}
                    for r in _acc if r["hbKind"]],
        "noHeartbeat": [{"id": r["id"], "agent": r["agent"]} for r in _acc if r["heartbeat"] in ("-", "")],
        "teammates": [{"id": r["id"], "agent": r["agent"], "teammate": r["teammate"]}
                      for r in _acc if r["teammate"]],
    }
    # §9.6: HOF `done` mà người giao chưa nghiệm (`result_check` trống) = kết quả đang được dùng bằng lời khai.
    # Đếm trên danh sách handoffs hiển thị (40 gần nhất) — HOF cũ trước v6 không có trường này, chỉ liệt kê
    # chứ không lên án: doctor phân biệt legacy khi soi.
    _done_all = [r for r in handoffs if r["status"] == "done"]
    handoff_health["closed"] = len(_done_all)
    handoff_health["checked"] = len([r for r in _done_all if r["resultCheck"].lower().startswith("pass")])
    handoff_health["doneUnchecked"] = [{"id": r["id"], "agent": r["agent"], "re": r["re"]}
                                       for r in _done_all if not r["resultCheck"]][:20]


    team = scan_team()
    for _z in team["zombies"]:
        print("cảnh báo: teammate `%s` %s (protocol §9.5.6 — tắt đi, cần lại thì spawn bằng HOF mới)"
              % (_z["name"], _z["why"]), file=sys.stderr)
    for _d in team["deadLetters"]:
        print("cảnh báo: TIN CHẾT — %d tin gửi cho `%s` nhưng agent đó không có trong team; spawn hỏng mà "
              "người gửi tưởng đã gửi được (protocol §9.5)" % (_d["count"], _d["to"]), file=sys.stderr)

    for _r in handoff_health["noHeartbeat"]:
        print("cảnh báo: %s (%s) đang `accepted` mà không có `heartbeat:` — tower không biết nó còn sống"
              % (_r["id"], _r["agent"]), file=sys.stderr)


    activity = scan_activity()
    # Vị trí "open" nhưng vùng của nó vừa có file đổi → thực tế đang chạy mà chưa nhận HOF
    for s in stations:
        if s["status"] != "open":
            continue
        key = (s["re"] or "").split("/")
        tag = key[1] if len(key) > 1 else ""
        s["unclaimedActivity"] = bool(tag and any(tag in a["path"] for a in activity))

    # ---------- comms / reviews / decisions ----------
    feed, reviews = [], []
    cdir = os.path.join(CM, "comms")
    if os.path.isdir(cdir):
        for f in sorted(os.listdir(cdir), reverse=True)[:30]:
            p = os.path.join(cdir, f)
            d = fm(read(p))
            body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S).strip()
            if d:
                feed.append({"time": mtime_hm(p), "id": f.replace(".md", ""), "from": d.get("from", "?").replace("dlc-", ""),
                             "to": d.get("to", "?").replace("dlc-", ""), "type": d.get("type", "note"),
                             "summary": re.sub(r"\s+", " ", body)[:140]})
    rdir = os.path.join(CM, "reviews")
    if os.path.isdir(rdir):
        for f in sorted(os.listdir(rdir), reverse=True)[:20]:
            p = os.path.join(rdir, f)
            d = fm(read(p))
            body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S).strip()
            finding = next((l for l in body.splitlines() if l.startswith("[")), "—")
            if d:
                reviews.append({"id": f.replace(".md", ""), "reviewer": d.get("reviewer", "?").replace("dlc-", ""),
                                "target": d.get("target", ""), "verdict": d.get("verdict", ""),
                                "checklist": d.get("checklist", ""), "findings": finding[:160]})
                feed.append({"time": mtime_hm(p), "id": f.replace(".md", ""), "from": d.get("reviewer", "?").replace("dlc-", ""),
                             "to": d.get("target", "").split("/")[0], "type": "finding" if "changes" in d.get("verdict", "") else "review-request",
                             "summary": (d.get("verdict", "") + " · " + finding)[:140]})
    # `decisions` đã đọc ở trên (parse_decisions) — flow của intent cần nó trước vòng intent.
    for _d in decisions:
        feed.append({"time": "", "id": _d["id"], "from": "orchestrator", "to": _d.pop("_to"),
                     "type": "decision", "summary": _d["what"][:140]})
    feed = [x for x in feed if x["summary"]][:25]
    for _d in decisions:
        if not _d.get("autopilot"):
            continue
        # Quyết xong mà không đóng sổ: người nhìn tower vẫn thấy thẻ đỏ của một việc AI đã quyết rồi.
        for _e in _d.get("escRefs") or []:
            if esc_is_open(_e):
                auto_warnings.append({"dec": _d["id"], "esc": _e, "intent": _d["intent"],
                                      "text": "%s đã quyết %s nhưng %s vẫn open" % (_d["id"], _e, _e)})
        _d["shownDoc"] = resolve_shown_doc(_d["intent"], _d.get("shownAt"))
        _d["reversedBy"] = _reversed_by.get(_d["id"], "")
        _d["steer"] = STEERS.get(_d["id"], "")
        _d["svg"] = svg_autopilot_decision(_d)
        # gate này có tài liệu mang human-view ⇒ thẻ có nút "Xem mô hình"
        for _m in (human_view.get(_d["intent"]) or {}).get("docs", {}).values():
            if _m["gate"] and _m["gate"] == (_d.get("gate") or "")[:1] and not _m["error"]:
                _d["modelDoc"] = _m["doc"]
        auto_decisions.append(_d)

    # Hai DEC autopilot còn hiệu lực áp hai phương án khác nhau cho cùng một mã (#36) — cùng luật với AP14:
    # đọc dòng `Áp` trước, DEC bị ghi `(thay DEC-NNNN)` hết hiệu lực ở mã đó.
    _idx = applied_index()
    for (_iid2, _code), _picks in sorted(_idx.items()):
        _live = live_applied(_iid2, _code, _idx)
        if len({p["opt"] for p in _live}) > 1:
            auto_warnings.append({"dec": _live[-1]["dec"], "with": _live[0]["dec"], "code": _code, "intent": _iid2,
                                  "text": "%s cùng quyết %s nhưng khác phương án (%s)" % (
                                      " và ".join(p["dec"] for p in _live), _code,
                                      " ≠ ".join(dict.fromkeys(p["opt"] for p in _live)))})
    # Trạng thái ĐANG ÁP của từng mã (câu hỏi, điểm cần chốt, ESC): phương án · DEC · DEC nó thay
    applied_now = {}
    for (_iid2, _code), _picks in sorted(_idx.items()):
        _live = live_applied(_iid2, _code, _idx)
        if _live and len({p["opt"] for p in _live}) == 1:
            _last = _live[-1]
            applied_now.setdefault(_iid2, {})[_code] = {
                "option": _last["opt"], "dec": _last["dec"], "gate": _last["gate"],
                "replaces": [p["repl"] for p in _picks if p["dec"] == _last["dec"] and p["repl"]]}
    # Thẻ "AI đã tự quyết": DEC này đã áp những mã nào, mã nào đã bị DEC sau thay
    for _d in auto_decisions:
        _d["appliedCodes"] = [
            {"code": c, "option": o,
             "replacedBy": next((p["dec"] for p in _idx.get((_d["intent"], c), []) if p["repl"] == _d["id"]), "")}
            for c, o, _r in _d.get("applied") or []]

    for _iid, _ms in metrics_by_intent.items():
        _mine = [d for d in auto_decisions if d["intent"] == _iid]
        _blk = [b for b in blocked_gates if b["intent"] == _iid]
        if not (_mine or _blk or AUTOPILOT["present"]):
            continue
        _dl = [{"file": "context-memory/governance/decisions-log.md",
                "section": "mục `## DEC-NNNN · … · autopilot` (hoặc `Người quyết: autopilot`)", "rows": len(_mine)}]
        _rev = [d for d in _mine if d["reversedBy"] or d["steer"]]
        _through = [d for d in _mine if d["blockHits"]]
        _short = [d for d in _mine if d["missing"]]
        for _key, _val, _label, _rule, _files, _rows, _warn, _tone in (
            ("autopilot.decisions", len(_mine), "quyết định AI đã tự quyết",
             "Đếm entry trong `decisions-log.md` do autopilot ghi cho intent này. Mỗi entry phải đủ các dòng "
             "Chọn · Bỏ · Đảo bằng · Hiện ở · Block check (protocol §5) — thiếu dòng nào thì người xem không "
             "đảo được có căn cứ.",
             _dl, [{"DEC": d["id"], "Gate": d["gate"], "Khi nào": d["when"], "Chọn": d["chosen"][:80],
                    "Block check": d["blockCheck"][:80] or "—",
                    "Thiếu dòng": ", ".join(d["missing"]) or "—"} for d in _mine],
             (["%d DEC autopilot thiếu dòng bắt buộc: %s" % (len(_short), ", ".join(d["id"] for d in _short))]
              if _short else []) + [w["text"] for w in auto_warnings if w["intent"] == _iid],
             "gate" if any(w["intent"] == _iid for w in auto_warnings) else "agent"),
            ("autopilot.reversed", "%d/%d" % (len(_rev), len(_mine)), "quyết định tự động đã bị người đảo",
             "Một quyết định tính là đã đảo khi có `inbox/steer-*.json` (hoặc `inbox/processed/steer-*.json`) trỏ "
             "vào nó, hoặc có DEC sau ghi `reverses: DEC-NNNN`. Cách đọc theo `governance/autopilot.md`: 10–30% "
             "là Lead đang nhìn thật · dưới 10% nghi không ai nhìn · trên 30% là giả định của AI kém.",
             _dl + [{"file": "inbox/", "section": "steer-*.json (chờ áp) · processed/steer-*.json (đã áp)",
                     "rows": sum(1 for d in _mine if d["steer"])}],
             [{"DEC": d["id"], "Gate": d["gate"], "Quyết định": d["what"][:80],
               "Đảo bằng": d["reversedBy"] or ("steer đã áp" if d["steer"] == "applied" else "steer chờ áp")}
              for d in _rev], [], "agent"),
            ("autopilot.blocked", len(_blk), "gate đang đứng vì autopilot block",
             "Đọc `blocked_by` trong `status.md` khi `gate_open` có giá trị. Số `#n` đầu dòng là điều kiện block "
             "trong `governance/autopilot.md` (1 câu chặn không có mặc định · 2 thiếu thông tin viết AC/test · "
             "3 nguồn P0 không tự đọc được · 4 ranh đỏ · 5 doctor FIX · 6 tự sửa quá số lần).",
             [{"file": "context-memory/intents/%s/status.md" % _iid,
               "section": "frontmatter `gate_open` · `blocked_by`", "rows": len(_blk)}],
             [{"Gate": b["gate"], "Điều kiện #": b["no"] or "—", "Lý do": b["why"]} for b in _blk],
             ["%s: block check ghi `hit` mà autopilot vẫn tự quyết — tự quyết qua block là lỗi (doctor FIX)"
              % d["id"] for d in _through], "gate" if _blk or _through else "done"),
        ):
            _ms[_key] = {"key": _key, "value": _val, "label": _label, "rule": _rule, "files": _files,
                         "rows": _rows[:80], "rowCount": len(_rows), "warnings": list(_warn), "tone": _tone}


    risks = parse_reg(os.path.join(CM, "governance", "risks.md"), "risk")
    debt = parse_reg(os.path.join(CM, "governance", "tech-debt-register.md"), "debt")
    ldir = os.path.join(CM, "lessons-learned")
    if os.path.isdir(ldir):
        for f in sorted(os.listdir(ldir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(ldir, f)
            d = fm(read(p))
            body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S)
            lm = re.search(r"Lesson:\s*(.+)", body)
            h1 = re.search(r"^#\s+(.+)$", body, re.M)
            # LL do người viết hiếm khi có dòng "Lesson:" — lấy tiêu đề H1 làm nội dung thay vì hiện ô trống.
            # Khoá frontmatter tiếng Việt (`loại`, `trạng-thái`) cũng phải đọc được: dự án thật viết như vậy.
            text = (lm.group(1) if lm else (h1.group(1) if h1 else "")).strip()
            text = re.sub(r"^LL-\d+\s*·\s*", "", text)
            lessons.append({"id": f.replace(".md", ""),
                            "trigger": (d.get("trigger") or d.get("loại") or d.get("phát-hiện-bởi") or "")[:120],
                            "lesson": text[:200], "patch": d.get("applied_to", ""),
                            "status": (d.get("status") or d.get("trạng-thái") or "proposed")[:80],
                            "path": os.path.relpath(p, A)})
    edir = os.path.join(CM, "escalations")
    if os.path.isdir(edir):
        for f in sorted(os.listdir(edir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(edir, f)
            d = fm(read(p))
            body = re.sub(r"^---.*?---\s*", "", read(p), flags=re.S)
            h1 = re.search(r"^#\s+(.+)$", body, re.M)
            escalations.append({
                "id": d.get("id", f.replace(".md", "")),
                "title": re.sub(r"^ESC-\d+\s*·\s*", "", h1.group(1).strip())[:160] if h1 else "",
                "foundBy": d.get("found_by", ""), "foundIn": d.get("found_in", ""),
                "where": d.get("where", ""), "severity": d.get("severity", ""),
                "level": norm_level(d.get("severity", "")),
                "scopeImpact": d.get("scope_impact", "none"),
                "owner": (d.get("owner") or "").strip(),
                "status": (d.get("status") or "open").strip(),
                "created": d.get("created", ""), "path": os.path.relpath(p, A),
                "intent": esc_intent(d)})
            _ev = esc_view(p, escalations[-1]["id"])
            if _ev:
                svg_escalations[escalations[-1]["id"]] = _ev


    gov_changelog = [{"v": l[2:60], "when": "", "by": "", "dec": "", "from": ""}
                     for l in read(os.path.join(CM, "governance", "changelog.md")).splitlines() if l.startswith("- ")][:6]

    # Task mặc định khi chưa chọn unit nào. Bảng task THẬT của mỗi unit nằm trong chính unit đó
    # (`unit.boltDetails[].tasks`) — không tra bằng khoá `UOW-NN` nữa: hai intent có thể cùng có UOW-01
    # và tra theo mã unit trần sẽ lấy task của intent khác (đúng cái đã xảy ra trên fixture).
    tasks, work, tasks_from = [], [], None
    if os.path.isdir(idir):
        cands = []
        for iid, us in units_by_intent.items():
            for u in us:
                for b in u.get("boltDetails", []):
                    if b["tasksFile"]:
                        cands.append((u.get("descoped"), b["tasksFile"], b["tasks"]))
        live_cands = [c for c in cands if not c[0]]
        pick = (live_cands or cands)[-1] if cands else None
        if pick:
            tasks_from = {"file": pick[1], "live": bool(live_cands),
                          "others": max(0, len(live_cands or cands) - 1)}
            tasks = pick[2]
    _ib = os.path.join(A, "inbox")
    if os.path.isdir(_ib):
        for _f in sorted(os.listdir(_ib)):
            if not _f.endswith(".json"):
                continue
            try:
                with open(os.path.join(_ib, _f), encoding="utf-8") as _fh:
                    _j = json.load(_fh)
            except Exception:  # noqa: BLE001 — file hỏng vẫn phải hiện là "đang treo"
                _j = {}
            inbox_pending.append({"file": _f, "kind": _j.get("kind") or _j.get("type") or _f.split("-")[0],
                                  "intent": _j.get("intent", ""), "code": _j.get("code", ""),
                                  "esc": _j.get("esc", ""), "gate": _j.get("gate", ""),
                                  **({"dec": _j["dec"]} if _j.get("dec") else {}),
                                  "at": _j.get("answered_at") or _j.get("decided_at") or _j.get("at", "")})

    first = intents[0]["id"] if intents else None
    decisions_out = [{k: d[k] for k in _DEC_KEYS} for d in decisions]
    data = {
        "autopilot": dict(AUTOPILOT, decisions=auto_decisions, blocked=blocked_gates, warnings=auto_warnings,
                      applied=applied_now),
        "svg": {"css": SVG_CSS, "flowByIntent": svg_flow_by_intent, "questions": svg_questions,
                "escalations": svg_escalations},
        "humanView": human_view,
        "inboxPending": inbox_pending,
        "project": {"name": os.path.basename(ROOT), "root": ROOT,
                    "generated": datetime.datetime.now().strftime("%d/%m %H:%M"), "plugin": PLUGIN_VERSION},
        "intents": intents, "unitsByIntent": units_by_intent, "gates": gates, "docs": docs,
        "sourcesByIntent": sources_by_intent, "flowByIntent": flow_by_intent,
        "metricsByIntent": metrics_by_intent,
        "revisionsByIntent": revisions_by_intent,
        "units": units_by_intent.get(first, []) if first else [],
        "stations": stations, "handoffs": handoffs, "activity": activity,
        "handoffHealth": handoff_health, "team": team,
        "tasks": tasks, "tasksFrom": tasks_from, "work": work, "feed": feed,
        "trace": ([{"kind": "dec", "id": decisions[-1]["id"], "note": decisions[-1]["what"][:60]}] if decisions else []) +
                 ([{"kind": "rv", "id": reviews[0]["id"], "note": reviews[0]["verdict"]}] if reviews else []) +
                 ([{"kind": "msg", "id": feed[0]["id"], "note": feed[0]["type"]}] if feed else []) +
                 ([{"kind": "intent", "id": intents[0]["id"], "note": intents[0]["name"][:50]}] if intents else []),
        "reviews": reviews, "decisions": decisions_out,
        "questions": questions, "questionsByIntent": questions_by_intent,
        "risks": risks, "debt": debt, "lessons": lessons, "escalations": escalations,
        "governance": {"dor": gov_doc("dor"), "dod": gov_doc("dod"), "changelog": gov_changelog},
    }

    # ---------- write ----------
    os.makedirs(OUT, exist_ok=True)
    ui = os.path.abspath(UI_SRC)
    if os.path.isdir(ui):
        for rel_root, dirs, files in os.walk(ui):
            rel = os.path.relpath(rel_root, ui)
            dst_dir = OUT if rel == "." else os.path.join(OUT, rel)
            os.makedirs(dst_dir, exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(rel_root, f), os.path.join(dst_dir, f))
    with open(os.path.join(OUT, "data.js"), "w", encoding="utf-8") as f:
        f.write("// generated by tower_generate.py — %s\nwindow.CT_DATA = %s;\n"
                % (datetime.datetime.now().isoformat(timespec="seconds"),
                   json.dumps(data, ensure_ascii=False, indent=1)))
    print(os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
