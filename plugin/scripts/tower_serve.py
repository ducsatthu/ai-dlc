#!/usr/bin/env python3
"""AI-DLC Tower server — serve tower UI + nhận Approve/Reject ghi vào .ai-dlc/inbox/.

Usage: python3 tower_serve.py [project_root] [port]
Bind 127.0.0.1 + token ngẫu nhiên (in URL lúc khởi động). POST không token → 403.
Quyết định ghi thành file JSON durable trong inbox/ — session Claude Code drain
qua Monitor (đang mở) hoặc SessionStart hook (phiên sau).
"""
import json
import os
import re
import secrets
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8642
A = os.path.join(ROOT, ".ai-dlc")
TOKEN = secrets.token_urlsafe(12)
INBOX = os.path.join(A, "inbox")
os.makedirs(INBOX, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def _token_ok(self):
        m = re.search(r"token=([\w~-]+)", self.path)
        return bool(m and m.group(1) == TOKEN)

    MIME = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
            ".jsx": "text/babel; charset=utf-8", ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml"}

    def do_GET(self):
        tower = os.path.join(A, "tower")
        rel = self.path.split("?")[0].lstrip("/") or "index.html"
        target = os.path.realpath(os.path.join(tower, rel))
        if not target.startswith(os.path.realpath(tower) + os.sep) and target != os.path.realpath(tower):
            self.send_error(403)
            return
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if not os.path.isfile(target):
            self.send_error(404, "Chua co tower - chay tower_generate.py truoc")
            return
        body = open(target, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", self.MIME.get(os.path.splitext(target)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if not self.path.startswith("/decision"):
            self.send_error(404)
            return
        if not self._token_ok():
            self.send_error(403, "Thieu hoac sai token")
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n) or b"{}")
            assert data.get("verdict") in ("approve", "reject")
            assert data.get("intent") and data.get("gate")
            if data["verdict"] == "reject" and not (data.get("comment") or "").strip():
                raise ValueError("reject can ly do")
        except Exception as e:  # noqa: BLE001
            self.send_error(400, str(e))
            return
        fname = "gate-{}-{}-{}.json".format(
            re.sub(r"[^\w-]", "", data["intent"]), re.sub(r"[^\w-]", "", data["gate"]), int(time.time())
        )
        with open(os.path.join(INBOX, fname), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *a):  # yên lặng
        pass


if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", PORT), H)
    print(f"AI-DLC Tower: http://127.0.0.1:{PORT}/?token={TOKEN}", flush=True)
    print(f"Inbox: {INBOX}", flush=True)
    srv.serve_forever()
