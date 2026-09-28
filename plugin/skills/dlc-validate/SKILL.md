---
name: dlc-validate
description: Stage 3–4 AI-DLC — Context Validation (Gate B, tài liệu là source-ledger.md) rồi Clarification (Gate C). Mỗi gate mở là DỪNG chờ người quyết trên Control Tower. (Autopilot §2.3: không dừng — chỉ câu chặn không có mặc định mới lên thẻ.)
---

Điều kiện: `gates_passed` chứa A; `as-is/` tồn tại; **`source-ledger.md` không còn dòng `planned`**
(còn → quay lại `/ai-dlc:dlc-discover`, không được validate trên bối cảnh đọc dở).

1. **Gate B — Validation**: spawn `ai-dlc:dlc-context-validator` → bản trình bày AS-IS (≤1 trang, mỗi
   khẳng định kèm nguồn) ghép vào mục 5 của `source-ledger.md`; validator tự pre-flight theo
   `checklists/ba.md` (ba-reviewer chỉ spawn khi người yêu cầu — v6 §4.17.4). Ledger là **gate_doc của Gate B** — người duyệt xác nhận cả hai việc: AS-IS đúng thực tế,
   và coverage nguồn đã đủ (mục 4 "vùng chưa có nguồn phủ" đã được xử lý). Ghi `gate_open: B`,
   `gate_doc: as-is/source-ledger.md`, regenerate tower, DỪNG.
2. **Gate C — Clarify**: khi B approved (DEC): spawn validator phần Clarify → **hai** file (protocol §4.10):
   - `open-questions-business.md` — câu chỉ người nghiệp vụ trả lời được, **viết bằng lời, cấm thuật ngữ code**,
     mỗi câu có phương án chọn sẵn + cái giá + đề xuất của AI + mặc định nếu im lặng. Đây là **gate_doc của C**.
   - `open-questions-tech.md` — câu người kỹ thuật trả lời, kèm bằng chứng `path:line`. Không ra Gate C;
     câu `CHẶN UOW-NN` là **điều kiện chặn Gate D**.
   - Quyết định chạm cả hai phía → viết **cặp mã** `OQB-NN` ↔ `OQT-NN`, nối bằng dòng *Soi chiếu*.
   Nguồn câu hỏi: `[CONFLICT]` trong ledger + mục 2.4 của intent-plan + giả định chưa ai xác nhận.
   Validator **tự soi file business bằng con mắt người không biết code** — thấy đường dẫn hay tên bảng thì
   viết lại (doctor mục 1b kiểm chéo đúng luật này; ba-reviewer chỉ spawn khi người yêu cầu). Ghi `gate_open: C`, `gate_doc: open-questions-business.md`, regenerate tower, DỪNG.
3. Khi C chốt: ghi câu trả lời vào mục *Đã trả lời* của đúng file (kèm DEC), đổi trạng thái trong bảng mục 0,
   bump `version` + changelog. Câu chưa chốt → working assumption `[ASSUMED]` + risk có chủ trong `risks.md`
   của Unit liên quan và `governance/risks.md`. Trước khi sang stage 5: rà `open-questions-tech.md`, câu
   `CHẶN` nào còn `open` thì đẩy cho tech lead ngay — đó là thứ sẽ chặn Gate D.
   Cập nhật status stage 5, regenerate tower. Đề xuất `/ai-dlc:dlc-units`.

**Autopilot (protocol §2.3, 6.4.0)**: `governance/autopilot.md` có `mode: autopilot` ⇒ mọi bước trên vẫn chạy đủ, artefact đủ mục;
chỗ ghi "DỪNG" / "KẾT THÚC LƯỢT" đổi thành: orchestrator chạy **block check** → không block thì tự ghi DEC autopilot
(có *Chọn / Bỏ / Đảo bằng / Hiện ở*) và **chạy tiếp lệnh kế** trong cùng lượt; block thì ghi `blocked_by` rồi mới dừng.
Gate C: câu `không chặn` / `làm lại nếu đổi muộn` áp cột *Nếu im lặng*; câu `CHẶN` không có mặc định khả thi hoặc đảo đắt
= block #1/#2 — **chỉ những câu đó** lên thẻ *Cần tôi trả lời*. Lệnh kế: `/ai-dlc:dlc-units`.
