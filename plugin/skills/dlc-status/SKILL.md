---
name: dlc-status
description: Báo cáo nhanh trạng thái AI-DLC của project — intents ở stage nào, gate nào đang mở chờ ai, ai đang giữ việc gì (bảng vị trí từ handoffs), coverage nguồn, unit lỗi DoR, inbox tồn. Chỉ đọc, rẻ và nhanh.
---

Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_brief.py <project_root>` và thuật lại stdout.
Script làm toàn bộ phần quét (frontmatter status.md · `handoffs/` · `inbox/` · session log) và kết xuất lại
`context-memory/session/board.md` — **đừng tự đi đọc lại các file đó** (protocol §10).

Báo cáo gồm:
- Mỗi intent 1 dòng: INT · tên · stage/8 · gate_open (+ **gate_doc** đang chờ đọc, chờ ai quyết gì)
- **Vị trí đang làm việc**: HOF nào `accepted`/`open`/`returned`, ai giữ, thuộc phạm vi nào, từ bao giờ
- Coverage nguồn: đã đọc bao nhiêu / tổng — còn `planned` thì nêu rõ (đang chặn gate nào)
- Units: số Unit · tổng est (h) · Unit nào >5h hoặc thiếu US/NFR/risk
- Inbox chưa drain (nếu có) — nhắc quyết định đã đến từ tower
- Cảnh báo: HOF `accepted` treo lâu (phiên trước có thể chết giữa chừng), gate thiếu gate_doc

Không sửa gì, không spawn agent. Muốn **vào việc** chứ không chỉ xem thì dùng `/dlc-resume`.
