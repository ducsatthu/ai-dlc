# Layout config: state của dự án nằm ở đâu, engine nào, tower kiểu gì

Tới 6.2.0 mỗi hook và script tự dò `.ai-dlc/context-memory/` theo luật riêng (đi lên 2 cấp, đi lên vô hạn, đi lên 6 cấp cho `aidlc/spaces`). Dự án đặc thù, như template của đội, đội đặt state ở thư mục khác, hay nhiều space trong một repo, không cấu hình được. Từ 6.3.0 một resolver duy nhất trả lời câu này: `scripts/layout.py` (python, stdlib) và `scripts/layout.ts` (bun). Hai bản cùng luật, cùng kết quả, kiểm chéo bằng `--json`. Mọi hook và script của gói gọi nó.

Quyết định chủ gói 2026-09-09: "ai-dlc đủ linh động để config và hoạt động được với bất kỳ cấu trúc folder nào; tower dùng được tuỳ hiện trạng; config từ file hoặc CLAUDE.md khi cần."

7.0.0-a (2026-10-16): template của đội không còn chạy AWS v2 mà chạy engine tự viết (`.agents/skills/aidlc/`, change là `docs/intents/NNNN-name/` bốn file). Resolver thêm engine `contracts`. Engine `aws-v2` vẫn dò ra để báo nhưng đã archive (`docs/archive/aws-v2/`), không script nào chạy trên nó. Căn cứ: `docs/template-contracts-engine-vs-ai-dlc.md`.

## 1. Thứ tự nguồn cấu hình

Nguồn trước thắng. Chỉ key có mặt mới đè.

| # | Nguồn | Khi nào dùng |
|---|---|---|
| 1 | env `AI_DLC_CONFIG=<file.json>`, `AI_DLC_ROOT`, `AI_DLC_ENGINE`, `AI_DLC_STATE`, `AI_DLC_SPACE`, `AI_DLC_GOVERNANCE`, `AI_DLC_TOWER_OUT`, `AI_DLC_TOWER_PORT`, `AI_DLC_TOWER_MODE` | một phiên, một máy, CI; ghi đè tạm không đụng repo |
| 2 | file `ai-dlc.config.json` hoặc `.ai-dlc/config.json`, tìm từ cwd đi lên (tối đa `search_up` cấp, mặc định 6) | dự án đặc thù, commit vào repo. Đây là cách chuẩn |
| 3 | fence ` ```ai-dlc ` trong `CLAUDE.md` hoặc `AGENTS.md` cùng thư mục; thân là JSON hoặc `key: value` phẳng (key chấm: `tower.port: 8642`) | dự án không muốn thêm file |
| 4 | tự dò khi không có config, tại mỗi cấp theo thứ tự: `.ai-dlc/context-memory/` là `ai-dlc`; bộ ba `.agents/skills/aidlc/SKILL.md`, `docs/memory/project.md`, `docs/intents/_templates/intent.md` là `contracts` (đúng bộ ba `start_change.py` của đội dùng); `aidlc/spaces/` kèm `.claude/tools/aidlc-audit.ts` là `aws-v2` (archive); `.ai-dlc/` trống tại cwd là `ai-dlc` (tương thích 6.1) | mọi dự án hiện có, không phải làm gì |

Mỗi cấp thư mục thử file rồi fence, rồi mới lên cấp cha. Tìm thấy config ở đâu thì thư mục đó là gốc mặc định (`root: "."`). Config thắng tự dò. Một thư mục vừa có `.ai-dlc/context-memory/` vừa là workspace `contracts` thì `ai-dlc` thắng, nhưng `notes` cảnh báo hai nguồn sự thật (doctor `D01`). Đặt `engine: contracts` hoặc `engine: off` để chốt.

## 2. Key

Mọi key tuỳ chọn.

```jsonc
{
  "engine": "auto",            // auto | ai-dlc | contracts | aws-v2 | off   (off = gói im lặng hoàn toàn ở dự án này)
  "root": ".",                 // thư mục workspace, tương đối với thư mục chứa file config
  "state": ".ai-dlc",          // thư mục state của engine: ai-dlc ".ai-dlc", contracts "docs/intents", aws-v2 "aidlc"
  "space": "auto",             // aws-v2 (archive): auto = cursor aidlc/active-space, rồi space duy nhất, rồi "default"
  "governance": null,          // luật của gói (sizing.md, autopilot.md, raci.md); mặc định xem §3
  "tower": { "out": null, "port": null, "mode": "auto" },   // mode: auto | ai-dlc | contracts | aws-v2 | off
  "search_up": 6
}
```

Path tương đối với `root`. File `{}` nghĩa là tự dò nhưng gốc là đây.

## 3. Kết quả resolve và script nào dùng gì

| Trường | engine `ai-dlc` | engine `contracts` | engine `aws-v2` (archive) |
|---|---|---|---|
| `state` | `<root>/.ai-dlc` (hoặc `state`) | `<root>/docs/intents` (hoặc `state`) | `<root>/aidlc` |
| `context_memory`, `inbox`, `workspace_map` | dưới `state` | không có | không có |
| `skill`, `memory` | không có | `<root>/.agents/skills/aidlc`, `<root>/docs/memory` | không có |
| `space`, `space_dir` | không có | không có | `<state>/spaces/<space>` |
| `governance` | `<state>/context-memory/governance` | `<root>/.ai-dlc/governance` (gói ghi; luật của đội ở `docs/memory/`, chỉ đọc) | `<root>/.ai-dlc/governance` |
| `tower.out` | `<state>/tower` | `<root>/.ai-dlc/tower` (nên gitignore) | không có |
| `tower.port` | 8642 | 8644 | 8643 |

| Script hoặc hook | ai-dlc | contracts | aws-v2, off, none |
|---|---|---|---|
| `hooks/session_start.sh` | banner luật, inbox, gate mở (như 6.2.0) | banner ngắn: lifecycle của đội, gói chỉ đọc, never infer approval; rồi `contracts_brief.py --short` | aws-v2: một dòng "đã archive". off, none: im lặng |
| `hooks/gate_guard.py` | chặn code-write trước Gate D theo `workspace_map` | cho qua (template có hook riêng `.agents/hooks/`) | cho qua |
| `hooks/observe.py` (7.0.0-a; SessionStart, PostToolUse `Bash|Write|Edit|MultiEdit`, Stop, SessionEnd) | ghi `<state>/log/YYYY-MM.jsonl` | ghi `<root>/.ai-dlc/log/YYYY-MM.jsonl`: validator, approvals.py, lệnh test (2 token và đỏ/xanh), file sửa trong `docs/intents/`, lượt. Không ghi nội dung, không ghi lệnh đầy đủ. `AI_DLC_OBSERVE=off` để tắt | im lặng |
| `scripts/session_brief.py` | brief 6.x | chuyển sang `contracts_brief.py` (`--json`, `--short`, `--doctor`, `--no-validate` đi theo) | aws-v2: báo archive. none: báo chưa init |
| `scripts/contracts_brief.py` (7.0.0-a) | không có | đọc bốn file mỗi change, `approvals.json` (băm SHA-256 như `approvals.py`), git, và chạy `validate_workflow.py` của đội ở stage suy ra (`draft`, `execute`, `outcome`, `merge`). `--doctor` mã `D01` đến `D21`, exit 1 khi FIX | exit 2 |
| `scripts/contracts_retro.py` (7.0.0-a) | không có | đọc `approvals.json`, `evidence.md`, log; ra ứng viên LL `R01` đến `R05`, `X01`; `--write` ghi `<governance>/lessons-learned/candidates.md` | exit 2 |
| `scripts/tower_generate.py`, `tower_serve.py` | tower 6.x tại `tower.out`, port `tower.port` | dừng và chỉ đường sang `contracts_brief.py` (tower cho engine này chưa có ở lát a) | dừng |

## 4. Ví dụ

Template đội (engine `contracts`): không cần config. Tự dò ra `contracts`, `state` là `docs/intents`, `governance` là `.ai-dlc/governance/`. Kiểm bằng `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/layout.py --explain`, phải in `engine: contracts`.

Repo có sẵn `.ai-dlc/` cũ nhưng nay chạy engine của đội, chốt bằng `ai-dlc.config.json`:

```json
{ "engine": "contracts" }
```

Repo ai-dlc đặt state ở `docs/aidlc/`, dùng fence trong `CLAUDE.md`:

````markdown
```ai-dlc
engine: ai-dlc
state: docs/aidlc
tower.port: 9000
```
````

Một đội nhiều repo, control plane ở thư mục cha, repo con muốn trỏ lên, dùng `ai-dlc.config.json` trong repo con:

```json
{ "root": "..", "governance": "rules" }
```

Tắt gói cho một dự án có `.ai-dlc/` cũ không dùng nữa: `{"engine": "off"}`. Hook im lặng, tower từ chối sinh.

Kiểm xem gói đang hiểu dự án thế nào:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/layout.py --explain       # engine, root, từng path, ghi chú vì sao
bun     ${CLAUDE_PLUGIN_ROOT}/scripts/layout.ts --explain       # phải in y hệt
```

## 5. Luật khi thêm script hoặc hook mới vào gói

- Không tự dò `.ai-dlc/`, `docs/intents/` hay `aidlc/`. Gọi `layout.resolve()` hoặc `resolveLayout()` rồi rẽ nhánh theo `engine`.
- Sửa luật resolve thì sửa cả hai file và chạy `python3 -m unittest tests.test_layout`. Fixture: ai-dlc thường, state tuỳ biến qua file, contracts tự dò, contracts từ thư mục con, hai engine cùng chỗ, aws-v2 tự dò, nhiều space, fence key-value, fence JSON, không có gì, `engine: off`.
- Skill (markdown) vẫn viết `.ai-dlc/...` cho dễ đọc. Agent lấy đường dẫn thật từ banner `session_start` hoặc `layout.py --explain`, không đoán.
- Ở engine `contracts` gói chỉ đọc: không ghi vào `docs/intents/`, không gọi `approvals.py`. Thứ gì muốn đội đổi thì thành đề xuất (`docs/template-contracts-engine-vs-ai-dlc.md` §7).
