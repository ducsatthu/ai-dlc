#!/usr/bin/env python3
"""AI-DLC Control Tower generator (v2 — Design System UI).

Usage: python3 tower_generate.py [project_root]

1) Copy runtime UI (React ui-kit của Control Tower Design System, đã flatten trong
   plugin/tower-ui/) vào <root>/.ai-dlc/tower/
2) Sinh <root>/.ai-dlc/tower/data.js (window.CT_DATA) từ state .ai-dlc/ thật.

Mở tĩnh (file://) xem được (cần internet cho React CDN); nút Approve/Reject cần
tower_serve.py. Regenerate sau mỗi sự kiện — data.js là phần duy nhất đổi.
"""
import datetime
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
A = os.path.join(ROOT, ".ai-dlc")
CM = os.path.join(A, "context-memory")
UI_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tower-ui")
OUT = os.path.join(A, "tower")

STAGE_HOLDER = {1: "intent-analyst", 2: "context-archaeologist", 3: "context-validator",
                4: "context-validator", 5: "unit-planner", 6: "bolt-coordinator",
                7: "acceptance-recorder", 8: "acceptance-recorder"}
BROWNFIELD = {"add-feature": "Add feature", "optimize-nfr": "Optimize NFR",
              "tech-debt": "Technical debt", "fix-defect": "Fix defect", "green-field": "Green-field"}
GATE_TITLE = {"A": "Duyệt Intent — outcome & scope", "B": "Xác nhận AS-IS model (Validation Mob)",
              "C": "Chốt open questions business", "D": "Approve Units + Bolt plan + DoD/DoR",
              "E": "Checkpoint trong Bolt", "F": "UAT / approve deploy", "G": "Duyệt lesson + patch"}


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
            mm = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if mm:
                d[mm.group(1)] = mm.group(2).strip()
    return d


def mtime_hm(p):
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H:%M")
    except OSError:
        return ""


def section(text, header):
    """Nội dung sau '**header:**' tới dòng trống kế hoặc '**' kế."""
    m = re.search(r"\*\*" + re.escape(header) + r":?\*\*\s*(.*?)(?=\n\s*\n|\n\*\*|\Z)", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


# ---------- intents ----------
intents, units_by_intent, gates, decisions_feed = [], {}, [], []
idir = os.path.join(CM, "intents")
if os.path.isdir(idir):
    for name in sorted(os.listdir(idir)):
        base = os.path.join(idir, name)
        st = fm(read(os.path.join(base, "status.md")))
        if not st:
            continue
        it_text = read(os.path.join(base, "intent.md"))
        it = fm(it_text)
        stage = int(st.get("stage", "1") or 1)
        gate_open = (st.get("gate_open") or "null").strip()
        gate_open = None if gate_open in ("null", "") else gate_open
        units = []
        udir = os.path.join(base, "units")
        if os.path.isdir(udir):
            for un in sorted(os.listdir(udir)):
                us = fm(read(os.path.join(udir, un, "spec.md")))
                bdir = os.path.join(udir, un, "bolts")
                bolts = sorted(os.listdir(bdir)) if os.path.isdir(bdir) else []
                nb = len(bolts)
                done_files = 0
                for bn in bolts:
                    bb = os.path.join(bdir, bn)
                    done_files += sum(os.path.isfile(os.path.join(bb, f)) for f in
                                      ("domain-design.md", "logical-design.md", "tasks.md"))
                pct = int(done_files / (nb * 3) * 100) if nb else 0
                status = "done" if us.get("status") == "done" else (
                    "in-bolt" if nb else ("pending-gate" if stage <= 5 else "pending-gate"))
                units.append({"id": un, "name": us.get("title", un), "status": status,
                              "bolt": bolts[-1] if bolts else "—", "done": pct, "risks": []})
        units_by_intent[name] = units
        n_done = sum(1 for u in units if u["status"] == "done")
        intents.append({
            "id": name, "name": it.get("title", name), "stage": stage,
            **({"gate": gate_open} if gate_open else {}),
            "holder": STAGE_HOLDER.get(stage, "orchestrator"),
            "brownfield": BROWNFIELD.get(it.get("brownfield_type", ""), it.get("brownfield_type", "")),
            "doc": "intent.md", "owner": "Human supervisor",
            "updated": mtime_hm(os.path.join(base, "status.md")) + " hôm nay",
            "units": [len(units), n_done], "risk": None,
        })
        if gate_open:
            brief_p = os.path.join(base, "decision-briefs", "brief-%s.md" % gate_open[:1])
            btxt = read(brief_p)
            options = re.findall(r"^- \(?\d?\)?\s*(.+)$", section(btxt, "Phương án"), re.M) or \
                [o.strip() for o in re.findall(r"\((\d)\)\s*([^(]+?)(?=\(\d\)|$)", section(btxt, "Phương án"))
                 and []]
            if not options:
                options = [s.strip() for s in re.split(r"\(\d\)", section(btxt, "Phương án")) if s.strip()][:3]
            gates.append({
                "key": "g-%s-%s" % (name, gate_open), "kind": "gate", "gate": gate_open[:1],
                "target": name, "title": GATE_TITLE.get(gate_open[:1], "Chờ quyết định"),
                "brief": section(btxt, "Bối cảnh") or ("Xem " + os.path.relpath(brief_p, A) if btxt else "Chưa có decision brief."),
                "options": options[:4],
                "recommendation": section(btxt, "Khuyến nghị"),
                "evidence": re.findall(r"\b(?:RV|MSG|DEC)-\d+\b", btxt)[:5],
            })

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
        d = fm(read(os.path.join(ldir, f)))
        body = re.sub(r"^---.*?---\s*", "", read(os.path.join(ldir, f)), flags=re.S)
        lm = re.search(r"Lesson:\s*(.+)", body)
        lessons.append({"id": f.replace(".md", ""), "trigger": d.get("trigger", "")[:120],
                        "lesson": lm.group(1).strip()[:160] if lm else "", "patch": d.get("applied_to", ""),
                        "status": d.get("status", "proposed")})


def gov_doc(name):
    p = os.path.join(CM, "governance", name + ".md")
    d = fm(read(p))
    items = [m.strip() for m in re.findall(r"^- \[ \] (.+)$", read(p), re.M)][:8]
    return {"version": "v" + str(d.get("version", "1")), "items": items}


gov_changelog = [{"v": l[2:60], "when": "", "by": "", "dec": "", "from": ""}
                 for l in read(os.path.join(CM, "governance", "changelog.md")).splitlines() if l.startswith("- ")][:6]

# tasks + work: bolt gần nhất có tasks.md
tasks, work = [], []
for it in intents:
    for u in units_by_intent.get(it["id"], []):
        pass  # tasks parse dưới đây theo file
if os.path.isdir(idir):
    newest = None
    for tpath in sorted(__import__("glob").glob(os.path.join(idir, "*", "units", "*", "bolts", "*", "tasks.md"))):
        newest = tpath
    if newest:
        for blk in re.findall(r"## (TSK-\d+)[ ·]*([^\n]*)\n(.*?)(?=\n## TSK-|\Z)", read(newest), re.S):
            t = dict(re.findall(r"^(\w+):\s*(.+)$", blk[2], re.M))
            tasks.append({"id": blk[0], "title": blk[1].strip() or blk[0], "status": t.get("status", "todo"),
                          **({"claimedBy": t["claimed_by"].replace("dlc-", "")} if t.get("claimed_by", "-") not in ("-", "") else {}),
                          "approver": t.get("approver", "—").replace("dlc-", ""),
                          **({"dependsOn": t["depends_on"].strip("[]")} if t.get("depends_on", "[]").strip("[]") else {}),
                          "msgCount": len(t.get("comms", "").strip("[]").split(",")) if t.get("comms", "[]").strip("[]") else 0})

kpis_bolts = sum(1 for i in intents if i["stage"] == 6)
data = {
    "intents": intents, "unitsByIntent": units_by_intent, "gates": gates,
    "units": units_by_intent.get(intents[0]["id"], []) if intents else [],
    "tasks": tasks, "work": work, "feed": feed,
    "trace": ([{"kind": "dec", "id": decisions[-1]["id"], "note": decisions[-1]["what"][:60]}] if decisions else []) +
             ([{"kind": "rv", "id": reviews[0]["id"], "note": reviews[0]["verdict"]}] if reviews else []) +
             ([{"kind": "msg", "id": feed[0]["id"], "note": feed[0]["type"]}] if feed else []) +
             ([{"kind": "intent", "id": intents[0]["id"], "note": intents[0]["name"][:50]}] if intents else []),
    "reviews": reviews, "decisions": decisions,
    "questions": [], "risks": risks, "debt": debt, "lessons": lessons,
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
