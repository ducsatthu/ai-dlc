#!/usr/bin/env python3
"""close_sweep.py — đóng intent theo SỰ THẬT ĐO ĐƯỢC, không chờ người làm việc hành chính (protocol §2.5, 6.6.0).

  python3 close_sweep.py [project_root]                 # chỉ đo, in bảng
  python3 close_sweep.py [project_root] --json
  python3 close_sweep.py [project_root] --apply [--dec DEC-NNNN] [--ref <nhánh>]

Một intent CHƯA đóng được tự đóng khi máy đo đủ ba điều kiện:
  C1  có ≥1 commit mang tên intent (frontmatter `commits:` ∪ `git log --all --grep INT-NNN`, bỏ merge) và MỌI
      commit đó là tổ tiên của nhánh phát hành (`--ref`, mặc định origin/HEAD → main → master).
  C2  không có gate đang mở (`gate_open` ≠ null) — gate mở nghĩa là có câu đang hỏi người, hoặc intent đang sống.
  C3  không có escalation `status: open` của intent với `severity: high` (hoặc tag security).
Khoảng trống hành chính (thiếu RV, kiểm tay không dấu vết, `[LEAD-CHOSE]` chưa đọc lại, gate E/F/G chưa ký, HOF
treo, unit thiếu US/NFR) KHÔNG chặn — DEC liệt kê chúng ở dòng "Đóng không bù".

`--apply`: một DEC cho cả lượt quét (`--dec`, mặc định = số DEC lớn nhất trong decisions-log + 1) và mỗi intent
đóng được: `stage: 8 · phase: closed · gate_open: null · closed_by · released` + khối "Đóng tự động" cuối status.md.
`gates_passed` KHÔNG đổi. Núm `closure: ask` trong governance/autopilot.md ⇒ chỉ đo, `--apply` bị từ chối.
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FLAGS = [a for a in sys.argv[1:] if a.startswith("--")]


def opt(name):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


for _n in ("--dec", "--ref"):
    _v = opt(_n)
    if _v in ARGS:
        ARGS.remove(_v)

ROOT = os.path.abspath(ARGS[0] if ARGS else os.getcwd())
A = os.path.join(ROOT, ".ai-dlc")
try:  # 7.0.0: state ở đâu do scripts/layout.py trả lời
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from layout import resolve as _resolve_layout
    _LAY = _resolve_layout(ROOT)
    if _LAY["engine"] not in ("ai-dlc",):
        print("close_sweep chỉ chạy trên engine ai-dlc (layout: %s)." % _LAY["engine"])
        sys.exit(2)
    ROOT, A = _LAY["root"], _LAY["state"]
except SystemExit:
    raise
except Exception:
    pass
CM = os.path.join(A, "context-memory")
NOW = datetime.datetime.now()
CLOSED = {"closed"}


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def fm(text):
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


def git(*a):
    r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def release_ref():
    want = opt("--ref")
    cands = [want] if want else []
    rc, out = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if rc == 0 and out:
        cands.append(out)
    cands += ["main", "master", "origin/main", "origin/master"]
    for c in cands:
        rc, sha = git("rev-parse", "--verify", "--quiet", c + "^{commit}")
        if rc == 0:
            return c, sha[:8]
    return None, None


def closure_mode():
    t = read(os.path.join(CM, "governance", "autopilot.md")) or read(os.path.join(A, "governance", "autopilot.md"))
    return fm(t).get("closure", "auto") or "auto"


def intent_commits(iid, meta):
    shas = set()
    raw = meta.get("commits", "")
    for tok in re.findall(r"\b[0-9a-f]{7,40}\b", raw):
        rc, full = git("rev-parse", "--verify", "--quiet", tok + "^{commit}")
        if rc == 0:
            shas.add(full)
    rc, out = git("log", "--all", "--no-merges", "--format=%H", "-E", "--grep", r"%s([^0-9]|$)" % iid)
    if rc == 0:
        shas.update(l for l in out.splitlines() if l)
    return sorted(shas)


def open_escalations(iid):
    hits = []
    for p in sorted(glob.glob(os.path.join(CM, "escalations", "ESC-*.md"))):
        d = fm(read(p))
        if d.get("intent") != iid or d.get("status", "").lower() not in ("open", "mở"):
            continue
        sev = d.get("severity", "").lower()
        if sev in ("high", "critical", "cao") or "security" in d.get("tags", "").lower():
            hits.append("%s (%s)" % (os.path.basename(p)[:-3], sev or "security"))
    return hits


GAP_RULES = [  # khoảng trống hành chính — chỉ để ghi, không chặn (protocol §2.5.3)
    ("gate E/F/G chưa ký", lambda d, t: not re.search(r"\bF\b", d.get("gates_passed", ""))),
    ("[LEAD-CHOSE] chưa đọc lại", lambda d, t: "[LEAD-CHOSE]" in t),
    ("kiểm tay chưa có dấu vết", lambda d, t: re.search(r"kiểm tay", t, re.I) is not None),
    ("phase tạm dừng do người", lambda d, t: d.get("phase") in ("paused",)),
]


def scan():
    ref, ref_sha = release_ref()
    rows = []
    for st in sorted(glob.glob(os.path.join(CM, "intents", "INT-*", "status.md"))):
        t = read(st)
        d = fm(t)
        iid = d.get("intent") or os.path.basename(os.path.dirname(st))
        if d.get("phase") in CLOSED:
            continue
        row = {"intent": iid, "status": os.path.relpath(st, ROOT), "phase": d.get("phase", ""),
               "stage": d.get("stage", ""), "why_not": [], "gaps": []}
        shas = intent_commits(iid, d)
        inref = [s for s in shas if ref and git("merge-base", "--is-ancestor", s, ref)[0] == 0]
        row["commits"], row["in_ref"] = len(shas), len(inref)
        if not shas:
            row["why_not"].append("C1 không có commit nào mang tên %s — đang làm dở, hay bị intent/batch khác thay?" % iid)
        elif len(inref) < len(shas):
            miss = [s[:8] for s in shas if s not in inref]
            row["why_not"].append("C1 %d/%d commit chưa vào %s: %s" % (len(miss), len(shas), ref, " ".join(miss[:6])))
        go = d.get("gate_open", "null")
        if go and go.lower() not in ("null", "none", "~", ""):
            row["why_not"].append("C2 gate %s đang mở" % go)
        esc = open_escalations(iid)
        if esc:
            row["why_not"].append("C3 escalation mở: " + ", ".join(esc))
        row["gaps"] = [name for name, f in GAP_RULES if f(d, t)]
        row["closable"] = not row["why_not"]
        rows.append(row)
    return ref, ref_sha, rows


def next_dec():
    t = read(os.path.join(CM, "governance", "decisions-log.md"))
    nums = [int(n) for n in re.findall(r"^## DEC-(\d+)", t, re.M)]
    return "DEC-%04d" % ((max(nums) if nums else 0) + 1)


def apply(ref, ref_sha, rows):
    todo = [r for r in rows if r["closable"]]
    if not todo:
        return None
    dec = opt("--dec") or next_dec()
    day = NOW.strftime("%d/%m/%Y")
    for r in todo:
        p = os.path.join(ROOT, r["status"])
        t = read(p)
        m = re.match(r"^---\n(.*?)\n---", t, re.S)
        rel = "%s %s · %d/%d commit — đo %s close_sweep" % (ref, ref_sha, r["in_ref"], r["commits"], NOW.strftime("%d/%m"))
        if m:
            head = m.group(1)
            for key, val in (("stage", "8"), ("phase", "closed   # %s · đóng tự động §2.5" % dec), ("gate_open", "null")):
                if re.search(r"(?m)^%s:" % key, head):
                    head = re.sub(r"(?m)^%s:.*$" % key, "%s: %s" % (key, val), head, count=1)
                else:
                    head += "\n%s: %s" % (key, val)
            head = re.sub(r"(?m)^(closed_by|released):.*\n?", "", head).rstrip("\n")
            head += '\nclosed_by: %s   # close_sweep §2.5\nreleased: "%s"' % (dec, rel)
            t = "---\n" + head + "\n---" + t[m.end():]
        else:
            t = "---\nintent: %s\nstage: 8\nphase: closed\ngate_open: null\nclosed_by: %s\nreleased: \"%s\"\n---\n" % (
                r["intent"], dec, rel) + t
        t = t.rstrip("\n") + "\n\n## Đóng tự động %s — %s (protocol §2.5)\n- Release: %s.\n- Đóng không bù: %s.\n- `gates_passed` giữ nguyên. Đảo: tower *Đảo* trên %s ⇒ mở lại intent.\n" % (
            day, dec, rel, "; ".join(r["gaps"]) or "không có", dec)
        open(p, "w", encoding="utf-8").write(t)
    log = os.path.join(CM, "governance", "decisions-log.md")
    lines = ["", "## %s · %s · đóng intent · %s · autopilot" % (dec, day, " ".join(r["intent"] for r in todo)),
             "- Quyết định: đóng %d intent theo sự thật đo được — Người quyết: autopilot-closure (protocol §2.5, `closure: %s`)" % (len(todo), closure_mode()),
             "- Căn cứ: `close_sweep.py` — C1 mọi commit ∈ `%s` (%s) · C2 không gate mở · C3 không escalation high mở" % (ref, ref_sha),
             "- Áp: phase closed, stage 8, `closed_by`, `released`; `gates_passed` không đổi",
             "- Đóng không bù: " + " · ".join("%s (%s)" % (r["intent"], "; ".join(r["gaps"]) or "—") for r in todo),
             "- Đảo bằng: tower *Đảo* ⇒ REV ⇒ mở lại đúng intent đó — rẻ (chỉ status.md)   - Hiện ở: status.md của từng intent, khối \"Đóng tự động\"",
             "- Block check: #1 n/a · #2 n/a · #3 n/a · #4 pass (không deploy, không gửi ngoài) · #5 C1–C3 pass · #6 n/a"]
    with open(log, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return dec


def main():
    ref, ref_sha, rows = scan()
    out = {"ref": ref, "ref_sha": ref_sha, "closure": closure_mode(), "intents": rows, "dec": None}
    if "--apply" in FLAGS:
        if out["closure"] == "ask":
            print("closure: ask trong governance/autopilot.md — không tự đóng; trình danh sách cho người.")
            sys.exit(3)
        if not ref:
            print("Không tìm thấy nhánh phát hành (origin/HEAD · main · master) — không đo được C1.")
            sys.exit(3)
        out["dec"] = apply(ref, ref_sha, rows)
    if "--json" in FLAGS:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print("close_sweep · nhánh phát hành %s (%s) · closure: %s" % (ref, ref_sha, out["closure"]))
    if not rows:
        print("  mọi intent đã đóng.")
    for r in rows:
        mark = "ĐÓNG ĐƯỢC" if r["closable"] else "GIỮ"
        print("  %s · %s · %d/%d commit ∈ %s" % (r["intent"], mark, r["in_ref"], r["commits"], ref))
        for w in r["why_not"]:
            print("      ✗ " + w)
        if r["closable"] and r["gaps"]:
            print("      đóng không bù: " + "; ".join(r["gaps"]))
    if out["dec"]:
        print("ĐÃ ÁP: %s · %d intent đóng." % (out["dec"], sum(r["closable"] for r in rows)))


if __name__ == "__main__":
    main()
