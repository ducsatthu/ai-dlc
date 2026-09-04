#!/usr/bin/env python3
"""AI-DLC Tower cho workspace AWS aidlc-workflows v2 (phương án A, 7.0.0 lát 2).

Đọc `aidlc/spaces/<space>/intents/<id>/aidlc-state.md` + `audit/*.md` (KHÔNG đọc `.ai-dlc/context-memory`),
đối chiếu `.ai-dlc/governance/raci.md`, sinh ba loại thẻ theo vai của NGƯỜI ĐANG XEM (git user của clone):
  · Cần tôi quyết  — stage `[?]` mà tôi nằm trong cột "quyết"  → nút Duyệt / Trả lại  ⇒ tower_approve.ts
  · Cần tôi trả lời — câu hỏi / xác nhận tóm tắt engine đã hỏi (DECISION_RECORDED) chưa có câu trả lời
  · Cần tôi kiểm    — stage `[?]` mà tôi nằm trong cột "kiểm" (soát artifact trước khi người quyết bấm)
Mọi thứ khác (intent, stage hiện tại, sự kiện, KPI tốc độ quyết) vào *Tra cứu*. Tầng 0 chỉ có thẻ cần người.

Chạy:  python3 tower_aws_v2.py [--project-dir <ws>] [--serve] [--port 8643] [--out <dir>]
  · mặc định: sinh <ws>/.ai-dlc/tower/index.html + state.json rồi in đường dẫn (nên gitignore .ai-dlc/tower/)
  · --serve: HTTP 127.0.0.1 — GET / · GET /state (sinh lại mỗi lần) · GET /doc?path= (markdown dưới workspace)
             · POST /pull (git pull --rebase) · POST /decision {intent, stage, result, input} → tower_approve.ts
Fail-open: không phải workspace AWS v2 → in lỗi rõ, exit 1. Chỉ stdlib.
"""
import argparse, datetime, json, os, re, secrets, statistics, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
APPROVE = os.path.join(HERE, "tower_approve.ts")

# ---------- workspace ----------
def find_ws(explicit=None):
    cands = [explicit, os.environ.get("AIDLC_PROJECT_DIR"), os.environ.get("CLAUDE_PROJECT_DIR")]
    d = os.getcwd()
    for _ in range(7):
        cands.append(d)
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    for c in cands:
        if c and os.path.isdir(os.path.join(c, "aidlc", "spaces")) and \
           os.path.isfile(os.path.join(c, ".claude", "tools", "aidlc-orchestrate.ts")):
            return os.path.abspath(c)
    return None

def git(ws, *args, ok=False):
    r = subprocess.run(["git", *args], cwd=ws, capture_output=True, text=True)
    if r.returncode != 0 and not ok:
        return ""
    return r.stdout.strip()

def rel(ws, p):
    return os.path.relpath(p, ws).replace(os.sep, "/")

# ---------- RACI ----------
def parse_raci(md):
    rows = []
    for line in md.splitlines():
        m = re.match(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|(?:\s*([^|]*?)\s*\|)?\s*$", line)
        if not m:
            continue
        gate = m.group(1).strip()
        if not gate or re.match(r"^-+$", gate) or gate.lower() == "gate":
            continue
        sp = lambda v: [x.strip() for x in (v or "").split(",") if x.strip() and x.strip() not in ("—", "-")]
        rows.append({"gate": gate, "decide": sp(m.group(2)), "check": sp(m.group(3))})
    return rows

def raci_row(rows, slug):
    for r in rows:
        if r["gate"] == slug:
            return r
    for r in rows:
        if r["gate"] != slug and "*" in r["gate"]:
            pat = "^" + ".*".join(re.escape(p) for p in r["gate"].split("*")) + "$"
            if re.match(pat, slug):
                return r
    return None

def is_me(names, me):
    mine = {me["email"].lower(), me["name"].lower()}
    return any(n.lower() in mine for n in names)

# ---------- state + audit ----------
FIELD = re.compile(r"^\*\*([^*]+)\*\*:\s*(.*)$")
CHECK = re.compile(r"^- \[(.)\] ([\w.-]+)(?:\s+—\s+(\S+))?")

def parse_state(text):
    st = {"fields": {}, "stages": []}
    phase = ""
    in_progress = False
    for line in text.splitlines():
        m = FIELD.match(line.strip("- ").strip()) if line.lstrip().startswith("- **") else FIELD.match(line)
        if m:
            st["fields"][m.group(1).strip()] = m.group(2).strip()
        if line.startswith("## "):
            in_progress = line.strip() == "## Stage Progress"
            continue
        if in_progress and line.startswith("### "):
            phase = line[4:].strip()
            continue
        c = CHECK.match(line)
        if c and in_progress:
            st["stages"].append({"mark": c.group(1), "slug": c.group(2), "mode": c.group(3) or "", "phase": phase})
    return st

def parse_audit(record):
    adir = os.path.join(record, "audit")
    events = []
    if not os.path.isdir(adir):
        return events
    for i, fn in enumerate(sorted(os.listdir(adir))):
        if not fn.endswith(".md"):
            continue
        try:
            txt = open(os.path.join(adir, fn), encoding="utf-8").read()
        except OSError:
            continue
        for j, block in enumerate(txt.replace("\r\n", "\n").split("\n---\n")):
            f = {}
            for line in block.splitlines():
                m = FIELD.match(line.strip())
                if m:
                    f[m.group(1).strip()] = m.group(2).strip()
            if "Event" in f:
                f["_shard"] = fn.replace(".md", "")
                f["_ord"] = (f.get("Timestamp", ""), i, j)
                events.append(f)
    events.sort(key=lambda e: e["_ord"])
    return events

def stage_artifacts(ws, record, slug):
    out = []
    for root, dirs, files in os.walk(record):
        if os.path.basename(root) == slug and "audit" not in root:
            for f in sorted(files):
                if f.endswith(".md"):
                    out.append(rel(ws, os.path.join(root, f)))
    return out

def hours_between(a, b):
    try:
        ta = datetime.datetime.fromisoformat(a.replace("Z", "+00:00"))
        tb = datetime.datetime.fromisoformat(b.replace("Z", "+00:00"))
        return round((tb - ta).total_seconds() / 3600, 2)
    except ValueError:
        return None

# ---------- build ----------
def build_state(ws):
    me = {"name": git(ws, "config", "user.name") or "?", "email": git(ws, "config", "user.email") or "?"}
    raci_path = os.path.join(ws, ".ai-dlc", "governance", "raci.md")
    raci = parse_raci(open(raci_path, encoding="utf-8").read()) if os.path.isfile(raci_path) else None
    decide, answer, check, intents, events_recent, durations = [], [], [], [], [], []
    spaces_dir = os.path.join(ws, "aidlc", "spaces")
    for space in sorted(os.listdir(spaces_dir)):
        idir = os.path.join(spaces_dir, space, "intents")
        if not os.path.isdir(idir):
            continue
        for iid in sorted(os.listdir(idir)):
            record = os.path.join(idir, iid)
            sp = os.path.join(record, "aidlc-state.md")
            if not os.path.isfile(sp):
                continue
            st = parse_state(open(sp, encoding="utf-8").read())
            ev = parse_audit(record)
            f = st["fields"]
            done = sum(1 for s in st["stages"] if s["mark"] == "x")
            total = len(st["stages"])
            last = ev[-1] if ev else {}
            intents.append({"space": space, "id": iid, "name": f.get("Project", iid), "scope": f.get("Scope", ""),
                            "current": f.get("Current Stage", ""), "next": f.get("Next Action", ""),
                            "phase": f.get("Phase", ""), "done": done, "total": total,
                            "open_gates": [s["slug"] for s in st["stages"] if s["mark"] == "?"],
                            "last_event": last.get("Event", ""), "last_ts": last.get("Timestamp", ""),
                            "state_path": rel(ws, sp)})
            # thời gian mở gate → quyết (KPI tốc độ)
            opened = {}
            for e in ev:
                s = e.get("Stage", "")
                if e["Event"] == "STAGE_AWAITING_APPROVAL":
                    opened[s] = e.get("Timestamp", "")
                elif e["Event"] in ("GATE_APPROVED", "GATE_REJECTED") and s in opened:
                    h = hours_between(opened.pop(s), e.get("Timestamp", ""))
                    if h is not None:
                        durations.append({"intent": iid, "stage": s, "hours": h, "by": e.get("User Input", "")})
            # thẻ QUYẾT / KIỂM
            for s in st["stages"]:
                if s["mark"] != "?":
                    continue
                row = raci_row(raci, s["slug"]) if raci else None
                since = opened.get(s["slug"], "")
                card = {"space": space, "intent": iid, "intent_name": f.get("Project", iid), "stage": s["slug"],
                        "phase": s["phase"] or f.get("Phase", ""), "since": since,
                        "artifacts": stage_artifacts(ws, record, s["slug"]),
                        "approvers": row["decide"] if row else [], "reviewers": row["check"] if row else [],
                        "raci": "missing" if raci is None else ("no-row" if row is None else "ok"),
                        "silence": "Đội đang đứng — gate không có mặc định (engine chặn tới khi có người quyết)."}
                card["mine"] = (raci is None) or (row is not None and is_me(row["decide"], me))
                decide.append(card)
                if row and is_me(row["check"], me):
                    check.append(dict(card, mine=True))
            # thẻ TRẢ LỜI: DECISION_RECORDED chưa có QUESTION_ANSWERED / SUMMARY_CONFIRMATION_RECORDED sau nó cùng stage
            pending = {}
            for e in ev:
                s = e.get("Stage", "")
                if e["Event"] == "DECISION_RECORDED":
                    key = (s, e.get("Checkpoint", ""), e.get("Unit", ""))
                    pending[key] = e
                elif e["Event"] in ("QUESTION_ANSWERED", "SUMMARY_CONFIRMATION_RECORDED"):
                    key = (s, e.get("Checkpoint", ""), e.get("Unit", ""))
                    pending.pop(key, None)
            for (s, cp, unit), e in pending.items():
                answer.append({"space": space, "intent": iid, "intent_name": f.get("Project", iid), "stage": s,
                               "question": e.get("Decision", ""), "options": e.get("Options", ""),
                               "checkpoint": cp, "unit": unit, "since": e.get("Timestamp", ""),
                               "file": e.get("Questions File", ""),
                               "silence": "Quá hạn ⇒ AI chọn phương án tốt nhất theo AI và ghi giả định "
                                          "\"lý do: im lặng quá hạn\" (quyết định chủ gói 2026-09-03).",
                               "how": "Trả lời trong phiên Claude/Codex đang giữ intent (AskUserQuestion) — tower chưa ghi thay."})
            for e in ev[-40:]:
                events_recent.append({"intent": iid, "ts": e.get("Timestamp", ""), "event": e["Event"],
                                      "stage": e.get("Stage", ""), "who": e.get("Actor", "") or e.get("User Input", ""),
                                      "shard": e["_shard"]})
    events_recent.sort(key=lambda e: e["ts"], reverse=True)
    kpi = {"decisions": len(durations),
           "median_hours": round(statistics.median([d["hours"] for d in durations]), 2) if durations else None,
           "max_hours": max([d["hours"] for d in durations]) if durations else None}
    return {"workspace": {"root": ws, "name": os.path.basename(ws), "branch": git(ws, "rev-parse", "--abbrev-ref", "HEAD"),
                          "head": git(ws, "rev-parse", "--short", "HEAD"),
                          "generated": datetime.datetime.now().strftime("%d/%m %H:%M:%S")},
            "me": me, "raci": "ok" if raci is not None else "missing",
            "cards": {"decide": decide, "answer": answer, "check": check},
            "intents": intents, "events": events_recent[:60], "kpi": kpi, "durations": durations[-20:]}

# ---------- HTML ----------
HTML = r"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>AI-DLC Tower · AWS v2</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#f7f7f5;--fg:#1a1a1a;--mut:#6b6b6b;--card:#fff;--line:#e3e3df;--acc:#1f5eff;--warn:#b45309;--ok:#15803d;--bad:#b91c1c}
@media(prefers-color-scheme:dark){:root{--bg:#141414;--fg:#ececec;--mut:#9a9a9a;--card:#1e1e1e;--line:#333;--acc:#7aa2ff}}
body{margin:0;font:14px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{display:flex;gap:16px;align-items:center;padding:12px 20px;border-bottom:1px solid var(--line);background:var(--card);position:sticky;top:0}
header b{font-size:16px} header .mut{color:var(--mut)} header .sp{flex:1}
main{max-width:980px;margin:0 auto;padding:20px}
h2{font-size:15px;margin:22px 0 10px;display:flex;gap:8px;align-items:center} h2 .n{background:var(--acc);color:#fff;border-radius:10px;padding:0 8px;font-size:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px}
.card .q{font-size:15px;font-weight:600} .card .meta{color:var(--mut);font-size:12.5px;margin:4px 0 8px}
.card .sil{border-left:3px solid var(--warn);padding:4px 10px;margin:8px 0;font-size:13px}
.card textarea{width:100%;box-sizing:border-box;min-height:56px;border:1px solid var(--line);border-radius:6px;padding:8px;font:inherit;background:var(--bg);color:var(--fg)}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px}
button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:6px 12px;cursor:pointer}
button.p{background:var(--acc);color:#fff;border-color:var(--acc)} button:disabled{opacity:.5;cursor:default}
a.doc{color:var(--acc);text-decoration:none;font-size:13px;margin-right:10px}
.empty{color:var(--mut);padding:16px;border:1px dashed var(--line);border-radius:10px}
.ok{color:var(--ok)} .bad{color:var(--bad)} .warn{color:var(--warn)}
details{margin-top:28px} summary{cursor:pointer;color:var(--mut)}
table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0} td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
pre.doc{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;max-height:60vh;overflow:auto;font-size:12.5px}
.pill{display:inline-block;border:1px solid var(--line);border-radius:10px;padding:0 8px;font-size:12px;color:var(--mut)}
</style></head><body>
<header><b>AI-DLC Tower</b><span class="mut" id="ws"></span><span class="sp"></span>
<span class="mut" id="me"></span><label class="mut"><input type="checkbox" id="all"> tất cả thẻ</label>
<button id="pull">Kéo mới</button><span class="mut" id="gen"></span></header>
<main>
<h2>Cần tôi quyết <span class="n" id="nD">0</span></h2><div id="decide"></div>
<h2>Cần tôi trả lời <span class="n" id="nA">0</span></h2><div id="answer"></div>
<h2>Cần tôi kiểm <span class="n" id="nC">0</span></h2><div id="check"></div>
<div id="docbox" hidden><h2>Tài liệu <button id="closedoc">đóng</button></h2><pre class="doc" id="doc"></pre></div>
<details><summary>Tra cứu ▾ — intent · sự kiện · KPI tốc độ quyết</summary><div id="lookup"></div></details>
</main>
<script>
const TOKEN=new URLSearchParams(location.search).get('token')||'';
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const ago=ts=>{if(!ts)return'';const h=(Date.now()-Date.parse(ts))/36e5;return h<1?Math.round(h*60)+' phút':h<48?h.toFixed(1)+' giờ':Math.round(h/24)+' ngày'};
let S=null;
async function load(){S=await (await fetch('/state?token='+TOKEN)).json();render();}
function docLink(p){return `<a class="doc" href="#" data-p="${esc(p)}">${esc(p.split('/').slice(-2).join('/'))}</a>`}
function cardDecide(c,i,kind){
  const who=c.approvers.length?c.approvers.join(', '):(c.raci==='missing'?'chưa có RACI — ai cũng thấy':'không có dòng RACI');
  return `<div class="card" data-i="${i}"><div class="q">${kind==='check'?'Soát trước khi người quyết bấm: ':'Duyệt stage '}<code>${esc(c.stage)}</code> · ${esc(c.intent_name)}</div>
  <div class="meta">${esc(c.intent)} · pha ${esc(c.phase)} · mở ${c.since?ago(c.since)+' trước':'?'} · người quyết: ${esc(who)}${c.reviewers.length?' · người kiểm: '+esc(c.reviewers.join(', ')):''}</div>
  <div>Xem: ${c.artifacts.map(docLink).join('')||'<span class="mut">chưa thấy artifact</span>'}</div>
  <div class="sil">Nếu im lặng: ${esc(c.silence)}</div>
  ${kind==='decide'?`<textarea placeholder="Lời của bạn — bắt buộc (được ghi nguyên văn vào audit + commit)"></textarea>
  <div class="row"><button class="p" data-act="approved">Duyệt</button><button data-act="rejected">Trả lại</button><span class="res mut"></span></div>`:''}
  </div>`}
function cardAnswer(a){return `<div class="card"><div class="q">${esc(a.checkpoint?'Xác nhận tóm tắt':'Câu hỏi')} · <code>${esc(a.stage)}</code> · ${esc(a.intent_name)}</div>
  <div class="meta">${esc(a.intent)}${a.unit?' · unit '+esc(a.unit):''} · hỏi ${ago(a.since)} trước</div>
  <div>${esc(a.question)}</div>${a.options?`<div class="meta">Phương án: ${esc(a.options)}</div>`:''}
  ${a.file?`<div>Xem: ${docLink(a.file)}</div>`:''}<div class="sil">Nếu im lặng: ${esc(a.silence)}</div><div class="meta">${esc(a.how)}</div></div>`}
function render(){
  const all=$('#all').checked;
  $('#ws').textContent=`${S.workspace.name} · ${S.workspace.branch}@${S.workspace.head}`;
  $('#me').textContent=`${S.me.name} <${S.me.email}>`+(S.raci==='missing'?' · RACI: chưa có':'');
  $('#gen').textContent='sinh '+S.workspace.generated;
  const d=S.cards.decide.filter(c=>all||c.mine), a=S.cards.answer, c=S.cards.check.filter(x=>all||x.mine);
  $('#nD').textContent=d.length;$('#nA').textContent=a.length;$('#nC').textContent=c.length;
  $('#decide').innerHTML=d.length?d.map((x,i)=>cardDecide(x,S.cards.decide.indexOf(x),'decide')).join(''):'<div class="empty">Không có gì cần bạn quyết.</div>';
  $('#answer').innerHTML=a.length?a.map(cardAnswer).join(''):'<div class="empty">Không có câu hỏi nào đang chờ.</div>';
  $('#check').innerHTML=c.length?c.map((x,i)=>cardDecide(x,i,'check')).join(''):'<div class="empty">Không có gì cần bạn kiểm.</div>';
  const k=S.kpi;
  $('#lookup').innerHTML=`<p class="mut">KPI tốc độ quyết: ${k.decisions} quyết định · trung vị ${k.median_hours??'—'} giờ · lâu nhất ${k.max_hours??'—'} giờ (mở gate → commit quyết).</p>
  <table><tr><th>Intent</th><th>Scope</th><th>Stage hiện tại</th><th>Tiến độ</th><th>Gate mở</th><th>Sự kiện cuối</th></tr>
  ${S.intents.map(i=>`<tr><td>${esc(i.name)}<br><span class="pill">${esc(i.id)}</span></td><td>${esc(i.scope)}</td><td>${esc(i.current)}<br><span class="mut">${esc(i.next)}</span></td><td>${i.done}/${i.total}</td><td>${esc(i.open_gates.join(', '))||'—'}</td><td>${esc(i.last_event)}<br><span class="mut">${ago(i.last_ts)} trước</span></td></tr>`).join('')}</table>
  <table><tr><th>Lúc</th><th>Sự kiện</th><th>Stage</th><th>Ai / lời</th><th>Shard</th></tr>
  ${S.events.map(e=>`<tr><td>${esc(e.ts)}</td><td>${esc(e.event)}</td><td>${esc(e.stage)}</td><td>${esc(e.who)}</td><td class="mut">${esc(e.shard.split('-').pop())}</td></tr>`).join('')}</table>`;
}
document.addEventListener('click',async ev=>{
  const a=ev.target.closest('a.doc');if(a){ev.preventDefault();const r=await fetch('/doc?token='+TOKEN+'&path='+encodeURIComponent(a.dataset.p));$('#doc').textContent=await r.text();$('#docbox').hidden=false;$('#docbox').scrollIntoView();return;}
  const b=ev.target.closest('button[data-act]');if(b){const card=b.closest('.card');const c=S.cards.decide[+card.dataset.i];const input=card.querySelector('textarea').value.trim();const res=card.querySelector('.res');
    if(!input){res.textContent='Cần lời của bạn.';res.className='res bad';return;}
    card.querySelectorAll('button').forEach(x=>x.disabled=true);res.textContent='đang ghi commit…';res.className='res mut';
    const r=await (await fetch('/decision?token='+TOKEN,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({intent:c.intent,space:c.space,stage:c.stage,result:b.dataset.act,input})})).json();
    res.textContent=r.ok?`✓ ${r.result} · commit ${r.commit}${r.pushed?' đã push':''}`:'✗ '+r.error;res.className='res '+(r.ok?'ok':'bad');
    if(r.ok)setTimeout(load,800);else card.querySelectorAll('button').forEach(x=>x.disabled=false);return;}
});
$('#closedoc').onclick=()=>{$('#docbox').hidden=true};
$('#all').onchange=render;
$('#pull').onclick=async()=>{$('#pull').disabled=true;const r=await (await fetch('/pull?token='+TOKEN,{method:'POST'})).json();$('#pull').disabled=false;$('#gen').textContent=r.ok?'đã kéo':'✗ '+r.error;load();};
load();setInterval(load,15000);
</script></body></html>
"""

# ---------- serve ----------
def make_handler(ws, token):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code, obj):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

        def _auth(self):
            q = parse_qs(urlparse(self.path).query)
            return q.get("token", [""])[0] == token

        def do_GET(self):
            p = urlparse(self.path)
            if p.path == "/":
                self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            if not self._auth():
                self._json(403, {"ok": False, "error": "thiếu hoặc sai token"})
                return
            if p.path == "/state":
                self._json(200, build_state(ws))
                return
            if p.path == "/doc":
                relp = parse_qs(p.query).get("path", [""])[0]
                full = os.path.abspath(os.path.join(ws, relp))
                if not full.startswith(ws + os.sep) or not full.endswith(".md") or not os.path.isfile(full):
                    self._json(404, {"ok": False, "error": "chỉ đọc file .md dưới workspace"})
                    return
                self._send(200, open(full, "rb").read(), "text/plain; charset=utf-8")
                return
            self._json(404, {"ok": False, "error": "không có endpoint"})

        def do_POST(self):
            if not self._auth():
                self._json(403, {"ok": False, "error": "thiếu hoặc sai token"})
                return
            p = urlparse(self.path)
            if p.path == "/pull":
                r = subprocess.run(["git", "pull", "--rebase", "--quiet"], cwd=ws, capture_output=True, text=True)
                self._json(200 if r.returncode == 0 else 500, {"ok": r.returncode == 0, "error": r.stderr.strip()})
                return
            if p.path == "/decision":
                try:
                    n = int(self.headers.get("Content-Length", "0"))
                    d = json.loads(self.rfile.read(n) or b"{}")
                    for k in ("intent", "stage", "result", "input"):
                        if not d.get(k):
                            raise ValueError("thiếu " + k)
                    if d["result"] not in ("approved", "rejected"):
                        raise ValueError("result phải là approved | rejected")
                except Exception as e:  # noqa: BLE001
                    self._json(400, {"ok": False, "error": str(e)})
                    return
                cmd = ["bun", APPROVE, "--project-dir", ws, "--intent", d["intent"], "--space", d.get("space", "default"),
                       "--stage", d["stage"], "--result", d["result"], "--input", d["input"]]
                r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True)
                try:
                    out = json.loads(r.stdout.strip().splitlines()[-1])
                except (ValueError, IndexError):
                    out = {"ok": False, "error": (r.stderr or r.stdout).strip()[-800:]}
                self._json(200 if out.get("ok") else 409, out)
                return
            self._json(404, {"ok": False, "error": "không có endpoint"})

        def log_message(self, *a):
            pass
    return H

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8643)
    ap.add_argument("--out")
    a = ap.parse_args()
    ws = find_ws(a.project_dir)
    if not ws:
        print("Không phải workspace AWS aidlc v2 (cần aidlc/spaces + .claude/tools/aidlc-orchestrate.ts) — dùng --project-dir", file=sys.stderr)
        sys.exit(1)
    out = a.out or os.path.join(ws, ".ai-dlc", "tower")
    os.makedirs(out, exist_ok=True)
    state = build_state(ws)
    with open(os.path.join(out, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(HTML)
    print(json.dumps({"workspace": ws, "out": out, "me": state["me"], "raci": state["raci"],
                      "decide": len(state["cards"]["decide"]), "answer": len(state["cards"]["answer"]),
                      "check": len(state["cards"]["check"]), "intents": len(state["intents"])}, ensure_ascii=False))
    if not a.serve:
        return
    token = secrets.token_urlsafe(12)
    srv = HTTPServer(("127.0.0.1", a.port), make_handler(ws, token))
    print(f"AI-DLC Tower (AWS v2): http://127.0.0.1:{a.port}/?token={token}", flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
