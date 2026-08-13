---
intent: INT-NNN
doc: open-questions-business
audience: business
gate: C
version: 1
generated_by: dlc-context-validator
generated: <ISO>
open: 0
blocking: 0
---

# Câu hỏi cần người nghiệp vụ quyết — INT-NNN · <tên intent>

> **File này viết cho người làm nghiệp vụ, không cần biết code.**
> Mỗi câu trả lời được trong ~2 phút: đọc câu hỏi → chọn một phương án → xong.
> Không cần mở file nào khác. Nếu bạn thấy tên file, tên bảng, tên hàm hay thuật ngữ lập trình
> ở đây → **đó là lỗi của AI**, bấm *Yêu cầu chỉnh sửa* và ghi "câu OQB-NN chưa dịch ra tiếng người".
>
> Câu hỏi kỹ thuật (dành cho tech lead) nằm ở file riêng: `open-questions-tech.md` — bạn **không cần** đọc file đó.
> Câu nào ở đây cần cả hai phía sẽ ghi *soi chiếu: OQT-NN*.

## 0. Bảng điều phối — ai phải trả lời gì

<!-- BẮT BUỘC giữ đúng tên cột: Control Tower đọc bảng này. Một dòng = một mã. -->

| Mã | Câu hỏi | Ai trả lời | Hạn | Nếu im lặng | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|---|---|
| OQB-01 | <câu hỏi rút gọn 1 dòng> | <vai + tên người cụ thể> | <trước Gate D · dd/mm> | <mặc định sẽ áp> | CHẶN UOW-NN | open |
| OQB-02 | … | … | … | … | không chặn | open |

**Đọc cột "Ảnh hưởng"**: `CHẶN UOW-NN` = không trả lời thì Unit đó không khởi động được ·
`làm lại nếu đổi muộn` = làm được ngay nhưng đổi sau sẽ tốn thêm · `không chặn` = trả lời lúc nào cũng được.

---

## Nhóm B1 — Phạm vi & ưu tiên
*Ai trả lời nhóm này: chủ sở hữu sản phẩm / PO. Câu ở đây quyết định làm gì đợt này, để gì lại sau.*

### OQB-01 · <câu hỏi viết như nói chuyện, kết thúc bằng dấu hỏi>

- **Ai trả lời**: <vai + tên>. <1 câu vì sao đúng người này — họ nắm cái gì mà người khác không nắm>
- **Hạn**: <mốc> · **Ảnh hưởng**: <CHẶN UOW-NN | làm lại nếu đổi muộn | không chặn>
- **Bối cảnh** (2–4 câu, bằng lời, không thuật ngữ): <hôm nay hệ thống đang làm thế nào, vì sao chỗ này chưa rõ,
  điều gì sẽ khác nhau tùy câu trả lời>

**Chọn một:**

| | Phương án | Nghĩa là gì với người dùng | Cái giá |
|---|---|---|---|
| ☐ | **A.** <tên ngắn> | <hệ quả nhìn thấy được> | <+Nh · hoặc "không tốn thêm"> |
| ☐ | **B.** <tên ngắn> | <hệ quả nhìn thấy được> | <+Nh> |
| ☐ | **C.** Chưa quyết, để đợt sau | <cái gì sẽ tạm thiếu> | <chi phí quay lại sửa: +Nh> |

- **AI đề xuất**: <A|B|C> — <1 câu lý do dựa trên bằng chứng đã đọc>
- **Đã soát mà không thấy đáp án**: <nguồn 1> · <nguồn 2> · <nguồn 3>
  <!-- BẮT BUỘC (protocol §4.10.9). Thiếu dòng này = câu hỏi chưa đủ điều kiện gửi đi.
       6 lần liên tiếp ở một dự án thật, đáp án đã nằm sẵn trong wiki hoặc trong chính code đang chạy —
       người trả lời mất công trả lời thứ AI có thể tự tra. Câu về một màn có mã thì phải soát chính spec
       của màn đó; câu dạng "hiện đang hiển thị gì / dùng con số nào" phải grep code trước rồi hỏi
       "hiện là Z, xác nhận giữ nguyên?" thay vì hỏi mở. -->
- **Nếu không trả lời trước hạn**: đi theo <phương án>, ghi `[ASSUMED]` và gắn rủi ro vào <UOW-NN>.
  Đổi sau mốc <dd/mm> tốn thêm khoảng <N>h.
- **Soi chiếu**: OQT-NN *(nếu câu này có bản kỹ thuật đi kèm; bỏ dòng này nếu không có)*
- **Trạng thái**: open

---

## Nhóm B2 — Quy tắc nghiệp vụ
*Ai trả lời: BA / PMO. Luật, trạng thái hợp lệ, điều kiện bắt buộc, cách tính.*

### OQB-02 · …
<lặp đúng cấu trúc thẻ trên>

---

## Nhóm B3 — Vai trò & quyền
*Ai trả lời: chủ sở hữu + PMO. Ai được nhìn gì, ai được làm gì, ai duyệt.*

---

## Nhóm B4 — Dữ liệu & nguồn sự thật
*Ai trả lời: người chịu trách nhiệm dữ liệu (data owner) / PMO. Số liệu lấy từ đâu, ai đúng khi hai nơi lệch nhau.*

---

## Nhóm B5 — Quy trình & vận hành
*Ai trả lời: người vận hành / PMO. Thông báo cho ai, khi nào, ai xử lý ngoại lệ, chờ bao lâu là quá lâu.*

---

## Nhóm B6 — Tuân thủ & rủi ro kinh doanh
*Ai trả lời: chủ sở hữu (± pháp chế/an ninh phía nghiệp vụ). Dữ liệu nhạy cảm, lưu bao lâu, ai chịu trách nhiệm.*

---

## Nhóm B7 — Trình bày & điều hướng
*Ai trả lời: chủ sở hữu / PO. Menu đặt ở đâu, nhãn gọi là gì, người dùng tìm thấy màn bằng cách nào.*

> Nhóm nào không có câu hỏi thì **xoá hẳn mục đó** — đừng để tiêu đề rỗng.

---

## Đã trả lời

| Mã | Chốt là gì | Ai quyết | Khi nào | DEC |
|---|---|---|---|---|
| OQB-NN | <câu trả lời 1 dòng> | <người> | <dd/mm> | DEC-NNNN |

## Đã bỏ khỏi phạm vi

| Mã | Vì sao bỏ | Theo |
|---|---|---|
| OQB-NN | <lý do> | DEC-NNNN |

## Changelog

- v1: bản đầu · sau Gate B
