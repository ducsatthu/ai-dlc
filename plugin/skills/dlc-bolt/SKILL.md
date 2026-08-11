---
name: dlc-bolt
description: Stage 6 AI-DLC — chạy một Bolt cho một Unit (args UOW-NN [BOLT-NN]) qua bolt-coordinator với đầy đủ review + checkpoint Gate E. Unit có thể chạy nhiều Bolt song song/tuần tự.
---

Điều kiện: gates_passed chứa D; Unit thuộc danh sách được duyệt; DoR pass.
1. Spawn `ai-dlc:dlc-bolt-coordinator` cho UOW-NN → đi đúng trình tự trong định nghĩa agent (Domain → Logical + ADR → review tech-lead + security → **Gate E(a) DỪNG** → task board → be-dev ∥ fe-dev → review BE/FE/security/qa theo phạm vi → Fix → **Gate E(b) DỪNG** demo).
2. Coordinator spawn `ai-dlc:dlc-be-dev` / `ai-dlc:dlc-fe-dev` theo task board; hàng rào PreToolUse hook đã chặn code-write khi chưa qua Gate D.
3. Mỗi checkpoint/gate: cập nhật status + tower rồi kết thúc lượt. Bolt xong: đề xuất bolt kế hoặc `/dlc-accept UOW-NN`.
