#!/usr/bin/env bun
// layout.ts — bản bun của scripts/layout.py, CÙNG luật, CÙNG kết quả (kiểm chéo bằng
// `python3 layout.py --json` vs `bun layout.ts --json` trên cùng fixture). Giữ cho script/hook bun nào của gói
// cần resolve layout mà không muốn thêm một tiến trình python (7.0.0-a: không hook bun nào còn dùng — nhánh
// aws-v2 đã archive; file giữ để tests kiểm chéo và cho tower tương lai).
// Mọi giải thích về nguồn cấu hình / key / thứ tự ưu tiên: đọc docstring của layout.py — không lặp ở đây.
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";

export type Engine = "ai-dlc" | "contracts" | "aws-v2" | "off" | "none";
export type Layout = {
  engine: Engine; root: string; config_source: string; state: string | null; space: string | null;
  spaces: string[]; space_dir: string | null; context_memory: string | null; inbox: string | null;
  governance: string | null; workspace_map: string | null; skill: string | null; memory: string | null;
  tower: { out: string | null; port: number | null; mode: string }; notes: string[];
};
type Cfg = Record<string, any>;

const CONFIG_FILES = ["ai-dlc.config.json", join(".ai-dlc", "config.json")];
const FENCE_FILES = ["CLAUDE.md", "AGENTS.md"];
const ENGINES = ["auto", "ai-dlc", "contracts", "aws-v2", "off"];
const DEFAULT_SEARCH_UP = 6;
const DEFAULT_PORT: Record<string, number> = { "ai-dlc": 8642, "aws-v2": 8643, contracts: 8644 };
const DEFAULT_STATE: Record<string, string> = { "ai-dlc": ".ai-dlc", "aws-v2": "aidlc", contracts: join("docs", "intents") };
const CONTRACTS_MARKERS = [
  join(".agents", "skills", "aidlc", "SKILL.md"),
  join("docs", "memory", "project.md"),
  join("docs", "intents", "_templates", "intent.md"),
];

const isDir = (p: string) => { try { return statSync(p).isDirectory(); } catch { return false; } };
const isFile = (p: string) => { try { return statSync(p).isFile(); } catch { return false; } };
const readText = (p: string) => { try { return readFileSync(p, "utf-8"); } catch { return null; } };

function parseFence(text: string): Cfg | null {
  const m = text.match(/^```ai-dlc[^\n]*\n([\s\S]*?)^```/m);
  if (!m) return null;
  const body = m[1].trim();
  if (!body) return {};
  if (body.startsWith("{")) { try { return JSON.parse(body); } catch { return null; } }
  const cfg: Cfg = {};
  for (let line of body.split("\n")) {
    line = line.split("#", 1)[0].trim();
    if (!line || !line.includes(":")) continue;
    const i = line.indexOf(":");
    const k = line.slice(0, i).trim(); const v = line.slice(i + 1).trim();
    if (!/^[A-Za-z_][\w.]*$/.test(k)) continue;
    let val: any; try { val = JSON.parse(v); } catch { val = v.replace(/^["']|["']$/g, ""); }
    const parts = k.split("."); let cur: any = cfg; let ok = true;
    for (const p of parts.slice(0, -1)) {
      if (!(p in cur)) cur[p] = {};
      cur = cur[p];
      if (typeof cur !== "object" || cur === null) { ok = false; break; }
    }
    if (ok) cur[parts[parts.length - 1]] = val;
  }
  return cfg;
}

function readJson(p: string): Cfg | null {
  const t = readText(p); if (t === null) return null;
  try { const d = JSON.parse(t); return d && typeof d === "object" && !Array.isArray(d) ? d : null; } catch { return null; }
}

function findConfig(start: string, searchUp: number): [Cfg | null, string | null, string | null] {
  let cur = resolve(start);
  for (let i = 0; i <= searchUp; i++) {
    for (const name of CONFIG_FILES) {
      const p = join(cur, name);
      if (isFile(p)) { const c = readJson(p); if (c !== null) return [c, "file:" + p, cur]; }
    }
    for (const name of FENCE_FILES) {
      const p = join(cur, name);
      if (isFile(p)) { const t = readText(p); const c = t === null ? null : parseFence(t); if (c !== null) return [c, "fence:" + p, cur]; }
    }
    const up = dirname(cur); if (up === cur) break; cur = up;
  }
  return [null, null, null];
}

function envOverrides(): Cfg {
  const e = process.env; const cfg: Cfg = {}; const tower: Cfg = {};
  if (e.AI_DLC_ENGINE) cfg.engine = e.AI_DLC_ENGINE;
  if (e.AI_DLC_STATE) cfg.state = e.AI_DLC_STATE;
  if (e.AI_DLC_SPACE) cfg.space = e.AI_DLC_SPACE;
  if (e.AI_DLC_GOVERNANCE) cfg.governance = e.AI_DLC_GOVERNANCE;
  if (e.AI_DLC_TOWER_OUT) tower.out = e.AI_DLC_TOWER_OUT;
  if (e.AI_DLC_TOWER_PORT && /^\d+$/.test(e.AI_DLC_TOWER_PORT)) tower.port = parseInt(e.AI_DLC_TOWER_PORT, 10);
  if (e.AI_DLC_TOWER_MODE) tower.mode = e.AI_DLC_TOWER_MODE;
  if (Object.keys(tower).length) cfg.tower = tower;
  return cfg;
}

function merge(base: Cfg, over: Cfg | null): Cfg {
  const out: Cfg = { ...base };
  for (const [k, v] of Object.entries(over ?? {})) {
    out[k] = v && typeof v === "object" && !Array.isArray(v) && out[k] && typeof out[k] === "object" ? merge(out[k], v) : v;
  }
  return out;
}

const isAiDlc = (d: string, state = ".ai-dlc") => isDir(join(d, state, "context-memory"));
const isContracts = (d: string) => CONTRACTS_MARKERS.every((m) => isFile(join(d, m)));
const isAwsV2 = (d: string, state = "aidlc") => isDir(join(d, state, "spaces")) && isFile(join(d, ".claude", "tools", "aidlc-audit.ts"));

function detectAt(d: string, state?: string): Engine | null {
  if (isAiDlc(d, state || ".ai-dlc")) return "ai-dlc";
  if (isContracts(d)) return "contracts";
  if (isAwsV2(d, state || "aidlc")) return "aws-v2";
  return null;
}

function stripInsideState(p: string): string {
  const parts = resolve(p).split("/");
  for (const name of [".ai-dlc", "aidlc"]) {
    const i = parts.indexOf(name);
    if (i > 0) return parts.slice(0, i).join("/") || "/";
  }
  return resolve(p);
}

function twoEnginesNote(d: string, engine: string, notes: string[]) {
  if (engine === "ai-dlc" && isContracts(d)) {
    notes.push(`CẢNH BÁO: ${d} cũng là workspace engine contracts (docs/intents/) — hai nguồn sự thật; đặt \`engine: contracts\` hoặc \`engine: off\` cho .ai-dlc cũ`);
  } else if (engine === "contracts" && isDir(join(d, ".ai-dlc", "context-memory"))) {
    notes.push(`CẢNH BÁO: ${d} có cả .ai-dlc/context-memory — hai nguồn sự thật, xem dlc-doctor D01`);
  }
}

function autodetect(start: string, searchUp: number, notes: string[]): [Engine | null, string | null] {
  let cur = stripInsideState(start);
  for (let i = 0; i <= searchUp; i++) {
    const det = detectAt(cur);
    if (det === "ai-dlc") notes.push(`tự dò: ${cur}/.ai-dlc/context-memory ⇒ engine ai-dlc`);
    else if (det === "contracts") notes.push(`tự dò: ${cur} có .agents/skills/aidlc + docs/memory + docs/intents/_templates ⇒ engine contracts (template đội)`);
    else if (det === "aws-v2") notes.push(`tự dò: ${cur}/aidlc/spaces + .claude/tools ⇒ engine aws-v2 (ĐÃ ARCHIVE 7.0.0 — gói không chạy trên engine này)`);
    if (det) return [det, cur];
    const up = dirname(cur); if (up === cur) break; cur = up;
  }
  const s = resolve(start);
  if (isDir(join(s, ".ai-dlc"))) { notes.push(`tự dò: ${s}/.ai-dlc trống (chưa context-memory) ⇒ engine ai-dlc, tương thích 6.1`); return ["ai-dlc", s]; }
  return [null, null];
}

function pickSpace(stateDir: string, wanted: string | undefined, notes: string[]): [string, string[]] {
  const spacesDir = join(stateDir, "spaces");
  let names: string[] = [];
  try { names = readdirSync(spacesDir).filter((n) => isDir(join(spacesDir, n))).sort(); } catch { names = []; }
  if (wanted && wanted !== "auto") {
    if (names.length && !names.includes(wanted)) notes.push(`space '${wanted}' không có trong ${spacesDir} (có: ${names.join(", ") || "—"}) — vẫn dùng theo config`);
    return [wanted, names];
  }
  const cursor = join(stateDir, "active-space");
  if (isFile(cursor)) { const v = (readText(cursor) ?? "").trim(); if (v) { notes.push(`space từ cursor ${cursor}`); return [v, names]; } }
  if (names.length === 1) { notes.push(`space duy nhất: ${names[0]}`); return [names[0], names]; }
  if (names.includes("default") || !names.length) return ["default", names];
  notes.push(`nhiều space (${names.join(", ")}), không có cursor ⇒ lấy '${names[0]}'; đặt \`space:\` trong config hoặc AI_DLC_SPACE`);
  return [names[0], names];
}

export function resolveLayout(start?: string, env = true): Layout {
  start = resolve(start || process.cwd());
  const notes: string[] = [];
  let cfg: Cfg = {}; let source = "none"; let cfgDir: string | null = null;
  const explicit = env ? process.env.AI_DLC_CONFIG : undefined;
  if (explicit && isFile(explicit)) {
    const c = readJson(explicit);
    if (c !== null) { cfg = c; source = "env:AI_DLC_CONFIG=" + explicit; cfgDir = dirname(resolve(explicit)); }
  }
  let searchUp = Number.isInteger(cfg.search_up) ? cfg.search_up : DEFAULT_SEARCH_UP;
  if (source === "none") {
    const [c, src, d] = findConfig(start, searchUp);
    if (c !== null) { cfg = c; source = src!; cfgDir = d; }
  }
  if (env) {
    cfg = merge(cfg, envOverrides());
    if (process.env.AI_DLC_ROOT) { cfg.root = process.env.AI_DLC_ROOT; cfgDir = process.cwd(); notes.push("root từ AI_DLC_ROOT"); }
  }
  searchUp = Number.isInteger(Number(cfg.search_up)) && cfg.search_up !== undefined ? Number(cfg.search_up) : DEFAULT_SEARCH_UP;

  let engine = String(cfg.engine ?? "auto").toLowerCase();
  if (!ENGINES.includes(engine)) { notes.push(`engine '${engine}' không hợp lệ ⇒ auto`); engine = "auto"; }

  let root: string | null = null;
  if (cfg.root !== undefined && cfg.root !== null) root = resolve(cfgDir ?? start, String(cfg.root));
  else if (cfgDir !== null) root = cfgDir;

  if (engine === "off") return result("off", root ?? start, cfg, source, notes, null, []);

  if (engine === "auto") {
    if (root !== null) {
      let det = detectAt(root, cfg.state as string | undefined);
      if (det === null) [det] = autodetect(root, 0, notes);
      engine = det ?? "none";
      if (engine !== "none") notes.push(`engine tự dò tại root config: ${engine}`);
    } else {
      const [det, r] = autodetect(start, searchUp, notes);
      engine = det ?? "none"; root = r ?? start;
    }
  } else if (root === null) {
    const state = (cfg.state as string) || DEFAULT_STATE[engine];
    let cur = stripInsideState(start); let found: string | null = null;
    for (let i = 0; i <= searchUp; i++) {
      if (isDir(join(cur, state)) || (engine === "contracts" && isContracts(cur))) { found = cur; break; }
      const up = dirname(cur); if (up === cur) break; cur = up;
    }
    root = found ?? start;
    if (found === null) notes.push(`engine ${engine} khai trong config nhưng không thấy ${state}/ từ ${start} đi lên ${searchUp} cấp`);
  }

  if (engine === "none") return result("none", root!, cfg, source, notes, null, []);
  twoEnginesNote(root!, engine, notes); // cả khi tự dò lẫn khi config khai tường minh
  if (engine === "aws-v2" && !notes.some((n) => n.includes("ARCHIVE"))) {
    notes.push("engine aws-v2 ĐÃ ARCHIVE 7.0.0 — không script nào của gói còn chạy trên nó (docs/archive/aws-v2/)");
  }
  const stateRel = (cfg.state as string) || DEFAULT_STATE[engine];
  const stateDir = resolve(root!, stateRel);
  let space: string | null = null; let spaces: string[] = [];
  if (engine === "aws-v2") [space, spaces] = pickSpace(stateDir, cfg.space, notes);
  return result(engine as Engine, root!, cfg, source, notes, stateDir, spaces, space);
}

function result(engine: Engine, root: string, cfg: Cfg, source: string, notes: string[], stateDir: string | null, spaces: string[], space: string | null = null): Layout {
  root = resolve(root);
  const towerCfg: Cfg = cfg.tower && typeof cfg.tower === "object" ? cfg.tower : {};
  const out: Layout = {
    engine, root, config_source: source, state: stateDir, space, spaces, space_dir: null, context_memory: null,
    inbox: null, governance: null, workspace_map: null, skill: null, memory: null, tower: { out: null, port: null, mode: "off" }, notes,
  };
  if (engine === "off" || engine === "none") return out;
  const govDefault = engine === "ai-dlc" ? join(stateDir!, "context-memory", "governance") : join(root, ".ai-dlc", "governance");
  out.governance = cfg.governance ? resolve(root, String(cfg.governance)) : govDefault;
  let towerOutDefault: string;
  if (engine === "ai-dlc") {
    out.context_memory = join(stateDir!, "context-memory");
    out.inbox = join(stateDir!, "inbox");
    out.workspace_map = join(stateDir!, "workspace-map.md");
    towerOutDefault = join(stateDir!, "tower");
  } else if (engine === "contracts") {
    out.skill = join(root, ".agents", "skills", "aidlc");
    out.memory = join(root, "docs", "memory");
    towerOutDefault = join(root, ".ai-dlc", "tower");
  } else {
    out.space_dir = space ? join(stateDir!, "spaces", space) : null;
    towerOutDefault = join(root, ".ai-dlc", "tower");
  }
  let mode = String(towerCfg.mode ?? "auto").toLowerCase();
  if (!["auto", "ai-dlc", "contracts", "aws-v2", "off"].includes(mode)) { notes.push(`tower.mode '${mode}' không hợp lệ ⇒ auto`); mode = "auto"; }
  if (mode === "auto") mode = engine;
  const port = Number.isInteger(Number(towerCfg.port)) && towerCfg.port !== undefined && towerCfg.port !== null && String(towerCfg.port) !== ""
    ? Number(towerCfg.port) : DEFAULT_PORT[engine];
  out.tower = { out: towerCfg.out ? resolve(root, String(towerCfg.out)) : towerOutDefault, port, mode };
  return out;
}

export function isUnder(file: string, dir: string): boolean {
  const f = resolve(file).replace(/\\/g, "/"); const d = resolve(dir).replace(/\\/g, "/").replace(/\/$/, "");
  return f === d || f.startsWith(d + "/");
}

if (import.meta.main) {
  const argv = process.argv.slice(2);
  const flags = new Set(argv.filter((a) => a.startsWith("--")));
  const args = argv.filter((a) => !a.startsWith("--"));
  const r = resolveLayout(args[0]);
  if (flags.has("--explain")) {
    console.log(`engine: ${r.engine}   root: ${r.root}   (config: ${r.config_source})`);
    for (const k of ["state", "space", "space_dir", "context_memory", "inbox", "governance", "workspace_map", "skill", "memory"] as const) if (r[k]) console.log(`  ${k.padEnd(15)} ${r[k]}`);
    console.log(`  ${"tower".padEnd(15)} ${r.tower.out} (port ${r.tower.port}, mode ${r.tower.mode})`);
    for (const n of r.notes) console.log("  · " + n);
  } else {
    console.log(JSON.stringify(r, null, 1));
  }
}
