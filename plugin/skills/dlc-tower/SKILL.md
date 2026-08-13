---
name: dlc-tower
description: Control Tower — generate dashboard từ .ai-dlc/ và serve local (LIVE: tự cập nhật khi agent ghi file, nút Approve/Yêu cầu chỉnh sửa/Reject ghi vào inbox).
---

1. Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py <project_root>` → `.ai-dlc/tower/index.html`.
2. Args chứa "serve" → chạy nền `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_serve.py <project_root>`
   (bind 127.0.0.1, in URL kèm token) và arm Monitor watch `.ai-dlc/inbox/*.json` để xử lý quyết định ngay
   khi tới (ghi DEC, drain sang processed/, chạy tiếp flow).
3. **Chế độ LIVE (2.2.0)**: khi serve, trang tự poll `/state` mỗi 5 giây và **server tự chạy lại generator**
   nếu `.ai-dlc/` mới hơn `data.js`. Người giám sát thấy vị trí đang làm việc, nhịp sống của từng agent và
   file vừa đổi mà không phải làm gì. Huy hiệu góc phải: `LIVE · <giờ>`.
   - Mở dạng file tĩnh (không serve) → huy hiệu `TĨNH — không tự cập nhật`, phải regenerate tay.
   - Đổi hàng đợi gate (gate mới mở/đóng) → banner nhắc tải lại trang (tài liệu gate không nằm trong `/state`).
4. Regenerate thủ công vẫn dùng được sau mỗi sự kiện, nhưng ở chế độ serve thì **không bắt buộc** nữa.
5. Muốn tower phản ánh đúng ai đang làm gì: agent phải tuân §9.4 — đặt `status: accepted` khi nhận HOF và
   cập nhật `heartbeat`/`progress` ở mỗi mốc. Nếu board hiện "chờ nhận" mà panel *Hoạt động gần đây* lại có
   file trong vùng đó vừa đổi, tower sẽ cảnh báo: có agent chạy mà không khai báo.
