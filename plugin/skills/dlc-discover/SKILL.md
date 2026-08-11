---
name: dlc-discover
description: Stage 2 AI-DLC — Context Discovery (brown-field) sau khi Gate A approve. Dựng AS-IS model tĩnh + động từ code/docs/tests/DB rồi chuyển sang validate.
---

Điều kiện: `gates_passed` chứa A (kiểm tra status.md — chưa có thì dừng, nêu gate đang chờ).
1. Ghi DEC Gate A nếu vừa nhận quyết định từ user/inbox.
2. Spawn `ai-dlc:dlc-context-archaeologist` cho INT đang mở → `as-is/` (static, dynamic, decisions-inventory).
3. Cập nhật status (stage 2 → 3), tower. Green-field thuần: ghi as-is tối giản (repo trống/chưa liên quan) và chuyển thẳng.
4. Đề xuất bước kế: `/dlc-validate`.
