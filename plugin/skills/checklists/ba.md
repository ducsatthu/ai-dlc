---
name: ba
version: 2
---
# Checklist BA (business) · v2
## review-intent-plan (Gate A — soi cả 3 phần của intent-plan.md)
### Phần 1 — Intent
- [ ] Intent là OUTCOME (đo được), không phải solution
- [ ] Problem nêu đúng nỗi đau, có nguồn (ticket/feedback/tài liệu)
- [ ] Có mục **ngoài phạm vi** (1.3) — chống scope creep ngầm
- [ ] Mâu thuẫn tài liệu (bản cũ vs quyết định mới) đã thành câu hỏi Gate A, không bị tự chọn một bên
- [ ] Vùng ảnh hưởng khớp workspace-map
### Phần 2 — Source Reading Plan
- [ ] Áp checklist `source-plan` v1 phần *plan-completeness* — không đạt là `request-changes`, không "duyệt tạm"
- [ ] Mỗi vùng ảnh hưởng ở 1.6 có nguồn P0 phủ
### Phần 3 — Provisional Unit Map
- [ ] Trục phân rã (3.1) được nêu rõ **và có nêu trục đã loại** — cho thấy đây là lựa chọn
- [ ] Mỗi Unit đủ **User Story · NFR · Rủi ro · ước lượng có breakdown**
- [ ] Không Unit nào >5h (protocol §4.9); không pseudo-unit (Update DB/Add API/Update UI)
- [ ] Mỗi Unit chỉ ra được nguồn nào chứng minh cho nó
### Tài liệu
- [ ] `intent-plan.md` **tự đủ**: đọc một mình vẫn quyết được, không phải mở file khác
- [ ] Có mục "Quyết định cần ở Gate A" nêu đúng những câu người phải trả lời

## business-validation (stage 2–4)
- [ ] Mỗi khẳng định business trong AS-IS có nguồn (trỏ được về dòng source-ledger); suy luận gắn [INFERRED]
- [ ] Open question không trùng quyết định đã có; mỗi câu có người trả lời + deadline + ảnh hưởng
- [ ] Mâu thuẫn nguồn trong ledger đã thành câu hỏi Gate C

## decision-brief (gate A–D)
- [ ] Bối cảnh ≤3 dòng · ≥2 phương án kèm trade-off · rủi ro · khuyến nghị + lý do
- [ ] Người đọc quyết được trong 2 phút, không cần mở tài liệu khác
- [ ] Brief trỏ đúng `gate_doc` để người duyệt xem toàn văn trên tower

## Changelog
- v2: thêm nhánh review-intent-plan (3 phần), ràng buộc tự đủ + nguồn + ≤5h; theo protocol v2
- v1: bản đầu
