---
name: dlc-bolt
description: Stage 6 AI-DLC — chạy một Bolt cho một Unit (args UOW-NN [BOLT-NN]) qua bolt-coordinator, soát design/code theo TẦNG review của Unit (§4.17) + checkpoint Gate E. Unit có thể chạy nhiều Bolt song song/tuần tự. (Autopilot §2.3: Gate E tự đóng khi có bằng chứng thật.)
---

> Engine `contracts` (template đội): skill này **không chạy**. Đội không có Bolt; unit đi thẳng từ `plan.md` sang code bằng
> `execute ready units` của `/aidlc`, tự sửa tối đa 3 lần rồi dừng. Gói chỉ có `dlc-status`, `dlc-doctor`, `dlc-retro`.

Điều kiện: gates_passed chứa D; Unit thuộc danh sách được duyệt; DoR pass; `spec.md` có `review:` tầng đã duyệt.
1. Spawn `ai-dlc:dlc-bolt-coordinator` cho UOW-NN → đi đúng trình tự trong định nghĩa agent (Domain →
   Logical + ADR → soát design **theo tầng** `none`/`peer`/`specialist` → **Gate E(a) DỪNG** → task board →
   be-dev ∥ fe-dev, checklist BE/FE nằm trong `read_first` của HOF dev (pre-flight §4.17.4) → soát code
   **theo tầng**: self-verify có bằng chứng · peer là dev còn lại · specialist đúng vai trigger → Fix →
   **Gate E(b) DỪNG** demo). Gate E(a)/E(b) của NGƯỜI dừng cho MỌI tầng.
2. Coordinator spawn `ai-dlc:dlc-be-dev` / `ai-dlc:dlc-fe-dev` theo task board; hàng rào PreToolUse hook đã chặn code-write khi chưa qua Gate D.
3. Mỗi checkpoint/gate: cập nhật status + tower rồi kết thúc lượt. Bolt xong: đề xuất bolt kế hoặc `/ai-dlc:dlc-accept UOW-NN`.

**Autopilot (protocol §2.3, 6.4.0)**: `governance/autopilot.md` có `mode: autopilot` ⇒ mọi bước trên vẫn chạy đủ, artefact đủ mục;
chỗ ghi "DỪNG" / "KẾT THÚC LƯỢT" đổi thành: orchestrator chạy **block check** → không block thì tự ghi DEC autopilot
(có *Chọn / Bỏ / Đảo bằng / Hiện ở*) và **chạy tiếp lệnh kế** trong cùng lượt; block thì ghi `blocked_by` rồi mới dừng.
Gate E(a)/E(b): soát design/code theo tầng **vẫn chạy đủ**; E(b) tự đóng khi self-verify/RV có bằng chứng thật và test xanh,
đỏ lặp quá `max_self_fix` = block #6. Lệnh kế: bolt kế hoặc `/ai-dlc:dlc-accept`.
