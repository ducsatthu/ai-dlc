---
name: backend
version: 2
source: LL-002 (Gate G · DEC-0027) — retro INT-001 dự án PCT
---
# Checklist Backend review · v2
- [ ] Khớp contract FROZEN (field, error codes, phân trang, timezone) — lệch = request-changes
- [ ] Khớp Logical Design/ADR; đúng pattern layer của dự án
- [ ] DB: migration + rollback + index cần thiết; không N+1; transaction boundary đúng
- [ ] Error handling nhất quán (envelope/format của dự án); log đủ để trace
- [ ] Tests: mỗi AC ≥1 test; edge case chính (empty/max/duplicate/permission)
- [ ] **Đụng enum/union**: thu hẹp hoặc xoá một giá trị ⇒ đã grep mọi `== '<giá trị đã xoá>'` trong repo và
      ghi kết quả vào evidence. *(Chữa: bỏ một persona khỏi danh sách làm điều kiện thi hành một business rule
      ở file khác vĩnh viễn sai — kiểu vẫn hợp lệ nên compiler im, test đặt giá trị cũ nên rơi về mặc định.)*
- [ ] **Luật nghiệp vụ đang thi hành ở đâu thì trỏ được ra đó**: mỗi BR/quy tắc chép vào code có link tới
      dòng nguồn trong `source-ledger` — luật nằm trong code mà không bao giờ chạy là lỗi im lặng.
- [ ] Phát hiện ngoài phạm vi unit ⇒ mở `escalations/ESC-NNN.md`, không chỉ ghi vào HOF (protocol §4.13)
## Changelog
- v2: grep khi đụng enum, luật nghiệp vụ trỏ được về nguồn, escalation cho phát hiện ngoài phạm vi (LL-002 P-3/P-4)
- v1: bản đầu
