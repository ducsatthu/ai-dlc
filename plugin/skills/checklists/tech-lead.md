---
name: tech-lead
version: 2
---
# Checklist Tech Lead · v2 — specialist theo trigger (§4.17: migration phá hủy · đổi public API · ADR trái pattern) + escalation
## review-approach / design
- [ ] Domain Design độc lập hạ tầng; Logical Design áp đúng NFR đã khai
- [ ] Mỗi quyết định kiến trúc có ADR (bối cảnh, phương án, hệ quả)
- [ ] Đúng pattern hiện có của dự án (dẫn file tương tự); lệch pattern phải có ADR
- [ ] Mọi external call: hỏi batch limit / timeout / retry ngay ở Domain Design
- [ ] Migration có rollback; breaking change có kế hoạch
## review-techstack / infra
- [ ] Dependency/hạ tầng thêm mới: có đáng không? cách đơn giản hơn? → không đáng thì ghi tech-debt-register và dùng cách thường
- [ ] IaC/config thay đổi được review như code
## Changelog
- v1: bản đầu
- v2: chuyển thành specialist theo trigger §4.17 — không còn review mặc định mọi design (6.0.0)
