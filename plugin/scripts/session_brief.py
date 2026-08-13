#!/usr/bin/env python3
"""AI-DLC session brief — quét .ai-dlc/ rồi in MỘT bản tóm tắt gọn để vào việc.

Usage:
  python3 session_brief.py [project_root] [--open-session] [--close-session SES-NNN] [--board-only]

Mục đích: phiên mới KHÔNG phải nạp lại cả dự án (protocol §10). Toàn bộ việc quét
thư mục xảy ra ở đây (Python), agent chỉ đọc stdout — vài chục dòng có tín hiệu cao.

Việc nó làm:
1. Đọc frontmatter: status.md từng intent · handoffs/*.md · inbox/*.json · session/log gần nhất.
   KHÔNG đọc toàn văn intent-plan/unit-plan/as-is — chỉ đếm và trích số.
2. Kết xuất `context-memory/session/board.md` (bảng vị trí) từ handoffs/ — nguồn sự thật duy nhất.
3. Seed `session/INDEX.md` nếu chưa có.
4. In briefing: intents · vị trí đang làm việc · inbox tồn · cảnh báo chặn gate · việc kế tiếp.
"""
import datetime
import glob
import json
import os
import re
import shutil
import sys

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FLAGS = {a for a in sys.argv[1:] if a.startswith("--")}
ROOT = os.path.abspath(ARGS[0] if ARGS else os.getcwd())
A = os.path.join(ROOT, ".ai-dlc")
CM = os.path.join(A, "context-memory")
HOF = os.path.join(CM, "handoffs")
SESS = os.path.join(CM, "session")
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
NOW = datetime.datetime.now()

RE_SRC_READ = re.compile(r"✅|\bread\b|đã\s*đọc|đọc\s*xong", re.I)
RE_SRC_TODO = re.compile(r"⬜|\bplanned\b|chưa\s*đọc|chưa\s*xử\s*lý", re.I)
RE_SRC_FINAL = re.compile(r"✅|\bread\b|đã\s*đọc|\bmissing\b|không\s*tìm\s*thấy|\bdeferred\b|hoãn|"
                          r"\bsuperseded\b|thay\s*thế", re.I)

_TOWER_CACHE = {}


def tower_counts(intent_id):
    """Số nguồn mà Control Tower đang hiện, nếu tower đã được sinh. Đọc `.ai-dlc/tower/data.js`
    một lần rồi cache. Không có / hỏng → None, brief tự đếm lấy."""
    if "d" not in _TOWER_CACHE:
        _TOWER_CACHE["d"] = None
        p = os.path.join(A, "tower", "data.js")
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
            _TOWER_CACHE["d"] = json.loads(txt[txt.index("{"):txt.rindex(";")])
        except (OSError, ValueError):
            pass
    d = _TOWER_CACHE["d"]
    if not d:
        return None
    c = ((d.get("sourcesByIntent") or {}).get(intent_id) or {}).get("counts")
    if not c or not c.get("total"):
        return None
    return c.get("read", 0), c.get("total", 0), c.get("planned", 0)


PHASE = {1: "inception", 2: "inception", 3: "inception", 4: "inception", 5: "inception",
         6: "construction", 7: "operations", 8: "operations"}
GATE_NEXT = {"A": "/dlc-discover", "B": "/dlc-validate", "C": "/dlc-units",
             "D": "/dlc-bolt <UOW-NN>", "E": "/dlc-bolt", "F": "/dlc-accept", "G": "/dlc-retro"}


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def fm(text):
    """Cắt chú thích cuối dòng kiểu YAML trên giá trị không nằm trong nháy — `gate_open: null  # …`
    phải đọc ra `null`, không phải cả câu (cùng luật với tower_generate.fm)."""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([\w-]+):\s*(.*)$", line)
            if not mm:
                continue
            v = mm.group(2).strip()
            if v[:1] not in ('"', "'"):
                v = re.sub(r"\s+#.*$", "", v).strip()
            d[mm.group(1)] = v
    return d


def head_fm(p, limit=40):
    """Chỉ đọc phần đầu file — đủ lấy frontmatter, không nuốt cả tài liệu."""
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return fm("".join(f.readline() for _ in range(limit)))
    except OSError:
        return {}


def md_section(text, pattern):
    """Thân của một mục markdown. Tiêu đề phải khớp NGAY sau dấu #— nếu không,
    `.*?` + DOTALL sẽ tóm nhầm một chuỗi giống số mục nằm trong đoạn văn khác
    (ví dụ "§3.2" trong phần 1)."""
    m = re.search(r"^#{2,4}\s*" + pattern + r"[^\n]*$\n(.*?)(?=^#{2,4}\s|\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def short_time(iso):
    if not iso or iso == "-":
        return "—"
    try:
        t = datetime.datetime.fromisoformat(iso.replace("Z", ""))
        # Agent ghi cả hai kiểu: `2026-08-13T10:00:00` và `2026-08-13T10:00:00+07:00`.
        # Trừ thẳng hai kiểu này cho TypeError và làm sập cả bản brief — bỏ tzinfo rồi mới trừ.
        if t.tzinfo is not None:
            t = t.replace(tzinfo=None)
        d = NOW - t
        if d.total_seconds() < 0:          # đồng hồ lệch / ghi giờ tương lai
            return "vừa xong"
        if d.days > 0:
            return "%dd trước" % d.days
        if d.seconds > 3600:
            return "%dh trước" % (d.seconds // 3600)
        return "%dp trước" % max(1, d.seconds // 60)
    except ValueError:
        return iso[:16]


def lst(v):
    """Parse list dạng [a, b] hoặc ["a — b"] trong frontmatter."""
    v = (v or "").strip()
    if not v or v in ("[]", "-"):
        return []
    try:
        out = json.loads(v)
        return out if isinstance(out, list) else [str(out)]
    except (ValueError, TypeError):
        return [x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]


if not os.path.isdir(A):
    print("Chưa có .ai-dlc/ ở %s — chạy /dlc-init trước." % ROOT)
    sys.exit(1)

# ---------- handoffs → vị trí ----------
stations = {"accepted": [], "open": [], "returned": [], "done": []}
for p in sorted(glob.glob(os.path.join(HOF, "HOF-*.md"))):
    d = head_fm(p)
    if not d:
        continue
    st = (d.get("status") or "open").strip()
    row = {
        "id": d.get("id", os.path.basename(p).replace(".md", "")),
        "to": (d.get("to") or "?").replace("dlc-", ""),
        "frm": (d.get("from") or "?").replace("dlc-", ""),
        "re": d.get("re", "—"), "kind": d.get("kind", "assign"),
        "created": d.get("created", "-"), "accepted": d.get("accepted", "-"),
        "closed": d.get("closed", "-"), "blocked": lst(d.get("blocked_by")),
        "heartbeat": d.get("heartbeat", "-"), "progress": (d.get("progress") or "-").strip(),
        "reads": len(lst(d.get("read_first"))), "path": os.path.relpath(p, A),
    }
    if st in stations:
        stations[st].append(row)
stations["done"] = sorted(stations["done"], key=lambda r: r["closed"], reverse=True)[:5]

# ---------- intents ----------
intents = []
idir = os.path.join(CM, "intents")
for name in sorted(os.listdir(idir)) if os.path.isdir(idir) else []:
    base = os.path.join(idir, name)
    st = head_fm(os.path.join(base, "status.md"))
    if not st:
        continue
    plan = head_fm(os.path.join(base, "intent-plan.md"))
    ledger_p = os.path.join(base, "as-is", "source-ledger.md")
    ledger = read(ledger_p)
    # Đếm nguồn theo TỪ KHOÁ TRONG DÒNG, không theo vị trí cột (protocol §4.11): sổ cái viết tay
    # dùng ✅/⬜ và số cột khác nhau, nên đếm bằng "cột thứ 3" cho ra 0/0 trên dự án thật.
    plan_txt = read(os.path.join(base, "intent-plan.md"))
    rows = {}
    for sid, rest in re.findall(r"^\|\s*(S\d+)\s*\|(.*)$", ledger, re.M):
        # GỘP mọi dòng của cùng một mã: sổ cái thật có nhiều bảng, và bảng "ưu tiên nguồn" không
        # có cột trạng thái. Lấy dòng đầu tiên gặp được là kết luận "chưa đọc" cho nguồn đã đọc.
        rows[sid] = rows.get(sid, "") + " | " + rest
    if not rows:                                   # chưa có sổ cái → lấy kế hoạch đọc ở intent-plan
        for sid in re.findall(r"^\|\s*(S\d+)\s*\|", plan_txt, re.M):
            rows.setdefault(sid, "")
    src_total = len(rows)
    src_read = sum(1 for r in rows.values() if RE_SRC_READ.search(r))
    # `planned` chỉ khi ô trạng thái NÓI THẾ. Dòng không có từ khoá nào (bảng thiếu cột trạng thái)
    # là "không rõ" — không được cộng vào planned, vì planned là con số chặn Gate B/D.
    src_planned = sum(1 for r in rows.values()
                      if not RE_SRC_READ.search(r) and RE_SRC_TODO.search(r))
    # Control Tower đọc cùng sổ cái này kỹ hơn (nhận bảng theo tên cột, có đường lùi khi lệch cột).
    # Có số của tower thì DÙNG SỐ ĐÓ — hai màn hình nói hai con số khác nhau về cùng một thứ là lỗi.
    tower = tower_counts(name)
    if tower:
        src_read, src_total, src_planned = tower
    # unit dự kiến ở phần 3.2 của intent-plan (có từ stage 1, trước khi units/ tồn tại)
    prov, prov_est = 0, 0.0
    sec32 = md_section(plan_txt, r"3\.2")
    if sec32:
        for row in re.findall(r"^\|\s*(UOW-\d+)\s*\|[^|]*\|([^|]*)\|", sec32, re.M):
            prov += 1
            try:
                prov_est += float(re.sub(r"[^\d.]", "", row[1]) or 0)
            except ValueError:
                pass
    units, over5, incomplete, est = [], 0, 0, 0.0
    udir = os.path.join(base, "units")
    for un in sorted(os.listdir(udir)) if os.path.isdir(udir) else []:
        up = os.path.join(udir, un)
        if not os.path.isdir(up):
            continue
        us = head_fm(os.path.join(up, "spec.md"))
        try:
            e = float(us.get("estimate_hours", 0) or 0)
        except ValueError:
            e = 0.0
        est += e
        if e > 5.0:
            over5 += 1
        if not all(os.path.getsize(os.path.join(up, f)) > 120
                   for f in ("user-stories.md", "nfr.md", "risks.md")
                   if os.path.isfile(os.path.join(up, f))) or \
           not all(os.path.isfile(os.path.join(up, f)) for f in ("user-stories.md", "nfr.md", "risks.md")):
            incomplete += 1
        units.append(un)
    try:
        stage = int(st.get("stage", 1))
    except ValueError:
        stage = 1
    go = (st.get("gate_open") or "null").strip()
    intents.append({
        "id": name, "title": plan.get("title", name), "stage": stage,
        "phase": st.get("phase", PHASE.get(stage, "inception")),
        "gate": None if go in ("null", "", "-") else go,
        "gate_doc": (st.get("gate_doc") or "").strip(),
        "passed": st.get("gates_passed", "[]"),
        "src": (src_read, src_total, src_planned),
        "units": len(units), "est": est, "over5": over5, "incomplete": incomplete,
        "prov": prov, "prov_est": prov_est,
        "plan_v": plan.get("version", st.get("plan_version", "")),
    })

# ---------- inbox ----------
inbox = sorted(glob.glob(os.path.join(A, "inbox", "*.json")))
inbox_rows = []
for p in inbox:
    try:
        j = json.load(open(p, encoding="utf-8"))
        inbox_rows.append((os.path.basename(p), j.get("intent", "?"), j.get("gate", "?"),
                           j.get("verdict", "?"), (j.get("comment") or "")[:70]))
    except (OSError, ValueError):
        inbox_rows.append((os.path.basename(p), "?", "?", "không đọc được", ""))

# ---------- session log gần nhất ----------
logs = sorted(glob.glob(os.path.join(SESS, "log", "SES-*.md")))
last_log = None
if logs:
    t = read(logs[-1])
    last_log = {"id": os.path.basename(logs[-1]).replace(".md", ""),
                "stop": (re.search(r"\*\*Dừng ở\*\*:\s*(.+)", t) or [None, "—"])[1].strip()[:110],
                "next": [l.strip("- ").strip() for l in
                         (re.search(r"\*\*Việc kế tiếp\*\*:\s*\n((?:\s*-.*\n?)+)", t) or [None, ""])[1].splitlines()
                         if l.strip().startswith("-")][:3]}

# ---------- kết xuất board.md ----------
os.makedirs(os.path.join(SESS, "log"), exist_ok=True)


def table(rows, cols, fmt):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    if not rows:
        out.append("| " + " | ".join(["—"] * len(cols)) + " |")
    for r in rows:
        out.append("| " + " | ".join(fmt(r)) + " |")
    return "\n".join(out)


board = """---
type: station-board
generated_by: session_brief.py
generated_at: %s
source: context-memory/handoffs/
---

# Bảng vị trí — ai đang giữ việc gì

> **Sinh ra từ `handoffs/`. KHÔNG sửa tay** — muốn đổi trạng thái một vị trí thì sửa file HOF rồi chạy lại
> `/dlc-status` hoặc `/dlc-resume`.

## Đang có người (`accepted`)

%s

## Đã giao, chưa ai nhận (`open`)

%s

## Trả lại — cần người xử lý (`returned`)

%s

## Vừa đóng (5 gần nhất)

%s
""" % (
    NOW.isoformat(timespec="seconds"),
    table(stations["accepted"], ["Vị trí", "HOF", "Phạm vi", "Nhận lúc", "Chặn bởi"],
          lambda r: [r["to"], "`%s`" % r["id"], "`%s`" % r["re"], short_time(r["accepted"]),
                     ", ".join(r["blocked"]) or "—"]),
    table(stations["open"], ["Giao cho", "HOF", "Phạm vi", "Giao lúc", "Chặn bởi"],
          lambda r: [r["to"], "`%s`" % r["id"], "`%s`" % r["re"], short_time(r["created"]),
                     ", ".join(r["blocked"]) or "—"]),
    table(stations["returned"], ["Từ", "HOF", "Phạm vi", "Giao lúc"],
          lambda r: [r["to"], "`%s`" % r["id"], "`%s`" % r["re"], short_time(r["created"])]),
    table(stations["done"], ["HOF", "Vị trí", "Phạm vi", "Đóng lúc"],
          lambda r: ["`%s`" % r["id"], r["to"], "`%s`" % r["re"], short_time(r["closed"])]),
)
with open(os.path.join(SESS, "board.md"), "w", encoding="utf-8") as f:
    f.write(board)

index_p = os.path.join(SESS, "INDEX.md")
if not os.path.isfile(index_p):
    src = os.path.join(TPL, "context-index.md")
    if os.path.isfile(src):
        shutil.copy2(src, index_p)

# ---------- mở phiên mới ----------
new_session = None
if "--open-session" in FLAGS:
    n = len(logs) + 1
    new_session = os.path.join(SESS, "log", "SES-%03d.md" % n)
    if not os.path.isfile(new_session):
        tpl = read(os.path.join(TPL, "session-log.md")) or "---\nid: SES-%03d\n---\n"
        tpl = tpl.replace("SES-NNN", "SES-%03d" % n).replace("<ISO>", NOW.isoformat(timespec="seconds"))
        tpl = tpl.replace("<ngày>", NOW.strftime("%d/%m/%Y"))
        tpl = tpl.replace("[INT-NNN]", "[" + ", ".join(i["id"] for i in intents) + "]")
        with open(new_session, "w", encoding="utf-8") as f:
            f.write(tpl)

close_id = None
for i, a in enumerate(sys.argv):
    if a == "--close-session" and i + 1 < len(sys.argv):
        close_id = sys.argv[i + 1]
if close_id:
    p = os.path.join(SESS, "log", close_id + ".md")
    if os.path.isfile(p):
        t = read(p)
        t = re.sub(r"^ended:.*$", "ended: " + NOW.isoformat(timespec="seconds"), t, count=1, flags=re.M)
        open(p, "w", encoding="utf-8").write(t)

if "--board-only" in FLAGS:
    print(os.path.join(SESS, "board.md"))
    sys.exit(0)

# ---------- briefing ----------
L = []
L.append("AI-DLC · %s · %s" % (os.path.basename(ROOT), NOW.strftime("%d/%m %H:%M")))
L.append("")
L.append("INTENTS")
if not intents:
    L.append("  (chưa có intent nào — /dlc-intent \"<yêu cầu>\")")
for it in intents:
    gate = ("GATE %s ĐANG MỞ → đọc %s%s" % (it["gate"], it["gate_doc"] or "?",
                                            " v" + it["plan_v"] if it["plan_v"] else "")) if it["gate"] else "không có gate chờ"
    L.append("  %s · stage %d/8 · %s · %s" % (it["id"], it["stage"], it["phase"], gate))
    L.append("     %s" % it["title"][:88])
    r, t, pl = it["src"]
    unit_txt = ("%d unit chốt · %.1fh" % (it["units"], it["est"])) if it["units"] else (
        ("%d unit dự kiến · %.1fh (chưa chốt — bản cuối ở Gate D)" % (it["prov"], it["prov_est"]))
        if it["prov"] else "chưa phân rã unit")
    L.append("     nguồn %d/%d đã đọc%s · %s%s%s" % (
        r, t, (" · %d còn planned" % pl) if pl else "", unit_txt,
        (" · %d unit >5h" % it["over5"]) if it["over5"] else "",
        (" · %d unit thiếu US/NFR/risk" % it["incomplete"]) if it["incomplete"] else ""))
L.append("")
L.append("VỊ TRÍ (từ handoffs/ — chi tiết: context-memory/session/board.md)")
if not any(stations[k] for k in ("accepted", "open", "returned")):
    L.append("  không vị trí nào đang mở")
for k, label in (("accepted", "đang làm"), ("open", "chờ nhận "), ("returned", "trả lại ")):
    for r in stations[k]:
        beat = r.get("heartbeat", "-")
        pulse = ("nhịp " + short_time(beat)) if k == "accepted" and beat not in ("-", "") else (
            "CHƯA BÁO NHỊP" if k == "accepted" else short_time(r["accepted"] if k == "accepted" else r["created"]))
        L.append("  %s %-9s %-18s %-28s %s%s" % (
            label, r["id"], r["to"], r["re"], pulse,
            (" · chặn bởi " + ", ".join(r["blocked"])) if r["blocked"] else ""))
        if k == "accepted" and r.get("progress", "-") not in ("-", ""):
            L.append("            → " + r["progress"][:96])
L.append("")
L.append("INBOX (quyết định từ tower chưa xử lý): %d" % len(inbox_rows))
for f_, i_, g_, v_, c_ in inbox_rows[:6]:
    L.append("  %s · Gate %s · %s%s" % (i_, g_, v_, (" · " + c_) if c_ else ""))
warn = []
for it in intents:
    if it["src"][2] and (it["gate"] in ("B", "D") or it["stage"] >= 2):
        warn.append("%s: %d nguồn còn `planned` — chặn Gate B/D (protocol §4.8)" % (it["id"], it["src"][2]))
    if it["over5"]:
        warn.append("%s: %d unit ước lượng >5h — phải tách trước Gate D (§4.9)" % (it["id"], it["over5"]))
    if it["incomplete"]:
        warn.append("%s: %d unit thiếu US/NFR/risk — không đạt DoR" % (it["id"], it["incomplete"]))
    if it["gate"] and not it["gate_doc"]:
        warn.append("%s: gate %s đang mở nhưng thiếu gate_doc — tower không cho duyệt (§2.1)" % (it["id"], it["gate"]))
for r in stations["accepted"]:
    beat = r.get("heartbeat", "-")
    if beat in ("-", ""):
        warn.append("%s (%s) đang accepted nhưng CHƯA BÁO NHỊP nào — không biết còn sống hay đã chết (§9.4)"
                    % (r["id"], r["to"]))
    elif short_time(beat).endswith(("h trước", "d trước")):
        warn.append("%s (%s) im lặng %s — hỏi thăm hoặc coi như chết, giao lại"
                    % (r["id"], r["to"], short_time(beat)))
for r in stations["open"]:
    warn.append("%s giao cho %s nhưng chưa ai đặt accepted — nếu agent đang chạy thì nó đang vi phạm §9.4"
                % (r["id"], r["to"]))
if warn:
    L.append("")
    L.append("CẢNH BÁO")
    for w in warn:
        L.append("  ! " + w)
L.append("")
L.append("VIỆC KẾ TIẾP (đề xuất — bạn chốt)")
n = 1
if inbox_rows:
    L.append("  %d. Drain inbox: ghi DEC, move sang inbox/processed/, chạy tiếp flow" % n); n += 1
for r in stations["returned"]:
    L.append("  %d. Xử lý %s trả lại (%s · %s)" % (n, r["id"], r["to"], r["re"])); n += 1
for r in stations["accepted"]:
    L.append("  %d. Tiếp tục %s — đọc %s rồi làm tiếp đúng phần còn treo" % (n, r["id"], r["path"])); n += 1
for it in intents:
    if it["gate"]:
        L.append("  %d. %s đang chờ người quyết Gate %s → /dlc-tower serve để đọc & duyệt" % (n, it["id"], it["gate"])); n += 1
    elif it["stage"] < 8:
        L.append("  %d. %s chưa có gate chờ → bước kế: %s" % (
            n, it["id"], GATE_NEXT.get(sorted(re.findall(r"[A-G]", it["passed"]))[-1] if re.findall(r"[A-G]", it["passed"]) else "A", "/dlc-status"))); n += 1
if n == 1:
    L.append("  (không có việc treo — mở intent mới bằng /dlc-intent)")
if last_log:
    L.append("")
    L.append("PHIÊN TRƯỚC (%s) dừng ở: %s" % (last_log["id"], last_log["stop"]))
    for x in last_log["next"]:
        L.append("  → " + x)
if new_session:
    L.append("")
    L.append("PHIÊN NÀY: %s (ghi lại lúc kết phiên)" % os.path.relpath(new_session, ROOT))
L.append("")
L.append("Tra cứu thêm: context-memory/session/INDEX.md — ĐỪNG đọc toàn văn intent-plan/unit-plan/as-is (§10).")
print("\n".join(L))
