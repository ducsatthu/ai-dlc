---
name: dlc-units
description: Stage 5 AI-DLC — refine Provisional Unit Map thành unit-plan.md chốt (mỗi Unit tự ra được sản phẩm + gọn một phiên, đủ User Story/NFR/Rủi ro, khai tầng review §4.17), unit-planner tự pre-flight theo checklist, mở Gate D rồi DỪNG. (Autopilot §2.3: không dừng trừ khi block.)
---

> Engine `contracts` (template đội): skill này **không chạy**. Work Unit nằm trong `plan.md` (`U-*`, `[owner:]`, `[repo:]`)
> và chốt tại `approve plan`. Gói chỉ có `dlc-status`, `dlc-doctor`, `dlc-retro` ở engine này.

Điều kiện: `gates_passed` chứa A, B, C; `as-is/source-ledger.md` không còn dòng `planned`.

1. Spawn `ai-dlc:dlc-unit-planner`:
   - Đối chiếu `intent-plan.md` phần 3 (provisional) với AS-IS → viết mục "Đã đổi gì so với provisional"
     (đổi gì, vì sao, dòng ledger nào chứng minh). Không đổi cũng phải nêu căn cứ.
   - Tạo `units/UOW-NN/` với `spec.md` (`releasable` + `session_fit` có con số + `estimate_hours` có
     breakdown + **`review:` tầng theo trigger §4.17 kèm căn cứ** + `sources:`), `user-stories.md`,
     `nfr.md`, `risks.md` — **ba file sau là bắt buộc, không được rỗng**.
   - Hợp nhất thành `unit-plan.md` (gate_doc của Gate D) theo template: bảng coverage nguồn, bảng Unit
     (có cột Review), chi tiết từng Unit, thứ tự thực thi + đường găng, DoR/DoD version, trade-off cần
     người quyết.
2. Unit-planner **tự pre-flight** (v6 — §4.17.4, thay cho spawn review board mặc định): đối chiếu
   `checklists/pm-po.md` (plan, ước lượng, risks) + `checklists/qa.md` (DoR từng Unit, coverage nguồn,
   NFR đo được), điền từng mục kèm con trỏ vào mục Pre-flight của unit-plan. pm-po-reviewer/qa-reviewer
   chỉ spawn khi người yêu cầu tại Gate D.
3. **Chặn cứng trước khi mở gate** — không đạt thì sửa, đừng mở:
   - Mọi Unit khai đủ `releasable` (hoặc `no` + `released_with`), `session_fit` **có con số**,
     `estimate_hours` >0 có breakdown, và **`review:` tầng kèm căn cứ trigger** (§4.17).
   - Mọi Unit đủ ba file US/NFR/risks, không file nào rỗng.
   - Bảng coverage nguồn không còn `planned`; nguồn `missing`/`deferred` đã thành risk có chủ.
4. Ghi `status.md`: `gate_open: D`, `gate_doc: unit-plan.md`. Chạy `tower_generate.py`.
   Mở **Gate D**, nói rõ người dùng cần đọc toàn văn `unit-plan.md` trên Control Tower — **duyệt bảng tầng
   review chính là duyệt "unit nào chạy không reviewer"**, muốn nâng tầng unit nào thì request-changes đúng
   dòng đó. DỪNG.
5. Khi approve: ghi DEC, status stage 6 (`phase: construction`), unlock các Unit được duyệt.
   Đề xuất `/ai-dlc:dlc-bolt UOW-NN`.

**Autopilot (protocol §2.3, 6.4.0)**: `governance/autopilot.md` có `mode: autopilot` ⇒ mọi bước trên vẫn chạy đủ, artefact đủ mục;
chỗ ghi "DỪNG" / "KẾT THÚC LƯỢT" đổi thành: orchestrator chạy **block check** → không block thì tự ghi DEC autopilot
(có *Chọn / Bỏ / Đảo bằng / Hiện ở*) và **chạy tiếp lệnh kế** trong cùng lượt; block thì ghi `blocked_by` rồi mới dừng.
Gate D: bảng tầng review được autopilot chốt theo trigger §4.17 — unit chạm auth/PII/migration/public API **không** được
hạ xuống `none` để khỏi chờ. Lệnh kế: `/ai-dlc:dlc-bolt` cho Unit đầu đường găng.
**Mô hình cho người xem (protocol §2.4, 6.5.0)**: sau bước 3, trước bước 4 — spawn `ai-dlc:dlc-modeler` dựng
`views/unit-plan.view.json`; chạy `human_view_check.py`.
