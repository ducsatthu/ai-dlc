---
name: security
version: 1
---
# Checklist Security/DevSecOps · v1
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
