---
name: dlc-init
description: Khởi tạo AI-DLC cho project hiện tại — seed .ai-dlc/ (context-memory, governance, overrides, inbox) và dựng Workspace Map bằng cách scan repo rồi hỏi user chốt. Idempotent, không overwrite state đã có.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` trước. Các bước:

0. (6.3.0) Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/layout.py --explain` trước. Engine `aws-v2` (workspace có
   `aidlc/spaces/` — template của đội) ⇒ **KHÔNG tạo `.ai-dlc/context-memory`**; chỉ tạo `<governance>/raci.md` từ
   `templates/raci.md` nếu thiếu và nhắc gitignore `.ai-dlc/tower/`, rồi dừng. Engine `off` ⇒ dừng. Dự án muốn state
   ở chỗ khác `.ai-dlc/` (ví dụ `docs/state`) ⇒ hỏi user rồi ghi `ai-dlc.config.json` (`templates/ai-dlc.config.json`)
   hoặc fence ```` ```ai-dlc ```` trong CLAUDE.md, và dùng đường dẫn `state` đó cho mọi bước dưới thay vì `.ai-dlc/`.
1. Nếu `.ai-dlc/` đã tồn tại → KHÔNG overwrite; báo trạng thái hiện có và dừng (chỉ bổ sung file thiếu).
2. Tạo cây thư mục theo protocol §3 (gồm `context-memory/handoffs/`, `context-memory/session/log/` và `context-memory/escalations/` — chỗ cho phát hiện ngoài phạm vi unit, §4.13). Seed từ `${CLAUDE_PLUGIN_ROOT}/templates/`: `governance/dor.md`, `governance/dod.md`, `governance/sizing.md` (núm `unit_max_hours`, mặc định `null` = không trần — §4.9 v5), `overrides/OVERRIDES.md`, `session/INDEX.md` (từ `context-index.md`); tạo rỗng: `governance/decisions-log.md`, `changelog.md`, `risks.md`, `tech-debt-register.md`.
3. **Space trước, map sau** (6.2.0 — một `.ai-dlc/` = một space, protocol §3). Hỏi user **đúng một câu**:
   *"Đội nào duyệt thay đổi ở các vùng code này? Cùng một nhóm người duyệt cho mọi vùng ⇒ một `.ai-dlc/` ở đây.
   Hai nhóm có practice/approval riêng ⇒ mỗi nhóm một `.ai-dlc/` tại thư mục họ sở hữu — dừng, init lại ở đó."*
   Không hỏi "frontend hay backend", không hỏi "mấy repo". Nếu cwd chứa nhiều git repo con của **cùng một
   đội** (`hrm-web/ hrm-api/…`) → `.ai-dlc/` đặt ngay tại cwd (thư mục cha), `repos:` liệt kê từng repo.
   **Workspace Map v2**: scan (thư mục code theo họ: domain/api/web/mobile/infra, wiki/docs, swagger, tests,
   `.git` con, CLAUDE.md/AGENTS.md của dự án) → điền `templates/workspace-map.md`: `repos:` (id + path) ·
   `areas:` (tên tự do, mỗi area `repo` + `path` + `tests`, path **tương đối với thư mục chứa `.ai-dlc/`**) ·
   `code:`/`tests:` (tương thích 6.x, suy từ areas) · `docs:` → **trình user xác nhận/sửa từng mục** (không
   tồn tại để null). User mô tả thêm bằng lời → ghi vào map. Ghi `.ai-dlc/workspace-map.md`. Tạo thêm
   `.ai-dlc/codekb/` (rỗng — được điền khi intent đầu tiên đóng).
4. Gợi ý `.gitignore`: đơn giản nhất `.ai-dlc/`; hoặc commit chọn lọc (giữ overrides/ + governance/ + decisions + lessons, ignore tower/ + comms/).
5. Ghi 1 dòng vào `.ai-dlc/context-memory/governance/changelog.md`: init bởi plugin version nào, ngày nào.
6. Kết thúc: in hướng dẫn bước tiếp theo (`/ai-dlc:dlc-intent "<yêu cầu>"`), và nhắc rằng phiên sau vào lại dự án bằng `/ai-dlc:dlc-resume` (không phải đọc lại từ đầu).
