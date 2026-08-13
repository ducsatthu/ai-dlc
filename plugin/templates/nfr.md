---
type: nfr
unit: UOW-NN
intent: INT-NNN
count: 0
---
# UOW-NN · NFR

> Chỉ ghi NFR **thật sự ràng buộc Unit này**. NFR không có ngưỡng số và cách đo là NFR vô nghĩa —
> reviewer `request-changes`. NFR kế thừa từ toàn hệ thì ghi rõ "kế thừa: <nguồn>", không chép lại cả bộ.

| # | Loại | Yêu cầu | Ngưỡng (số) | Đo bằng (test/công cụ) | Nguồn ngưỡng | Bắt buộc? |
|---|---|---|---|---|---|---|
| N1 | performance | | | | S1 §… | MUST |
| N2 | security | | | | checklist security v1 | MUST |
| N3 | khả dụng/xử lý lỗi | | | | | SHOULD |
| N4 | tương thích/ràng buộc dữ liệu | | | | | |
| N5 | vận hành (log/metric/alert) | | | | | |

## Chưa chốt được
| # | NFR | Thiếu gì để chốt | Ai chốt | Xử lý tạm |
|---|---|---|---|---|
