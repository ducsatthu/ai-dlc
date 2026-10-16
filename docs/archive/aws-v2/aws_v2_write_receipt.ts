#!/usr/bin/env bun
// aws_v2_write_receipt.ts — PostToolUse (Write|Edit|MultiEdit|NotebookEdit) hook của gói ai-dlc,
// chạy KÈM hook của workspace AWS aidlc-workflows v2, không thay nó.
//
// Vì sao có hook này (docs/spikes/aws-v2-cross-clone-approval.md, kết luận #2): hook gốc
// `.claude/hooks/aidlc-write-audit-log.ts` ghi receipt ARTIFACT_CREATED|UPDATED với trường `File`
// là ĐƯỜNG DẪN TUYỆT ĐỐI của máy ghi. Guard "artifact phải được ghi lại sau khi người xác nhận
// tóm tắt" so `resolvePath(projectDir, File)` ⇒ trên clone khác không bao giờ khớp ⇒ gate không
// duyệt được từ máy khác. Guard đã nhận đường dẫn tương đối; hook này ghi thêm MỘT receipt với
// `File` tương đối (cùng seam appendAuditEntry của workspace, cùng Tool/Context), để mọi clone
// đều xác thực được. Không sửa gì trong repo template của đội — chủ gói quyết 2026-09-03.
//
// Fail-open triệt để: không phải workspace AWS v2 / không có audit shard / file ngoài record+codekb /
// import lỗi ⇒ exit 0 không in gì. Tắt: AI_DLC_AWS_RECEIPT=off.
import { existsSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { resolveLayout } from "../scripts/layout.ts";

async function main(): Promise<number> {
  if (process.env.AI_DLC_AWS_RECEIPT === "off") return 0;
  if (process.stdin.isTTY) return 0;
  let parsed: any;
  try { parsed = JSON.parse(await Bun.stdin.text()); } catch { return 0; }
  const tool: string = parsed?.tool_name ?? "";
  const file: string = parsed?.tool_input?.file_path ?? parsed?.tool_input?.notebook_path ?? "";
  if (!file) return 0;

  const projectDir = findProjectDir(parsed?.cwd);
  if (!projectDir) return 0;
  const tools = join(projectDir, ".claude", "tools");

  let lib: any, audit: any;
  try {
    lib = await import(join(tools, "aidlc-lib.ts"));
    audit = await import(join(tools, "aidlc-audit.ts"));
  } catch { return 0; }

  const abs = (isAbsolute(file) ? file : resolve(projectDir, file)).replace(/\\/g, "/");
  let recordRoot: string, codekbRoot: string, auditFile: string;
  try {
    recordRoot = String(lib.docsRoot(projectDir)).replace(/\\/g, "/").replace(/\/$/, "");
    codekbRoot = join(lib.codekbDir(projectDir, "_"), "..").replace(/\\/g, "/").replace(/\/$/, "");
    auditFile = lib.auditFilePath(projectDir);
  } catch { return 0; }
  const underRecord = abs === recordRoot || abs.startsWith(`${recordRoot}/`);
  const underCodekb = abs.startsWith(`${codekbRoot}/`);
  if (!underRecord && !underCodekb) return 0;
  if (/[/\\]audit[/\\][^/\\]+\.md$/.test(abs)) return 0; // recursion guard: không ghi receipt cho shard
  if (!existsSync(auditFile)) return 0; // orchestrator tạo ledger lúc bắt đầu workflow; không tự tạo

  const context = underRecord && abs.length > recordRoot.length
    ? abs.slice(recordRoot.length + 1).replace(/\//g, " > ")
    : `codekb > ${abs.slice(codekbRoot.length + 1).replace(/\//g, " > ")}`;

  let eventType = "ARTIFACT_UPDATED";
  if (tool !== "Edit" && tool !== "MultiEdit") {
    try { const st = statSync(abs); if (Math.abs(st.mtimeMs - st.birthtimeMs) < 10) eventType = "ARTIFACT_CREATED"; }
    catch { eventType = "ARTIFACT_CREATED"; }
  }
  const relFile = relative(projectDir, abs).replace(/\\/g, "/");
  try {
    audit.appendAuditEntry(eventType, { Tool: tool, File: relFile, Context: context, Receipt: "ai-dlc:relative" }, projectDir);
  } catch { return 0; }
  return 0;
}

// Workspace AWS v2 = thư mục có aidlc/spaces + .claude/tools/aidlc-audit.ts. Ưu tiên
// AIDLC_PROJECT_DIR, rồi CLAUDE_PROJECT_DIR, rồi cwd của hook đi lên tối đa 6 cấp.
function findProjectDir(hookCwd?: string): string | null {
  // 6.3.0: layout.ts (config file · fence CLAUDE.md · env · tự dò) — engine khác aws-v2 ⇒ không phải việc của hook này
  try {
    const lay = resolveLayout(process.env.AIDLC_PROJECT_DIR || process.env.CLAUDE_PROJECT_DIR || hookCwd || process.cwd());
    if (lay.engine === "aws-v2") return lay.root;
    if (lay.engine === "ai-dlc" || lay.engine === "off") return null;
  } catch { /* fallback */ }
  const isWs = (d: string) => existsSync(join(d, "aidlc", "spaces")) && existsSync(join(d, ".claude", "tools", "aidlc-audit.ts"));
  for (const env of [process.env.AIDLC_PROJECT_DIR, process.env.CLAUDE_PROJECT_DIR]) {
    if (env && isWs(resolve(env))) return resolve(env);
  }
  let d = resolve(hookCwd || process.cwd());
  for (let i = 0; i < 6; i++) {
    if (isWs(d)) return d;
    const up = dirname(d); if (up === d) break; d = up;
  }
  return null;
}

process.exit(await main());
