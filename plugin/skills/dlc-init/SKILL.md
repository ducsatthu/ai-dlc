---
name: dlc-init
description: Khởi tạo AI-DLC cho project hiện tại — seed .ai-dlc/ (context-memory, governance, overrides, inbox) và dựng Workspace Map bằng cách scan repo rồi hỏi user chốt. Idempotent, không overwrite state đã có.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` trước. Các bước:

1. Nếu `.ai-dlc/` đã tồn tại → KHÔNG overwrite; báo trạng thái hiện có và dừng (chỉ bổ sung file thiếu).
2. Tạo cây thư mục theo protocol §3. Seed từ `${CLAUDE_PLUGIN_ROOT}/templates/`: `governance/dor.md`, `governance/dod.md`, `overrides/OVERRIDES.md`; tạo rỗng: `governance/decisions-log.md`, `changelog.md`, `risks.md`, `tech-debt-register.md`.
3. **Workspace Map**: scan repo (thư mục code FE/BE, wiki/docs, swagger, tests, đọc CLAUDE.md/AGENTS.md của dự án nếu có) → điền `templates/workspace-map.md` thành đề xuất → **trình user xác nhận/sửa từng mục** (mục không tồn tại để null). User mô tả thêm bằng lời → ghi vào map. Ghi file `.ai-dlc/workspace-map.md`.
4. Gợi ý `.gitignore`: đơn giản nhất `.ai-dlc/`; hoặc commit chọn lọc (giữ overrides/ + governance/ + decisions + lessons, ignore tower/ + comms/).
5. Ghi 1 dòng vào `.ai-dlc/context-memory/governance/changelog.md`: init bởi plugin version nào, ngày nào.
6. Kết thúc: in hướng dẫn bước tiếp theo (`/dlc-intent "<yêu cầu>"`).
