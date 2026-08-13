---
name: dlc-discover
description: Stage 2 AI-DLC — Context Discovery sau khi Gate A approve. Đọc ĐÚNG các nguồn trong Source Reading Plan đã duyệt, dựng AS-IS model + source-ledger (mọi nguồn phải có trạng thái cuối) rồi chuyển sang validate.
---

Điều kiện: `gates_passed` chứa A (kiểm tra `status.md` — chưa có thì dừng, nêu gate đang chờ).

1. Ghi DEC Gate A nếu vừa nhận quyết định từ user/inbox; move file inbox sang `processed/`.
2. Spawn `ai-dlc:dlc-context-archaeologist` cho INT đang mở:
   - Tạo `as-is/source-ledger.md` với **đúng số dòng** như bảng 2.1 của `intent-plan.md`.
   - Đọc theo thứ tự đã chốt (2.2), đóng từng dòng bằng trạng thái cuối + evidence (vùng đã đọc + phát hiện).
   - Nguồn ngoài plan → dòng `[ADDED]`; mâu thuẫn → `[CONFLICT]` + câu hỏi Gate C.
   - Dựng `as-is/static-model.md`, `dynamic-model.md`, `decisions-inventory.md` — mỗi khẳng định trỏ về ledger.
3. **Kiểm tra chặn cứng**: ledger còn dòng `planned` → KHÔNG chuyển stage, báo rõ còn thiếu nguồn nào và
   cần gì để đóng (protocol §4.8).
4. Cập nhật `status.md` (stage 2 → 3), chạy `tower_generate.py`. Green-field thuần: ghi as-is tối giản
   (repo trống/chưa liên quan) — nhưng ledger vẫn phải đóng đủ dòng cho các nguồn đã lên kế hoạch.
5. Đề xuất bước kế: `/dlc-validate`.
