---
name: dlc-retro
description: Learning loop AI-DLC — retro sau release (hoặc theo yêu cầu): rút lesson learned từ dấu vết intent, đề xuất patch checklist/DoD, mở Gate G rồi DỪNG; approve thì apply vào overrides + nhắc contribute.
---

**Engine `contracts`** (7.0.0-a, template đội): không có HOF, MSG, RV để đọc. Retro dựa trên dấu vết máy ghi.
1. Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/contracts_retro.py <root> --write` (thêm `--since YYYY-MM-DD` cho một đợt).
   Script đọc `docs/intents/*/approvals.json`, `evidence.md` và `.ai-dlc/log/*.jsonl` (hook `observe.py` ghi), đếm mẫu lặp,
   ghi `<governance>/lessons-learned/candidates.md`. Mã: `R01` gate bị trả lại nhiều vòng · `R02` cùng lệnh test đỏ liên tiếp ·
   `R03` validator error lặp sau khi đã duyệt · `R04` unit Fail nhiều lần · `R05` gate chờ lâu sau khi validator sạch ·
   `X01` cùng mẫu ở nhiều change (đọc trước).
2. Spawn `ai-dlc:dlc-retro-keeper` với `candidates.md` và PR comment của change (nếu lấy được). Kết quả: `LL-NNN.md` trong
   `<governance>/lessons-learned/`, mỗi LL trỏ ít nhất một mã ứng viên và bằng chứng của mã đó. Không có ứng viên thì không
   có LL. Không bịa lesson từ cảm giác.
3. Gate G: người nói approve trong chat, ghi DEC vào `<governance>/decisions-log.md`.
4. Patch: gói không sửa luật của đội. LL thành đề xuất PR vào `docs/memory/` (hoặc `REVIEW.md`, `docs/intents/_templates/`).
   Lesson thuộc về gói thì `/ai-dlc:dlc-contribute`.
Log là bằng chứng retro nên commit `.ai-dlc/log/`; chỉ ignore `.ai-dlc/tower/`. Các bước dưới là của engine `ai-dlc`.

1. Spawn `ai-dlc:dlc-retro-keeper` cho intent vừa đóng (hoặc intent user chỉ định) → LL-NNN + patch đề xuất (diff cụ thể, version cũ→mới).
   Nguồn bằng chứng của retro, theo thứ tự: **`handoffs/HOF-*.md`** (việc đi qua tay ai, bao nhiêu vòng,
   `returned` vì thiếu gì, HOF nào treo lâu) · `revisions/REV-*.md` (gate phải sửa mấy vòng, vì sao) ·
   `as-is/source-ledger.md` (nguồn nào `missing`/`deferred` đã trả giá) · RV/DEC/MSG · `session/log/SES-*.md`.
   Chuỗi HOF là chỗ nhìn ra vấn đề phối hợp giữa các vị trí — đừng bỏ qua nó để chỉ đọc kết quả cuối.
1b. **Đếm sự vắng mặt, không chỉ đọc cái đang có** (LL-002 §1 · LL-003) — ba phép đối chiếu rẻ, mỗi cái từng
   lộ ra một lỗ hổng mà mọi thứ khác đều im lặng:
   - `comms/` (review-request đã gửi) **so với** `reviews/RV-*.md` có `re:` trỏ unit của intent này.
     Ca thật: 13 gửi đi, 0 verdict quay lại, 17 unit vẫn đóng.
   - `units/*/spec.md` `status: done` **so với** `rv:`/`review_waived_by:` — có bao nhiêu unit tự khai xong.
   - Unit đã đóng **so với** sự tồn tại của `bolts/BOLT-NN/`, `tasks.md`, `evidence/`. Ca thật: 14/18 unit
     không có thư mục bolt nào, trong khi mọi HOF đều khai đang chạy `BOLT-01`.
   Khoảng trống tìm ra ở đây **ghi vào LL, KHÔNG dựng bù**: hồ sơ viết ngược từ code đã chạy là mô tả code
   đội lốt quyết định thiết kế, và nó xoá luôn khả năng ai đó phát hiện vấn đề ở intent sau.
2. Mở **Gate G**, DỪNG (trình LL + patch).
3. Approve → DEC; apply patch vào `.ai-dlc/overrides/` (mode patch, frontmatter source: LL-NNN); tăng version + changelog governance; cập nhật OVERRIDES.md index; nhắc `/ai-dlc:dlc-contribute` nếu lesson mang tính chuẩn chung.

**Autopilot (protocol §2.3, 6.4.0)**: retro vẫn chạy đủ; thêm bảng KPI `autopilot.decisions · reversed · blocked(#) ·
reversed_after_release` và liệt kê từng DEC bị **Đảo** (đó là nguồn LL tốt nhất: AI chọn gì, người đổi thành gì, vì sao).
LL ghi không chờ; **patch vào overrides/gói vẫn dừng chờ người ký** (đổi luật cho lần sau = đảo đắt).
