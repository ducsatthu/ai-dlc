---
name: dlc-retro
description: Learning loop AI-DLC — retro sau release (hoặc theo yêu cầu): rút lesson learned từ dấu vết intent, đề xuất patch checklist/DoD, mở Gate G rồi DỪNG; approve thì apply vào overrides + nhắc contribute.
---

1. Spawn `ai-dlc:dlc-retro-keeper` cho intent vừa đóng (hoặc intent user chỉ định) → LL-NNN + patch đề xuất (diff cụ thể, version cũ→mới).
2. Mở **Gate G**, DỪNG (trình LL + patch).
3. Approve → DEC; apply patch vào `.ai-dlc/overrides/` (mode patch, frontmatter source: LL-NNN); tăng version + changelog governance; cập nhật OVERRIDES.md index; nhắc `/dlc-contribute` nếu lesson mang tính chuẩn chung.
