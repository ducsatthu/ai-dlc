---
name: dlc-map
description: Xem hoặc cập nhật Workspace Map của project (.ai-dlc/workspace-map.md). Mọi thay đổi map là một DEC và ghi changelog trong file map.
---

1. Không có args → in map hiện tại + các mục null.
2. User mô tả thay đổi bằng lời → cập nhật đúng mục YAML, thêm dòng Changelog trong file, append DEC vào `governance/decisions-log.md` (người quyết: HUMAN).
3. Nhắc: agents chỉ resolve path qua map — mục null mà flow cần tới thì agent sẽ hỏi, không đoán.
