---
version: 1
scope: governance
---
# Kích thước Unit — núm của dự án này

Gói **không** áp trần giờ (protocol §4.9 v5). Unit được cắt theo hai câu hỏi, không theo đồng hồ:

1. **Ra được sản phẩm một mình không?** → `releasable: yes`, hoặc `no` kèm `released_with: UOW-NN`.
2. **Một phiên có ôm nổi không?** → `session_fit:` kèm **con số** (mấy màn/endpoint/bảng · mấy nguồn
   phải đọc · vùng code quen hay lạ).

```yaml
unit_max_hours: null
```

`null` = không trần (mặc định). Đặt một con số nếu dự án này **có lý do riêng** để giới hạn — ví dụ đội
mới, vùng code lạ, hoặc muốn ép nhịp release ngắn trong giai đoạn đầu. Khi có số, tower và `/dlc-doctor`
chỉ **cảnh báo** khi vượt, không chặn gate: chặn gate vẫn là hai điều kiện trên.

> Đặt trần ở đây là một **quyết định có chủ**, nên ghi kèm một DEC nói vì sao và khi nào gỡ. Trần giờ vốn
> là thứ đo sai vấn đề: nó bắt cắt theo thời lượng thay vì theo đường ra sản phẩm, và ca thật đã cho thấy
> hậu quả — một Unit bị tách thành 3.5h + 2.75h chỉ để lọt trần, hai mảnh phải ra chung mới có nghĩa.

## Đổi núm này

Sửa file, ghi một DEC, rồi chạy lại `/dlc-tower`. Đang giữa một intent thì trần mới **không** áp ngược cho
Unit đã qua Gate D — không dựng bù hồ sơ (protocol §4.9, mục kế hoạch cũ).
