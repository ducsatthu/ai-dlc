# Layout config — state của dự án nằm ở đâu, engine nào, tower kiểu gì (7.0.0)

> Tới 6.2.0 mỗi hook/script tự dò `.ai-dlc/context-memory/` theo luật riêng (đi lên 2 cấp, đi lên vô hạn, đi lên 6 cấp cho `aidlc/spaces`…). Dự án đặc thù — template có sẵn `aidlc/spaces/<space>/`, đội đặt state ở thư mục khác, nhiều space trong một repo — không cấu hình được. Từ 7.0.0 **một resolver duy nhất** trả lời câu này: `scripts/layout.py` (python, stdlib) và `scripts/layout.ts` (bun) — cùng luật, cùng kết quả, kiểm chéo bằng `--json`. Mọi hook/script của gói gọi nó; không script nào tự đoán đường dẫn nữa.
> Quyết định chủ gói 2026-09-09: *"ai-dlc đủ linh động để config và hoạt động được với bất kỳ cấu trúc folder nào; tower dùng được tuỳ hiện trạng; config từ file hoặc CLAUDE.md khi cần."*

## 1 · Thứ tự nguồn cấu hình (nguồn trước THẮNG, chỉ key có mặt mới đè)

| # | Nguồn | Khi nào dùng |
|---|---|---|
| 1 | **env** `AI_DLC_CONFIG=<file.json>` · `AI_DLC_ROOT` · `AI_DLC_ENGINE` · `AI_DLC_STATE` · `AI_DLC_SPACE` · `AI_DLC_GOVERNANCE` · `AI_DLC_TOWER_OUT` · `AI_DLC_TOWER_PORT` · `AI_DLC_TOWER_MODE` | một phiên / một máy / CI; ghi đè tạm không đụng repo |
| 2 | **file** `ai-dlc.config.json` hoặc `.ai-dlc/config.json` — tìm từ cwd đi lên (≤ `search_up` cấp, mặc định 6) | dự án đặc thù, commit vào repo — **cách chuẩn** |
| 3 | **fence** ` ```ai-dlc ` trong `CLAUDE.md` hoặc `AGENTS.md` cùng thư mục — thân là JSON, hoặc `key: value` phẳng (key chấm: `tower.port: 8642`) | dự án không muốn thêm file; khai ngay trong tài liệu harness đang có |
| 4 | **tự dò** (không có config): `.ai-dlc/context-memory/` ⇒ engine `ai-dlc` · `aidlc/spaces/` + `.claude/tools/aidlc-audit.ts` ⇒ engine `aws-v2` · `.ai-dlc/` trống tại cwd ⇒ `ai-dlc` (tương thích 6.1) | mọi dự án hiện có — **không phải làm gì**, hành vi cũ giữ nguyên |

Mỗi cấp thư mục thử theo thứ tự file → fence, rồi mới lên cấp cha; tìm thấy config ở đâu thì thư mục đó là gốc mặc định (`root: "."`). Config **thắng** tự dò: nếu thư mục cha có fence mà thư mục con có `.ai-dlc/` riêng, resolver theo fence — muốn con thắng thì đặt config ở con.

## 2 · Key (mọi key tuỳ chọn)

```jsonc
{
  "engine": "auto",            // auto | ai-dlc | aws-v2 | off   — off = gói im lặng hoàn toàn ở dự án này
  "root": ".",                 // thư mục workspace, tương đối với thư mục chứa file config
  "state": ".ai-dlc",          // thư mục state của engine: ai-dlc mặc định ".ai-dlc"; aws-v2 mặc định "aidlc"
  "space": "auto",             // aws-v2: auto = cursor aidlc/active-space → space duy nhất → "default"; hoặc tên space
  "governance": null,          // luật của gói (raci.md · test-viewpoints.md · sizing.md…) — mặc định xem §3
  "tower": { "out": null, "port": null, "mode": "auto" },   // mode: auto | ai-dlc | aws-v2 | off
  "search_up": 6
}
```

Path tương đối với `root`. Không có key nào bắt buộc: file `{}` = tự dò nhưng "gốc là đây".

## 3 · Kết quả resolve — script nào dùng gì

| Trường | engine `ai-dlc` | engine `aws-v2` |
|---|---|---|
| `state` | `<root>/.ai-dlc` (hoặc `state`) | `<root>/aidlc` (hoặc `state`) |
| `context_memory` · `inbox` · `workspace_map` | dưới `state` | — |
| `space` · `space_dir` | — | `<state>/spaces/<space>` |
| `governance` | `<state>/context-memory/governance` | `<root>/.ai-dlc/governance` |
| `tower.out` | `<state>/tower` | `<root>/.ai-dlc/tower` (nên gitignore) |
| `tower.port` | 8642 | 8643 |

| Script / hook | ai-dlc | aws-v2 | off / none |
|---|---|---|---|
| `hooks/session_start.sh` | banner luật + inbox + gate mở (như 6.2.0) | banner ngắn: gói là lớp chính sách, tower_aws_v2, tower_approve | im lặng |
| `hooks/gate_guard.py` | chặn code-write trước Gate D theo `workspace_map` | cho qua (engine AWS có hook riêng) | cho qua |
| `hooks/aws_v2_write_receipt.ts` | no-op | receipt `File` tương đối | no-op |
| `scripts/tower_generate.py` · `tower_serve.py` | tower 6.x tại `tower.out`, port `tower.port` | **tự chuyển sang** `tower_aws_v2.py [--serve]` — một lệnh `/ai-dlc:dlc-tower serve` cho cả hai engine | dừng, không tạo gì |
| `scripts/tower_aws_v2.py` | — | raci từ `governance`, output `tower.out`, port `tower.port`, `mode: off` ⇒ không sinh | — |
| `scripts/tower_approve.ts` | — | root + `space` mặc định + raci từ `governance` (`--space` tường minh vẫn thắng) | — |
| `scripts/session_brief.py` | brief 6.x | in đường dẫn tower_aws_v2 rồi thoát | báo chưa init |

## 4 · Ví dụ

**Template đội (AWS v2, một space)** — không cần config: tự dò ra `aws-v2`, space `default`, governance `.ai-dlc/governance/`.

**Repo có sẵn nhiều space, đặt state ở `docs/aidlc/`** — fence trong `CLAUDE.md`:

````markdown
```ai-dlc
engine: aws-v2
state: docs/aidlc
space: web
governance: docs/governance
tower.port: 9000
```
````

**Một đội nhiều repo, control plane ở thư mục cha, repo con muốn trỏ lên** — `ai-dlc.config.json` trong repo con:

```json
{ "root": "..", "governance": "rules" }
```

**Tắt gói cho một dự án** (repo có `.ai-dlc/` cũ nhưng không dùng nữa): `{"engine": "off"}` — hook im lặng, tower từ chối sinh.

**Kiểm xem gói đang hiểu dự án thế nào:**

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/layout.py --explain       # engine, root, từng path, ghi chú vì sao
bun     ${CLAUDE_PLUGIN_ROOT}/scripts/layout.ts --explain       # phải in y hệt
```

## 5 · Luật khi thêm script/hook mới vào gói

- Không tự dò `.ai-dlc/` hay `aidlc/` — gọi `layout.resolve()` / `resolveLayout()`, rẽ nhánh theo `engine`.
- Sửa luật resolve thì sửa **cả hai** file và chạy kiểm chéo `--json` trên fixture (ai-dlc thường · ai-dlc state tuỳ biến qua file · aws-v2 tự dò · aws-v2 nhiều space có/không cursor · fence key-value · fence JSON · không có gì · `engine: off`).
- Skill (markdown) vẫn viết `.ai-dlc/...` cho dễ đọc; agent lấy đường dẫn thật từ banner `session_start` hoặc `layout.py --explain`, không đoán.
