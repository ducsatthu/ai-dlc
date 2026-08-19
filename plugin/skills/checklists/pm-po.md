---
name: pm-po
version: 4
---
# Checklist PM/PO · v4 — từ v6 dùng làm pre-flight của unit-planner; pm-po-reviewer chỉ spawn khi người yêu cầu (§4.17)
- [ ] **Mỗi Unit khai `review:` tầng kèm căn cứ trigger** (§4.17) — bảng tầng là thứ người duyệt ở Gate D
## Unit & phân rã
- [ ] Mỗi Unit = observable outcome; không có pseudo-unit (Update DB/Add API/Update UI)
- [ ] AC từng Unit đo được, trace về intent
- [ ] **Mỗi Unit khai `releasable`** (nếu `no` thì có `released_with`) **và `session_fit` có con số** (§4.9 v5)
- [ ] Ước lượng có **breakdown theo hạng mục** (design/BE/FE/test/review) — không còn trần giờ cứng
- [ ] Căn cứ ước lượng là **con số thật** (mấy endpoint, mấy màn, mấy bảng) — không phải cảm tính
- [ ] Unit không tự ra được sản phẩm đã gộp/cắt lại, và mỗi mảnh vẫn là capability quan sát được
      (không cắt thành task kỹ thuật; hai mảnh phải ghép mới release được = cắt sai trục)
- [ ] Tổng est của các Unit khớp bảng tổng quan; không Unit nào ghi số tròn cho có, không `session_fit` chép nguyên si giữa các Unit
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
- v3: bỏ trần 5h; Unit đo bằng `releasable` + `session_fit` có con số (protocol §4.9 v5)
- v4: pre-flight của unit-planner + mục khai `review:` tầng (§4.17, 6.0.0)
