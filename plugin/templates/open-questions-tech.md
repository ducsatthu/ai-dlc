---
intent: INT-NNN
doc: open-questions-tech
audience: tech
gate: D
version: 1
generated_by: dlc-context-validator
generated: <ISO>
open: 0
blocking: 0
---

# Câu hỏi cần người kỹ thuật quyết — INT-NNN · <tên intent>

> **File này viết cho tech lead / architect / QA lead / devops.** Được phép dùng đường dẫn, tên bảng,
> tên kiểu dữ liệu — nhưng **mọi khẳng định phải có bằng chứng** (`path:line` hoặc dòng trong `source-ledger.md`).
> Câu nào cần người nghiệp vụ quyết thì **không** kết ở đây: viết bản bằng lời sang `open-questions-business.md`
> và nối hai chiều bằng mã (*soi chiếu*).
>
> **Luật chặn**: câu mang `Ảnh hưởng: CHẶN UOW-NN` mà còn `open` thì Unit đó **không được vào Gate D**
> (protocol §4.10). Muốn đi tiếp phải chốt, hoặc hạ xuống `[ASSUMED]` kèm rủi ro ghi trong `risks.md` của Unit.

## 0. Bảng điều phối

<!-- BẮT BUỘC giữ đúng tên cột: Control Tower đọc bảng này. -->

| Mã | Câu hỏi | Ai trả lời | Hạn | Nếu im lặng | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|---|---|
| OQT-01 | <câu hỏi rút gọn 1 dòng> | <vai kỹ thuật cụ thể> | <trước Gate D · dd/mm> | <phương án mặc định> | CHẶN UOW-NN | open |

---

## Nhóm T1 — Kiến trúc & ranh giới module
*Ai trả lời: tech lead / architect. Đặt ở đâu, thuộc về ai, tách hay gộp.*

### OQT-01 · <câu hỏi>

- **Ai trả lời**: <vai + tên> · **Hạn**: <mốc> · **Ảnh hưởng**: <CHẶN UOW-NN | đắt dần | không chặn>
- **Bằng chứng**: `<path:line>` — <trích 1 dòng hoặc tóm tắt chính xác cái đang có>
- **Bối cảnh**: <2–4 câu: hiện trạng, chỗ va chạm, ràng buộc kỹ thuật đã biết>

**Chọn một:**

| | Phương án | Hệ quả kỹ thuật | Chi phí | Rủi ro |
|---|---|---|---|---|
| ☐ | **A.** … | <đụng những đâu> | <+Nh> | <cái gì có thể vỡ> |
| ☐ | **B.** … | … | <+Nh> | … |

- **AI đề xuất**: <A|B> — <lý do, dẫn bằng chứng>
- **Đã soát mà không thấy đáp án**: `<path>` · `<path>` · <lệnh grep đã chạy>
  <!-- BẮT BUỘC (protocol §4.10.9). Câu dạng "hiện đang là gì / dùng con số nào" là câu về HIỆN TRẠNG:
       code trả lời được thì đó không phải câu hỏi, cùng lắm là câu xác nhận. -->
- **Nếu không trả lời trước hạn**: <mặc định>, ghi `[ASSUMED]` + rủi ro vào `units/UOW-NN/risks.md`.
  **Đắt dần**: <có/không — càng trả lời muộn càng nhiều chỗ bám vào nền hiện tại thì ghi rõ mốc>
- **Soi chiếu**: OQB-NN *(nếu quyết định cuối thuộc về nghiệp vụ)*
- **Trạng thái**: open

---

## Nhóm T2 — Mô hình dữ liệu & migration
*Ai trả lời: tech lead + người giữ DB. Trường nào, ràng buộc nào, dữ liệu cũ xử lý sao.*

## Nhóm T3 — Tích hợp & hợp đồng API
*Ai trả lời: tech lead + đầu mối hệ thống liên quan. Ai gọi ai, hợp đồng chốt ở đâu, đổi có phá ai không.*

## Nhóm T4 — Phi chức năng (hiệu năng · bảo mật · khả dụng)
*Ai trả lời: tech lead / security. Ngưỡng bao nhiêu là đạt, đo bằng gì.*

## Nhóm T5 — Kiểm thử & môi trường
*Ai trả lời: QA lead / devops. Test ở đâu, dữ liệu mẫu lấy đâu, môi trường nào chạy được.*

## Nhóm T6 — Nợ kỹ thuật & rủi ro triển khai
*Ai trả lời: tech lead. Cái gì biết là nợ mà vẫn làm, trả khi nào.*

> Nhóm rỗng thì xoá hẳn.

---

## Đã trả lời

| Mã | Chốt là gì | Ai quyết | Khi nào | Ghi ở đâu (ADR/DEC) |
|---|---|---|---|---|
| OQT-NN | … | … | … | ADR-NN · DEC-NNNN |

## Changelog

- v1: bản đầu · sau Gate B
