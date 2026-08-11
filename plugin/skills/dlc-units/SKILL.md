---
name: dlc-units
description: Stage 5 AI-DLC — phân rã Intent thành Units + Bolt plan, review bởi PM/PO + QA (DoR), decision brief D, mở Gate D rồi DỪNG.
---

Điều kiện: gates_passed chứa A,B,C.
1. Spawn `ai-dlc:dlc-unit-planner` → units/UOW-NN/ + Bolt plan.
2. Song song spawn: `ai-dlc:dlc-pm-po-reviewer` (plan + risks) và `ai-dlc:dlc-qa-reviewer` (DoR check từng Unit) → RV. request-changes → unit-planner sửa (tối đa 2 vòng, sau đó escalation).
3. `ai-dlc:dlc-ba-reviewer` soạn brief-D (kèm trade-off defer Unit nào nếu có).
4. Mở **Gate D**, DỪNG. Khi approve: ghi DEC, status stage 6, unlock các Unit được duyệt. Đề xuất `/dlc-bolt UOW-NN`.
