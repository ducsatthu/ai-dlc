---
name: qa
version: 5
source: LL-002 (Gate G · DEC-0027) — retro INT-001 dự án PCT
---
# Checklist QA/QC · v5 — từ v6 dùng làm pre-flight của unit-planner (DoR) và bolt-coordinator; qa-reviewer chỉ spawn theo trigger NFR có ngưỡng đo hoặc khi người yêu cầu (§4.17)
## DoR check (trước Bolt)
- [ ] AC đo được; dependency rõ; open questions liên quan đã đóng; dữ liệu test có
- [ ] Đủ ba file: `user-stories.md` · `nfr.md` · `risks.md` — và không file nào chỉ có tiêu đề
- [ ] **Mọi nguồn Unit này cần (`sources:` trong spec.md) đã ở trạng thái `read` trong source-ledger** —
      còn `planned` là chưa đủ điều kiện vào Bolt
- [ ] Ước lượng có breakdown; nếu Unit vừa cắt, AC của các mảnh không chồng lấn/bỏ sót **và mỗi mảnh tự
      release được** (§4.9 v5)
- [ ] Mỗi NFR có ngưỡng số + cách đo → tức là test được; NFR không đo được → request-changes
- [ ] Mỗi User Story có edge case/lỗi (hoặc câu hỏi Gate C nếu chưa quyết)

## trong Bolt
- [ ] Test strategy khớp phạm vi; mỗi AC ≥1 test; regression risk với hành vi hiện có được nêu
- [ ] Test cho NFR (không chỉ chức năng) với ngưỡng đúng như `nfr.md`

## QC evidence (stage 7)
- [ ] Chạy lại tests thật — kết quả trong evidence là kết quả thật
- [ ] Đối chiếu AC từng dòng theo dod.md; limitations ghi thành văn
- [ ] Evidence đủ: test output + screenshots + trace links
- [ ] Giả định `[ASSUMED]` nào chưa được xác nhận vẫn còn hiệu lực → nêu rõ trong evidence

## Phép đo phải tự chứng minh (v3 — protocol §4.15)
- [ ] **Mỗi phép đo có một ca đối chứng đã biết chắc kết quả ngược lại** đi kèm. Ca đối chứng không ra như
      mong đợi ⇒ kết luận "công cụ đo hỏng", KHÔNG kết luận về hệ thống. *(Chữa: 4 lần đo hỏng cho kết quả
      NGƯỢC — redirect làm `curl` báo guard không chạy trong khi guard chạy đúng; `grep` trúng payload i18n;
      vòng lặp shell mất `PATH` nên request rỗng bị đọc thành "vào được". 3/4 lần suýt báo cáo ra ngoài.)*
- [ ] **Test bảo vệ phải mutation-test**: bỏ nhánh được bảo vệ thì test phải đỏ. Test chưa từng thấy đỏ chưa
      chứng minh được gì. Ghi rõ bao nhiêu test đỏ / tổng — *"bỏ allow-list chỉ làm 1/8 test đỏ"* là thông
      tin đáng giá về 7 test còn lại.
- [ ] **Smoke HTTP 200 không phải bằng chứng hành vi**: đã bấm thử các affordance chính, hoặc có test tương tác.
- [ ] Mỗi test truy ngược được về Unit (`*.uowNN.test.*` hoặc `spec.md` liệt kê đường dẫn test)
- [ ] Unit khai `done` mà không có `rv:`/`review_waived_by:` ⇒ **request-changes** (protocol §4.12)

## Changelog
- v3: phép đo tự chứng minh + mutation test + smoke không đủ + test truy ngược về unit + chặn `done` thiếu review (LL-002 P-2/P-5, LL-001 P-3)
- v2: DoR soi coverage nguồn + ba file US/NFR/risk + ≤5h; NFR phải đo được; theo protocol v2
- v1: bản đầu
- v4: bỏ trần 5h; Unit đo bằng `releasable` + `session_fit` có con số (protocol §4.9 v5)
- v5: chuyển thành pre-flight của unit-planner/bolt-coordinator; qa-reviewer theo trigger NFR hoặc khi người yêu cầu (§4.17, 6.0.0)
