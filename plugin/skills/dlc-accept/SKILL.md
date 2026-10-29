---
name: dlc-accept
description: Stage 7–8 AI-DLC — gom Acceptance Evidence + tự chạy lại test thật, security check theo trigger §4.17, mở Gate F (UAT) rồi DỪNG; sau approve thì Release + publish docs theo workspace map + persist Context Memory. (Autopilot §2.3: tự đóng nghiệm thu Unit; deploy luôn dừng.)
---

> Engine `contracts` (template đội): skill này **không chạy**. Nghiệm thu là `review outcome` rồi `approve outcome` của
> `/aidlc`, bằng chứng trong `evidence.md`. Gói chỉ có `dlc-status`, `dlc-doctor`, `dlc-retro` ở engine này.

Điều kiện: mọi Bolt của UOW-NN xong Gate E(b).
1. Spawn `ai-dlc:dlc-acceptance-recorder` (stage 7) → evidence/ theo pinned/dod.md; recorder **tự chạy lại
   test thật** + một ca đối chứng (§4.15), ghi output vào evidence.
2. Reviewer theo tầng (§4.17): unit trong phạm vi có `review: specialist(security)` hoặc còn MUST finding
   mở → spawn `ai-dlc:dlc-security-reviewer` xác nhận MUST=0; qa-reviewer chỉ khi người yêu cầu tại Gate F.
   Evidence thiếu → quay lại fix, KHÔNG mở gate.
3. Mở **Gate F**, DỪNG. Approve → DEC, spawn acceptance-recorder (stage 8): trace chain verify, publish docs vào đích theo workspace-map, changelog, đóng Unit; mọi Unit xong → đóng intent bằng `scripts/close_sweep.py --apply` (protocol §2.5 — commit chưa vào nhánh phát hành thì intent chờ merge, không chờ người), đề xuất `/ai-dlc:dlc-retro`.
4. **Promote codekb** (6.2.0, khi intent đóng — brownfield có `as-is/static-model.md`): recorder copy
   **nguyên văn** `as-is/{static-model,dynamic-model,decisions-inventory}.md` (+ gộp `delta.md` nếu có) vào
   `codekb/<repo>/` cho từng repo intent chạm, ghi `freshness.md` từ `templates/codekb-freshness.md`
   (`git_head` = HEAD **lúc AS-IS được đọc** — lấy từ ledger/SES, không phải HEAD hôm nay; `areas_scanned`;
   `ledger` trỏ ledger intent này; thêm dòng *Lịch sử promote*). Codekb cũ bị ghi đè — bản cũ vẫn nằm ở
   `as-is/` của intent trước, không mất. Không "làm đẹp", không viết ngược từ code (CLAUDE.md: không dựng bù hồ sơ).

**Autopilot (protocol §2.3, 6.4.0)**: `governance/autopilot.md` có `mode: autopilot` ⇒ mọi bước trên vẫn chạy đủ, artefact đủ mục;
chỗ ghi "DỪNG" / "KẾT THÚC LƯỢT" đổi thành: orchestrator chạy **block check** → không block thì tự ghi DEC autopilot
(có *Chọn / Bỏ / Đảo bằng / Hiện ở*) và **chạy tiếp lệnh kế** trong cùng lượt; block thì ghi `blocked_by` rồi mới dừng.
Gate F: autopilot chỉ tự đóng phần **nghiệm thu Unit** (evidence đủ + tự chạy lại test + security MUST = 0);
**deploy môi trường khách/prod là ranh đỏ #4 — luôn dừng chờ người**. Gate G (retro): LL tự ghi, patch gói vẫn cần người ký.
