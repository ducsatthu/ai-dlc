---
name: dlc-bolt
description: Stage 6 AI-DLC — chạy một Bolt cho một Unit (args UOW-NN [BOLT-NN]) qua bolt-coordinator, soát design/code theo TẦNG review của Unit (§4.17) + checkpoint Gate E. Unit có thể chạy nhiều Bolt song song/tuần tự.
---

Điều kiện: gates_passed chứa D; Unit thuộc danh sách được duyệt; DoR pass; `spec.md` có `review:` tầng đã duyệt.
1. Spawn `ai-dlc:dlc-bolt-coordinator` cho UOW-NN → đi đúng trình tự trong định nghĩa agent (Domain →
   Logical + ADR → soát design **theo tầng** `none`/`peer`/`specialist` → **Gate E(a) DỪNG** → task board →
   be-dev ∥ fe-dev, checklist BE/FE nằm trong `read_first` của HOF dev (pre-flight §4.17.4) → soát code
   **theo tầng**: self-verify có bằng chứng · peer là dev còn lại · specialist đúng vai trigger → Fix →
   **Gate E(b) DỪNG** demo). Gate E(a)/E(b) của NGƯỜI dừng cho MỌI tầng.
2. Coordinator spawn `ai-dlc:dlc-be-dev` / `ai-dlc:dlc-fe-dev` theo task board; hàng rào PreToolUse hook đã chặn code-write khi chưa qua Gate D.
3. Mỗi checkpoint/gate: cập nhật status + tower rồi kết thúc lượt. Bolt xong: đề xuất bolt kế hoặc `/dlc-accept UOW-NN`.
