---
id: ESC-NNN
found_by: <agent hoặc HUMAN>
found_in: HOF-NNNN            # lượt việc nào phát hiện ra
where: <path:line hoặc vùng>  # chỗ có vấn đề, KHÔNG phải chỗ đang làm
severity: low | medium | high
scope_impact: none | scope | business   # chạm scope/business ⇒ phải mở gate động (protocol §4 điểm 6)
owner:                        # trống = CHƯA AI NHẬN. Đây là lý do file này tồn tại.
status: open                  # open → claimed → done | wontfix (kèm DEC)
created: <ISO>
---

# ESC-NNN · <một câu nói đúng cái sai>

## Thấy gì
<Nguyên văn hiện tượng + đường dẫn. Trích code/dữ liệu thật, không diễn giải.>

## Vì sao không tự sửa
<Ngoài phạm vi Unit nào / đụng unit nào đang chạy song song / cần quyết định của ai.>

## Hậu quả nếu để nguyên
<Ai gặp, gặp lúc nào, dưới dạng gì. "Người dùng thấy link 404" cụ thể hơn "dữ liệu không nhất quán".>

## Việc phải làm (đề xuất)
<Một việc, ước lượng thô. Nếu cần thành Unit riêng thì nói rõ.>

---

> **Vì sao có file này** (protocol §4.13 · LL-002 P-3): luật "không sửa ngoài phạm vi Unit" là đúng — nó giữ
> cho các Unit song song không giẫm chân nhau. Nhưng ghi phát hiện vào HOF **không phải giao việc**: HOF đóng
> lại là phát hiện chìm theo nó. Một dự án thật có cùng một lỗi được **bốn** HOF ghi nhận rồi vẫn tới tay
> người dùng dưới dạng link 404, vì không có chỗ nào để phát hiện sống lâu hơn lượt việc sinh ra nó.
