---
name: dlc-validate
description: Stage 3–4 AI-DLC — Context Validation (Gate B) rồi Clarification (Gate C). Mỗi gate mở là DỪNG chờ người quyết.
---

Điều kiện: gates_passed chứa A; as-is/ tồn tại.
1. Spawn `ai-dlc:dlc-context-validator` phần Validation → bản trình bày AS-IS; `ai-dlc:dlc-ba-reviewer` validate business + brief-B. Mở **Gate B**, DỪNG.
2. Khi B approved (DEC): spawn validator phần Clarify → `open-questions.md` (route người trả lời); ba-reviewer brief-C. Mở **Gate C**, DỪNG.
3. Khi C chốt: ghi câu trả lời vào open-questions (status closed), câu chưa chốt → working assumption [ASSUMED] + risk. Cập nhật status stage 5, tower. Đề xuất `/dlc-units`.
