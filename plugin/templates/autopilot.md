---
doc: autopilot
version: 2
mode: autopilot            # autopilot | lead
# autopilot: chạy ĐỦ mọi stage và artefact; gate KHÔNG chờ người — orchestrator tự quyết bằng DEC có trade-off,
#            chỉ dừng khi chạm một trong các điều kiện block dưới. Người xem và ĐẢO trên tower.
# lead:      luật 6.x — mỗi gate kết thúc lượt, chờ người bấm trên tower.
wait_hours: 0              # >0: tại gate, chờ N giờ làm việc cho người quyết trước khi tự quyết (0 = quyết ngay)
max_units_per_intent: 8    # stage 1 cắt phạm vi: quá số này ⇒ đề xuất tách intent (ghi DEC autopilot), không làm to
max_self_fix: 2            # cùng một chỗ tự sửa quá N lần vẫn fail ⇒ block, không lặp
notify: []                 # kênh gọi người khi block (PushNotification/Slack — tuỳ dự án; rỗng = chỉ tower)
---

# Autopilot — gate không chờ, nhưng KHÔNG bỏ bước

> Autopilot **không** là "fast mode bỏ qua bước". Tám stage, mọi artefact (intent-plan · source-ledger · AS-IS ·
> open-questions · unit-plan · design + ADR · self-verify/RV · evidence · LL) vẫn phải sinh đầy đủ và đúng
> template. Thứ thay đổi chỉ là **ai quyết ở gate** và **độ sâu tương xứng với phạm vi**: AI cắt phạm vi đủ
> nhỏ để mỗi stage làm trọn trong một lượt, thay vì làm nông rồi kiểm lại. Doctor coi stage thiếu artefact
> là **FIX** (không dựng bù — CLAUDE.md).

## Khi nào DỪNG (block) — hết danh sách này là tự quyết

| # | Điều kiện block | Kiểm bằng |
|---|---|---|
| 1 | Câu hỏi có `Ảnh hưởng: CHẶN UOW-NN` mà **không có phương án mặc định khả thi**, hoặc phương án nào cũng **đảo đắt** (xoá/di trú dữ liệu, public API, auth/PII, tiền, cam kết với khách) | bảng mục 0 của `open-questions-*.md`: cột *Nếu im lặng* rỗng, hoặc cột giá của mọi phương án chạm từ khoá đảo đắt |
| 2 | Validator/QA ghi `CHẶN` vì **thông tin không đủ để viết AC/test** (không phải vì chưa chọn) | thẻ câu hỏi có dòng "Đã soát mà không thấy đáp án" ≥ 3 nguồn **và** không có phương án A/B/C |
| 3 | Nguồn P0 trong Source Reading Plan `missing`/`planned` phủ vùng ảnh hưởng — AI không tự đọc được (ngoài repo, cần người cấp). **Chặn đúng phần việc phụ thuộc nguồn đó**, không chặn cả intent (protocol §2.3.3) | `source-ledger.md` + cột *Dùng cho Unit* |
| 4 | **Ranh đỏ**: deploy môi trường khách/prod · migration phá huỷ (`DROP/TRUNCATE/DELETE` không WHERE) · gửi ra ngoài (PR lên repo khách, email, chat) · chi tiền · đổi quyền truy cập | tên stage/task + grep lệnh |
| 5 | `dlc-doctor` có mục **FIX** trên intent này | doctor |
| 6 | Cùng một chỗ tự sửa quá `max_self_fix` lần vẫn fail (test đỏ lặp, request-changes nội bộ lặp) | đếm REV/lượt fix cùng target |

Block ⇒ ghi `status.md`: `gate_open: X`, `blocked_by: "<#n · 1 câu>"`, tower hiện thẻ đỏ; **kết thúc lượt**
như luật `lead`. Không block ⇒ **tự quyết** (§2.3 protocol): DEC `by: autopilot` với *Chọn / Bỏ / Giá / Đảo bằng /
Hiện ở / Block check*, `gates_auto` thêm gate đó, đi tiếp ngay trong cùng lượt.

## Cắt phạm vi vừa đủ (stage 1 — intent-analyst)

- Provisional Unit Map > `max_units_per_intent` **hoặc** một Unit không `releasable` trong một lượt ⇒ **tách intent**
  (INT kế cho phần sau), ghi DEC autopilot "cắt phạm vi", không làm to để rồi làm nông.
- Mỗi stage kết thúc bằng artefact **đúng template, đủ mục** — không có mục "để sau". Mục nào thật sự chưa
  có dữ liệu thì ghi `[ASSUMED]` + risk có chủ, đó là quyết định được ghi, không phải lỗ hổng.

## Người đảo thế nào

- Tower thẻ *AI đã tự quyết* → nút **Đảo** ⇒ `inbox/steer-*.json` ⇒ orchestrator ghi `revisions/REV-NN` (from: HUMAN,
  gate của DEC đó), giao agent chủ artefact làm lại đúng phần, DEC mới trỏ DEC bị đảo (`reverses: DEC-NNNN`).
- `wait_hours > 0`: gate mở kèm `wait_until`; người quyết trong hạn thì như `lead`; hết hạn ⇒ tự quyết, DEC ghi
  thêm `reason: silent-timeout`.

## KPI (retro đối chiếu — luật không có KPI thì không thêm)

`autopilot.decisions` · `autopilot.reversed` (đảo / tổng — 10–30% là Lead đang nhìn thật; <10% nghi không nhìn;
>30% giả định kém) · `autopilot.blocked` theo điều kiện #1–#6 · `autopilot.reversed_after_release` → 0.

## Changelog

- v1: bản đầu (gói 6.4.0) — quyết định chủ gói 2026-09-28, nợ LL.
- v2 (gói 6.5.0): điều kiện #3 chặn **đúng phần việc phụ thuộc**, không chặn cả intent — từ chạy thử INT-001 dự án demo: luật cũ không nói kiểm ở gate nào.
