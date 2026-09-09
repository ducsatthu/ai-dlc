#!/usr/bin/env python3
"""AI-DLC layout resolver — MỘT chỗ duy nhất trả lời "state của dự án nằm ở đâu, engine nào, tower kiểu gì".

Tới 6.2.0 mỗi hook/script tự dò `.ai-dlc/context-memory` theo luật riêng (đi lên 2 cấp, đi lên vô hạn, đi lên
6 cấp cho `aidlc/spaces`…). Dự án đặc thù (template có sẵn `aidlc/spaces/<space>`, đội đặt state ở thư mục
khác, nhiều space trong một repo) không cấu hình được. Nay mọi script/hook gọi `resolve()` ở đây.

Thứ tự nguồn cấu hình (nguồn trước THẮNG, chỉ key có mặt mới đè):
  1. env: AI_DLC_CONFIG=<file json> · AI_DLC_ROOT=<dir> · AI_DLC_ENGINE · AI_DLC_STATE · AI_DLC_SPACE
          AI_DLC_GOVERNANCE · AI_DLC_TOWER_OUT · AI_DLC_TOWER_PORT · AI_DLC_TOWER_MODE
  2. file `ai-dlc.config.json` hoặc `.ai-dlc/config.json` — tìm từ cwd đi lên (≤ search_up cấp)
  3. fence ```ai-dlc trong CLAUDE.md hoặc AGENTS.md cùng thư mục — JSON, hoặc `key: value` phẳng (dotted key)
  4. tự dò: `.ai-dlc/context-memory/` (engine ai-dlc) · `aidlc/spaces/` + `.claude/tools/aidlc-audit.ts`
     (engine aws-v2) · `.ai-dlc/` trống ở cwd (ai-dlc, tương thích 6.1)

Key (mọi key tuỳ chọn; path tương đối với `root`, `root` tương đối với thư mục chứa file config):
  engine      auto | ai-dlc | aws-v2 | off
  root        "."                      thư mục workspace
  state       ".ai-dlc" | "aidlc" | … thư mục state của engine
  space       "auto" | <tên>           aws-v2: space nào (auto = cursor `aidlc/active-space` → space duy nhất → default)
  governance  thư mục luật của gói (raci.md, test-viewpoints.md, sizing.md…)
  tower       {out, port, mode: auto|ai-dlc|aws-v2|off}
  search_up   6

Kết quả `resolve()` là dict path TUYỆT ĐỐI + `config_source` + `notes` (giải thích từng lựa chọn).
CLI: python3 layout.py [start] [--json | --env | --explain]   (mặc định --json). Chỉ stdlib, fail-open.
"""
import json
import os
import re
import sys

CONFIG_FILES = ("ai-dlc.config.json", os.path.join(".ai-dlc", "config.json"))
FENCE_FILES = ("CLAUDE.md", "AGENTS.md")
ENGINES = ("auto", "ai-dlc", "aws-v2", "off")
DEFAULT_SEARCH_UP = 6
DEFAULT_PORT = {"ai-dlc": 8642, "aws-v2": 8643}

# ---------- đọc config thô ----------

def _parse_fence(text):
    """Fence ```ai-dlc … ``` đầu tiên trong CLAUDE.md/AGENTS.md. Thân bắt đầu bằng `{` ⇒ JSON;
    không thì `key: value` mỗi dòng, key dotted (`tower.port: 8642`), giá trị JSON nếu parse được."""
    m = re.search(r"^```ai-dlc[^\n]*\n(.*?)^```", text, re.S | re.M)
    if not m:
        return None
    body = m.group(1).strip()
    if not body:
        return {}
    if body.startswith("{"):
        try:
            return json.loads(body)
        except ValueError:
            return None
    cfg = {}
    for line in body.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if not re.match(r"^[A-Za-z_][\w.]*$", k):
            continue
        try:
            val = json.loads(v)
        except ValueError:
            val = v.strip("\"'")
        cur = cfg
        parts = k.split(".")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
            if not isinstance(cur, dict):
                break
        else:
            cur[parts[-1]] = val
    return cfg


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _find_config(start, search_up):
    """Đi lên từ start: mỗi cấp thử file config rồi fence CLAUDE.md/AGENTS.md. Trả (cfg, source, dir)."""
    cur = os.path.abspath(start)
    for _ in range(search_up + 1):
        for name in CONFIG_FILES:
            p = os.path.join(cur, name)
            if os.path.isfile(p):
                cfg = _read_json(p)
                if cfg is not None:
                    return cfg, "file:" + p, cur
        for name in FENCE_FILES:
            p = os.path.join(cur, name)
            if os.path.isfile(p):
                try:
                    with open(p, encoding="utf-8", errors="replace") as f:
                        cfg = _parse_fence(f.read())
                except OSError:
                    cfg = None
                if cfg is not None:
                    return cfg, "fence:" + p, cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return None, None, None


def _env_overrides():
    e = os.environ
    cfg = {}
    if e.get("AI_DLC_ENGINE"):
        cfg["engine"] = e["AI_DLC_ENGINE"]
    if e.get("AI_DLC_STATE"):
        cfg["state"] = e["AI_DLC_STATE"]
    if e.get("AI_DLC_SPACE"):
        cfg["space"] = e["AI_DLC_SPACE"]
    if e.get("AI_DLC_GOVERNANCE"):
        cfg["governance"] = e["AI_DLC_GOVERNANCE"]
    tower = {}
    if e.get("AI_DLC_TOWER_OUT"):
        tower["out"] = e["AI_DLC_TOWER_OUT"]
    if e.get("AI_DLC_TOWER_PORT"):
        try:
            tower["port"] = int(e["AI_DLC_TOWER_PORT"])
        except ValueError:
            pass
    if e.get("AI_DLC_TOWER_MODE"):
        tower["mode"] = e["AI_DLC_TOWER_MODE"]
    if tower:
        cfg["tower"] = tower
    return cfg


def _merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out

# ---------- tự dò ----------

def _is_ai_dlc(d, state=".ai-dlc"):
    return os.path.isdir(os.path.join(d, state, "context-memory"))


def _is_aws_v2(d, state="aidlc"):
    return os.path.isdir(os.path.join(d, state, "spaces")) and \
        os.path.isfile(os.path.join(d, ".claude", "tools", "aidlc-audit.ts"))


def _strip_inside_state(p, state_names=(".ai-dlc", "aidlc")):
    """Đứng bên trong cây state ⇒ nhảy ra thư mục chứa nó (luật tower_generate 4.0.0)."""
    parts = os.path.abspath(p).split(os.sep)
    for name in state_names:
        if name in parts:
            i = parts.index(name)
            if i > 0:
                return os.sep.join(parts[:i]) or os.sep
    return os.path.abspath(p)


def _autodetect(start, search_up, notes):
    cur = _strip_inside_state(start)
    for _ in range(search_up + 1):
        if _is_ai_dlc(cur):
            notes.append("tự dò: %s/.ai-dlc/context-memory ⇒ engine ai-dlc" % cur)
            return "ai-dlc", cur
        if _is_aws_v2(cur):
            notes.append("tự dò: %s/aidlc/spaces + .claude/tools ⇒ engine aws-v2" % cur)
            return "aws-v2", cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    s = os.path.abspath(start)
    if os.path.isdir(os.path.join(s, ".ai-dlc")):
        notes.append("tự dò: %s/.ai-dlc trống (chưa context-memory) ⇒ engine ai-dlc, tương thích 6.1" % s)
        return "ai-dlc", s
    return None, None

# ---------- space (aws-v2) ----------

def _pick_space(state_dir, wanted, notes):
    spaces_dir = os.path.join(state_dir, "spaces")
    try:
        names = sorted(n for n in os.listdir(spaces_dir) if os.path.isdir(os.path.join(spaces_dir, n)))
    except OSError:
        names = []
    if wanted and wanted != "auto":
        if names and wanted not in names:
            notes.append("space '%s' không có trong %s (có: %s) — vẫn dùng theo config" % (wanted, spaces_dir, ", ".join(names) or "—"))
        return wanted, names
    cursor = os.path.join(state_dir, "active-space")
    if os.path.isfile(cursor):
        try:
            v = open(cursor, encoding="utf-8").read().strip()
        except OSError:
            v = ""
        if v:
            notes.append("space từ cursor %s" % cursor)
            return v, names
    if len(names) == 1:
        notes.append("space duy nhất: %s" % names[0])
        return names[0], names
    if "default" in names or not names:
        return "default", names
    notes.append("nhiều space (%s), không có cursor ⇒ lấy '%s'; đặt `space:` trong config hoặc AI_DLC_SPACE" % (", ".join(names), names[0]))
    return names[0], names

# ---------- resolve ----------

def resolve(start=None, env=True):
    start = os.path.abspath(start or os.getcwd())
    notes = []
    cfg = {}
    source = "none"
    cfg_dir = None

    explicit = os.environ.get("AI_DLC_CONFIG") if env else None
    if explicit and os.path.isfile(explicit):
        c = _read_json(explicit)
        if c is not None:
            cfg, source, cfg_dir = c, "env:AI_DLC_CONFIG=" + explicit, os.path.dirname(os.path.abspath(explicit))
    search_up = int(cfg.get("search_up", DEFAULT_SEARCH_UP)) if isinstance(cfg.get("search_up", 0), int) else DEFAULT_SEARCH_UP
    if source == "none":
        c, src, d = _find_config(start, search_up)
        if c is not None:
            cfg, source, cfg_dir = c, src, d
    if env:
        cfg = _merge(cfg, _env_overrides())
        if os.environ.get("AI_DLC_ROOT"):
            cfg["root"] = os.environ["AI_DLC_ROOT"]
            cfg_dir = os.getcwd()
            notes.append("root từ AI_DLC_ROOT")
    try:
        search_up = int(cfg.get("search_up", DEFAULT_SEARCH_UP))
    except (TypeError, ValueError):
        search_up = DEFAULT_SEARCH_UP

    engine = str(cfg.get("engine", "auto")).lower()
    if engine not in ENGINES:
        notes.append("engine '%s' không hợp lệ ⇒ auto" % engine)
        engine = "auto"

    root = None
    if cfg.get("root") is not None:
        root = os.path.abspath(os.path.join(cfg_dir or start, str(cfg["root"])))
    elif cfg_dir is not None:
        root = cfg_dir

    if engine == "off":
        return _result("off", root or start, cfg, source, notes, None, [])

    if engine == "auto":
        if root is not None:
            state = cfg.get("state")
            if _is_ai_dlc(root, state or ".ai-dlc"):
                engine = "ai-dlc"
            elif _is_aws_v2(root, state or "aidlc"):
                engine = "aws-v2"
            else:
                det, _r = _autodetect(root, 0, notes)
                engine = det or "none"
            if engine != "none":
                notes.append("engine tự dò tại root config: %s" % engine)
        else:
            det, r = _autodetect(start, search_up, notes)
            engine, root = (det or "none"), (r or start)
    elif root is None:
        # engine khai rõ nhưng không có root ⇒ tìm thư mục có state tương ứng
        state = cfg.get("state") or (".ai-dlc" if engine == "ai-dlc" else "aidlc")
        cur = _strip_inside_state(start)
        found = None
        for _ in range(search_up + 1):
            if os.path.isdir(os.path.join(cur, state)):
                found = cur
                break
            nxt = os.path.dirname(cur)
            if nxt == cur:
                break
            cur = nxt
        root = found or start
        if found is None:
            notes.append("engine %s khai trong config nhưng không thấy %s/ từ %s đi lên %d cấp" % (engine, state, start, search_up))

    if engine == "none":
        return _result("none", root, cfg, source, notes, None, [])

    state_rel = cfg.get("state") or (".ai-dlc" if engine == "ai-dlc" else "aidlc")
    state_dir = os.path.abspath(os.path.join(root, state_rel))
    space, spaces = (None, [])
    if engine == "aws-v2":
        space, spaces = _pick_space(state_dir, cfg.get("space"), notes)
    return _result(engine, root, cfg, source, notes, state_dir, spaces, space)


def _result(engine, root, cfg, source, notes, state_dir, spaces, space=None):
    root = os.path.abspath(root)
    tower_cfg = cfg.get("tower") if isinstance(cfg.get("tower"), dict) else {}
    out = {
        "engine": engine,
        "root": root,
        "config_source": source,
        "state": state_dir,
        "space": space,
        "spaces": spaces,
        "space_dir": None,
        "context_memory": None,
        "inbox": None,
        "governance": None,
        "workspace_map": None,
        "tower": {"out": None, "port": None, "mode": "off"},
        "notes": notes,
    }
    if engine in ("off", "none"):
        return out
    gov_default = os.path.join(state_dir, "context-memory", "governance") if engine == "ai-dlc" \
        else os.path.join(root, ".ai-dlc", "governance")
    out["governance"] = os.path.abspath(os.path.join(root, cfg["governance"])) if cfg.get("governance") else gov_default
    if engine == "ai-dlc":
        out["context_memory"] = os.path.join(state_dir, "context-memory")
        out["inbox"] = os.path.join(state_dir, "inbox")
        out["workspace_map"] = os.path.join(state_dir, "workspace-map.md")
        tower_out_default = os.path.join(state_dir, "tower")
    else:
        out["space_dir"] = os.path.join(state_dir, "spaces", space) if space else None
        tower_out_default = os.path.join(root, ".ai-dlc", "tower")
    mode = str(tower_cfg.get("mode", "auto")).lower()
    if mode not in ("auto", "ai-dlc", "aws-v2", "off"):
        notes.append("tower.mode '%s' không hợp lệ ⇒ auto" % mode)
        mode = "auto"
    if mode == "auto":
        mode = engine
    try:
        port = int(tower_cfg.get("port", DEFAULT_PORT[engine]))
    except (TypeError, ValueError):
        port = DEFAULT_PORT[engine]
    out["tower"] = {
        "out": os.path.abspath(os.path.join(root, tower_cfg["out"])) if tower_cfg.get("out") else tower_out_default,
        "port": port,
        "mode": mode,
    }
    return out

# ---------- CLI ----------

def _shell_quote(s):
    return "'" + str(s).replace("'", "'\\''") + "'"


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    r = resolve(args[0] if args else None)
    if "--env" in flags:
        t = r["tower"]
        lines = [
            "AI_DLC_L_ENGINE=%s" % _shell_quote(r["engine"]),
            "AI_DLC_L_ROOT=%s" % _shell_quote(r["root"]),
            "AI_DLC_L_STATE=%s" % _shell_quote(r["state"] or ""),
            "AI_DLC_L_SPACE=%s" % _shell_quote(r["space"] or ""),
            "AI_DLC_L_SPACE_DIR=%s" % _shell_quote(r["space_dir"] or ""),
            "AI_DLC_L_CONTEXT_MEMORY=%s" % _shell_quote(r["context_memory"] or ""),
            "AI_DLC_L_INBOX=%s" % _shell_quote(r["inbox"] or ""),
            "AI_DLC_L_GOVERNANCE=%s" % _shell_quote(r["governance"] or ""),
            "AI_DLC_L_TOWER_OUT=%s" % _shell_quote(t["out"] or ""),
            "AI_DLC_L_TOWER_PORT=%s" % _shell_quote(t["port"] or ""),
            "AI_DLC_L_TOWER_MODE=%s" % _shell_quote(t["mode"]),
            "AI_DLC_L_SOURCE=%s" % _shell_quote(r["config_source"]),
        ]
        print("\n".join(lines))
        return 0
    if "--explain" in flags:
        print("engine: %s   root: %s   (config: %s)" % (r["engine"], r["root"], r["config_source"]))
        for k in ("state", "space", "space_dir", "context_memory", "inbox", "governance", "workspace_map"):
            if r.get(k):
                print("  %-15s %s" % (k, r[k]))
        print("  %-15s %s (port %s, mode %s)" % ("tower", r["tower"]["out"], r["tower"]["port"], r["tower"]["mode"]))
        for n in r["notes"]:
            print("  · " + n)
        return 0
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
