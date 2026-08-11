#!/usr/bin/env python3
"""AI-DLC Control Tower generator.

Usage: python3 tower_generate.py [project_root]
Đọc <root>/.ai-dlc/ → sinh <root>/.ai-dlc/tower/index.html (self-contained, dark-first).
Views: Mission Control (Gate Queue + Pipeline Board + feeds) và Bản đồ AI-DLC
(3 band Inception/Construction/Operations theo Hình 1 white paper, trạng thái sống).
"""
import html
import json
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
A = os.path.join(ROOT, ".ai-dlc")
CM = os.path.join(A, "context-memory")


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def fm(text):
    """frontmatter đơn giản -> dict (string values)."""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if mm:
                d[mm.group(1)] = mm.group(2).strip()
    return d


def esc(s):
    return html.escape(str(s), quote=True)


# ---------- collect ----------
STAGES = ["1 Request", "2 Discovery", "3 Validation", "4 Clarify", "5 Units", "6 Construction", "7 Acceptance", "8 Release"]

intents = []
idir = os.path.join(CM, "intents")
if os.path.isdir(idir):
    for name in sorted(os.listdir(idir)):
        base = os.path.join(idir, name)
        st = fm(read(os.path.join(base, "status.md")))
        if not st:
            continue
        it = fm(read(os.path.join(base, "intent.md")))
        gates = re.findall(r"[A-G]", st.get("gates_passed", ""))
        units = []
        udir = os.path.join(base, "units")
        if os.path.isdir(udir):
            for un in sorted(os.listdir(udir)):
                ub = os.path.join(udir, un)
                us = fm(read(os.path.join(ub, "spec.md")))
                bolts = []
                bdir = os.path.join(ub, "bolts")
                if os.path.isdir(bdir):
                    for bn in sorted(os.listdir(bdir)):
                        bb = os.path.join(bdir, bn)
                        prog = {
                            "domain": os.path.isfile(os.path.join(bb, "domain-design.md")),
                            "logical": os.path.isfile(os.path.join(bb, "logical-design.md")),
                            "code": os.path.isfile(os.path.join(bb, "tasks.md")),
                        }
                        tasks = []
                        for blk in re.findall(r"## (TSK-\d+[^\n]*)\n(.*?)(?=\n## TSK-|\Z)", read(os.path.join(bb, "tasks.md")), re.S):
                            tfm = dict(re.findall(r"^(\w+):\s*(.+)$", blk[1], re.M))
                            tasks.append({"title": blk[0].strip(), **tfm})
                        bolts.append({"name": bn, "prog": prog, "tasks": tasks})
                units.append({"id": un, "title": us.get("title", un), "status": us.get("status", ""), "bolts": bolts})
        briefs = {}
        bdir2 = os.path.join(base, "decision-briefs")
        if os.path.isdir(bdir2):
            for f in os.listdir(bdir2):
                m = re.match(r"brief-([A-G])", f)
                if m:
                    briefs[m.group(1)] = read(os.path.join(bdir2, f))
        intents.append({
            "id": name, "title": it.get("title", name),
            "stage": int(st.get("stage", "1") or 1),
            "phase": st.get("phase", ""),
            "gates": gates,
            "gate_open": (st.get("gate_open") or "null").strip(),
            "brownfield": it.get("brownfield_type", ""),
            "units": units, "briefs": briefs,
        })

msgs = []
cdir = os.path.join(CM, "comms")
if os.path.isdir(cdir):
    for f in sorted(os.listdir(cdir), reverse=True)[:25]:
        d = fm(read(os.path.join(cdir, f)))
        if d:
            msgs.append({"id": f.replace(".md", ""), **d})

rvs = []
rdir = os.path.join(CM, "reviews")
if os.path.isdir(rdir):
    for f in sorted(os.listdir(rdir), reverse=True)[:15]:
        d = fm(read(os.path.join(rdir, f)))
        if d:
            rvs.append({"id": f.replace(".md", ""), **d})

risks = [l for l in read(os.path.join(CM, "governance", "risks.md")).splitlines() if re.match(r"^[-*] ", l)][:8]
inbox_pending = sorted(f for f in (os.listdir(os.path.join(A, "inbox")) if os.path.isdir(os.path.join(A, "inbox")) else []) if f.endswith(".json"))

GATE_DESC = {
    "A": "Duyệt Intent — outcome & scope đúng chưa?",
    "B": "Xác nhận AS-IS model (Validation Mob)",
    "C": "Chốt open questions business",
    "D": "Approve Units + Bolt plan + DoD/DoR",
    "E": "Checkpoint trong Bolt (design/demo)",
    "F": "UAT / approve deploy",
    "G": "Duyệt lesson learned + patch",
}

# ---------- render ----------
def stage_chips(it):
    out = []
    for i, s in enumerate(STAGES, 1):
        cls = "done" if i < it["stage"] else ("active" if i == it["stage"] else "")
        label = s.split(" ")[0]
        if i == it["stage"] and it["gate_open"] not in ("null", ""):
            label += " ◇" + esc(it["gate_open"])
        out.append(f'<span class="chip {cls}" title="{esc(s)}">{label}</span>')
    return "".join(out)


def gate_cards():
    cards = []
    for it in intents:
        g = it["gate_open"]
        if g and g != "null":
            brief = it["briefs"].get(g[:1], "")
            brief_html = f'<details><summary>Decision brief</summary><pre>{esc(brief[:2500])}</pre></details>' if brief else ""
            cards.append(
                f'<div class="gate-item" data-gate="{esc(g)}" data-intent="{esc(it["id"])}">'
                f'<span class="g-dot"></span><div class="g-body"><strong>Gate {esc(g)} · {esc(it["id"])}</strong>'
                f' — {esc(GATE_DESC.get(g[:1], "Chờ quyết định"))}<div class="g-title">{esc(it["title"])}</div>{brief_html}'
                f'<div class="g-actions"><button onclick="decide(this,\'approve\')">✓ Approve</button>'
                f'<button class="rej" onclick="decide(this,\'reject\')">✗ Reject</button>'
                f'<input placeholder="comment / lý do (bắt buộc khi reject)"></div></div></div>'
            )
    for f in inbox_pending:
        cards.append(f'<div class="gate-item processed"><span class="g-dot"></span><div class="g-body">Inbox chưa xử lý: <code>{esc(f)}</code> — mở session Claude Code để drain.</div></div>')
    return "".join(cards) or '<p class="empty">Không có gì chờ bạn — agents đang làm việc.</p>'


def map_view():
    """Bản đồ AI-DLC — Hình 1 white paper, trạng thái sống."""
    rows = []
    for it in intents:
        # Inception band
        unit_cards = "".join(
            f'<span class="ucard{" ok" if it["stage"] > 5 or u["status"] == "approved" else ""}">{esc(u["id"])}'
            f'<em>{esc(u["title"][:28])}</em><b>{"Mob ✓" if "D" in it["gates"] else "chờ xác nhận"}</b></span>'
            for u in it["units"]
        ) or '<span class="muted">chưa phân rã Unit</span>'
        art_inc = []
        for label, key in [("User Stories", "user-stories"), ("NFR", "nfr"), ("Rủi ro", "risks"), ("PR-FAQ", "pr-faq")]:
            have = any(os.path.isfile(os.path.join(idir, it["id"], "units", u["id"], key + ".md")) for u in it["units"])
            art_inc.append(f'<span class="achip{" on" if have else ""}">{label}</span>')
        # Construction band
        lanes = []
        for u in it["units"]:
            pills = "".join(
                '<span class="bolt"><b>{}</b><i class="{}">D</i><i class="{}">L+ADR</i><i class="{}">C+T</i></span>'.format(
                    esc(b["name"]),
                    "on" if b["prog"]["domain"] else "",
                    "on" if b["prog"]["logical"] else "",
                    "on" if b["prog"]["code"] else "",
                )
                for b in u["bolts"]
            ) or '<span class="muted">chưa có bolt</span>'
            lanes.append(f'<div class="lane"><span class="lane-l">{esc(u["id"])}</span>{pills}</div>')
        brown = '<div class="brown">brown-field: nâng mã lên mô hình tĩnh + động (as-is)</div>' if it["brownfield"] and it["brownfield"] != "green-field" else ""
        rows.append(f"""
<div class="mapcard">
  <div class="map-h">{esc(it['id'])} · {esc(it['title'])} <span class="chip active">{esc(it['phase'])}</span></div>
  <div class="band"><div class="b-role">Product Owner, Developers, QA, AI<br><b>Mob Elaboration</b></div>
    <div class="b-flow"><span class="intent-node">Intent</span> → {unit_cards}</div>
    <div class="b-art">{''.join(art_inc)}<span class="achip{' on' if it['units'] else ''}">Bolt đề xuất</span></div></div>
  <div class="band"><div class="b-role">Developers, AI · PO khi cần<br><b>Mob Construction</b></div>
    <div class="b-flow">{brown}{''.join(lanes)}</div>
    <div class="b-art"><span class="achip">Domain Design</span><span class="achip">Logical + ADR</span><span class="achip">Code + Unit Test</span><span class="achip">Deployment Unit</span></div></div>
  <div class="band"><div class="b-role">Product Owner, Developers, AI</div>
    <div class="b-flow"><span class="muted">{'Deployment Unit production · telemetry · runbook chờ phê duyệt' if it['stage'] >= 8 else 'chưa tới Operations'}</span></div>
    <div class="b-art"><span class="achip">Telemetry</span><span class="achip">Runbook</span></div></div>
  <div class="map-cap">Ở mọi điểm phân rã, AI đề xuất trước và con người xác nhận trước khi đi tiếp.</div>
</div>""")
    return "".join(rows) or '<p class="empty">Chưa có intent — chạy /dlc-intent để bắt đầu.</p>'


def boards():
    out = []
    for it in intents:
        for u in it["units"]:
            for b in u["bolts"]:
                if not b["tasks"]:
                    continue
                rows = "".join(
                    f'<div class="trow"><span class="tid">{esc(t["title"].split("·")[0].strip())}</span>'
                    f'<span class="chip {"done" if t.get("status")=="done" else ("active" if t.get("status") in ("claimed","in-progress","review") else "")}">{esc(t.get("status","?"))}</span>'
                    f'<span class="tmeta">{esc(t["title"].split("·",1)[1].strip() if "·" in t["title"] else "")} · claim: {esc(t.get("claimed_by","-"))} · duyệt: {esc(t.get("approver","-"))} · deps: {esc(t.get("depends_on","[]"))}</span></div>'
                    for t in b["tasks"]
                )
                out.append(f'<div class="board"><h4>{esc(it["id"])} / {esc(u["id"])} / {esc(b["name"])}</h4>{rows}</div>')
    return "".join(out) or '<p class="empty">Chưa có task board.</p>'


def feed():
    rows = "".join(
        f'<div><span class="frm">{esc(m.get("from","?"))}</span> → <span class="frm">{esc(m.get("to","?"))}</span>'
        f' <span class="typ">· {esc(m.get("type",""))} · {esc(m.get("re",""))} · {esc(m["id"])}</span></div>'
        for m in msgs
    )
    return rows or '<p class="empty">Chưa có trao đổi.</p>'


def reviews_html():
    rows = "".join(
        f'<span class="verdict {"ok" if "approve" in m.get("verdict","") else "rc"}">{esc(m["id"])} · {esc(m.get("reviewer","?").replace("dlc-",""))} · {esc(m.get("verdict","?"))}</span> '
        for m in rvs
    )
    return rows or '<p class="empty">Chưa có review.</p>'


n_gates = sum(1 for i in intents if i["gate_open"] not in ("null", "")) + len(inbox_pending)
n_bolts = sum(1 for i in intents for u in i["units"] for b in u["bolts"] if any(b["prog"].values()))

page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🗼 AI-DLC Control Tower</title><style>
:root{{--bg:#0E1419;--surface:#161D24;--s2:#1D262F;--ink:#E6ECF2;--muted:#93A1AE;--line:#2A3540;--accent:#E9A23B;--abg:rgba(233,162,59,.13);--blue:#7FAEDC;--bbg:rgba(127,174,220,.12);--ok:#58B383;--okbg:rgba(88,179,131,.13);--mono:ui-monospace,"SF Mono",Menlo,monospace;--sans:-apple-system,"Segoe UI",sans-serif}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:14px;line-height:1.55;padding:20px}}
.wrap{{max-width:1200px;margin:0 auto}}header{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:16px}}
h1{{font-size:18px;font-family:var(--mono);letter-spacing:.06em}}.kpi{{font-family:var(--mono);font-size:12px;color:var(--muted)}}.kpi b{{color:var(--accent)}}
nav{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}}nav button{{background:var(--s2);color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:6px 14px;cursor:pointer;font-family:var(--mono);font-size:12px}}nav button.on{{color:var(--accent);border-color:var(--accent);background:var(--abg)}}
section{{display:none}}section.on{{display:block}}h3{{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:18px 0 8px}}
.chip{{font-family:var(--mono);font-size:10.5px;padding:2px 7px;border-radius:4px;border:1px solid var(--line);color:var(--muted);display:inline-block;margin:1px}}
.chip.done{{color:var(--ok);border-color:var(--ok);background:var(--okbg)}}.chip.active{{color:var(--accent);border-color:var(--accent);background:var(--abg)}}
.gate-item{{display:flex;gap:10px;border:1px solid var(--accent);background:var(--abg);border-radius:10px;padding:12px 14px;margin-bottom:10px}}
.gate-item.processed{{opacity:.7;border-style:dashed}}.g-dot{{width:9px;height:9px;border-radius:50%;background:var(--accent);margin-top:6px;flex:none}}
.g-title{{color:var(--muted);font-size:12.5px}}.g-actions{{margin-top:8px;display:flex;gap:8px;flex-wrap:wrap}}
.g-actions button{{background:var(--ok);color:#0E1419;border:0;border-radius:6px;padding:5px 14px;font-weight:700;cursor:pointer}}
.g-actions button.rej{{background:transparent;color:var(--accent);border:1px solid var(--accent)}}
.g-actions input{{flex:1;min-width:220px;background:var(--surface);border:1px solid var(--line);border-radius:6px;color:var(--ink);padding:5px 10px}}
details pre{{white-space:pre-wrap;font-size:11.5px;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px;margin-top:6px;max-height:260px;overflow:auto;font-family:var(--mono)}}
.prow{{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line);flex-wrap:wrap}}.prow .int{{font-family:var(--mono);font-size:12px;min-width:220px}}
.grid{{display:grid;grid-template-columns:1.2fr .8fr;gap:20px}}@media(max-width:860px){{.grid{{grid-template-columns:1fr}}}}
.feed div{{font-family:var(--mono);font-size:11.5px;padding:3px 0;border-bottom:1px dotted var(--line)}}.frm{{color:var(--blue)}}.typ{{color:var(--muted)}}
.verdict{{font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:4px;border:1px solid var(--line);display:inline-block;margin:2px}}
.verdict.ok{{color:var(--ok);border-color:var(--ok);background:var(--okbg)}}.verdict.rc{{color:var(--accent);border-color:var(--accent);background:var(--abg)}}
.empty{{color:var(--muted);padding:10px 0}}
.mapcard{{border:1px solid var(--line);border-radius:12px;background:var(--surface);margin-bottom:18px;overflow:hidden}}
.map-h{{padding:10px 16px;border-bottom:1px solid var(--line);font-family:var(--mono);font-size:13px}}
.band{{display:grid;grid-template-columns:180px 1fr 210px;border-bottom:1px solid var(--line)}}@media(max-width:860px){{.band{{grid-template-columns:1fr}}}}
.b-role{{padding:12px;font-size:11px;color:var(--muted);border-right:1px solid var(--line)}}.b-flow{{padding:12px;min-height:56px}}.b-art{{padding:12px;border-left:1px solid var(--line)}}
.intent-node{{font-family:var(--mono);font-size:11px;border:1.5px solid var(--ink);border-radius:6px;padding:3px 8px}}
.ucard{{display:inline-flex;flex-direction:column;font-family:var(--mono);font-size:10.5px;border:1px solid var(--line);border-radius:6px;padding:4px 8px;margin:3px;background:var(--s2)}}
.ucard em{{font-style:normal;color:var(--muted)}}.ucard b{{color:var(--accent)}}.ucard.ok b{{color:var(--ok)}}
.achip{{display:inline-block;font-family:var(--mono);font-size:10px;border:1px dashed var(--line);border-radius:4px;padding:2px 6px;margin:2px;color:var(--muted)}}.achip.on{{border-style:solid;color:var(--ink);background:var(--s2)}}
.lane{{display:flex;align-items:center;gap:6px;margin:4px 0;flex-wrap:wrap}}.lane-l{{font-family:var(--mono);font-size:10.5px;color:var(--muted);min-width:64px}}
.bolt{{font-family:var(--mono);font-size:10px;border:1px solid var(--blue);border-radius:999px;padding:2px 8px;background:var(--bbg)}}
.bolt i{{font-style:normal;color:var(--muted);margin-left:5px}}.bolt i.on{{color:var(--ok);font-weight:700}}
.brown{{font-size:11px;color:var(--accent);margin-bottom:6px}}.map-cap{{padding:8px 16px;font-size:11px;color:var(--muted);font-style:italic}}
.muted{{color:var(--muted);font-size:12px}}
.board{{border:1px solid var(--line);border-radius:10px;background:var(--surface);padding:12px 14px;margin-bottom:12px}}
.board h4{{font-family:var(--mono);font-size:12px;margin-bottom:8px}}.trow{{display:flex;gap:8px;align-items:baseline;padding:4px 0;border-bottom:1px dotted var(--line);flex-wrap:wrap}}
.tid{{font-family:var(--mono);font-size:11.5px;min-width:60px}}.tmeta{{font-family:var(--mono);font-size:10.5px;color:var(--muted)}}
footer{{margin-top:24px;color:var(--muted);font-size:11px;font-family:var(--mono)}}
</style></head><body><div class="wrap">
<header><h1>🗼 AI-DLC CONTROL TOWER</h1><div class="kpi">Gates chờ: <b>{n_gates}</b> · Intents: {len(intents)} · Bolts active: {n_bolts}</div></header>
<nav><button class="on" onclick="show(this,'mc')">Mission Control</button><button onclick="show(this,'map')">Bản đồ AI-DLC</button><button onclick="show(this,'tasks')">Task Boards</button><button onclick="show(this,'comm')">Comms & Reviews</button></nav>
<section id="mc" class="on">
  <h3>Gate Queue — chờ quyết định của bạn</h3>{gate_cards()}
  <div class="grid"><div><h3>Pipeline Board</h3>
  {''.join(f'<div class="prow"><span class="int">{esc(i["id"])} · {esc(i["title"][:40])}</span>{stage_chips(i)}</div>' for i in intents) or '<p class="empty">Chưa có intent.</p>'}
  <h3>Risks</h3>{''.join(f'<div class="feed"><div>{esc(r)}</div></div>' for r in risks) or '<p class="empty">Trống.</p>'}</div>
  <div><h3>Comms feed</h3><div class="feed">{feed()}</div></div></div>
</section>
<section id="map"><h3>Bản đồ AI-DLC — Hình 1 white paper, trạng thái sống (Vai trò/Nghi thức · Dòng chảy · Artefact)</h3>{map_view()}</section>
<section id="tasks"><h3>Task Boards</h3>{boards()}</section>
<section id="comm"><h3>Review Verdicts</h3>{reviews_html()}<h3>Comms</h3><div class="feed">{feed()}</div></section>
<footer>Generated từ .ai-dlc/ · Approve/Reject cần tower_serve.py (nút sẽ báo nếu server không chạy) · AI đề xuất trước — con người xác nhận trước khi đi tiếp.</footer>
</div><script>
function show(btn,id){{document.querySelectorAll('nav button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');document.querySelectorAll('section').forEach(s=>s.classList.remove('on'));document.getElementById(id).classList.add('on');}}
function decide(btn,verdict){{
  const card=btn.closest('.gate-item');const input=card.querySelector('input');const comment=input?input.value.trim():'';
  if(verdict==='reject'&&!comment){{alert('Reject bắt buộc kèm lý do.');input.focus();return;}}
  const payload={{gate:card.dataset.gate,intent:card.dataset.intent,verdict:verdict,comment:comment,decided_at:new Date().toISOString()}};
  const token=new URLSearchParams(location.search).get('token')||'';
  fetch('/decision?token='+encodeURIComponent(token),{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}})
    .then(r=>{{if(!r.ok)throw 0;card.style.opacity=.5;btn.disabled=true;card.querySelector('.g-body').insertAdjacentHTML('beforeend','<div style="color:var(--ok)">Đã ghi vào inbox — session sẽ xử lý.</div>');}})
    .catch(()=>alert('Không gửi được — tower đang mở dạng file tĩnh. Chạy /dlc-tower serve để bật nút, hoặc quyết định trực tiếp trong terminal.'));
}}
</script></body></html>"""

out_dir = os.path.join(A, "tower")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)
print(os.path.join(out_dir, "index.html"))
