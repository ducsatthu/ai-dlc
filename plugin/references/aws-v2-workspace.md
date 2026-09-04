# Workspace AWS `aidlc-workflows` v2 — cấu trúc gói `ai-dlc` đọc và ghi (phương án A)

> Từ 2026-09-03 gói `ai-dlc` là **lớp chính sách + tower TRÊN engine AWS v2** đã vendor trong template khởi tạo dự án của đội (upstream `awslabs/aidlc-workflows` 2.5.75). Gói **không sửa** template; mọi thứ gói cần đều nằm trong plugin (hook, script, tower). File này là bản đồ cấu trúc đó — mọi script/skill của gói resolve đường dẫn theo đây, không đoán.
> Nguồn: đọc trực tiếp `.claude/tools/aidlc-lib.ts` (`discoverSiblingRepos`, `docsRoot`, `auditFilePath`, `humanActedSinceGate`…) và spike `docs/spikes/aws-v2-cross-clone-approval.md`.

## 1 · Một workspace = một git repo

```
<workspace>/                      # git repo riêng của đội — CONTROL PLANE, commit thẳng = quyết định
├── AGENTS.md  CLAUDE.md          # CLAUDE.md = "@AGENTS.md"; profile Lite|Standard, Review Mode
├── .claude/                      # harness Claude: hooks/ tools/ skills/ (40 aidlc-*) agents/ aidlc-common/ settings.json
├── .codex/  .agents/             # harness Codex + hook chung (git/secret guardrails)
├── docs/                         # AS-IS ĐÃ KIỂM CHỨNG (index · product · architecture · operations · decisions/)
├── aidlc/                        # STATE ENGINE — xem mục 2
├── sources/                      # code: một thư mục mỗi deliverable (backend/ frontend/ mobile/ infra/ docs-site/)
│   └── aidlc-integration/        # upstream-lock.json · runtime-manifest.json · plugins/ · tools/vendor-aidlc.sh · validate_aidlc.py
└── <repo-con>/                   # (tuỳ chọn) repo git riêng KÉO VỀ làm thư mục con — engine tự phát hiện, gitignored
```

- **Sibling repo**: mọi thư mục con trực tiếp có `.git` (trừ `aidlc/ .git/ .ai-dlc/ node_modules/` và thư mục harness) được `discoverSiblingRepos` coi là repo code. `repos.json` (`{org, repos:[{name,url,branch}]}`) + `aidlc-workspace-sync.ts` clone đúng bộ trên máy mới, sinh khối `.gitignore` quản lý + file VSCode multi-root. Disk thắng manifest lúc chạy.
- Gói `ai-dlc` tìm workspace bằng: `AIDLC_PROJECT_DIR` → `CLAUDE_PROJECT_DIR` → cwd đi lên ≤ 6 cấp, điều kiện `aidlc/spaces/` **và** `.claude/tools/aidlc-audit.ts`.

## 2 · `aidlc/` — state engine

```
aidlc/
├── active-space                  # IGNORED — cursor per clone
├── .aidlc-clone-id               # IGNORED — 12 hex, mint lần đầu; đặt tên shard audit
├── .aidlc-sessions/              # IGNORED
└── spaces/<space>/               # mặc định `default`
    ├── memory/ org.md team.md project.md phases/<phase>.md templates/   # LUẬT: org → team → project → phase, additive
    ├── knowledge/                # tham khảo (không phải luật)
    ├── codekb/<repo>/            # bản đồ code bền vững
    └── intents/
        ├── intents.json          # registry (COMMIT)
        ├── active-intent         # IGNORED — cursor per clone; không có ⇒ engine lấy intent duy nhất
        └── <YYMMDD-slug>/        # RECORD của một intent (COMMIT)
            ├── aidlc-state.md    # MỘT file: Stage Progress checkbox, Current Stage, Next Action, Autonomy Mode
            ├── audit/<host>-<clone-id>.md   # MỘT shard MỖI CLONE, append-only — merge git không conflict
            ├── ideation/ inception/ construction/<unit>/ operation/ verification/   # artifact theo stage
            ├── runtime-graph.json  .aidlc-*   # IGNORED
            └── …
```

### 2.1 Checkbox trong `aidlc-state.md` (gói đọc để sinh thẻ)

| Ký hiệu | Nghĩa | Thẻ tower |
|---|---|---|
| `- [ ] <slug>` | pending | — |
| `- [-] <slug>` | in progress (`EXECUTE`) | *Đang làm* (Tra cứu) |
| `- [?] <slug>` | **awaiting-approval — GATE MỞ** | **Cần tôi quyết** |
| `- [x] <slug>` | done | — |
| `- [S] <slug>` | skipped | — |

### 2.2 Event audit gói quan tâm (block markdown, `**Event**: …`, tách bằng `---`)

| Event | Ai ghi | Gói dùng để |
|---|---|---|
| `HUMAN_TURN` | hook `UserPromptSubmit` (fields `{}`), **hoặc `tower_approve.ts` với `Actor`/`Source: tower`** | presence guard; gói đọc `Actor` để biết **ai** |
| `STAGE_AWAITING_APPROVAL` → `GATE_APPROVED` / `GATE_REJECTED` (`User Input`) | engine qua `report` | thẻ đóng; `User Input` chứa `— <tên> <email>` do gói nối vào |
| `DECISION_RECORDED` / `QUESTION_ANSWERED` / `SUMMARY_CONFIRMATION_RECORDED` | `aidlc-log.ts decision|answer` | thẻ *Cần tôi trả lời*; xác nhận tóm tắt = Preview→Confirm |
| `REVIEW_REQUESTED` / `REVIEW_COMPLETED` (`Reviewer`, `Verdict`, `Iteration`) | `aidlc-log.ts review` | tầng review; thẻ *Cần tôi kiểm* khi reviewer là người |
| `ARTIFACT_CREATED` / `ARTIFACT_UPDATED` (`Tool`, `File`, `Context`) | hook `PostToolUse` (File **tuyệt đối**) + **hook gói `aws_v2_write_receipt.ts` (File tương đối, `Receipt: ai-dlc:relative`)** | receipt ghi-sau-xác-nhận hợp lệ trên mọi clone |
| `ERROR_LOGGED` | engine | doctor của gói |

## 3 · Guard engine trước một gate (thứ tự, theo spike)

1. Artifact `produces` tồn tại dưới record dir của stage.
2. Xác nhận tóm tắt: `decision --checkpoint summary-confirmation` khi `[Answer]:` **trống** → người điền `Looks correct` → `HUMAN_TURN` → `answer --details "Looks correct"`; file câu hỏi **khoá hash** từ đây.
3. Mỗi artifact có receipt ghi **sau** xác nhận (mục 2.2 — lý do có hook gói).
4. Stage khai `reviewer` ⇒ `REVIEW_REQUESTED` → `REVIEW_COMPLETED --verdict READY|NOT-READY --iteration n`.
5. `report --result awaiting-approval` ⇒ `[?]`.
6. Approve: `HUMAN_TURN` **sau** resolution gần nhất trên **mọi shard** (engine không kiểm *ai* — gói kiểm) → `report --result approved --user-input "<lời người>"` ⇒ `[x]`, `Current Stage` nhảy.

Lifecycle chỉ qua `aidlc-orchestrate.ts next|report|park` — gọi thẳng `aidlc-state.ts approve|gate-start` bị chặn.

## 4 · Gói `ai-dlc` đặt gì ở đâu (không đụng template)

| Thứ | Ở gói | Chạy khi |
|---|---|---|
| Hook receipt tương đối | `hooks/aws_v2_write_receipt.ts` (`PostToolUse Write|Edit|MultiEdit|NotebookEdit`) | mọi lần dev ghi artifact trong phiên Claude — fail-open nếu không phải workspace AWS v2 |
| Nút quyết định | `scripts/tower_approve.ts --stage --result --input` — kiểm RACI `.ai-dlc/governance/raci.md` trước | máy người duyệt, ngoài phiên |
| Tower | `scripts/tower_aws_v2.py [--serve]` đọc `aidlc-state.md` + `audit/*.md` → ba loại thẻ theo vai người xem; sinh `.ai-dlc/tower/` (gitignore) | máy bất kỳ; nút *Kéo mới* = `git pull --rebase` |
| Governance của gói | `<workspace>/.ai-dlc/governance/raci.md` (template `templates/raci.md`; sau này test-viewpoints, sizing, LL) — engine AWS đã loại `.ai-dlc` khỏi sibling discovery | đội commit |
| Luật của gói (Tester, im lặng = mặc định, Gate R 6 dòng, LL) | (7.0.0) sinh vào `aidlc/spaces/<space>/memory/team.md` `## Mandated` + plugin `sources/aidlc-integration/plugins/` | khi đội bật |

Đường dẫn ghi vào audit/state của gói: **luôn tương đối với workspace**, không bao giờ tuyệt đối (ca gốc: kết luận #2 spike).
