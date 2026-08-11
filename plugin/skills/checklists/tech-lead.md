---
name: tech-lead
version: 1
---
# Checklist Tech Lead · v1
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
