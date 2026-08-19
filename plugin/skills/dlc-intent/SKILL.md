---
name: dlc-intent
description: Bắt đầu một Intent AI-DLC mới từ yêu cầu của user (stage 1 · Inception) — tạo INT-NNN, snapshot pinned, dựng intent-plan.md hoàn chỉnh (Intent + Source Reading Plan + Provisional Units tự ra được sản phẩm, gọn một phiên), mở Gate A rồi DỪNG chờ duyệt trên Control Tower.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` (§1.1, §2.1, §4.8, §4.9). Yêu cầu `.ai-dlc/` đã init
(chưa có → chạy `/dlc-init` trước).

Đầu ra của stage 1 là **`intent-plan.md`** — tài liệu markdown tự đủ, được Control Tower render toàn văn
để người duyệt đọc trước khi bấm Approve. Không có tài liệu này thì không có Gate A.

1. Cấp ID `INT-NNN` kế tiếp; tạo cây `intents/INT-NNN/` (kèm `revisions/`, `as-is/`, `decision-briefs/`)
   + `status.md` từ template.
2. **Pinned snapshot**: copy toàn bộ `${CLAUDE_PLUGIN_ROOT}/skills/checklists/*` + `governance/dor.md,dod.md`
   (SAU khi áp `.ai-dlc/overrides/`) vào `intents/INT-NNN/pinned/`.
3. Spawn `ai-dlc:dlc-intent-analyst` với yêu cầu của user → `intent.md` (bản gọn) + **phần 1** của
   `intent-plan.md` (dựng từ `${CLAUDE_PLUGIN_ROOT}/templates/intent-plan.md`).
4. Spawn `ai-dlc:dlc-source-planner` → **phần 2 (Source Reading Plan)**: quét thật workspace theo
   workspace-map, điền bảng nguồn với "thông tin cụ thể phải lấy ra" cho từng nguồn, ghi lệnh/pattern đã
   quét vào mục 2.5, đẩy nguồn ngoài repo thành câu hỏi ở 2.4.
5. Quay lại `ai-dlc:dlc-intent-analyst` → **phần 3 (Provisional Unit Map)**: trục phân rã + Units, mỗi Unit
   có User Story · NFR (ngưỡng số) · Rủi ro (mức/trigger/chủ) · **`releasable` + `session_fit` có con số**
   (§4.9 v5) · ước lượng có breakdown · nguồn chứng minh.
6. Intent-analyst **tự pre-flight** cả 3 phần theo `checklists/ba.md` + `checklists/source-plan.md`, điền
   từng mục kèm con trỏ vào mục cuối intent-plan (v6 — §4.17.4: ba-reviewer chỉ spawn khi người yêu cầu
   tại Gate A).
7. **Tự kiểm trước khi mở gate** (không đạt thì sửa, đừng mở gate):
   - Mọi vùng ảnh hưởng (1.6) có ≥1 nguồn P0 phủ; vùng không phủ được nêu đích danh ở 2.5.
   - Không Unit nào thiếu `releasable`/`session_fit` có con số; không Unit nào thiếu US/NFR/risk.
   - Tài liệu tự đủ: đọc một mình quyết được, không phải mở file khác.
8. Ghi `status.md`: `gate_open: A`, **`gate_doc: intent-plan.md`**, `plan_version: 1`. Chạy
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py` để tower có bản preview mới nhất.
9. Mở **Gate A** theo nghi thức protocol §2 — nói rõ với người dùng: mở Control Tower để **đọc toàn văn
   intent-plan.md rồi mới Approve / Yêu cầu chỉnh sửa / Reject**, rồi **KẾT THÚC LƯỢT**.
   Không chạy stage 2 khi chưa có quyết định.
