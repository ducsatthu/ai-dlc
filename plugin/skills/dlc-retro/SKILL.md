---
name: dlc-retro
description: Learning loop AI-DLC — retro sau release (hoặc theo yêu cầu): rút lesson learned từ dấu vết intent, đề xuất patch checklist/DoD, mở Gate G rồi DỪNG; approve thì apply vào overrides + nhắc contribute.
---

1. Spawn `ai-dlc:dlc-retro-keeper` cho intent vừa đóng (hoặc intent user chỉ định) → LL-NNN + patch đề xuất (diff cụ thể, version cũ→mới).
   Nguồn bằng chứng của retro, theo thứ tự: **`handoffs/HOF-*.md`** (việc đi qua tay ai, bao nhiêu vòng,
   `returned` vì thiếu gì, HOF nào treo lâu) · `revisions/REV-*.md` (gate phải sửa mấy vòng, vì sao) ·
   `as-is/source-ledger.md` (nguồn nào `missing`/`deferred` đã trả giá) · RV/DEC/MSG · `session/log/SES-*.md`.
   Chuỗi HOF là chỗ nhìn ra vấn đề phối hợp giữa các vị trí — đừng bỏ qua nó để chỉ đọc kết quả cuối.
1b. **Đếm sự vắng mặt, không chỉ đọc cái đang có** (LL-002 §1 · LL-003) — ba phép đối chiếu rẻ, mỗi cái từng
   lộ ra một lỗ hổng mà mọi thứ khác đều im lặng:
   - `comms/` (review-request đã gửi) **so với** `reviews/RV-*.md` có `re:` trỏ unit của intent này.
     Ca thật: 13 gửi đi, 0 verdict quay lại, 17 unit vẫn đóng.
   - `units/*/spec.md` `status: done` **so với** `rv:`/`review_waived_by:` — có bao nhiêu unit tự khai xong.
   - Unit đã đóng **so với** sự tồn tại của `bolts/BOLT-NN/`, `tasks.md`, `evidence/`. Ca thật: 14/18 unit
     không có thư mục bolt nào, trong khi mọi HOF đều khai đang chạy `BOLT-01`.
   Khoảng trống tìm ra ở đây **ghi vào LL, KHÔNG dựng bù**: hồ sơ viết ngược từ code đã chạy là mô tả code
   đội lốt quyết định thiết kế, và nó xoá luôn khả năng ai đó phát hiện vấn đề ở intent sau.
2. Mở **Gate G**, DỪNG (trình LL + patch).
3. Approve → DEC; apply patch vào `.ai-dlc/overrides/` (mode patch, frontmatter source: LL-NNN); tăng version + changelog governance; cập nhật OVERRIDES.md index; nhắc `/dlc-contribute` nếu lesson mang tính chuẩn chung.
