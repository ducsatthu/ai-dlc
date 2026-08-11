---
name: dlc-contribute
description: Đóng gói một lesson (LL-NNN) + override diff thành PR lên repo plugin ai-dlc để nâng chuẩn chung. Có bước sanitize thông tin nội bộ và preview trước khi tạo PR.
---

1. Args = LL-NNN (mặc định: LL mới nhất đã applied). Gom: LL + override diff liên quan + ngữ cảnh.
2. **Sanitize**: bỏ tên khách hàng/số liệu nội bộ/URL riêng — thay bằng placeholder. In preview đầy đủ cho user duyệt.
3. User đồng ý → tạo branch + commit vào repo plugin (remote lấy từ cấu hình marketplace) và mở PR bằng `gh` (thiếu gh/quyền → in patch để gửi tay). Body PR link LL nguồn.
4. Nhắc maintainer flow: merge → bump version checklist + semver + CHANGELOG (entry bắt buộc link LL).
