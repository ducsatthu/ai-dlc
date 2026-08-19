---
id: HOF-NNNN
from: <agent|HUMAN>
to: <agent>
re: INT-NNN[/UOW-NN[/BOLT-NN[/TSK-NN]]]
kind: assign|review|return|escalate|takeover
status: open
created: <ISO>
accepted: -
closed: -
heartbeat: -
progress: -
result_check: -      # NGƯỜI GIAO điền khi nghiệm (§9.6): "pass · <ISO> · <đã kiểm gì>" | "returned · <thiếu gì>"
teammate: -          # tên teammate nếu lượt này chạy bằng phiên riêng (agent team) — §9.5
read_first: []
blocked_by: []
---

# HOF-NNNN · <tên việc, ≤10 từ>

> **Agent nhận việc — làm ngay khi bắt đầu (protocol §9.4):** đặt `status: accepted` + `accepted: <ISO>`
> TRƯỚC khi đọc `read_first`. Sau đó mỗi mốc cập nhật `heartbeat: <ISO>` + `progress: <1 câu>`.
> Không cập nhật = Control Tower coi vị trí này là "chưa ai nhận" dù bạn đang chạy.
>
> `heartbeat` phải là **giờ thật lúc bạn ghi dòng đó** (`date -Iseconds`). Tower đối chiếu nó với mtime của
> chính file này: để nửa đêm, copy giờ cũ hay bịa giờ tròn đều bị gắn cờ *nhịp khai không tin được*.
> Chạy bằng teammate (phiên riêng) thì điền thêm `teammate: <tên pane>` — §9.5.

## Nhiệm vụ (1 câu)
<Làm gì. Một câu. Nếu không viết nổi một câu thì gói việc còn mơ hồ — làm rõ trước khi giao.>

## Phải đọc trước (trỏ, KHÔNG chép)
| # | Đọc gì | Vì sao cần cho việc này |
|---|---|---|
| 1 | `intents/INT-NNN/units/UOW-NN/spec.md` | AC và ước lượng của Unit |
| 2 | `intents/INT-NNN/as-is/source-ledger.md#S2` | trạng thái hiện tại của bảng dữ liệu |

> Quá 8 dòng ở bảng này = gói việc quá to → tách thành nhiều HOF.
> Cần một nguồn không có ở đây → **không tự đọc thầm**: thêm dòng vào ledger (`[ADDED]`) + ghi ở *Còn treo*.

## Ràng buộc / cấm
- <Ví dụ: không sửa contract đã FROZEN; không ghi ngoài path X; không mở rộng scope sang Y.>

## Xong lượt này nghĩa là gì (DoD của lượt)
- [ ] <điều kiện quan sát được 1>
- [ ] <điều kiện quan sát được 2>

## Trả về gì
| Output | Đích | Format |
|---|---|---|
| | | |

---
<!-- Từ đây trở xuống do AGENT NHẬN điền khi đóng HOF. Trỏ path, không chép nội dung. -->

## Đã làm
-

## Còn treo / bàn giao tiếp
-

## Việc phát sinh ngoài phạm vi (không tự làm)
-

---
<!-- Mục dưới cùng do NGƯỜI GIAO điền khi nghiệm kết quả (§9.6) — trước đó kết quả chưa được dùng. -->

## Nghiệm kết quả (người giao — §9.6)
- Đối chiếu *Đã làm* với DoD của lượt: <đủ/thiếu mục nào>
- Bằng chứng đã mở kiểm thật: <chạy test nào / mở file nào — kết quả>
- Kết luận: `result_check: pass|returned` (đã ghi lên frontmatter)
