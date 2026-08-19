#!/usr/bin/env python3
"""AI-DLC Control Tower generator (v3 — gate doc preview + dòng chảy 3 pha).

Usage: python3 tower_generate.py [project_root]

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
import json
import os
import re
import shutil
import sys

def resolve_root(start):
    """Tìm gốc dự án AI-DLC thật. TRƯỚC 4.0.0 script nhận bừa cwd làm gốc và tạo `.ai-dlc/tower/`
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


ROOT, ASKED = resolve_root(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
if ROOT is None:
    sys.exit("Không tìm thấy dự án AI-DLC nào từ '%s' (thiếu `.ai-dlc/context-memory/`).\n"
             "Không tạo gì cả — chạy `/dlc-init` nếu đây là dự án mới, hoặc truyền đúng gốc:\n"
             "  python3 tower_generate.py <đường-dẫn-gốc-dự-án>" % ASKED)
if os.path.abspath(ROOT) != os.path.abspath(ASKED):
    print("gốc dự án: %s (bạn đưa vào '%s')" % (ROOT, ASKED), file=sys.stderr)
A = os.path.join(ROOT, ".ai-dlc")
CM = os.path.join(A, "context-memory")
UI_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tower-ui")
OUT = os.path.join(A, "tower")

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


# ---------- intents ----------
intents, units_by_intent, gates, docs = [], {}, [], {}
questions_by_intent, questions = {}, []
metrics_by_intent = {}
sources_by_intent, flow_by_intent, revisions_by_intent = {}, {}, {}
idir = os.path.join(CM, "intents")


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
    for m in list(re.finditer(r"\[CONFLICT\]", body))[:10]:
        before = re.sub(r"\s+", " ", body[max(0, m.start() - 70):m.start()])
        if re.search(r"không\s+(có|phải|gặp)\s*$|chưa\s+có\s*$", before, re.I):
            continue
        line = re.sub(r"\s+", " ", body[body.rfind("\n", 0, m.start()) + 1:
                                        (body.find("\n", m.end()) + 1 or len(body))]).strip()
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


def parse_plan_rows(base):
    """Unit đang được ĐỀ XUẤT: quét mọi dòng bảng `| UOW-NN |` trong unit-plan.md.
    Không bám số mục vì unit-plan mỗi dự án đánh số khác nhau. Ô est là ô đầu tiên
    chứa dạng `4.5h` (chấp cả **4.5h**). Dòng tổng (id rỗng) tự loại vì regex đòi UOW-NN."""
    txt = read(os.path.join(base, "unit-plan.md"))
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
        m = re.search(r"^##+[^\n]*(?:Bảng điều phối|Bang dieu phoi)[^\n]*$(.*?)(?=^##\s)", txt, re.M | re.S)
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

    Trả (status, raw). Trước 3.1.1 chỉ `done` mới tính là xong, nên 21 unit ghi `approved` của PCT
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


UNIT_MAX_H = unit_max_hours()
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

    Trần 5h cũ bắt tách theo đồng hồ nên đẻ ra unit vụn không tự release được (`DEC-0052` của PCT tách
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
            "problems": (["est %.1fh > 5h" % est] if est > 5.0 else []),
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
        # (UOW-19..22 của PCT là ví dụ: đã giao xong mà bị tính là ngoài phạm vi).
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


MSG_IDX = scan_records("comms", ("from", "to", "re", "type", "status"))
RV_IDX = scan_records("reviews", ("reviewer", "target", "verdict", "checklist", "re"))
ESC_IDX = scan_records("escalations", ("found_by", "found_in", "where", "severity",
                                       "scope_impact", "owner", "status", "created", "id"))

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
            })

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

    Ca thật (PCT · HOF-0039 · 13/08): agent ghi HOF lúc 18:13 nhưng khai `heartbeat: …T00:00:00Z`,
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


stations, handoffs = [], []
hdir = os.path.join(CM, "handoffs")
LANE = {"be-dev": "pipeline", "fe-dev": "pipeline", "bolt-coordinator": "pipeline",
        "orchestrator": "pipeline", "intent-analyst": "pipeline", "source-planner": "pipeline",
        "context-archaeologist": "pipeline", "context-validator": "pipeline", "unit-planner": "pipeline",
        "acceptance-recorder": "pipeline", "retro-keeper": "pipeline"}
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
def scan_team():
    """Agent team của CHÍNH dự án này — chỉ đọc `~/.claude/teams/*/config.json` có `cwd` của lead trùng ROOT.

    Hai thứ cần thấy:
    1. Ai đang thật sự chạy như một phiên riêng (ghép pane với dòng trên board).
    2. **Tin chết** — hộp thư mang tên một teammate KHÔNG có trong `members`. Ca thật (PCT · 13/08): 5 lần
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
        # Lead hay ngồi ở gốc monorepo trong khi dự án AI-DLC là một thư mục con (ca PCT trong portal-hub)
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
    for m in re.finditer(r"^\s{2,}\w+:\s*(\S+)\s*$", wm, re.M):
        v = m.group(1).strip().strip('"')
        if v and v != "null":
            p = os.path.join(ROOT, v)
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
decisions = []
for m in re.finditer(r"^## (DEC-\d+) · ([^·\n]+) · ([^·\n]+) · (\S+)\n(.*?)(?=\n## |\Z)",
                     read(os.path.join(CM, "governance", "decisions-log.md")), re.S | re.M):
    body = m.group(5)
    what = re.search(r"Quyết định:\s*(.+)", body)
    basis = re.search(r"Căn cứ:\s*(.+)", body)
    decisions.append({"id": m.group(1), "when": m.group(2).strip(), "gate": m.group(3).replace("Gate", "").strip(),
                      "by": "Human supervisor", "what": (what.group(1).strip()[:180] if what else ""),
                      "basis": (basis.group(1).strip()[:60] if basis else "")})
    feed.append({"time": "", "id": m.group(1), "from": "orchestrator", "to": m.group(4),
                 "type": "decision", "summary": (what.group(1).strip()[:140] if what else "")})
feed = [x for x in feed if x["summary"]][:25]


def parse_reg(path, kind):
    out = []
    for l in read(path).splitlines():
        m = re.match(r"^- (\S+) · (\w+) · (.+)", l)
        if m:
            rest = m.group(3)
            owner = re.search(r"chủ:\s*([^·]+)", rest)
            out.append({"id": m.group(1), "sev": {"high": "high", "medium": "med", "low": "low"}.get(m.group(2), m.group(2)),
                        "text": rest.split("·")[0].strip()[:160],
                        "owner": owner.group(1).strip() if owner else "—"})
    return out


risks = parse_reg(os.path.join(CM, "governance", "risks.md"), "risk")
debt = parse_reg(os.path.join(CM, "governance", "tech-debt-register.md"), "debt")

lessons = []
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

# escalations/ — phát hiện NGOÀI phạm vi unit (protocol §4.13). Không có chỗ này thì phát hiện
# chìm theo HOF đóng lại; tower phải hiện nó cho tới khi có người nhận.
escalations = []
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
            "scopeImpact": d.get("scope_impact", "none"),
            "owner": (d.get("owner") or "").strip(),
            "status": (d.get("status") or "open").strip(),
            "created": d.get("created", ""), "path": os.path.relpath(p, A)})


def gov_doc(name):
    p = os.path.join(CM, "governance", name + ".md")
    d = fm(read(p))
    items = [m.strip() for m in re.findall(r"^- \[ \] (.+)$", read(p), re.M)][:10]
    return {"version": "v" + str(d.get("version", "1")), "items": items}


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

first = intents[0]["id"] if intents else None
data = {
    "project": {"name": os.path.basename(ROOT), "root": ROOT,
                "generated": datetime.datetime.now().strftime("%d/%m %H:%M"), "plugin": "5.0.0"},
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
    "reviews": reviews, "decisions": decisions,
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
