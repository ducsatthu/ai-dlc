#!/usr/bin/env python3
"""AI-DLC Tower server — serve tower UI + nhận quyết định gate ghi vào .ai-dlc/inbox/.

Usage: python3 tower_serve.py [project_root] [port]
Bind 127.0.0.1 + token ngẫu nhiên (in URL lúc khởi động). POST không token → 403.
Quyết định ghi thành file JSON durable trong inbox/ — session Claude Code drain
qua Monitor (đang mở) hoặc SessionStart hook (phiên sau).

v2 (theo protocol v2):
- Ba verdict: approve · request-changes · reject. `request-changes`/`reject` bắt buộc comment.
- `approve` bắt buộc cờ `previewed: true` — chặn approve mù ở tầng server, không chỉ tầng UI.
- GET /doc?path=<rel> trả markdown tươi từ .ai-dlc/context-memory (chỉ đọc, guard path traversal).
"""
import json
import os
import re
import secrets
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote

def resolve_root(start):
    """Cùng luật với tower_generate: không nhận bừa cwd làm gốc dự án. Chạy nhầm chỗ thì DỪNG,
    đừng đẻ ra một `.ai-dlc/` rác trông y như dự án thật (xem tower_generate.resolve_root)."""
    p = os.path.abspath(start)
    parts = p.split(os.sep)
    if ".ai-dlc" in parts:
        p = os.sep.join(parts[:parts.index(".ai-dlc")]) or os.sep
    cur = p
    while True:
        if os.path.isdir(os.path.join(cur, ".ai-dlc", "context-memory")):
            return cur, p
        nxt = os.path.dirname(cur)
        if nxt == cur:
            return None, p
        cur = nxt


ROOT, ASKED = resolve_root(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
if ROOT is None:
    sys.exit("Không tìm thấy dự án AI-DLC nào từ '%s' (thiếu `.ai-dlc/context-memory/`).\n"
             "Không tạo gì cả — chạy `/dlc-init` trước, hoặc truyền đúng gốc dự án." % ASKED)
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8642
A = os.path.join(ROOT, ".ai-dlc")
INBOX = os.path.join(A, "inbox")
CM = os.path.join(A, "context-memory")
os.makedirs(INBOX, exist_ok=True)

VERDICTS = ("approve", "request-changes", "reject")

# Token BỀN qua restart (lưu file) — URL cũ/bookmark vẫn dùng được.
TOKEN_FILE = os.path.join(A, ".tower-token")
if os.path.isfile(TOKEN_FILE):
    TOKEN = open(TOKEN_FILE).read().strip()
else:
    TOKEN = secrets.token_urlsafe(12)
    with open(TOKEN_FILE, "w") as _f:
        _f.write(TOKEN)


GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tower_generate.py")
DATA_JS = os.path.join(A, "tower", "data.js")
_last_gen = [0.0]
REGEN_MIN_INTERVAL = 3.0     # giây — chặn regenerate dồn dập khi agent ghi liên tục


def newest_state_mtime():
    """mtime mới nhất trong .ai-dlc/ (trừ tower/) — rẻ, chỉ đi qua state chứ không qua code."""
    newest = 0.0
    for dirpath, dirnames, files in os.walk(A):
        dirnames[:] = [d for d in dirnames if d != "tower"]
        for f in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(dirpath, f)))
            except OSError:
                pass
    return newest


def regen_if_stale():
    """Tower là ảnh chụp; agent ghi file xong mà không ai sinh lại thì người giám sát
    nhìn vào số liệu cũ. Server tự sinh lại khi state mới hơn data.js."""
    now = time.time()
    if now - _last_gen[0] < REGEN_MIN_INTERVAL:
        return False
    try:
        data_mtime = os.path.getmtime(DATA_JS)
    except OSError:
        data_mtime = 0.0
    if newest_state_mtime() <= data_mtime:
        _last_gen[0] = now
        return False
    _last_gen[0] = now
    try:
        subprocess.run([sys.executable, GEN, ROOT], capture_output=True, timeout=60, check=False)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def read_data():
    try:
        s = open(DATA_JS, encoding="utf-8").read()
        return json.loads(s[s.index("{"):s.rindex(";")])
    except (OSError, ValueError):
        return {}


class H(BaseHTTPRequestHandler):
    def _token_ok(self):
        m = re.search(r"token=([\w~-]+)", self.path)
        if m and m.group(1) == TOKEN:
            return True
        # Chấp nhận cookie đã set từ lần mở URL-có-token đầu tiên
        cookie = self.headers.get("Cookie", "")
        return ("ct_token=%s" % TOKEN) in cookie

    MIME = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
            ".jsx": "text/babel; charset=utf-8", ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml"}

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _fail(self, code, msg):
        """Lỗi kèm body JSON UTF-8. KHÔNG dùng send_error: reason phrase encode
        latin-1 nên mọi ký tự tiếng Việt/em-dash làm đứt kết nối (client thấy 000)."""
        self._send(code, json.dumps({"ok": False, "error": msg}, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/doc":
            self._serve_doc(parse_qs(parsed.query).get("path", [""])[0])
            return
        if parsed.path == "/state":
            self._serve_state()
            return
        tower = os.path.join(A, "tower")
        rel = parsed.path.lstrip("/") or "index.html"
        target = os.path.realpath(os.path.join(tower, unquote(rel)))
        if not target.startswith(os.path.realpath(tower) + os.sep) and target != os.path.realpath(tower):
            self._fail(403, "Ngoài thư mục tower/")
            return
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if not os.path.isfile(target):
            self._fail(404, "Chưa có tower — chạy tower_generate.py trước")
            return
        body = open(target, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", self.MIME.get(os.path.splitext(target)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Mở bằng URL có token đúng → set cookie để các lần sau mở URL trần vẫn bấm nút được
        if self._token_ok():
            self.send_header("Set-Cookie", "ct_token=%s; Path=/; SameSite=Strict" % TOKEN)
        self.end_headers()
        self.wfile.write(body)

    def _serve_state(self):
        """Phần state hay đổi, cho UI poll. Tự sinh lại tower nếu .ai-dlc/ mới hơn data.js
        → không cần ai nhớ chạy /dlc-tower mỗi lần agent ghi file."""
        if not self._token_ok():
            self._fail(403, "Thiếu hoặc sai token")
            return
        regenerated = regen_if_stale()
        d = read_data()
        payload = {
            "generated": (d.get("project") or {}).get("generated", ""),
            "regenerated": regenerated,
            "stations": d.get("stations", []),
            "handoffs": d.get("handoffs", []),
            "activity": d.get("activity", []),
            "tasks": d.get("tasks", []),
            "feed": d.get("feed", [])[:12],
            "gateKeys": [g.get("key") for g in d.get("gates", [])],
            "intents": [{"id": i.get("id"), "stage": i.get("stage"), "gate": i.get("gate"),
                         "units": i.get("units"), "estimate": i.get("estimate")}
                        for i in d.get("intents", [])],
        }
        self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _serve_doc(self, rel):
        """Markdown tươi của một artifact trong .ai-dlc/ — chỉ đọc, chỉ trong context-memory."""
        if not self._token_ok():
            self._fail(403, "Thiếu hoặc sai token")
            return
        target = os.path.realpath(os.path.join(A, unquote(rel or "")))
        base = os.path.realpath(CM)
        if not target.startswith(base + os.sep) or not target.endswith(".md") or not os.path.isfile(target):
            self._fail(404, "Không tìm thấy tài liệu trong context-memory/")
            return
        payload = json.dumps({"path": rel, "markdown": open(target, encoding="utf-8", errors="replace").read(),
                              "mtime": int(os.path.getmtime(target))}, ensure_ascii=False).encode("utf-8")
        self._send(200, payload)

    def do_POST(self):
        if not self.path.startswith("/decision"):
            self._fail(404, "Endpoint không tồn tại")
            return
        if not self._token_ok():
            self._fail(403, "Thiếu hoặc sai token")
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n) or b"{}")
            verdict = data.get("verdict")
            if verdict not in VERDICTS:
                raise ValueError("verdict phải là một trong: " + ", ".join(VERDICTS))
            if not (data.get("intent") and data.get("gate")):
                raise ValueError("thiếu intent hoặc gate")
            if verdict in ("reject", "request-changes") and not (data.get("comment") or "").strip():
                raise ValueError("%s cần nói rõ cần sửa / từ chối vì cái gì" % verdict)
            if verdict == "approve" and data.get("previewed") is not True:
                raise ValueError("approve phải kèm previewed=true — đọc toàn văn tài liệu gate trước khi duyệt")
        except Exception as e:  # noqa: BLE001
            self._fail(400, str(e))
            return
        fname = "gate-{}-{}-{}-{}.json".format(
            re.sub(r"[^\w-]", "", data["intent"]), re.sub(r"[^\w-]", "", data["gate"]),
            verdict.replace("-", ""), int(time.time())
        )
        with open(os.path.join(INBOX, fname), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._send(200, b'{"ok":true}')

    def log_message(self, *a):  # yên lặng
        pass


if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", PORT), H)
    print(f"AI-DLC Tower: http://127.0.0.1:{PORT}/?token={TOKEN}", flush=True)
    print(f"Inbox: {INBOX}", flush=True)
    srv.serve_forever()
