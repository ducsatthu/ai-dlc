---
name: frontend
version: 3
source: LL-001 (Gate G · DEC-0027) — retro INT-001 dự án PCT
---
# Checklist Frontend · v3 — pre-flight của dev · self-verify · peer/specialist review

> **Cách dùng từ v6 (protocol §4.17)**: dev đọc checklist này TRƯỚC khi code (nằm trong `read_first`
> của HOF) và điền SAU khi code. Unit tier `none` → điền vào `evidence/self-verify.md`, mỗi mục kèm
> **con trỏ bằng chứng**, §4.15 bắt buộc. Tier `peer`/`specialist` → reviewer dùng đúng checklist này
> để verify, không discover.
- [ ] Chỉ dùng field có trong contract FROZEN — không bịa field
- [ ] Đúng pattern dự án: server/client component, state, data fetching, cấu trúc thư mục
- [ ] i18n đủ locale theo quy ước dự án; không hardcode chuỗi
- [ ] Trạng thái loading / error / empty đủ; a11y cơ bản (label, focus, keyboard)
- [ ] Tests: mỗi AC ≥1 test
- [ ] **Không có nút chết**: mọi affordance render ra đều có hành vi, hoặc `disabled` + `title` nói vì sao
      chưa dùng được. *(Chữa: nút "Uỷ quyền" có, dialog có, không AC nào của unit nào yêu cầu nối hai thứ
      lại — 682 test xanh, smoke 200, chỉ bấm tay mới lộ.)*
- [ ] **Đã bấm thử** các affordance chính của màn (không chỉ HTTP 200 / render pass)
- [ ] **AC ghi "X thuộc unit khác" ⇒ phải chỉ ra AC nào (của unit nào) nối X vào Y.** Không có ⇒
      request-changes: đó là lỗ hổng giữa hai unit, không phải chi tiết triển khai.
- [ ] Thu hẹp/xoá giá trị của một union kiểu ⇒ đã grep mọi `=== '<giá trị đã xoá>'` trong repo (protocol §4.16)
## Changelog
- v2: 4 mục từ retro INT-001 — nút chết, bấm thử, đường nối giữa hai unit, grep khi đụng enum (LL-001 P-1/P-2/P-3, LL-002 P-4)
- v1: bản đầu
- v3: đổi cách dùng — pre-flight + self-verify của dev theo §4.17 (6.0.0, quyết định chủ gói, nợ LL); nội dung mục giữ nguyên
