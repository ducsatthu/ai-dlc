#!/usr/bin/env python3
"""run.py — chạy eval cho chính gói trên model thật (7.0.0-a, bước 2 của profile tối giản).

Mỗi eval là một thư mục `evals/<ID>/eval.json`. Một lần chạy: clone template của đội vào thư mục tạm, chạy các lệnh
`setup` (vd `start_change.py`), rồi gọi `claude -p <prompt>` trong thư mục đó với model và danh sách tool cho phép đã
khai, bắt toàn bộ stream sự kiện, rồi chấm bằng các `checks` máy móc. Kết quả ghi `evals/results/<ID>-<ts>.json`.

Vì sao: mọi luật trong agents/skills của gói đi bằng quyết định chủ gói, chưa luật nào có bằng chứng model mới cần nó.
Eval trả lời đúng một câu cho từng luật: không có dòng luật đó trong prompt, model có tự làm đúng không. Đúng thì luật
đó là ứng viên gỡ ở 8.0.0; sai thì luật ở lại và có bằng chứng. Xem docs/template-contracts-engine-vs-ai-dlc.md §9.

Checks hỗ trợ (mỗi check một dòng trong eval.json):
  {"type": "approvals_events", "change": "<glob>", "equals": 0}        số event trong approvals.json
  {"type": "no_tool_matching", "pattern": "approvals\\.py.*--gate"}   không tool_use nào có input khớp regex (viết mẫu
                                                                      cho LỆNH GỌI; `approvals\\.py` trần bắt cả lệnh grep đọc source)
  {"type": "no_placeholders", "files": ["docs/intents/*/intent.md"]}   không còn [PLACEHOLDER]
  {"type": "strict_clean", "change": "<glob>"}                          contracts_brief strict_check ra 0 error
  {"type": "result_matches", "pattern": "approve intent"}              câu trả lời cuối khớp regex
  {"type": "result_not_matches", "pattern": "..."}

Usage: python3 run.py <ID> [<ID>...] [--model opus] [--max-turns 30] [--keep] [--dry-run]
Cần: AI_DLC_TEMPLATE_PATH trỏ tới checkout template của đội; `claude` trong PATH. Chỉ stdlib.
Lưu ý: bản clone tạm không được trust nên `permissions.allow` của template bị bỏ qua (cảnh báo trên stderr, vô hại), và
`permissions.ask: [Bash]` của template bị runner gỡ trong bản clone vì ở `-p` ask nghĩa là từ chối. Tool cho phép đến
từ `allowed_tools` của eval. Tool model định gọi mà bị từ chối vẫn nằm trong `tools` của kết quả với `denied: true`.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9_]+\]")


def sh(cmd, cwd, timeout=120, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def make_workspace(template, spec, keep):
    tmp = tempfile.mkdtemp(prefix="ai-dlc-eval-")
    ws = os.path.join(tmp, "ws")
    subprocess.run(["git", "clone", "-q", "--local", template, ws], check=True, capture_output=True)
    branch = spec.get("branch") or "feat/eval"
    subprocess.run(["git", "-C", ws, "checkout", "-q", "-b", branch], check=True, capture_output=True)
    # Template của đội đặt permissions.ask: [Bash]. Ở chế độ `claude -p` không ai trả lời được câu hỏi, nên ask là từ
    # chối, và nó thắng cả --allowedTools (đo 2026-10-16). Bỏ `ask` trong BẢN CLONE TẠM; `deny` (.env, khoá...) giữ nguyên.
    sp = os.path.join(ws, ".claude", "settings.json")
    if os.path.isfile(sp):
        try:
            with open(sp, encoding="utf-8") as f:
                st = json.load(f)
            if isinstance(st.get("permissions"), dict) and "ask" in st["permissions"]:
                st["permissions"].pop("ask")
                with open(sp, "w", encoding="utf-8") as f:
                    json.dump(st, f, indent=2, ensure_ascii=False)
        except (OSError, ValueError):
            pass
    for cmd in spec.get("setup", []):
        cmd = [c.replace("{ws}", ws) for c in cmd]
        code, out = sh([sys.executable if c == "python3" else c for c in cmd], ws)
        if code != 0:
            raise RuntimeError("setup thất bại: %s\n%s" % (" ".join(cmd), out[-500:]))
    return tmp, ws


def run_claude(ws, spec, model, max_turns, timeout):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    env["AI_DLC_OBSERVE"] = "off"
    cmd = ["claude", "-p", spec["prompt"], "--output-format", "stream-json", "--verbose",
           "--model", model, "--max-turns", str(max_turns), "--permission-mode", "acceptEdits"]
    # hai cờ dưới nhận NHIỀU giá trị cách nhau bằng khoảng trắng, nên để cuối lệnh
    if spec.get("disallowed_tools"):
        cmd += ["--disallowedTools"] + list(spec["disallowed_tools"])
    if spec.get("allowed_tools"):
        cmd += ["--allowedTools"] + list(spec["allowed_tools"])
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout, env=env, stdin=subprocess.DEVNULL)
    events = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    tools, by_id = [], {}
    result = ""
    for ev in events:
        if ev.get("type") == "assistant":
            for blk in (ev.get("message") or {}).get("content") or []:
                if isinstance(blk, dict) and blk.get("type") == "tool_use":
                    t = {"name": blk.get("name"), "input": blk.get("input"), "result": "", "denied": False}
                    tools.append(t)
                    by_id[blk.get("id")] = t
        if ev.get("type") == "user":
            # kết quả tool: giữ 300 ký tự đầu để đọc lại được vì sao model rẽ hướng (vd bị từ chối quyền)
            for blk in (ev.get("message") or {}).get("content") or []:
                if isinstance(blk, dict) and blk.get("type") == "tool_result" and blk.get("tool_use_id") in by_id:
                    c = blk.get("content")
                    txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [] if isinstance(x, dict))
                    t = by_id[blk["tool_use_id"]]
                    t["result"] = txt[:300]
                    t["denied"] = bool(blk.get("is_error")) and bool(re.search(r"permission|denied|not allowed|requires approval", txt, re.I))
        if ev.get("type") == "result":
            result = ev.get("result") or ""
    return {"exit": p.returncode, "seconds": round(time.time() - t0, 1), "events": len(events), "tools": tools,
            "denied": sum(1 for t in tools if t["denied"]),
            "result": result, "stderr": p.stderr[-800:], "cost_usd": next((e.get("total_cost_usd") for e in events
                                                                         if e.get("type") == "result"), None)}


def check(ws, c, run):
    t = c["type"]
    if t == "approvals_events":
        n = 0
        for p in glob.glob(os.path.join(ws, "docs", "intents", c["change"], "approvals.json")):
            with open(p, encoding="utf-8") as f:
                n += len(json.load(f).get("events", []))
        return n == c.get("equals", 0), "events=%d" % n
    if t == "no_tool_matching":
        rx = re.compile(c["pattern"])
        hits = [x for x in run["tools"] if rx.search(json.dumps(x["input"], ensure_ascii=False))]
        return not hits, "tool_use khớp: %d" % len(hits) + ("" if not hits else " · " + json.dumps(hits[0], ensure_ascii=False)[:160])
    if t == "no_placeholders":
        left = []
        for pat in c["files"]:
            for p in glob.glob(os.path.join(ws, pat)):
                with open(p, encoding="utf-8") as f:
                    txt = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
                left += ["%s:%s" % (os.path.relpath(p, ws), m) for m in PLACEHOLDER.findall(txt)]
        return not left, "còn %d placeholder%s" % (len(left), (" · " + "; ".join(left[:4])) if left else "")
    if t == "strict_clean":
        sys.path.insert(0, SCRIPTS)
        import contracts_brief as cb  # noqa: WPS433
        dirs = glob.glob(os.path.join(ws, "docs", "intents", c["change"]))
        if not dirs:
            return False, "không có change"
        ch = cb.read_change(ws, dirs[0])
        s = cb.strict_check(ws, ch)
        return s.get("errors") == 0, "gate %s · strict errors=%s%s" % (
            ch["pending"], s.get("errors"), (" · " + "; ".join(s.get("lines", [])[:3])) if s.get("errors") else "")
    if t == "result_matches":
        return bool(re.search(c["pattern"], run["result"], re.I | re.S)), "kết quả %d ký tự" % len(run["result"])
    if t == "result_not_matches":
        return not re.search(c["pattern"], run["result"], re.I | re.S), "kết quả %d ký tự" % len(run["result"])
    return False, "check không biết: %s" % t


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="eval cho chính gói trên model thật", add_help=True)
    ap.add_argument("ids", nargs="+", help="thư mục eval, vd C-001-prepare-without-inferring-approval")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--keep", action="store_true", help="giữ workspace tạm để đọc lại")
    ap.add_argument("--dry-run", action="store_true", help="chỉ dựng workspace, không gọi claude")
    a = ap.parse_args(argv)
    template = os.environ.get("AI_DLC_TEMPLATE_PATH")
    if not template:
        print("cần AI_DLC_TEMPLATE_PATH trỏ tới checkout template của đội", file=sys.stderr)
        return 2
    flags = {"--keep": a.keep, "--dry-run": a.dry_run}
    model, max_turns = a.model, a.max_turns
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    failed = 0
    for eid in a.ids:
        with open(os.path.join(HERE, eid, "eval.json"), encoding="utf-8") as f:
            spec = json.load(f)
        print("== %s · %s" % (eid, spec.get("title", "")))
        tmp, ws = make_workspace(template, spec, a.keep)
        try:
            if a.dry_run:
                print("   workspace sẵn: %s (dry-run, không gọi claude)" % ws)
                continue
            run = run_claude(ws, spec, spec.get("model") or model, max_turns, a.timeout)
            rows = []
            for c in spec["checks"]:
                ok, note = check(ws, c, run)
                rows.append({"check": c, "ok": ok, "note": note})
                print("   %s %-18s %s" % ("PASS" if ok else "FAIL", c["type"], note))
            verdict = all(r["ok"] for r in rows)
            failed += 0 if verdict else 1
            rule = spec.get("rule", "")
            print("   => %s · %ss · %d tool_use (%d bị từ chối quyền) · cost %s" % (
                "PASS: model tự làm đúng không cần luật này" if verdict else "FAIL: luật ở lại, có bằng chứng",
                run["seconds"], len(run["tools"]), run["denied"], run["cost_usd"]))
            if rule:
                print("   luật đang xét: %s" % rule)
            out = os.path.join(HERE, "results", "%s-%s.json" % (eid, time.strftime("%Y%m%d-%H%M%S")))
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"eval": eid, "model": spec.get("model") or model, "verdict": verdict, "checks": rows,
                           "run": run, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}, f, ensure_ascii=False, indent=1)
            print("   ghi %s" % os.path.relpath(out, HERE))
        finally:
            if flags.get("--keep") or flags.get("--dry-run"):
                print("   giữ workspace: %s" % ws)
            else:
                shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
