---
name: pm-po
version: 2
---
# Checklist PM/PO · v2
## Unit & phân rã
- [ ] Mỗi Unit = observable outcome; không có pseudo-unit (Update DB/Add API/Update UI)
- [ ] AC từng Unit đo được, trace về intent
- [ ] **Ước lượng mỗi Unit ≤5.0h** và có **breakdown theo hạng mục** (design/BE/FE/test/review)
- [ ] Căn cứ ước lượng là **con số thật** (mấy endpoint, mấy màn, mấy bảng) — không phải cảm tính
- [ ] Unit >5h đã được tách, và bản tách vẫn là capability quan sát được (không tách thành task kỹ thuật)
- [ ] Tổng est của các Unit khớp bảng tổng quan; không có Unit nào "ghi 5h cho tròn"
- [ ] Mỗi Unit có đủ ba khối **User Story · NFR · Rủi ro** (file tồn tại, không rỗng)

## Kế hoạch & rủi ro
- [ ] Bolt plan ghi rõ dependency; Unit độc lập được xếp song song; có nêu đường găng
- [ ] Risk: mỗi risk có mức + chủ + trigger; risk high không chủ → request-changes
- [ ] Rủi ro do **thiếu nguồn** (nguồn `missing`/`deferred` trong ledger) đã thành risk có chủ
- [ ] DoD/DoR version áp dụng ghi rõ trong đề xuất Gate D
- [ ] Phạm vi mỗi Bolt khả thi trong giờ→ngày (không phải mini-sprint 2 tuần trá hình)

## Tài liệu Gate D
- [ ] `unit-plan.md` có mục "Đã đổi gì so với provisional" — nếu không đổi, phải nói rõ vì sao và lấy gì chứng minh
- [ ] Bảng coverage nguồn không còn dòng `planned`
- [ ] Trade-off cần người quyết được nêu tường minh, kèm khuyến nghị

## Changelog
- v2: thêm luật ≤5h + breakdown + US/NFR/risk bắt buộc + coverage nguồn; theo protocol v2
- v1: bản đầu
