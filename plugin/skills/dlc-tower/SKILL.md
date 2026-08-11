---
name: dlc-tower
description: Control Tower — generate dashboard HTML từ .ai-dlc/ (Mission Control + Bản đồ AI-DLC theo white paper) và tùy chọn serve local có nút Approve/Reject ghi vào inbox.
---

1. Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py <project_root>` → `.ai-dlc/tower/index.html`.
2. Args chứa "serve" → chạy nền `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_serve.py <project_root>` (bind 127.0.0.1, in URL kèm token) và arm Monitor watch `.ai-dlc/inbox/*.json` để xử lý quyết định ngay khi tới (ghi DEC, drain sang processed/, chạy tiếp flow).
3. Không serve → mở file tĩnh cũng xem được (không có nút bấm ghi inbox).
4. Orchestrator PHẢI regenerate tower sau mỗi sự kiện (đổi stage, RV mới, gate mở/đóng, task đổi trạng thái).
