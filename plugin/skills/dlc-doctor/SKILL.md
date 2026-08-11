---
name: dlc-doctor
description: Audit sức khỏe AI-DLC của project — override mồ côi/không nguồn gốc, override đã được upstream (gợi ý xóa), lệch version checklist giữa pinned và plugin, inbox tồn đọng, map thiếu mục.
---

Chỉ đọc + báo cáo (sửa gì phải được user đồng ý từng mục):
1. `.ai-dlc/overrides/**`: thiếu frontmatter reason/source → cảnh báo; nội dung ⊆ bản plugin hiện tại → "đã upstream, nên xóa"; xung đột bản mới → in diff.
2. So version checklist: pinned của intent đang chạy vs plugin hiện tại → liệt kê lệch (chỉ thông tin — pinned vẫn thắng trong intent đó).
3. `inbox/` có file chưa processed → nhắc drain. `workspace-map.md` mục null mà flow sắp cần → nhắc.
4. In bảng tổng: OK / WARN / FIX kèm hành động đề xuất.
