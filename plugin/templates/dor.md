---
name: dor
version: 3
updated_by: /dlc-init (seed mặc định — duyệt lại tại Gate D đầu tiên)
---
# Definition of Ready · v3 — Unit đủ điều kiện vào Bolt khi:
- [ ] AC đo được, trace về intent
- [ ] Đủ ba khối: User Story (`user-stories.md`) · NFR (`nfr.md`) · Rủi ro (`risks.md`)
- [ ] Khai `releasable` (nếu `no` thì có `released_with`) + `session_fit` có con số (§4.9 v5) + `review:` tầng kèm căn cứ (§4.17); ước lượng có breakdown theo hạng mục và căn cứ bằng con số thật
- [ ] Mọi nguồn Unit cần (`sources:`) đã ở trạng thái `read` trong `as-is/source-ledger.md` — có evidence
- [ ] Open questions liên quan đã đóng hoặc có [ASSUMED] + risk có chủ
- [ ] Dependency với Unit khác đã rõ và thỏa
- [ ] Dữ liệu test / môi trường có sẵn
- [ ] Mỗi NFR có ngưỡng số + cách đo (tức là test được)
## Changelog
- v3: bỏ câu trần 5h sót; thay bằng `releasable`/`session_fit` (§4.9 v5) + khai `review:` tầng (§4.17) — 6.0.0
- v2: thêm coverage nguồn, trần 5h, ba khối US/NFR/risk, NFR phải đo được (protocol v2)
- v1: seed mặc định từ plugin
