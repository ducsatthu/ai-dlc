#!/usr/bin/env python3
"""contracts_brief.py — brief + doctor của gói cho engine `contracts` (7.0.0-a, CHỈ ĐỌC).

Engine `contracts` = workflow của template đội (`project-starter-template-ai`): skill `.agents/skills/aidlc/`,
mỗi change là `docs/intents/NNNN-name/` với đúng bốn file — `intent.md` · `plan.md` · `approvals.json` (sổ duyệt
băm SHA-256, append-only) · `evidence.md`. Gate: feature/infra `intent → plan → outcome`; bugfix/refactor
`contract → outcome`. Luật của đội: *never infer approval* — gói KHÔNG bao giờ gọi `approvals.py` thay người.

Script này đọc bốn file + `git` + chạy `validate_workflow.py` của đội ở đúng stage, rồi in một bản brief
ngắn (hoặc `--json` cho tower/test). `--doctor` thêm các kiểm tra máy móc của gói (chưa có luật mới — mọi
phát hiện đi từ chính luật của template; xem docs/template-contracts-engine-vs-ai-dlc.md §5.1).

Usage: python3 contracts_brief.py [root] [--json] [--short] [--doctor] [--no-validate]
Exit: 0 · `--doctor` có FIX ⇒ 1 · không phải workspace contracts ⇒ 2. Chỉ stdlib. Fail-open ở mọi bước phụ.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR_REL = os.path.join(".agents", "skills", "aidlc", "scripts", "validate_workflow.py")
GATES = {"feature": ["intent", "plan", "outcome"], "infra": ["intent", "plan", "outcome"],
         "bugfix": ["contract", "outcome"], "refactor": ["contract", "outcome"]}
BIND = {"intent": ["intent.md"], "plan": ["intent.md", "plan.md"], "contract": ["intent.md", "plan.md"],
        "outcome": ["intent.md", "plan.md", "evidence.md"]}
FOUR = ("intent.md", "plan.md", "approvals.json", "evidence.md")
AUDIT = FOUR + (".backlog-sync.json",)
SAY = {"intent": "approve intent", "plan": "approve plan", "contract": "approve intent (Intent + Plan một lần)",
       "outcome": "approve outcome", "merge": "người review approve + merge PR trên platform"}
CHANGE_DIR = re.compile(r"^\d{4}-[a-z0-9][a-z0-9-]*$")
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9_]+\]")
SHA = re.compile(r"^(?:[\w./-]+@)?[0-9a-f]{40}$")


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def sha256(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def strip_comments(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def meta(t, key):
    m = re.search(r"^-\s*\*\*%s\*\*:\s*(.+?)\s*$" % re.escape(key), t, re.M)
    return m.group(1).strip() if m else ""


def section(t, title):
    m = re.search(r"^##\s+%s\s*$\n(.*?)(?=^##\s|\Z)" % re.escape(title), t, re.S | re.M)
    return m.group(1).strip() if m else ""


def table_rows(body):
    """Dòng bảng markdown trừ header + dòng gạch; mỗi dòng là list ô đã strip."""
    rows = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c) and cells:
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def is_none(body):
    b = strip_comments(body).strip()
    return (not b) or bool(re.fullmatch(r"(none|không|—|-|n/a)\.?", b, re.I)) or bool(PLACEHOLDER.fullmatch(b))


def git(root, *args):
    try:
        p = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def is_contracts_root(d):
    return all(os.path.isfile(os.path.join(d, *p)) for p in (
        (".agents", "skills", "aidlc", "SKILL.md"), ("docs", "memory", "project.md"),
        ("docs", "intents", "_templates", "intent.md")))


def find_root(start):
    try:
        sys.path.insert(0, HERE)
        from layout import resolve  # noqa: WPS433
        lay = resolve(start)
        if lay["engine"] == "contracts":
            return lay["root"]
    except Exception:  # noqa: BLE001 — fail-open, dò tay bên dưới
        pass
    cur = os.path.abspath(start)
    for _ in range(7):
        if is_contracts_root(cur):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return None


# ---------- một change ----------

def approvals_state(cdir, gates):
    """Mỗi gate: current (approve + mọi hash khớp) · stale (approve nhưng byte đã đổi) · revision (request-changes
    sau cùng) · none. Băm theo đúng cách của approvals.py: toàn bộ byte file."""
    p = os.path.join(cdir, "approvals.json")
    out = {g: {"state": "none", "by": None, "at": None, "stale_files": []} for g in gates}
    if not os.path.isfile(p):
        return out, "missing"
    try:
        events = json.loads(read(p)).get("events", [])
    except (ValueError, AttributeError):
        return out, "unreadable"
    now = {f: sha256(os.path.join(cdir, f)) for f in ("intent.md", "plan.md", "evidence.md")}
    for ev in events:
        g = ev.get("gate")
        if g not in out:
            continue
        rec = out[g]
        rec["by"], rec["at"] = ev.get("by"), ev.get("at")
        if ev.get("decision") != "approve":
            rec.update(state="revision", stale_files=[])
            continue
        files = ev.get("files") or {f: None for f in BIND[g]}
        stale = [f for f, h in files.items() if now.get(f) != h]
        rec.update(state="stale" if stale else "current", stale_files=stale)
    return out, "ok"


def parse_units(plan):
    units = []
    for line in section(plan, "Order of work").splitlines():
        m = re.match(r"^\s*\d+\.\s+(U-\d+)\s*[—-]+\s*(.*)$", line)
        if not m:
            continue
        rest = m.group(2)
        units.append({
            "id": m.group(1), "text": re.sub(r"\s*\[[^\]]*\]", "", rest).strip()[:80],
            "ac": re.findall(r"AC-\d+", rest), "gate": "[gate]" in rest, "knowledge": "[knowledge]" in rest,
            "owner": (re.search(r"\[owner:\s*([^\]]+)\]", rest) or [None, None])[1],
            "repo": (re.search(r"\[repo:\s*([^\]]+)\]", rest) or [None, None])[1],
        })
    return units


def unit_results(evidence):
    """Dòng CUỐI mỗi unit trong bảng Work Units là hiện hành (luật của template)."""
    last = {}
    for cells in table_rows(section(evidence, "Work Units")):
        if len(cells) >= 3 and re.match(r"U-\d+", cells[0]):
            last[cells[0]] = {"result": cells[2], "commit": cells[4] if len(cells) > 4 else ""}
    return last


def read_change(root, cdir):
    name = os.path.basename(cdir)
    intent = strip_comments(read(os.path.join(cdir, "intent.md")))
    plan = strip_comments(read(os.path.join(cdir, "plan.md")))
    evidence = strip_comments(read(os.path.join(cdir, "evidence.md")))
    scope = (meta(intent, "Scope") or "feature").lower()
    gates = GATES.get(scope, GATES["feature"])
    appr, appr_status = approvals_state(cdir, gates)
    pending = next((g for g in gates if appr[g]["state"] != "current"), None)
    outcome = section(evidence, "Outcome")
    impl = meta(outcome, "Implementation commit")
    has_impl = bool(impl) and all(SHA.match(x.strip()) for x in impl.split(","))
    if pending in ("intent", "plan", "contract"):
        stage = "draft"
    elif pending == "outcome":
        stage = "outcome" if has_impl else "execute"
    else:
        stage = "merge"
    units = parse_units(plan)
    results = unit_results(evidence)
    ac_ids = [c[0] for c in table_rows(section(intent, "Success criteria")) if c and re.match(r"AC-\d+", c[0])]
    ac_done = [c[0] for c in table_rows(section(evidence, "Acceptance evidence"))
               if c and re.match(r"AC-\d+", c[0]) and len(c) > 1 and c[1].lower().startswith("pass")]
    branch = meta(plan, "Branch")
    files_listed = re.findall(r"`([^`]+)`", section(plan, "Files that change"))
    extra = sorted(f for f in os.listdir(cdir) if f not in AUDIT and not f.startswith("."))
    missing = [f for f in FOUR if not os.path.isfile(os.path.join(cdir, f))]
    rel = os.path.relpath(cdir, root)
    return {
        "id": name, "dir": rel, "title": (re.search(r"^#\s*Intent:\s*(.+)$", intent, re.M) or [None, name])[1].strip(),
        "scope": scope, "owner": meta(intent, "Owner"), "repos": meta(intent, "Implementation repository") or ".",
        "backlog": meta(intent, "Backlog") or "none", "security": meta(intent, "Security triggers") or "none",
        "branch": branch, "gates": gates, "approvals": appr, "approvals_file": appr_status,
        "pending": pending, "say": SAY.get(pending or "merge"), "stage": stage,
        "units": units, "unit_results": results,
        "units_pass": sum(1 for u in units if results.get(u["id"], {}).get("result", "").lower().startswith("pass")),
        "units_fail": [u["id"] for u in units if results.get(u["id"], {}).get("result", "").lower().startswith("fail")],
        "ac": ac_ids, "ac_pass": ac_done,
        "open_questions": not is_none(section(intent, "Open questions")),
        "knowledge_impact": any(("docs/" in r[0] or "CHANGELOG" in r[0]) and not PLACEHOLDER.search(r[0])
                                for r in table_rows(section(intent, "Knowledge impact")) if r),
        "has_knowledge_unit": any(u["knowledge"] for u in units),
        "files_listed": files_listed, "extra_files": extra,
        "extra_unlisted": [f for f in extra if not any(x.endswith(rel + "/" + f) or x == rel + "/" + f for x in files_listed)],
        "missing_files": missing, "placeholders": bool(PLACEHOLDER.search(intent + plan)),
        "validator": None,
    }


def run_validator(root, ch):
    v = os.path.join(root, VALIDATOR_REL)
    if not os.path.isfile(v):
        return {"available": False}
    try:
        p = subprocess.run([sys.executable, v, ch["dir"], "--stage", ch["stage"]], cwd=root,
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return {"available": True, "error": str(e)[:120]}
    out = (p.stdout + "\n" + p.stderr).strip().splitlines()
    m = next((re.search(r"Result:\s*(\d+)\s*error.*?(\d+)\s*warning", l) for l in reversed(out)
              if "Result:" in l), None)
    return {"available": True, "stage": ch["stage"], "exit": p.returncode,
            "errors": int(m.group(1)) if m else None, "warnings": int(m.group(2)) if m else None,
            "lines": [l for l in out if l.startswith(("ERROR", "WARNING"))][:8]}


def git_state(root, ch):
    cur = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    br = ch["branch"]
    exists = bool(br) and not PLACEHOLDER.search(br) and \
        git(root, "rev-parse", "--verify", "--quiet", "refs/heads/" + br) is not None
    dirty = git(root, "status", "--porcelain", "--", ch["dir"])
    return {"current_branch": cur, "change_branch_exists": exists, "dir_dirty": bool(dirty), "available": cur is not None}


# ---------- doctor (máy móc, không luật mới) ----------

def doctor(root, changes):
    f = []
    if os.path.isdir(os.path.join(root, ".ai-dlc", "context-memory")):
        f.append(("FIX", "D01", ".ai-dlc/context-memory/ nằm cạnh docs/intents/: hai nguồn sự thật. Engine của đội là "
                                "docs/intents/. Xoá .ai-dlc cũ hoặc đặt `engine: off`. Không chạy /ai-dlc:dlc-init ở đây."))
    if not os.path.isfile(os.path.join(root, VALIDATOR_REL)):
        f.append(("WARN", "D02", "không thấy %s, gói không kiểm được contract bằng validator của đội" % VALIDATOR_REL))
    idir = os.path.join(root, "docs", "intents")
    for n in sorted(os.listdir(idir)) if os.path.isdir(idir) else []:
        p = os.path.join(idir, n)
        if os.path.isdir(p) and not CHANGE_DIR.match(n) and n not in ("_templates", "ideation") and not n.startswith("."):
            f.append(("WARN", "D03", "docs/intents/%s/ không theo mẫu NNNN-ten, validator và tower không nhận là change" % n))
    for ch in changes:
        tag = ch["id"]
        if ch["missing_files"]:
            f.append(("FIX", "D10", "%s thiếu %s. Một change là đúng bốn file" % (tag, ", ".join(ch["missing_files"]))))
        if ch["approvals_file"] == "unreadable":
            f.append(("FIX", "D11", "%s approvals.json không đọc được (JSON hỏng)" % tag))
        for g, rec in ch["approvals"].items():
            if rec["state"] == "stale":
                f.append(("FIX", "D12", "%s gate `%s` đã approve bởi %s nhưng %s đổi byte sau đó. Duyệt đã mất hiệu lực; "
                                        "cần `%s` lại (gói không tự ghi)" % (tag, g, rec["by"], ", ".join(rec["stale_files"]), SAY[g])))
            elif rec["state"] == "revision":
                f.append(("WARN", "D13", "%s gate `%s` đang ở request-changes (%s). Sửa contract rồi xin duyệt lại" % (tag, g, rec["by"])))
        if ch["pending"] == "outcome" and ch["units_fail"]:
            f.append(("WARN", "D14", "%s unit %s dòng cuối Fail, chưa đủ điều kiện review outcome" % (tag, ", ".join(ch["units_fail"]))))
        if ch["knowledge_impact"] and not ch["has_knowledge_unit"]:
            f.append(("WARN", "D15", "%s khai Knowledge impact nhưng plan không có unit [knowledge] cuối" % tag))
        if ch["extra_unlisted"]:
            f.append(("INFO", "D16", "%s có file ngoài bốn file: %s. Validator chỉ kiểm drift ở outcome và merge, nên commit "
                                     "trước implementation commit hoặc khai vào Files that change" % (tag, ", ".join(ch["extra_unlisted"]))))
        v = ch.get("validator") or {}
        if v.get("available") and v.get("errors"):
            f.append(("FIX", "D20", "%s validate_workflow --stage %s: %d error. %s" % (
                tag, v["stage"], v["errors"], "; ".join(v.get("lines", [])[:3]) or "xem output")))
        g = ch.get("git") or {}
        if g.get("available") and ch["pending"] in ("outcome", None) and not g["change_branch_exists"]:
            f.append(("WARN", "D21", "%s plan Branch `%s` không tồn tại trong repo này" % (tag, ch["branch"] or "?")))
    return f


# ---------- in ----------

def brief_lines(root, changes, short=False):
    L = ["AI-DLC · engine contracts (template đội) · %s" % os.path.basename(root)]
    if not changes:
        L.append("  chưa có change nào trong docs/intents/. Bắt đầu bằng `/aidlc` (skill của đội): start <outcome>")
        return L
    L.append("")
    L.append("CHANGES (docs/intents/)")
    for ch in changes:
        appr = " ".join(("%s:%s" % (g, {"current": "✓", "stale": "✗cũ", "revision": "↺", "none": "·"}[ch["approvals"][g]["state"]]))
                        for g in ch["gates"])
        L.append("  %s · %s · %s · %s" % (ch["id"], ch["scope"], appr,
                                         ("chờ `%s`" % ch["say"]) if ch["pending"] else "đủ duyệt, chờ merge PR"))
        if short:
            continue
        L.append("     %s" % ch["title"][:90])
        L.append("     owner %s · repo %s · branch %s · backlog %s · security %s" % (
            ch["owner"] or "?", ch["repos"], ch["branch"] or "?", ch["backlog"], ch["security"]))
        if ch["units"]:
            L.append("     units %d (pass %d%s) · AC %d (pass %d)%s" % (
                len(ch["units"]), ch["units_pass"], (", fail " + ",".join(ch["units_fail"])) if ch["units_fail"] else "",
                len(ch["ac"]), len(ch["ac_pass"]), " · Knowledge impact → unit [knowledge]" if ch["knowledge_impact"] else ""))
        v = ch.get("validator") or {}
        if v.get("available") is False:
            L.append("     validator: không có trong workspace")
        elif v.get("errors") is not None:
            L.append("     validate --stage %s: %d error · %d warning%s" % (
                v["stage"], v["errors"], v["warnings"], (" — " + v["lines"][0][:70]) if v["lines"] and v["errors"] else ""))
        if ch["open_questions"]:
            L.append("     ! Open questions chưa là None. Người phải trả lời trước khi duyệt Intent")
    need = [ch for ch in changes if ch["pending"]]
    L.append("")
    L.append("CẦN NGƯỜI (gói không ghi thay; luật đội: never infer approval)")
    if not need:
        L.append("  không gate nào chờ")
    for ch in need:
        v = ch.get("validator") or {}
        ok = v.get("errors") == 0
        L.append("  %s → nói `%s` trong chat; agent ghi bằng approvals.py --by <tên bạn>%s" % (
            ch["id"], ch["say"], "" if ok else (". Validator chưa sạch, duyệt sẽ bị từ chối" if v.get("errors") else ". Chưa kiểm validator")))
    if not short:
        L.append("")
        L.append("Gói ai-dlc chỉ đọc ở engine này. Lifecycle theo AGENTS.md và docs/intents/README.md của đội. Doctor: --doctor.")
    return L


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    root = find_root(args[0] if args else os.getcwd())
    if not root:
        print("Không phải workspace engine `contracts` (cần .agents/skills/aidlc/SKILL.md + docs/memory/project.md + "
              "docs/intents/_templates/intent.md). Kiểm: python3 %s/layout.py --explain" % HERE, file=sys.stderr)
        return 2
    idir = os.path.join(root, "docs", "intents")
    changes = [read_change(root, os.path.join(idir, n)) for n in sorted(os.listdir(idir))
               if CHANGE_DIR.match(n) and os.path.isdir(os.path.join(idir, n))] if os.path.isdir(idir) else []
    for ch in changes:
        ch["git"] = git_state(root, ch)
        if "--no-validate" not in flags:
            ch["validator"] = run_validator(root, ch)
    findings = doctor(root, changes) if "--doctor" in flags else []
    if "--json" in flags:
        print(json.dumps({"engine": "contracts", "root": root, "changes": changes,
                          "doctor": [{"level": l, "code": c, "msg": m} for l, c, m in findings]},
                         ensure_ascii=False, indent=1, default=str))
    else:
        print("\n".join(brief_lines(root, changes, short="--short" in flags)))
        if "--doctor" in flags:
            print("\nDOCTOR (máy móc, theo luật của chính template, không có luật mới)")
            if not findings:
                print("  OK, không phát hiện gì")
            for l, c, m in findings:
                print("  %-4s %s %s" % (l, c, m))
    return 1 if any(l == "FIX" for l, _, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
