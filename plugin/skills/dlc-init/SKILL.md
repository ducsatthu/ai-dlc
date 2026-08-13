---
name: dlc-init
description: Khởi tạo AI-DLC cho project hiện tại — seed .ai-dlc/ (context-memory, governance, overrides, inbox) và dựng Workspace Map bằng cách scan repo rồi hỏi user chốt. Idempotent, không overwrite state đã có.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` trước. Các bước:

1. Nếu `.ai-dlc/` đã tồn tại → KHÔNG overwrite; báo trạng thái hiện có và dừng (chỉ bổ sung file thiếu).
2. Tạo cây thư mục theo protocol §3 (gồm `context-memory/handoffs/`, `context-memory/session/log/` và `context-memory/escalations/` — chỗ cho phát hiện ngoài phạm vi unit, §4.13). Seed từ `${CLAUDE_PLUGIN_ROOT}/templates/`: `governance/dor.md`, `governance/dod.md`, `governance/sizing.md` (núm `unit_max_hours`, mặc định `null` = không trần — §4.9 v5), `overrides/OVERRIDES.md`, `session/INDEX.md` (từ `context-index.md`); tạo rỗng: `governance/decisions-log.md`, `changelog.md`, `risks.md`, `tech-debt-register.md`.
3. **Workspace Map**: scan repo (thư mục code FE/BE, wiki/docs, swagger, tests, đọc CLAUDE.md/AGENTS.md của dự án nếu có) → điền `templates/workspace-map.md` thành đề xuất → **trình user xác nhận/sửa từng mục** (mục không tồn tại để null). User mô tả thêm bằng lời → ghi vào map. Ghi file `.ai-dlc/workspace-map.md`.
4. Gợi ý `.gitignore`: đơn giản nhất `.ai-dlc/`; hoặc commit chọn lọc (giữ overrides/ + governance/ + decisions + lessons, ignore tower/ + comms/).
5. Ghi 1 dòng vào `.ai-dlc/context-memory/governance/changelog.md`: init bởi plugin version nào, ngày nào.
6. Kết thúc: in hướng dẫn bước tiếp theo (`/dlc-intent "<yêu cầu>"`), và nhắc rằng phiên sau vào lại dự án bằng `/dlc-resume` (không phải đọc lại từ đầu).
