---
name: dlc-intent
description: Bắt đầu một Intent AI-DLC mới từ yêu cầu của user (stage 1 · Inception) — tạo INT-NNN, snapshot pinned, phân tích intent, decision brief, mở Gate A rồi DỪNG chờ duyệt.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md`. Yêu cầu `.ai-dlc/` đã init (chưa có → chạy dlc-init trước).

1. Cấp ID `INT-NNN` kế tiếp; tạo cây `intents/INT-NNN/` + `status.md` từ template.
2. **Pinned snapshot**: copy toàn bộ `${CLAUDE_PLUGIN_ROOT}/skills/checklists/*` + `governance/dor.md,dod.md` (SAU khi áp `.ai-dlc/overrides/`) vào `intents/INT-NNN/pinned/`.
3. Spawn agent `ai-dlc:dlc-intent-analyst` với yêu cầu của user → `intent.md`.
4. Spawn agent `ai-dlc:dlc-ba-reviewer` → review intent theo checklist pinned + soạn `decision-briefs/brief-A.md`.
5. Mở **Gate A** theo nghi thức protocol §2 (status, tower regenerate, PushNotification nếu phù hợp) — trình bày decision brief + các điểm cần confirm, rồi **KẾT THÚC LƯỢT**. Không chạy stage 2 khi chưa có quyết định.
