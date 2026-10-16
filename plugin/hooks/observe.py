#!/usr/bin/env python3
"""observe.py — hook GHI LOG, không chặn (7.0.0-a). Nguồn dữ liệu máy ghi cho retro.

Tới 6.5.0 mọi thứ retro đọc (HOF, MSG, REV, SES) đều do agent tự viết. Hook này ghi dấu vết do máy thấy:
validator chạy ra sao, approvals.py được gọi khi nào, lệnh test đỏ hay xanh và lặp mấy lần, file nào trong
docs/intents/ bị sửa, mỗi lượt kết thúc lúc nào. `scripts/contracts_retro.py` đọc log này cùng approvals.json
và evidence.md để sinh ứng viên lesson learned.

Ghi gì và KHÔNG ghi gì:
- Chỉ ghi sự kiện có cấu trúc: loại · thời gian · change · stage/gate · kết quả. Không ghi nội dung file, không
  ghi toàn câu lệnh, không ghi stdout. Lệnh test chỉ giữ hai token đầu, bỏ mọi token có dấu `=` (biến môi
  trường, cờ mang giá trị). Đường dẫn file bí mật (.env, *.pem, *.key, key.json, tfstate…) ghi là «redacted».
- Lệnh shell không thuộc nhóm validate / approvals / start_change / test / git / gh thì không ghi gì.

Nơi ghi: engine `contracts` → `<root>/.ai-dlc/log/YYYY-MM.jsonl`; engine `ai-dlc` → `<state>/log/YYYY-MM.jsonl`.
Engine khác hoặc không dò ra → im lặng. Tắt khẩn: `AI_DLC_OBSERVE=off`.

Hook events nối trong hooks.json: SessionStart · PostToolUse (Bash|Write|Edit|MultiEdit) · Stop · SessionEnd.
Fail-open tuyệt đối: mọi lỗi ⇒ exit 0, không in gì ra stderr để khỏi làm ồn phiên.
"""
import datetime
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = re.compile(r"(^|/)(\.env(\..*)?|.*\.pem|.*\.key|id_rsa|id_ed25519|key\.json|.*\.tfvars|.*\.tfstate)$")
CHANGE = re.compile(r"docs/intents/(\d{4}-[a-z0-9][a-z0-9-]*)")
TEST_HEADS = {"pytest", "npm", "pnpm", "yarn", "bun", "node", "go", "cargo", "make", "vitest", "jest", "mocha",
              "phpunit", "dotnet", "mvn", "gradle", "rspec", "tox", "unittest"}
RE_FAIL = re.compile(r"\bFAILED\b|\bfailed\b|\bFAIL\b|Traceback|Error:|failures=\d|errors=\d|✗|\bnot ok\b")
RE_PASS = re.compile(r"\bpassed\b|^OK\b|\bOK\s*$|\bok\b|\bPASS(ED)?\b|\bsuccess", re.M)
RE_RESULT = re.compile(r"Result:\s*(\d+)\s*error.*?(\d+)\s*warning")


def layout(cwd):
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
        from layout import resolve  # noqa: WPS433
        return resolve(cwd)
    except Exception:  # noqa: BLE001
        return None


def log_dir(lay):
    if not lay:
        return None, None
    if lay["engine"] == "contracts":
        return os.path.join(lay["root"], ".ai-dlc", "log"), lay["root"]
    if lay["engine"] == "ai-dlc" and lay.get("state"):
        return os.path.join(lay["state"], "log"), lay["root"]
    return None, None


def rel(path, root):
    try:
        r = os.path.relpath(os.path.abspath(path), root)
    except ValueError:
        return path
    return path if r.startswith("..") else r


def text_of(resp):
    if isinstance(resp, dict):
        return "%s\n%s" % (resp.get("stdout") or "", resp.get("stderr") or "")
    return str(resp or "")


def outcome(txt):
    if RE_FAIL.search(txt):
        return "fail"
    if RE_PASS.search(txt):
        return "pass"
    return "unknown"


def clean_tokens(seg):
    try:
        toks = shlex.split(seg)
    except ValueError:
        toks = seg.split()
    toks = [t for t in toks if "=" not in t and not t.startswith(("http://", "https://"))]
    return toks


def bash_event(cmd, resp, root):
    txt = text_of(resp)
    change = (CHANGE.search(cmd) or [None, None])[1]
    if "validate_workflow.py" in cmd:
        m = RE_RESULT.search(txt)
        stage = (re.search(r"--stage\s+(\w+)", cmd) or [None, None])[1]
        return {"ev": "validate", "change": change, "stage": stage,
                "errors": int(m.group(1)) if m else None, "warnings": int(m.group(2)) if m else None}
    if "approvals.py" in cmd:
        return {"ev": "approve", "change": change,
                "gate": (re.search(r"--gate\s+(\w+)", cmd) or [None, None])[1],
                "decision": (re.search(r"--decision\s+([\w-]+)", cmd) or [None, None])[1],
                "ok": "Recorded" in txt}
    if "start_change.py" in cmd:
        return {"ev": "start", "change": change}
    for seg in re.split(r"&&|\|\||;|\|", cmd):
        toks = clean_tokens(seg)
        if not toks:
            continue
        head = os.path.basename(toks[0])
        if head == "git" and len(toks) > 1:
            return {"ev": "git", "sub": toks[1][:20], "change": change}
        if head == "gh" and len(toks) > 1:
            return {"ev": "gh", "sub": " ".join(toks[1:3])[:30], "change": change}
        if head in TEST_HEADS or (len(toks) > 1 and "test" in toks[1].lower()) or "test" in head.lower():
            if head == "git":
                continue
            return {"ev": "test", "head": " ".join(toks[:2])[:40], "outcome": outcome(txt), "change": change}
    return None


def build(data, root):
    kind = data.get("hook_event_name") or ("PostToolUse" if data.get("tool_name") else None)
    if kind == "SessionStart":
        return {"ev": "session_start", "source": str(data.get("source") or "")[:20]}
    if kind == "SessionEnd":
        return {"ev": "session_end", "reason": str(data.get("reason") or "")[:20]}
    if kind == "Stop":
        return {"ev": "stop"}
    if kind != "PostToolUse":
        return None
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    if tool == "Bash":
        return bash_event(str(ti.get("command") or ""), data.get("tool_response"), root)
    if tool in ("Write", "Edit", "MultiEdit"):
        fp = str(ti.get("file_path") or "")
        if not fp:
            return None
        r = rel(fp, root)
        if SECRET.search(r):
            r = "«redacted»"
        return {"ev": "write", "tool": tool, "path": r[:200], "change": (CHANGE.search(r) or [None, None])[1]}
    return None


def main():
    if os.environ.get("AI_DLC_OBSERVE", "").lower() == "off":
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    cwd = data.get("cwd") or os.getcwd()
    ldir, root = log_dir(layout(cwd))
    if not ldir:
        return 0
    ev = build(data, root)
    if not ev:
        return 0
    now = datetime.datetime.now().astimezone()
    ev = dict({"ts": now.isoformat(timespec="seconds"), "s": str(data.get("session_id") or "")[:8]}, **ev)
    try:
        os.makedirs(ldir, exist_ok=True)
        with open(os.path.join(ldir, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
