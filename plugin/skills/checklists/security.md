---
name: security
version: 2
---
# Checklist Security/DevSecOps · v2 — specialist theo trigger (§4.17: auth/authz/session/token/crypto/PII/secret). Vẫn có quyền block release khi MUST chưa đóng.
## design (threat model nhẹ)
- [ ] Authz: từng endpoint/màn theo đúng role-matrix dự án; deny-by-default
- [ ] Dữ liệu nhạy cảm: nhận diện, mã hóa/che khi log
## code
- [ ] Không secrets trong code/config commit; input validation server-side; chống injection (SQL/command/XSS)
- [ ] Upload/download: content-type, size limit, path traversal
## deps & pipeline
- [ ] Dep mới: CVE check + lockfile; CI không leak env
## Phân loại: [MUST] chặn release · [SHOULD] ghi nhận
## Changelog
- v1: bản đầu
- v2: chuyển thành specialist theo trigger §4.17 — không còn review mặc định mọi bolt (6.0.0); quyền block MUST giữ nguyên
