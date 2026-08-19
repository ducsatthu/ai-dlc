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
3. Mở **Gate F**, DỪNG. Approve → DEC, spawn acceptance-recorder (stage 8): trace chain verify, publish docs vào đích theo workspace-map, changelog, đóng Unit; mọi Unit xong → đóng intent, đề xuất `/dlc-retro`.
