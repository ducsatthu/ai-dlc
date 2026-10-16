---
name: dlc-tower
description: Control Tower — generate dashboard từ .ai-dlc/ và serve local (LIVE: tự cập nhật khi agent ghi file, nút Approve/Yêu cầu chỉnh sửa/Reject ghi vào inbox).
---

0. (6.3.0 · 7.0.0-a) Vị trí state và loại tower do `scripts/layout.py` quyết (`references/layout-config.md`). Không chắc gói
   đang hiểu dự án thế nào: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/layout.py --explain`. Output/port lấy từ config
   (`tower.out`, `tower.port`). Engine `aws-v2`: đã archive 7.0.0, lệnh dừng.

   Engine `contracts` (template đội, `docs/intents/` bốn file): tower là một script khác, không có bước generate.
   Chạy nền `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_contracts.py <project_root>` (bind 127.0.0.1, port 8644, in URL
   kèm token). Trang chỉ có một màn chính "Cần tôi quyết": mỗi change chờ gate là một thẻ với bốn file đọc toàn văn, kết
   quả `validate_workflow.py` của đội, ô tên người và hai nút Duyệt / Yêu cầu sửa. Bấm Duyệt là server gọi
   `approvals.py --by <tên người gõ>` của đội. Luật đội never infer approval vẫn giữ: agent không bấm thay, không gọi
   `approvals.py`, không có inbox `gate-*.json` để drain. Việc của agent sau khi người bấm: thấy `approvals.json` đổi
   (hoặc đọc `contracts_brief.py --short`), commit nó trên nhánh của change rồi làm tiếp theo lifecycle của đội.
   Bước 1 đến 5 dưới đây chỉ cho engine `ai-dlc`.
1. Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py <project_root>` → `.ai-dlc/tower/index.html`.
2. Args chứa "serve" → chạy nền `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_serve.py <project_root>`
   (bind 127.0.0.1, in URL kèm token) và arm Monitor watch `.ai-dlc/inbox/*.json` để xử lý ngay khi tới:
   `gate-*` (ghi DEC, chạy tiếp flow) · `answer-*` (Lead trả lời câu hỏi trên thẻ — áp nguyên văn vào
   open-questions, gỡ chặn) · `direction-*` (chỉ đạo escalation) — luật ở protocol §5; xong mới move sang
   `processed/`.
3. **Chế độ LIVE (2.2.0)**: khi serve, trang tự poll `/state` mỗi 5 giây và **server tự chạy lại generator**
   nếu `.ai-dlc/` mới hơn `data.js`. Người giám sát thấy vị trí đang làm việc, nhịp sống của từng agent và
   file vừa đổi mà không phải làm gì. Huy hiệu góc phải: `LIVE · <giờ>`.
   - Mở dạng file tĩnh (không serve) → huy hiệu `TĨNH — không tự cập nhật`, phải regenerate tay.
   - Đổi hàng đợi gate (gate mới mở/đóng) → banner nhắc tải lại trang (tài liệu gate không nằm trong `/state`).
4. Regenerate thủ công vẫn dùng được sau mỗi sự kiện, nhưng ở chế độ serve thì **không bắt buộc** nữa.
5. Muốn tower phản ánh đúng ai đang làm gì: agent phải tuân §9.4 — đặt `status: accepted` khi nhận HOF và
   cập nhật `heartbeat`/`progress` ở mỗi mốc. Nếu board hiện "chờ nhận" mà panel *Hoạt động gần đây* lại có
   file trong vùng đó vừa đổi, tower sẽ cảnh báo: có agent chạy mà không khai báo.

**6.4.0 — SVG + autopilot**: tower vẽ flow intent, cây lựa chọn cho từng câu hỏi và thẻ *AI đã tự quyết* (Chọn ≠ Bỏ)
bằng SVG sinh sẵn trong `data.js`. Ngoài `gate-*`/`answer-*`/`direction-*`, inbox có thêm **`steer-*.json`** (người bấm
*Đảo* một DEC autopilot) — Monitor inbox phải bắt cả mẫu này và xử lý **trước tiên** theo protocol §2.3.6.
