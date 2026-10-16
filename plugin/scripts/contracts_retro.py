#!/usr/bin/env python3
"""contracts_retro.py — sinh ỨNG VIÊN lesson learned cho engine `contracts` từ dấu vết máy ghi (7.0.0-a).

Nguồn, theo thứ tự tin cậy: `docs/intents/*/approvals.json` (sổ duyệt của đội) · `docs/intents/*/evidence.md`
(dòng Fail) · `.ai-dlc/log/*.jsonl` (hook `observe.py`: validator, lệnh test, approvals.py, file sửa, lượt).
Không đọc transcript, không đọc nội dung file làm việc.

Một ứng viên = một mẫu lặp lại có mã, có bằng chứng trỏ được. Script này chỉ gom và đếm; viết LL và quyết
sửa luật vẫn là người (retro-keeper soạn, người ký). Luật của gói: "sai hai lần → ứng viên" (playbook #5).

Mã:
  R01 cùng một gate bị request-changes ≥2 lần trong một change
  R02 cùng một lệnh test đỏ liên tiếp ≥ max_self_fix lần trong một phiên (tự sửa lặp)
  R03 validator báo error ở stage execute/outcome/merge ≥2 lần cho một change
  R04 một unit có ≥2 dòng Fail trong evidence.md
  R05 gate chờ người quá lâu: validator sạch rồi mới approve sau > wait_hours (mặc định 24)
  X01 cùng một mã R0x nổ ở ≥2 change khác nhau (lặp giữa các change: ứng viên mạnh nhất)

Usage: python3 contracts_retro.py [root] [--since YYYY-MM-DD] [--max-self-fix N] [--wait-hours H] [--json] [--write]
  --write ghi `<governance>/lessons-learned/candidates.md` (file sinh ra, không sửa tay). Mặc định chỉ in.
Exit 0. Không phải workspace contracts ⇒ 2. Chỉ stdlib.
"""
import datetime
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from contracts_brief import CHANGE_DIR, find_root, read, section, strip_comments, table_rows  # noqa: E402

DESCRIBE = {
    "R01": "gate bị trả lại nhiều vòng",
    "R02": "tự sửa lặp trên cùng một lệnh test",
    "R03": "validator báo error lặp ở stage sau khi đã duyệt",
    "R04": "unit Fail nhiều lần trong evidence",
    "R05": "gate chờ người lâu sau khi validator đã sạch",
    "X01": "cùng mẫu lỗi ở nhiều change",
}


def arg(flags, name, default):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def parse_ts(s):
    try:
        t = datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def load_log(root, since):
    events = []
    for p in sorted(glob.glob(os.path.join(root, ".ai-dlc", "log", "*.jsonl"))):
        for line in read(p).splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t = parse_ts(e.get("ts"))
            if t is None or (since and t < since):
                continue
            e["_t"] = t
            events.append(e)
    return sorted(events, key=lambda e: e["_t"])


def changes_of(root):
    idir = os.path.join(root, "docs", "intents")
    return sorted(n for n in os.listdir(idir) if CHANGE_DIR.match(n) and os.path.isdir(os.path.join(idir, n))) \
        if os.path.isdir(idir) else []


def approvals(root, ch):
    try:
        return json.loads(read(os.path.join(root, "docs", "intents", ch, "approvals.json"))).get("events", [])
    except (ValueError, AttributeError):
        return []


def evidence_fails(root, ch):
    ev = strip_comments(read(os.path.join(root, "docs", "intents", ch, "evidence.md")))
    fails = {}
    for cells in table_rows(section(ev, "Work Units")):
        if len(cells) >= 3 and re.match(r"U-\d+", cells[0]) and cells[2].lower().startswith("fail"):
            fails[cells[0]] = fails.get(cells[0], 0) + 1
    return fails


def analyze(root, events, max_self_fix, wait_hours):
    cands = []
    per_change = {}

    def add(code, change, msg, evidence, level="WARN"):
        cands.append({"code": code, "level": level, "change": change, "msg": msg, "evidence": evidence})
        per_change.setdefault(change, set()).add(code)

    chs = changes_of(root)
    for ch in chs:
        # R01 · R05 từ approvals.json (nguồn tin cậy nhất)
        rc = {}
        for e in approvals(root, ch):
            if e.get("decision") == "request-changes":
                rc.setdefault(e.get("gate"), []).append(e.get("at"))
        for gate, ats in rc.items():
            if len(ats) >= 2:
                add("R01", ch, "gate `%s` bị request-changes %d lần" % (gate, len(ats)), ats)
        for e in approvals(root, ch):
            if e.get("decision") != "approve":
                continue
            t_ok = parse_ts(e.get("at"))
            clean = [v for v in events if v.get("ev") == "validate" and v.get("change") == ch
                     and v.get("errors") == 0 and t_ok and v["_t"] <= t_ok]
            if clean and t_ok:
                hours = (t_ok - clean[-1]["_t"]).total_seconds() / 3600
                if hours > wait_hours:
                    add("R05", ch, "gate `%s` approve sau %.0fh kể từ lần validator sạch cuối" % (e.get("gate"), hours),
                        [clean[-1]["ts"], e.get("at")], level="INFO")
        # R03 từ log validate
        bad = [v for v in events if v.get("ev") == "validate" and v.get("change") == ch
               and (v.get("errors") or 0) > 0 and v.get("stage") in ("execute", "outcome", "merge")]
        if len(bad) >= 2:
            add("R03", ch, "validator báo error %d lần ở stage %s" % (len(bad), "/".join(sorted({b["stage"] for b in bad}))),
                [b["ts"] for b in bad])
        # R04 từ evidence.md
        for unit, n in evidence_fails(root, ch).items():
            if n >= 2:
                add("R04", ch, "%s có %d dòng Fail trong evidence.md" % (unit, n), [unit])
    # R02 từ log test: chuỗi đỏ liên tiếp cùng head trong một phiên
    by_session = {}
    for v in events:
        if v.get("ev") == "test":
            by_session.setdefault(v.get("s"), []).append(v)
    for s, tests in by_session.items():
        streak, head, change, first = 0, None, None, None
        for v in tests + [{"ev": "test", "head": None, "outcome": "pass"}]:
            if v.get("outcome") == "fail" and v.get("head") == head:
                streak += 1
            else:
                if head and streak >= max_self_fix:
                    add("R02", change or "—", "`%s` đỏ %d lần liên tiếp (phiên %s)" % (head, streak, s), [first])
                head, change, first = v.get("head"), v.get("change"), v.get("ts")
                streak = 1 if v.get("outcome") == "fail" else 0
    # X01 lặp giữa các change
    code_changes = {}
    for ch, codes in per_change.items():
        for c in codes:
            code_changes.setdefault(c, set()).add(ch)
    for c, chset in sorted(code_changes.items()):
        if len(chset) >= 2:
            cands.insert(0, {"code": "X01", "level": "FIX", "change": "*", "evidence": sorted(chset),
                             "msg": "%s (%s) nổ ở %d change: %s. Ứng viên LL mạnh" % (c, DESCRIBE[c], len(chset), ", ".join(sorted(chset)))})
    stats = {
        "changes": len(chs), "events": len(events),
        "sessions": len({v.get("s") for v in events if v.get("s")}),
        "turns": sum(1 for v in events if v.get("ev") == "stop"),
        "validate_runs": sum(1 for v in events if v.get("ev") == "validate"),
        "validate_clean": sum(1 for v in events if v.get("ev") == "validate" and v.get("errors") == 0),
        "tests": sum(1 for v in events if v.get("ev") == "test"),
        "tests_fail": sum(1 for v in events if v.get("ev") == "test" and v.get("outcome") == "fail"),
        "approve_calls": sum(1 for v in events if v.get("ev") == "approve"),
    }
    return cands, stats


def render(root, cands, stats, since, max_self_fix):
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    L = ["---", "type: retro-candidates", "generated_by: contracts_retro.py", "generated_at: %s" % now,
         "window_since: %s" % (since.date().isoformat() if since else "all"),
         "sources: docs/intents/*/approvals.json · docs/intents/*/evidence.md · .ai-dlc/log/*.jsonl", "---", "",
         "# Ứng viên lesson learned (file sinh ra, không sửa tay)", "",
         "Mỗi dòng là một mẫu lặp lại máy đếm được. Chưa phải lesson. retro-keeper đọc, chọn, viết `LL-NNN.md`; người ký.", ""]
    cross = [c for c in cands if c["code"] == "X01"]
    L.append("## Lặp giữa nhiều change")
    L.append("")
    L += ["- %s %s" % (c["code"], c["msg"]) for c in cross] or ["- không có"]
    L.append("")
    L.append("## Theo change")
    L.append("")
    rest = [c for c in cands if c["code"] != "X01"]
    if not rest:
        L.append("- không có")
    for ch in sorted({c["change"] for c in rest}):
        L.append("### %s" % ch)
        for c in [x for x in rest if x["change"] == ch]:
            L.append("- %s `%s` %s · bằng chứng: %s" % (c["level"], c["code"], c["msg"], ", ".join(str(x) for x in c["evidence"][:4])))
        L.append("")
    L.append("## Số liệu nền")
    L.append("")
    L.append("| change | phiên | lượt | validate (sạch/tổng) | test (đỏ/tổng) | approvals.py gọi |")
    L.append("|---|---|---|---|---|---|")
    L.append("| %d | %d | %d | %d/%d | %d/%d | %d |" % (
        stats["changes"], stats["sessions"], stats["turns"], stats["validate_clean"], stats["validate_runs"],
        stats["tests_fail"], stats["tests"], stats["approve_calls"]))
    L.append("")
    L.append("Ngưỡng: max_self_fix = %d. Mã: %s." % (max_self_fix, " · ".join("%s %s" % kv for kv in DESCRIBE.items())))
    return "\n".join(L) + "\n"


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--") and (argv.index(a) == 0 or not argv[argv.index(a) - 1].startswith("--"))]
    root = find_root(args[0] if args else os.getcwd())
    if not root:
        print("Không phải workspace engine `contracts`.", file=sys.stderr)
        return 2
    since_s = arg(flags, "--since", None)
    since = parse_ts(since_s + "T00:00:00") if since_s else None
    if since and since.tzinfo is None:
        since = since.replace(tzinfo=datetime.timezone.utc)
    try:
        max_self_fix = int(arg(flags, "--max-self-fix", 3))
        wait_hours = float(arg(flags, "--wait-hours", 24))
    except ValueError:
        max_self_fix, wait_hours = 3, 24.0
    events = load_log(root, since)
    cands, stats = analyze(root, events, max_self_fix, wait_hours)
    md = render(root, cands, stats, since, max_self_fix)
    out_path = None
    if "--write" in flags:
        gov = os.path.join(root, ".ai-dlc", "governance")
        try:
            sys.path.insert(0, HERE)
            from layout import resolve  # noqa: WPS433
            gov = resolve(root).get("governance") or gov
        except Exception:  # noqa: BLE001
            pass
        out_path = os.path.join(gov, "lessons-learned", "candidates.md")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
    if "--json" in flags:
        print(json.dumps({"root": root, "candidates": cands, "stats": stats, "written": out_path},
                         ensure_ascii=False, indent=1, default=str))
    else:
        print(md, end="")
        if out_path:
            print("→ đã ghi %s" % os.path.relpath(out_path, root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
