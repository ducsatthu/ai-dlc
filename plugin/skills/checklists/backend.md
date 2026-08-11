---
name: backend
version: 1
---
# Checklist Backend review · v1
- [ ] Khớp contract FROZEN (field, error codes, phân trang, timezone) — lệch = request-changes
- [ ] Khớp Logical Design/ADR; đúng pattern layer của dự án
- [ ] DB: migration + rollback + index cần thiết; không N+1; transaction boundary đúng
- [ ] Error handling nhất quán (envelope/format của dự án); log đủ để trace
- [ ] Tests: mỗi AC ≥1 test; edge case chính (empty/max/duplicate/permission)
## Changelog
- v1: bản đầu
