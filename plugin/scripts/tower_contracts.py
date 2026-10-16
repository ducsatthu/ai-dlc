#!/usr/bin/env python3
"""tower_contracts.py — Control Tower cho engine `contracts` (7.0.0-a, lát a-2).

Engine `contracts` là workflow của template đội: mỗi change là `docs/intents/NNNN-name/` bốn file, duyệt ghi vào
`approvals.json` bằng `approvals.py --by <tên người>`. Luật đội: never infer approval. Quyết định chủ gói 2026-10-16
câu 2: autopilot ở engine này là "soạn sẵn, người bấm một nút". Tower này là cái nút đó.

Màn mặc định chỉ có "Cần tôi quyết": mỗi change đang chờ một gate là một thẻ, trên thẻ có tài liệu gate đọc toàn
văn, kết quả validator của đội, và hai nút Duyệt / Yêu cầu sửa. Bấm nút thì server gọi đúng `approvals.py` của đội
với tên người đã gõ. Gói không tự ghi gì vào approvals.json, không sửa bốn file, không có hàng đợi inbox riêng.

Server kiểm trước khi gọi: gate phải là gate đang chờ (tính lại từ approvals.json lúc bấm), tên phải là tên người
(không rỗng, không "ai", không ngoặc vuông), duyệt phải kèm previewed=true (đã mở tài liệu gate trên thẻ), và
validator của đội phải sạch ở stage hiện tại, kể cả kiểm strict đúng như approvals.py sẽ kiểm (contracts_brief.strict_check). Mỗi lần gọi ghi một sự kiện vào `.ai-dlc/log/YYYY-MM.jsonl`
(change, gate, decision, kết quả; không ghi tên người) để `contracts_retro.py` đọc.

Usage: python3 tower_contracts.py [root] [port]      (port mặc định: tower.port của layout, 8644)
Exit 2 khi không phải workspace contracts. Chỉ stdlib. Bind 127.0.0.1, URL kèm token.
"""
import datetime
import json
import os
import re
import secrets
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import contracts_brief as cb  # noqa: E402

APPROVALS_REL = os.path.join(".agents", "skills", "aidlc", "scripts", "approvals.py")
DOC_FILES = ("intent.md", "plan.md", "evidence.md", "approvals.json")
PROTECTED_BRANCHES = ("main", "master", "develop")


def human_name_ok(name):
    """Cùng luật với approvals.py của đội: tên người đã xác nhận, không phải AI, không placeholder."""
    n = (name or "").strip()
    return bool(n) and n.lower() not in ("ai", "agent", "claude", "codex", "tower") and "[" not in n and len(n) <= 80


def collect(root, validate=True):
    idir = os.path.join(root, "docs", "intents")
    names = sorted(n for n in os.listdir(idir) if cb.CHANGE_DIR.match(n) and os.path.isdir(os.path.join(idir, n))) \
        if os.path.isdir(idir) else []
    changes = [cb.read_change(root, os.path.join(idir, n)) for n in names]
    for ch in changes:
        ch["git"] = cb.git_state(root, ch)
        ch["validator"] = cb.run_validator(root, ch) if validate else None
        ch["validator_strict"] = cb.strict_check(root, ch) if validate else None
        ch["bind"] = cb.BIND.get(ch["pending"], []) if ch["pending"] else []
    return changes


def state(root, validate=True):
    changes = collect(root, validate)
    findings = cb.doctor(root, changes)
    branch = cb.git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return {
        "engine": "contracts", "root": root, "project": os.path.basename(root),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "user": cb.git(root, "config", "user.name") or "",
        "branch": branch, "branch_protected": branch in PROTECTED_BRANCHES,
        "approvals_py": os.path.isfile(os.path.join(root, APPROVALS_REL)),
        "need": [c for c in changes if c["pending"]],
        "changes": changes,
        "doctor": [{"level": l, "code": c, "msg": m} for l, c, m in findings],
    }


def log_event(root, ev):
    now = datetime.datetime.now().astimezone()
    ev = dict({"ts": now.isoformat(timespec="seconds"), "s": "tower", "via": "tower"}, **ev)
    ldir = os.path.join(root, ".ai-dlc", "log")
    try:
        os.makedirs(ldir, exist_ok=True)
        with open(os.path.join(ldir, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError:
        pass


def record_decision(root, data):
    """Kiểm rồi gọi approvals.py của đội. Trả (http_code, payload)."""
    change = str(data.get("change") or "")
    gate = str(data.get("gate") or "")
    decision = str(data.get("decision") or "")
    by = str(data.get("by") or "").strip()
    if not cb.CHANGE_DIR.match(change):
        return 400, {"ok": False, "error": "thiếu hoặc sai mã change (NNNN-ten)"}
    cdir = os.path.join(root, "docs", "intents", change)
    if not os.path.isdir(cdir):
        return 404, {"ok": False, "error": "không có change %s trong docs/intents/" % change}
    if decision not in ("approve", "request-changes"):
        return 400, {"ok": False, "error": "decision phải là approve hoặc request-changes"}
    if not human_name_ok(by):
        return 400, {"ok": False, "error": "cần tên người đã xác nhận: không rỗng, không phải AI, không ngoặc vuông"}
    ch = cb.read_change(root, cdir)
    if not ch["pending"]:
        return 409, {"ok": False, "error": "%s đã đủ duyệt, không còn gate nào chờ" % change}
    if gate != ch["pending"]:
        return 409, {"ok": False, "error": "gate đang chờ của %s là `%s`, không phải `%s`. Tải lại trang" % (change, ch["pending"], gate)}
    if decision == "approve":
        if data.get("previewed") is not True:
            return 400, {"ok": False, "error": "duyệt phải kèm previewed=true: mở %s trên thẻ trước" % ", ".join(cb.BIND[gate])}
        v = cb.run_validator(root, ch)
        if v.get("available") and v.get("errors"):
            return 409, {"ok": False, "error": "validate_workflow --stage %s còn %d error, sửa contract trước rồi duyệt"
                                               % (v["stage"], v["errors"]), "validator": v}
        if v.get("available") and v.get("exit") not in (0, None) and v.get("errors") is None:
            return 409, {"ok": False, "error": "validator của đội thoát mã %s mà không ra Result, không duyệt mù" % v.get("exit"),
                         "validator": v}
        s = cb.strict_check(root, ch)
        if s.get("available") and s.get("errors"):
            return 409, {"ok": False, "error": "approvals.py sẽ từ chối `%s`: nó kiểm strict file gate ràng, còn %d error: %s"
                                               % (cb.SAY[gate], s["errors"], "; ".join(s.get("lines", [])[:3])), "validator_strict": s}
    script = os.path.join(root, APPROVALS_REL)
    if not os.path.isfile(script):
        return 501, {"ok": False, "error": "không thấy %s trong workspace, gói không tự ghi approvals.json thay" % APPROVALS_REL}
    try:
        p = subprocess.run([sys.executable, script, ch["dir"], "--gate", gate, "--decision", decision, "--by", by],
                           cwd=root, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        log_event(root, {"ev": "approve", "change": change, "gate": gate, "decision": decision, "ok": False})
        return 500, {"ok": False, "error": "không chạy được approvals.py: %s" % str(e)[:160]}
    ok = p.returncode == 0
    log_event(root, {"ev": "approve", "change": change, "gate": gate, "decision": decision, "ok": ok})
    out = (p.stdout + "\n" + p.stderr).strip()
    if not ok:
        return 409, {"ok": False, "error": "approvals.py từ chối: %s" % (out[-300:] or "exit %d" % p.returncode)}
    after = cb.read_change(root, cdir)
    return 200, {"ok": True, "message": out[-300:], "change": change, "gate": gate, "decision": decision,
                 "pending": after["pending"], "say": after["say"],
                 "next": "approvals.json của %s đã đổi. Commit nó trên nhánh của change (%s), không commit trên main/develop."
                         % (change, ch["branch"] or "nhánh plan khai")}


# ---------- trang ----------

PAGE = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-DLC Tower · contracts</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e2e2dd;--ok:#1d7a3e;--warn:#9a6700;--bad:#b42318;--accent:#2457c5;--mono:ui-monospace,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1f1f1d;--ink:#ecece8;--muted:#9c9c95;--line:#33332f;--ok:#4cc27a;--warn:#e2b340;--bad:#f0776b;--accent:#7ea6ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
header{display:flex;gap:12px;align-items:baseline;padding:14px 16px;border-bottom:1px solid var(--line);flex-wrap:wrap}
header h1{font-size:17px;margin:0;font-weight:600}header .live{margin-left:auto;font-size:12px;color:var(--muted)}
main{max-width:980px;margin:0 auto;padding:16px}
h2{font-size:14px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:22px 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px}
.card .t{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}.card .t b{font-size:16px}
.tag{font:12px var(--mono);padding:1px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted)}
.tag.ok{color:var(--ok);border-color:var(--ok)}.tag.bad{color:var(--bad);border-color:var(--bad)}.tag.warn{color:var(--warn);border-color:var(--warn)}
.meta{color:var(--muted);font-size:13px;margin-top:4px}
.docs{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
button,.btn{font:inherit;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}button:disabled{opacity:.5;cursor:default}
.docs button.seen{border-color:var(--ok);color:var(--ok)}
.act{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px;padding-top:10px;border-top:1px dashed var(--line)}
.act input{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);min-width:200px}
.hint{font-size:13px;color:var(--muted);margin-top:8px}.hint.bad{color:var(--bad)}.hint.ok{color:var(--ok)}
.val{font:12.5px var(--mono);white-space:pre-wrap;color:var(--muted);margin-top:6px}
table{width:100%;border-collapse:collapse;font-size:13.5px}td,th{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:500}
.empty{color:var(--muted);padding:18px;text-align:center;border:1px dashed var(--line);border-radius:10px}
#modal{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;padding:16px}
#modal .box{background:var(--card);color:var(--ink);max-width:860px;width:100%;max-height:90vh;overflow:auto;border-radius:12px;padding:16px 20px}
#modal pre{white-space:pre-wrap;font:13px/1.5 var(--mono)}
details summary{cursor:pointer;color:var(--muted)}
</style></head><body>
<header><h1>AI-DLC Tower · engine contracts</h1><span id="proj" class="tag"></span><span id="branch" class="tag"></span><span class="live" id="live">đang tải</span></header>
<main>
<h2>Cần tôi quyết</h2><div id="need"></div>
<h2>Tra cứu</h2><div id="all"></div>
<h2>Doctor</h2><div id="doctor"></div>
<p class="hint">Gói ai-dlc không ghi thay người. Nút Duyệt gọi đúng <code>approvals.py --by &lt;tên bạn&gt;</code> của đội; lý do yêu cầu sửa ghi vào PR review hoặc nói với agent trong chat.</p>
</main>
<div id="modal" onclick="if(event.target===this)this.style.display='none'"><div class="box"><div style="display:flex;justify-content:space-between;align-items:baseline"><b id="mtitle"></b><button onclick="document.getElementById('modal').style.display='none'">Đóng</button></div><pre id="mbody"></pre></div></div>
<script>
const TOKEN = new URLSearchParams(location.search).get('token') || '';
const seen = {};            // change → Set(file đã mở)
const names = {};           // change → tên đang gõ
let S = null;
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const api = (p, opt) => fetch(p + (p.includes('?') ? '&' : '?') + 'token=' + encodeURIComponent(TOKEN), opt).then(r => r.json().then(j => Object.assign(j, {_code: r.status})));
const STATE_LBL = {current: 'đã duyệt', stale: 'duyệt mất hiệu lực', revision: 'yêu cầu sửa', none: 'chưa'};
const STATE_CLS = {current: 'ok', stale: 'bad', revision: 'warn', none: ''};

function gates(ch) {
  return ch.gates.map(g => { const a = ch.approvals[g]; return '<span class="tag ' + STATE_CLS[a.state] + '" title="' + esc(a.by || '') + ' ' + esc(a.at || '') + '">' + g + ': ' + STATE_LBL[a.state] + '</span>'; }).join(' ');
}
function validator(ch) {
  const v = ch.validator || {};
  if (v.available === false) return '<span class="tag warn">validator: không có trong workspace</span>';
  if (v.errors == null) return '<span class="tag warn">validator: chưa ra Result' + (v.error ? ' (' + esc(v.error) + ')' : '') + '</span>';
  const cls = v.errors ? 'bad' : (v.warnings ? 'warn' : 'ok');
  const s = ch.validator_strict || {};
  const strict = !s.available ? '' : (s.errors == null ? ' <span class="tag warn">kiểm strict không chạy được</span>'
    : (s.errors ? ' <span class="tag bad">approvals.py sẽ từ chối: ' + s.errors + ' error strict</span>' : ' <span class="tag ok">strict như approvals.py: sạch</span>'));
  return '<span class="tag ' + cls + '">validate --stage ' + esc(v.stage) + ': ' + v.errors + ' error · ' + v.warnings + ' warning</span>' + strict
    + (v.lines && v.lines.length ? '<div class="val">' + esc(v.lines.join('\n')) + '</div>' : '')
    + (s.errors ? '<div class="val">' + esc(s.lines.join('\n')) + '</div>' : '');
}
function cleanFor(ch) {
  const v = ch.validator || {}, s = ch.validator_strict || {};
  if (v.available === false) return true;                 // không có validator trong workspace: approvals.py cũng không có
  if (v.errors !== 0) return false;
  return !s.available || s.errors === 0;
}
function card(ch) {
  const id = ch.id, g = ch.pending, bind = ch.bind || [];
  const s = seen[id] || (seen[id] = new Set());
  const allSeen = bind.every(f => s.has(f));
  const clean = cleanFor(ch);
  const docs =['intent.md', 'plan.md', 'evidence.md', 'approvals.json'].map(f =>
    '<button class="' + (s.has(f) ? 'seen' : '') + '" onclick="openDoc(\'' + id + '\',\'' + f + '\')">' + (bind.includes(f) ? '● ' : '') + f + '</button>').join('');
  const name = names[id] != null ? names[id] : (S.user || '');
  return '<div class="card" id="c-' + id + '"><div class="t"><b>' + esc(id) + '</b><span>' + esc(ch.title) + '</span><span class="tag">' + esc(ch.scope) + '</span><span class="tag">chờ <code>' + esc(ch.say) + '</code></span></div>'
    + '<div class="meta">owner ' + esc(ch.owner || '?') + ' · repo ' + esc(ch.repos) + ' · branch ' + esc(ch.branch || '?') + ' · backlog ' + esc(ch.backlog) + ' · security ' + esc(ch.security) + '</div>'
    + '<div class="meta">' + gates(ch) + '</div>'
    + (ch.units.length ? '<div class="meta">units ' + ch.units.length + ' (pass ' + ch.units_pass + (ch.units_fail.length ? ', fail ' + ch.units_fail.join(',') : '') + ') · AC ' + ch.ac.length + ' (pass ' + ch.ac_pass.length + ')</div>' : '')
    + (ch.open_questions ? '<div class="hint bad">Open questions chưa là None. Trả lời trong intent.md trước khi duyệt.</div>' : '')
    + '<div class="meta" style="margin-top:8px">' + validator(ch) + '</div>'
    + '<div class="docs">' + docs + '</div>'
    + '<div class="hint">● = file gate <code>' + g + '</code> ràng băm. Đọc hết các file ● rồi nút Duyệt mới mở.</div>'
    + '<div class="act"><input placeholder="Tên bạn (người quyết)" value="' + esc(name) + '" oninput="names[\'' + id + '\']=this.value">'
    + '<button class="primary" ' + (allSeen && clean ? '' : 'disabled') + ' onclick="decide(\'' + id + '\',\'' + g + '\',\'approve\')">Duyệt ' + g + '</button>'
    + '<button onclick="decide(\'' + id + '\',\'' + g + '\',\'request-changes\')">Yêu cầu sửa</button></div>'
    + '<div class="hint" id="h-' + id + '">' + (!clean ? 'Validator chưa sạch (kể cả kiểm strict như approvals.py): duyệt sẽ bị từ chối cho tới khi hết error.' :(!allSeen ? 'Chưa mở đủ file ●.' : 'Sẵn sàng. Bấm Duyệt là gọi approvals.py với tên ở ô bên.')) + '</div></div>';
}
function render() {
  document.getElementById('proj').textContent = S.project;
  const b = document.getElementById('branch'); b.textContent = 'branch ' + (S.branch || '?'); b.className = 'tag' + (S.branch_protected ? ' warn' : '');
  b.title = S.branch_protected ? 'Đang ở nhánh bảo vệ: approvals.json ghi ra phải commit trên nhánh của change' : '';
  document.getElementById('live').textContent = 'LIVE · ' + S.generated.slice(11, 19) + (S.approvals_py ? '' : ' · không thấy approvals.py');
  document.getElementById('need').innerHTML = S.need.length ? S.need.map(card).join('') : '<div class="empty">Không gate nào chờ bạn. ' + (S.changes.length ? 'Mọi change đã đủ duyệt, còn merge PR trên platform.' : 'Chưa có change nào trong docs/intents/. Bắt đầu bằng /aidlc của đội.') + '</div>';
  document.getElementById('all').innerHTML = S.changes.length ? '<table><tr><th>change</th><th>scope</th><th>gate</th><th>stage</th><th>units</th><th>branch</th><th>file lạ</th></tr>'
    + S.changes.map(ch => '<tr><td><b>' + esc(ch.id) + '</b><div class="meta">' + esc(ch.title) + '</div></td><td>' + esc(ch.scope) + '</td><td>' + gates(ch) + '</td><td><code>' + esc(ch.stage) + '</code></td><td>' + ch.units.length + ' / pass ' + ch.units_pass + '</td><td>' + esc(ch.branch || '?') + (ch.git && ch.git.available && !ch.git.change_branch_exists ? ' <span class="tag warn">chưa có</span>' : '') + '</td><td>' + esc((ch.extra_unlisted || []).join(', ') || '') + '</td></tr>').join('') + '</table>'
    : '<div class="empty">trống</div>';
  document.getElementById('doctor').innerHTML = S.doctor.length ? '<table>' + S.doctor.map(d => '<tr><td><span class="tag ' + (d.level === 'FIX' ? 'bad' : d.level === 'WARN' ? 'warn' : '') + '">' + d.level + ' ' + d.code + '</span></td><td>' + esc(d.msg) + '</td></tr>').join('') + '</table>' : '<div class="empty">OK, không phát hiện gì</div>';
}
function openDoc(id, f) {
  api('/doc?change=' + id + '&file=' + f).then(j => {
    if (!j.ok) { alertHint(id, j.error, true); return; }
    document.getElementById('mtitle').textContent = id + '/' + f;
    document.getElementById('mbody').textContent = j.text;
    document.getElementById('modal').style.display = 'flex';
    (seen[id] || (seen[id] = new Set())).add(f);
    render();
  });
}
function alertHint(id, msg, bad) { const h = document.getElementById('h-' + id); if (h) { h.textContent = msg; h.className = 'hint ' + (bad ? 'bad' : 'ok'); } }
function decide(id, gate, decision) {
  const by = (names[id] != null ? names[id] : (S.user || '')).trim();
  if (!by) { alertHint(id, 'Gõ tên bạn trước.', true); return; }
  if (decision === 'request-changes' && !confirm('Ghi request-changes cho ' + id + ' gate ' + gate + ' với tên ' + by + '? Lý do bạn ghi vào PR review hoặc chat.')) return;
  const bind = ((S.need.find(c => c.id === id) || {}).bind) || [];
  const previewed = bind.every(f => (seen[id] || new Set()).has(f));
  document.querySelectorAll('#c-' + id + ' button').forEach(b => b.disabled = true);
  api('/approve', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change: id, gate, decision, by, previewed})})
    .then(j => { alertHint(id, j.ok ? (j.message + ' ' + j.next) : j.error, !j.ok); if (j.ok) seen[id] = new Set(); setTimeout(poll, 400); })
    .catch(e => alertHint(id, String(e), true));
}
function poll() {
  api('/state').then(j => { if (j.ok === false) { document.getElementById('live').textContent = j.error; return; } S = j; render(); })
    .catch(() => { document.getElementById('live').textContent = 'mất kết nối với tower'; });
}
poll(); setInterval(poll, 5000);
</script></body></html>
"""


def make_handler(root, token):
    class H(BaseHTTPRequestHandler):
        def _token_ok(self):
            m = re.search(r"token=([\w~-]+)", self.path)
            if m and m.group(1) == token:
                return True
            return ("ct_token=%s" % token) in self.headers.get("Cookie", "")

        def _send(self, code, body, ctype="application/json; charset=utf-8", cookie=False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if cookie:
                self.send_header("Set-Cookie", "ct_token=%s; Path=/; SameSite=Strict" % token)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code, obj):
            self._send(code, json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8"))

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8", cookie=self._token_ok())
                return
            if not self._token_ok():
                self._json(403, {"ok": False, "error": "thiếu hoặc sai token"})
                return
            if parsed.path == "/state":
                q = parse_qs(parsed.query)
                self._json(200, state(root, validate=q.get("validate", ["1"])[0] != "0"))
                return
            if parsed.path == "/doc":
                q = parse_qs(parsed.query)
                change, fname = unquote(q.get("change", [""])[0]), unquote(q.get("file", [""])[0])
                if not cb.CHANGE_DIR.match(change) or fname not in DOC_FILES:
                    self._json(404, {"ok": False, "error": "chỉ đọc bốn file của một change trong docs/intents/"})
                    return
                p = os.path.join(root, "docs", "intents", change, fname)
                if not os.path.isfile(p):
                    self._json(404, {"ok": False, "error": "không có %s/%s" % (change, fname)})
                    return
                self._json(200, {"ok": True, "change": change, "file": fname, "text": cb.read(p),
                                 "mtime": int(os.path.getmtime(p))})
                return
            self._json(404, {"ok": False, "error": "không có endpoint này"})

        def do_POST(self):
            if urlparse(self.path).path != "/approve":
                self._json(404, {"ok": False, "error": "không có endpoint này"})
                return
            if not self._token_ok():
                self._json(403, {"ok": False, "error": "thiếu hoặc sai token"})
                return
            try:
                n = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(n) or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("body phải là JSON object")
            except Exception as e:  # noqa: BLE001
                self._json(400, {"ok": False, "error": "body không đọc được: %s" % e})
                return
            code, payload = record_decision(root, data)
            self._json(code, payload)

        def log_message(self, *a):
            pass

    return H


def make_server(root, port=0, token=None):
    token = token or secrets.token_urlsafe(16)
    srv = HTTPServer(("127.0.0.1", port), make_handler(root, token))
    srv.token = token
    return srv


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    root = cb.find_root(args[0] if args else os.getcwd())
    if not root:
        print("Không phải workspace engine `contracts`. Kiểm: python3 %s/layout.py --explain" % HERE, file=sys.stderr)
        return 2
    port = None
    if len(args) > 1:
        port = int(args[1])
    else:
        try:
            from layout import resolve  # noqa: WPS433
            port = int((resolve(root).get("tower") or {}).get("port") or 8644)
        except Exception:  # noqa: BLE001
            port = 8644
    srv = make_server(root, port)
    print("AI-DLC Tower (contracts): http://127.0.0.1:%d/?token=%s" % (srv.server_address[1], srv.token), flush=True)
    print("Workspace: %s · duyệt ghi bằng approvals.py của đội, log ở .ai-dlc/log/" % root, flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
