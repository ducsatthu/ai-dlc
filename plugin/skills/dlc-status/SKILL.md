---
name: dlc-status
description: Báo cáo nhanh trạng thái AI-DLC của project — intents ở stage nào, gate nào đang mở chờ ai, bolts/tasks đang chạy, risks high. Chỉ đọc file, rẻ và nhanh.
---

Chỉ ĐỌC `.ai-dlc/` (status.md các intent, gate queue từ status + inbox chưa xử lý, tasks.md đang active, governance/risks.md) và in báo cáo gọn:
- Mỗi intent 1 dòng: INT · tên · stage/8 · gate_open (+ chờ ai quyết gì)
- Inbox chưa drain (nếu có) — nhắc quyết định đã đến từ tower
- Tasks in-progress/blocked đáng chú ý · risks high
Không sửa gì, không spawn agent.
