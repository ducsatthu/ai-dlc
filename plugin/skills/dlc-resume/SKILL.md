---
name: dlc-resume
description: Vào lại một dự án AI-DLC đã có bằng phiên mới — dựng bảng vị trí từ handoffs, in briefing gọn (intent · gate chờ · ai đang giữ việc gì · inbox · cảnh báo), rồi tiếp tục đúng chỗ dừng. Nạp ít context: tra cứu bằng file markdown khi cần, không nạp lại cả dự án.
---

Đọc `${CLAUDE_PLUGIN_ROOT}/references/protocol.md` §9 (handoff) và §10 (ngân sách context) — hai mục đó là
luật của lệnh này. Yêu cầu `.ai-dlc/` đã tồn tại (chưa có → `/dlc-init`).

## Luật context của lệnh này (quan trọng hơn tốc độ)

Bạn đang vào một dự án có thể đã chạy nhiều tuần. **KHÔNG nạp lại cả dự án.**

- **Được đọc ở bước vào phiên**: stdout của `session_brief.py`, và **tối đa 1 file HOF** của việc bạn sắp làm tiếp.
- **KHÔNG đọc toàn văn** `intent-plan.md`, `unit-plan.md`, `as-is/*`, `decisions-log.md`. Chúng dài, và bạn
  chưa biết mình cần phần nào.
- Cần chi tiết → mở `context-memory/session/INDEX.md`, tra "cần biết X → file Y mục Z", rồi đọc **đúng mục**
  đó (Grep hoặc đọc theo offset). File >200 dòng thì không đọc cả file.
- Phát hiện chỗ hay phải tra mà INDEX chưa có → **thêm một dòng vào INDEX.md**. Đó là cách phiên sau rẻ hơn phiên này.
- Không tóm tắt tài liệu vào hội thoại. Cần lưu thì ghi vào file (HOF / session log), kèm nguồn.

## Các bước

1. **Briefing** — chạy:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_brief.py <project_root> --open-session
   ```
   Script quét `handoffs/`, `status.md` từng intent, `inbox/`, session log gần nhất; kết xuất lại
   `context-memory/session/board.md`; seed `session/INDEX.md` nếu thiếu; tạo `session/log/SES-NNN.md` cho
   phiên này; in briefing. **Đọc stdout, đừng đi đọc lại các file nó vừa quét.**

2. **Trình bày cho người** — thuật lại briefing gọn, đúng thứ tự ưu tiên:
   gate đang chờ người quyết → inbox chưa drain → HOF `returned` → HOF `accepted` treo lâu (dấu hiệu phiên
   trước chết giữa chừng) → cảnh báo nguồn `planned` / unit >5h → intent chưa có gate chờ.

3. **Drain inbox trước mọi thứ khác** (nếu có): mỗi file `inbox/*.json` → đối chiếu `gate_open` trong
   status.md → ghi DEC → move sang `inbox/processed/`. `verdict: request-changes` thì chuyển `/dlc-revise`,
   KHÔNG đóng gate.

4. **Chốt một việc để tiếp** — hỏi người nếu có nhiều lựa chọn ngang nhau; có việc treo rõ ràng thì đề xuất
   thẳng. Rồi:
   - Việc đang treo ở một HOF `accepted`/`returned` → **đọc đúng file HOF đó**, làm tiếp từ mục *Còn treo*.
     Không dựng lại bối cảnh từ đầu, không hỏi lại người những gì HOF đã ghi.
   - Việc mới → **viết HOF mới** (template `${CLAUDE_PLUGIN_ROOT}/templates/handoff.md`) rồi spawn agent bằng
     đúng một câu: *"Đọc `.ai-dlc/context-memory/handoffs/HOF-NNNN.md`, làm theo, cập nhật lại chính file đó
     khi xong."* Không nhồi bối cảnh vào prompt (§9).

5. **Trong lúc làm** — mỗi lần giao việc cho agent khác là một HOF mới; mỗi lần một agent xong là HOF đóng
   lại kèm *Đã làm* / *Còn treo*. Chạy lại `session_brief.py --board-only` sau mỗi lần đổi trạng thái để
   board khớp thực tế (tower cũng đọc `handoffs/` nên `/dlc-tower` sẽ hiện đúng).

6. **Kết phiên** — điền `session/log/SES-NNN.md` (vào phiên thấy gì · đã làm · dừng ở đâu · việc kế tiếp ·
   có gì đáng thành LL không), rồi:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_brief.py <project_root> --close-session SES-NNN
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tower_generate.py <project_root>
   ```
   Mục *Việc kế tiếp* là thứ phiên sau đọc đầu tiên — viết đủ để bắt đầu ngay, không viết "tiếp tục công việc".

## Cấm

- Bắt đầu làm khi inbox còn quyết định chưa drain (bạn sẽ làm trên trạng thái cũ).
- Spawn agent bằng prompt dài thay vì HOF — mất dấu vết, retro không tra được, agent chết là mất bối cảnh.
- Sửa tay `session/board.md` (file sinh ra — sửa HOF rồi chạy lại script).
- Vượt gate đang mở vì "phiên trước chắc đã duyệt rồi". Chưa có DEC là chưa duyệt.
