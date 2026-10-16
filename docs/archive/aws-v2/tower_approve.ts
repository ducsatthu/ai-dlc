#!/usr/bin/env bun
// tower_approve.ts — một nút bấm trên tower = một quyết định gate trên engine AWS aidlc-workflows v2,
// ghi bằng commit git của NGƯỜI bấm. Chạy trên máy của người duyệt, ngoài phiên Claude/Codex.
//
// Cơ sở: docs/spikes/aws-v2-cross-clone-approval.md — engine chấp nhận approve từ clone khác;
// engine KHÔNG kiểm "ai" (presence guard toàn workflow), nên định danh + luật đúng người là việc
// của script này: git user là tác giả commit, và được ghi vào HUMAN_TURN (Actor) + User Input.
//
// Usage:
//   bun tower_approve.ts --stage <slug> --result approved|rejected --input "<lựa chọn / phản hồi>"
//                        [--intent <id>] [--space default] [--project-dir <dir>]
//                        [--no-pull] [--no-push] [--dry-run]
//
// Các bước (mỗi bước fail ⇒ dừng, state không đổi):
//   1. tìm workspace (aidlc/spaces) · lấy git user.name/email (bắt buộc)
//   2. git pull --rebase (trừ --no-pull) — quyết định phải dựa trên state mới nhất
//   3. --intent ⇒ `aidlc intent switch` (cursor active-intent là per-clone, gitignored)
//   4. đọc aidlc-state.md: stage phải đang `[?]` (awaiting-approval)
//   4b. RACI: `.ai-dlc/governance/raci.md` trong workspace — git email phải nằm trong cột "quyết" của dòng
//       khớp stage (khớp chính xác, rồi glob `*`); KHÔNG có file ⇒ cho qua kèm cảnh báo `raci: missing`
//       (bậc 1 adoption); có file mà không có tên ⇒ từ chối. Engine không kiểm ai — đây là chỗ duy nhất kiểm.
//   5. ghi HUMAN_TURN {Actor, Source: tower, Stage} qua đúng seam của hook (appendAuditEntry)
//   6. `aidlc-orchestrate.ts report --stage --result --user-input "<input> — <name> <email>"`
//   7. kiểm state sau: approved ⇒ `[x]`; rejected ⇒ không còn `[?]`
//   8. git add aidlc/ · commit (author = người bấm) · push (retry 1 lần sau pull --rebase)
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { resolveLayout, type Layout } from "./layout.ts";

type Result = "approved" | "rejected";
type Flags = {
  stage?: string; result?: Result; input?: string; intent?: string; space: string;
  projectDir?: string; pull: boolean; push: boolean; dryRun: boolean; spaceExplicit: boolean;
};

function parseFlags(argv: string[]): Flags {
  const f: Flags = { space: "default", pull: true, push: true, dryRun: false, spaceExplicit: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]; const v = argv[i + 1];
    if (a === "--stage") { f.stage = v; i++; }
    else if (a === "--result") { f.result = v as Result; i++; }
    else if (a === "--input") { f.input = v; i++; }
    else if (a === "--intent") { f.intent = v; i++; }
    else if (a === "--space") { f.space = v; f.spaceExplicit = true; i++; }
    else if (a === "--project-dir") { f.projectDir = v; i++; }
    else if (a === "--no-pull") f.pull = false;
    else if (a === "--no-push") f.push = false;
    else if (a === "--dry-run") f.dryRun = true;
    else if (a === "-h" || a === "--help") { usage(); process.exit(0); }
    else die(`Cờ không biết: ${a}`);
  }
  return f;
}

function usage(): void {
  console.error(
    'Usage: bun tower_approve.ts --stage <slug> --result approved|rejected --input "<text>" ' +
    "[--intent <id>] [--space default] [--project-dir <dir>] [--no-pull] [--no-push] [--dry-run]",
  );
}

function die(msg: string, code = 1): never {
  console.log(JSON.stringify({ ok: false, error: msg }));
  process.exit(code);
}

function run(cmd: string, args: string[], cwd: string, allowFail = false): { code: number; out: string; err: string } {
  const r = spawnSync(cmd, args, { cwd, encoding: "utf-8" });
  const res = { code: r.status ?? 1, out: (r.stdout ?? "").trim(), err: (r.stderr ?? "").trim() };
  if (res.code !== 0 && !allowFail) die(`${cmd} ${args.join(" ")} thất bại (${res.code}): ${res.err || res.out}`);
  return res;
}

let LAYOUT: Layout | null = null;

function findProjectDir(explicit?: string): string {
  // 7.0.0: layout.ts trả lời (config file · fence CLAUDE.md · env · tự dò) — fallback luật cũ
  try {
    const lay = resolveLayout(explicit || process.cwd());
    if (lay.engine === "aws-v2") { LAYOUT = lay; return lay.root; }
  } catch { /* fallback */ }
  if (explicit) {
    const d = resolve(explicit);
    if (!existsSync(join(d, "aidlc", "spaces"))) die(`Không thấy aidlc/spaces dưới ${d}`);
    return d;
  }
  let d = process.cwd();
  for (let i = 0; i < 6; i++) {
    if (existsSync(join(d, "aidlc", "spaces"))) return d;
    const up = dirname(d); if (up === d) break; d = up;
  }
  die("Không tìm thấy workspace (thư mục chứa aidlc/spaces) từ cwd đi lên 6 cấp — dùng --project-dir");
}

function gitIdentity(pd: string): { name: string; email: string } {
  const name = run("git", ["config", "user.name"], pd, true).out;
  const email = run("git", ["config", "user.email"], pd, true).out;
  if (!name || !email) die("git user.name / user.email chưa đặt — quyết định phải có tác giả thật");
  return { name, email };
}

function resolveRecordDir(pd: string, space: string, intent?: string): string {
  const intentsDir = join(pd, "aidlc", "spaces", space, "intents");
  if (!existsSync(intentsDir)) die(`Không thấy ${intentsDir}`);
  if (intent) {
    const d = join(intentsDir, intent);
    if (!existsSync(join(d, "aidlc-state.md"))) die(`Intent ${intent} không có aidlc-state.md`);
    return d;
  }
  const cursor = join(intentsDir, "active-intent");
  if (existsSync(cursor)) {
    const id = readFileSync(cursor, "utf-8").trim();
    const d = join(intentsDir, id);
    if (existsSync(join(d, "aidlc-state.md"))) return d;
  }
  // lone-intent fallback — cùng luật với engine
  const entries = run("ls", ["-1", intentsDir], pd).out.split("\n")
    .filter((e) => e && existsSync(join(intentsDir, e, "aidlc-state.md")));
  if (entries.length === 1) return join(intentsDir, entries[0]);
  die(`Có ${entries.length} intent, cursor active-intent không có — truyền --intent <id>`);
}

function checkboxState(stateContent: string, slug: string): string | null {
  const re = new RegExp(`^- \\[(.)\\] ${slug.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&")}(?:\\s|$)`, "m");
  const m = stateContent.match(re);
  return m ? m[1] : null;
}

// --- RACI: ai được quyết gate nào (.ai-dlc/governance/raci.md, template plugin/templates/raci.md) ---
// Bảng markdown: | gate | quyết | kiểm |  — gate = slug stage hoặc glob (`*`, `units-*`); quyết/kiểm =
// danh sách email hoặc tên, cách nhau bởi dấu phẩy. Dòng đầu khớp thắng; `*` là dòng mặc định.
type RaciRow = { gate: string; decide: string[]; check: string[] };
export function parseRaci(md: string): RaciRow[] {
  const rows: RaciRow[] = [];
  for (const line of md.split("\n")) {
    const m = line.match(/^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|(?:\s*([^|]*?)\s*\|)?\s*$/);
    if (!m) continue;
    const gate = m[1].trim();
    if (!gate || /^-+$/.test(gate) || /^gate$/i.test(gate)) continue;
    const split = (v: string) => v.split(",").map((x) => x.trim()).filter((x) => x && x !== "—" && x !== "-");
    rows.push({ gate, decide: split(m[2] ?? ""), check: split(m[3] ?? "") });
  }
  return rows;
}
function globMatch(pattern: string, slug: string): boolean {
  const re = new RegExp("^" + pattern.split("*").map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join(".*") + "$");
  return re.test(slug);
}
export function raciCheck(pd: string, stage: string, who: { name: string; email: string }): { status: "ok" | "missing"; row?: RaciRow } {
  const path = join(LAYOUT?.governance ?? join(pd, ".ai-dlc", "governance"), "raci.md");
  if (!existsSync(path)) return { status: "missing" };
  const rows = parseRaci(readFileSync(path, "utf-8"));
  const row = rows.find((r) => r.gate === stage) ?? rows.find((r) => r.gate !== stage && globMatch(r.gate, stage));
  if (!row) die(`RACI (${path}) không có dòng cho stage ${stage} và không có dòng mặc định \`*\``);
  const me = [who.email.toLowerCase(), who.name.toLowerCase()];
  const ok = row.decide.some((p) => me.includes(p.toLowerCase()));
  if (!ok) die(`RACI: ${who.name} <${who.email}> không nằm trong cột "quyết" của gate ${row.gate} (được phép: ${row.decide.join(", ") || "—"}) — engine không kiểm ai, nên tower từ chối tại đây`);
  return { status: "ok", row };
}

async function main(): Promise<void> {
  const f = parseFlags(process.argv.slice(2));
  if (!f.stage || !f.result || !f.input) { usage(); die("Thiếu --stage / --result / --input"); }
  if (f.result !== "approved" && f.result !== "rejected") die("--result phải là approved | rejected");
  if (!f.input.trim()) die("--input trống — quyết định phải có lời của người");

  const pd = findProjectDir(f.projectDir);
  if (!f.spaceExplicit && LAYOUT?.space) f.space = LAYOUT.space;
  const who = gitIdentity(pd);
  const actor = `${who.name} <${who.email}>`;
  const tools = join(pd, ".claude", "tools");
  if (!existsSync(join(tools, "aidlc-orchestrate.ts"))) die("Workspace không có .claude/tools/aidlc-orchestrate.ts (engine AWS v2)");

  if (f.pull) run("git", ["pull", "--rebase", "--quiet"], pd);
  if (f.intent) run("bun", [join(tools, "aidlc.ts"), "intent", "switch", f.intent], pd);

  const record = resolveRecordDir(pd, f.space, f.intent);
  const intentId = record.split("/").pop()!;
  const statePath = join(record, "aidlc-state.md");
  const before = checkboxState(readFileSync(statePath, "utf-8"), f.stage);
  if (before === null) die(`Stage ${f.stage} không có trong ${statePath}`);
  if (before !== "?") die(`Stage ${f.stage} đang ở [${before}], không phải [?] awaiting-approval — không có gì để quyết (đã có người khác quyết? pull lại và xem tower)`);

  const raci = raciCheck(pd, f.stage, who);
  const userInput = `${f.input.trim()} — ${actor}`;
  if (f.dryRun) {
    console.log(JSON.stringify({ ok: true, dryRun: true, projectDir: pd, intent: intentId, stage: f.stage, result: f.result, actor, raci: raci.status, userInput }));
    return;
  }

  // 5. HUMAN_TURN qua cùng seam với hook UserPromptSubmit (event reserved với CLI công khai).
  const audit = await import(join(tools, "aidlc-audit.ts"));
  audit.appendAuditEntry("HUMAN_TURN", { Actor: actor, Source: "tower", Stage: f.stage }, pd, intentId, f.space);

  // 6. report — lifecycle transition là engine-owned.
  const rep = run("bun", [join(tools, "aidlc-orchestrate.ts"), "report", "--stage", f.stage, "--result", f.result, "--user-input", userInput], pd, true);
  let repJson: any = null;
  try { repJson = JSON.parse(rep.out.split("\n").pop() ?? ""); } catch { /* engine in text */ }
  if (rep.code !== 0 || (repJson && repJson.kind === "error")) {
    die(`Engine từ chối: ${repJson?.message ?? rep.err ?? rep.out}`);
  }

  // 7. Kiểm state sau.
  const after = checkboxState(readFileSync(statePath, "utf-8"), f.stage);
  if (f.result === "approved" && after !== "x") die(`report nói xong nhưng state là [${after}], không phải [x]`);
  if (f.result === "rejected" && after === "?") die("report nói xong nhưng gate vẫn [?]");

  // 8. Commit là quyết định.
  run("git", ["add", "aidlc"], pd);
  const msg = `decision(${intentId}/${f.stage}): ${f.result} — ${who.name}\n\n${f.input.trim()}\n\nActor: ${actor}\nSource: tower_approve.ts`;
  run("git", ["commit", "--quiet", "-m", msg], pd);
  let pushed = false;
  if (f.push) {
    let p = run("git", ["push", "--quiet"], pd, true);
    if (p.code !== 0) {
      run("git", ["pull", "--rebase", "--quiet"], pd);
      const again = checkboxState(readFileSync(statePath, "utf-8"), f.stage);
      if (f.result === "approved" && again !== "x") die("Sau rebase state không còn [x] — người khác đã đổi gate này; xem lại tower");
      p = run("git", ["push", "--quiet"], pd, true);
      if (p.code !== 0) die(`push thất bại lần 2: ${p.err}`);
    }
    pushed = true;
  }
  const sha = run("git", ["rev-parse", "--short", "HEAD"], pd).out;
  console.log(JSON.stringify({ ok: true, intent: intentId, stage: f.stage, result: f.result, actor, raci: raci.status, state: after, commit: sha, pushed }));
}

if (import.meta.main) await main();
