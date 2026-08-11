---
name: dlc-accept
description: Stage 7–8 AI-DLC — gom Acceptance Evidence, QC bởi QA + Security, mở Gate F (UAT) rồi DỪNG; sau approve thì Release + publish docs theo workspace map + persist Context Memory.
---

Điều kiện: mọi Bolt của UOW-NN xong Gate E(b).
1. Spawn `ai-dlc:dlc-acceptance-recorder` (stage 7) → evidence/ theo pinned/dod.md.
2. Spawn `ai-dlc:dlc-qa-reviewer` (QC evidence — chạy lại test thật) + `ai-dlc:dlc-security-reviewer` (MUST=0). Thiếu → quay lại fix, KHÔNG mở gate.
3. Mở **Gate F**, DỪNG. Approve → DEC, spawn acceptance-recorder (stage 8): trace chain verify, publish docs vào đích theo workspace-map, changelog, đóng Unit; mọi Unit xong → đóng intent, đề xuất `/dlc-retro`.
