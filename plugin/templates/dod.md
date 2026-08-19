---
name: dod
version: 4
updated_by: /dlc-init (seed mặc định — duyệt lại tại Gate D đầu tiên)
source: LL-002 (Gate G · DEC-0027) · LL-001 — retro INT-001 dự án PCT
---
# Definition of Done · v4 — Unit được coi là xong khi:

## Bắt buộc (v1–v2)

- [ ] Mọi AC pass với test thật (không mock kết quả)
- [ ] Mọi NFR trong `nfr.md` được đo đúng ngưỡng đã khai, kết quả nằm trong evidence
- [ ] Quality gate **theo tầng review đã duyệt ở Gate D** (§4.17): tier `none` = self-verify đủ mục có con
      trỏ + ca đối chứng/mutation test (§4.15) · tier `peer`/`specialist` = RV verdict `approve*` từ đúng vai
- [ ] Security gate: [MUST] findings = 0
- [ ] Docs cập nhật đúng đích theo workspace-map
- [ ] Chuỗi truy vết đủ: code → design → spec → **source-ledger** → DEC → RV → MSG → intent
- [ ] Giả định `[ASSUMED]` còn hiệu lực được nêu lại; cái nào đã sai → risk/tech-debt có chủ
- [ ] Limitations ghi thành văn trong evidence

## Bắt buộc (v3 — sinh từ retro, mỗi mục ghi rõ nó chữa cái gì)

> Đừng áp mà không đọc lý do: mỗi mục làm Unit nặng thêm và chỉ đáng khi hiểu nó đổi lấy gì.

- [ ] **Review có địa chỉ, không phải lời hứa** *(chữa: 13 review-request gửi đi, 0 verdict nhận về, 17 unit
      vẫn đóng)* — `spec.md` mang một trong ba, ĐÚNG theo tầng: `reviewed_by:` + `rv: RV-NNN` (file RV
      **tồn tại thật**, `re:` khớp Unit) · `self_verify:` trỏ file thật đủ mục có con trỏ (chỉ tier `none`
      đã duyệt) · `review_waived_by: DEC-NNNN` (ngoại lệ). Thiếu cả ba ⇒ không được `done`.
      Gửi review-request rồi đóng HOF trong cùng lượt là ca luật này tồn tại để chặn. (protocol §4.12 · §4.17)

- [ ] **Mọi nút render ra đều phải có hành vi** *(chữa: nút "Uỷ quyền" tồn tại, dialog tồn tại, không ai nối
      hai thứ lại — cả 682 test đều xanh)* — hoặc có `onClick` thật, hoặc `disabled` + `title` giải thích vì
      sao chưa dùng được. Nút sống mà không làm gì là **lỗi**, không phải placeholder.

- [ ] **Bấm thử, không chỉ smoke HTTP** *(chữa: trang render 200 không phân biệt được nút sống với nút chết)*
      — một lượt bấm các affordance chính trước khi tuyên bố xong, hoặc test tương tác cho từng nút.

- [ ] **Phát hiện ngoài phạm vi thành việc, không thành ghi chú** *(chữa: id-space bị 4 HOF ghi nhận rồi vẫn
      tới tay người dùng dưới dạng 404)* — mở `escalations/ESC-NNN.md`, không chỉ ghi vào HOF. (§4.13)

- [ ] **Đụng enum thì grep mọi so sánh bằng** *(chữa: xoá `'ADMIN'` khỏi persona giết một luật ở file khác;
      compiler lẫn test đều im)* — thu hẹp/xoá giá trị của union ⇒ grep toàn repo `=== '<giá trị>'`. (§4.16)

- [ ] **Phép đo tự chứng minh trước khi tin** *(chữa: 4 lần đo hỏng cho kết quả NGƯỢC, 3 lần suýt báo ra ngoài)*
      — chạy một ca đối chứng đã biết chắc kết quả ngược lại; test bảo vệ phải mutation-test. (§4.15)

- [ ] **Test truy ngược được về Unit** — đặt tên `*.uowNN.test.*`, hoặc `spec.md` liệt kê thẳng đường dẫn
      file test phủ nó. Không truy được thì không chứng minh được Unit này đã được kiểm.

- [ ] **Câu hỏi gửi cho người có dòng "đã soát nguồn nào"** *(chữa: 8 lần hỏi thứ đã có sẵn đáp án trong wiki
      hoặc trong chính code đang chạy)* — xem §4.10 điểm 9.

- [ ] **Unit lỗi thời vào `units/_trash/` + `TOMBSTONE.md`**, hạ `status: obsolete`. Unit được viết lại sau
      khi trượt thì không vào đây. Không xoá. (§4.14)

## Changelog

- **v4**: quality gate theo tầng review §4.17 — self-verify (tier `none`) là đường bằng chứng thứ ba bên
  cạnh RV và DEC miễn (6.0.0, quyết định chủ gói, nợ LL).
- **v3**: 9 mục từ retro INT-001 (`LL-001` 8 patch + `LL-002` P-2..P-6, Gate G · DEC-0027). Trọng tâm:
  biến các luật sẵn có từ **câu chữ** thành **trường đối chiếu được** — v1 đã yêu cầu "reviewer approve"
  và nó vẫn trượt 17 lần liên tiếp vì không ai kiểm được.
- v2: thêm NFR đo thật, mắt xích source-ledger trong chuỗi truy vết, xử lý [ASSUMED] (protocol v2)
- v1: seed mặc định từ plugin
