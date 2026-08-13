---
name: dlc-units
description: Stage 5 AI-DLC — refine Provisional Unit Map thành unit-plan.md chốt (mỗi Unit ≤5h, đủ User Story/NFR/Rủi ro) + Bolt plan, review bởi PM/PO + QA (DoR), mở Gate D rồi DỪNG.
---

Điều kiện: `gates_passed` chứa A, B, C; `as-is/source-ledger.md` không còn dòng `planned`.

1. Spawn `ai-dlc:dlc-unit-planner`:
   - Đối chiếu `intent-plan.md` phần 3 (provisional) với AS-IS → viết mục "Đã đổi gì so với provisional"
     (đổi gì, vì sao, dòng ledger nào chứng minh). Không đổi cũng phải nêu căn cứ.
   - Tạo `units/UOW-NN/` với `spec.md` (`estimate_hours` ≤5.0 + breakdown + `sources:`), `user-stories.md`,
     `nfr.md`, `risks.md` — **ba file sau là bắt buộc, không được rỗng**.
   - Hợp nhất thành `unit-plan.md` (gate_doc của Gate D) theo template: bảng coverage nguồn, bảng Unit,
     chi tiết từng Unit, thứ tự thực thi + đường găng, DoR/DoD version, trade-off cần người quyết.
2. Song song spawn: `ai-dlc:dlc-pm-po-reviewer` (plan, ước lượng, risks) và `ai-dlc:dlc-qa-reviewer`
   (DoR check từng Unit, gồm coverage nguồn + NFR có đo được không) → RV.
   `request-changes` → unit-planner sửa (tối đa 2 vòng, sau đó escalation).
3. **Chặn cứng trước khi mở gate** — không đạt thì sửa, đừng mở:
   - Không Unit nào `estimate_hours > 5.0`; mọi ước lượng có breakdown và căn cứ bằng con số thật.
   - Mọi Unit đủ ba file US/NFR/risks, không file nào rỗng.
   - Bảng coverage nguồn không còn `planned`; nguồn `missing`/`deferred` đã thành risk có chủ.
4. `ai-dlc:dlc-ba-reviewer` soạn `brief-D.md` (kèm trade-off defer Unit nào nếu có).
5. Ghi `status.md`: `gate_open: D`, `gate_doc: unit-plan.md`. Chạy `tower_generate.py`.
   Mở **Gate D**, nói rõ người dùng cần đọc toàn văn `unit-plan.md` trên Control Tower rồi mới quyết, DỪNG.
6. Khi approve: ghi DEC, status stage 6 (`phase: construction`), unlock các Unit được duyệt.
   Đề xuất `/dlc-bolt UOW-NN`.
