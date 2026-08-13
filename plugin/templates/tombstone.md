---
unit: UOW-NN
status: obsolete
moved_at: <ISO>
decided_by: DEC-NNNN | RV-NNN     # ai/cái gì quyết bỏ unit này
replaced_by: UOW-NN | —           # unit thay thế, hoặc "—" nếu phạm vi bị bỏ hẳn
---

# TOMBSTONE · UOW-NN — <tên unit cũ>

## Vì sao lỗi thời
<Bị viết đè khi replan (DEC nào), hay trượt review mà không được viết lại (RV nào). Một đoạn ngắn.>

## Nó từng định làm gì
<Để người đọc retro sau này hiểu phạm vi cũ mà không phải mở lại spec.>

## Thay bằng gì
<UOW mới, hoặc "phạm vi này đã bỏ tại DEC-NNNN".>

---

> **Không xoá, chuyển vào `units/_trash/`** (protocol §4.14 · LL-002 P-6): retro sống bằng chính đống dấu vết
> này — phát hiện lớn nhất của một retro thật (*"13 lần xin review, 0 lần được review"*) tìm ra bằng cách đối
> chiếu `comms/` với `reviews/`; nếu unit và HOF liên quan đã bị xoá theo từng lượt replan thì phát hiện đó
> không tồn tại. Mục tiêu của việc dọn không phải giải phóng chỗ, mà là **unit lỗi thời đừng đứng lẫn trong
> kế hoạch đang chạy và đừng đeo trạng thái nói dối** (4 unit chưa bao giờ được xây vẫn mang `approved` suốt
> cả intent). Mọi thống kê bỏ qua `units/_*`.
