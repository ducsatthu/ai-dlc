---
name: dlc-accept
description: Stage 7–8 AI-DLC — gom Acceptance Evidence + tự chạy lại test thật, security check theo trigger §4.17, mở Gate F (UAT) rồi DỪNG; sau approve thì Release + publish docs theo workspace map + persist Context Memory.
---

Điều kiện: mọi Bolt của UOW-NN xong Gate E(b).
1. Spawn `ai-dlc:dlc-acceptance-recorder` (stage 7) → evidence/ theo pinned/dod.md; recorder **tự chạy lại
   test thật** + một ca đối chứng (§4.15), ghi output vào evidence.
2. Reviewer theo tầng (§4.17): unit trong phạm vi có `review: specialist(security)` hoặc còn MUST finding
   mở → spawn `ai-dlc:dlc-security-reviewer` xác nhận MUST=0; qa-reviewer chỉ khi người yêu cầu tại Gate F.
   Evidence thiếu → quay lại fix, KHÔNG mở gate.
3. Mở **Gate F**, DỪNG. Approve → DEC, spawn acceptance-recorder (stage 8): trace chain verify, publish docs vào đích theo workspace-map, changelog, đóng Unit; mọi Unit xong → đóng intent, đề xuất `/ai-dlc:dlc-retro`.
4. **Promote codekb** (6.2.0, khi intent đóng — brownfield có `as-is/static-model.md`): recorder copy
   **nguyên văn** `as-is/{static-model,dynamic-model,decisions-inventory}.md` (+ gộp `delta.md` nếu có) vào
   `codekb/<repo>/` cho từng repo intent chạm, ghi `freshness.md` từ `templates/codekb-freshness.md`
   (`git_head` = HEAD **lúc AS-IS được đọc** — lấy từ ledger/SES, không phải HEAD hôm nay; `areas_scanned`;
   `ledger` trỏ ledger intent này; thêm dòng *Lịch sử promote*). Codekb cũ bị ghi đè — bản cũ vẫn nằm ở
   `as-is/` của intent trước, không mất. Không "làm đẹp", không viết ngược từ code (CLAUDE.md: không dựng bù hồ sơ).
