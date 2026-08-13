---
type: source-ledger
id: INT-NNN
gate: B
version: 1
based_on: intent-plan.md v<N>
planned: 0
read: 0
missing: 0
deferred: 0
added: 0
conflicts: 0
---

# INT-NNN · Source Ledger (tài liệu Gate B)

> Sổ cái nguồn: mỗi nguồn trong Source Reading Plan phải kết thúc ở một trạng thái **cuối**.
> Còn dòng `planned` → CẤM mở Gate B (protocol §4.8). Đây là bằng chứng "đã đọc thật", không phải danh sách ý định.

## 1. Tổng kết coverage

| Trạng thái | Số | Nghĩa |
|---|---|---|
| `read` | | đã đọc, có evidence (vùng đọc + phát hiện) |
| `missing` | | không tồn tại / không truy cập được → đã hỏi ai, ngày nào |
| `deferred` | | cố ý hoãn → ai chịu, tới mốc nào, rủi ro chấp nhận |
| `superseded` | | bị nguồn khác thay thế → trỏ tới nguồn thay |
| `[ADDED]` | | phát hiện ngoài plan, đã bổ sung |

## 2. Sổ cái

| # | Nguồn | Trạng thái | Vùng đã đọc (dòng/section) | Phát hiện rút ra (1 câu) | Dùng cho Unit | Ghi chú |
|---|---|---|---|---|---|---|
| S1 | wiki/docs/… | read | §2.3, §4 | … | UOW-01 | |
| S2 | app-be/…/models.py | read | L1–L120 | … | UOW-01, UOW-02 | |
| S3 | swagger/openapi.yaml | missing | — | file không tồn tại | — | đã hỏi <ai> ngày <ngày> |
| S9 | app-be/jobs/cron_x.py | read `[ADDED]` | L30–L88 | … | UOW-05 | ngoài plan — phát hiện khi đọc S2 |

## 3. Mâu thuẫn giữa các nguồn

| # | Nguồn A nói | Nguồn B nói | Ảnh hưởng tới | Ai chốt được | Trạng thái |
|---|---|---|---|---|---|
| C1 | | | | | open → Gate C |

**Agent KHÔNG tự chọn bên nào.** Mỗi mâu thuẫn thành một câu hỏi Gate C.

## 4. Vùng vẫn chưa có nguồn phủ

<Chỗ intent chạm tới mà không nguồn nào nói được. Đây là rủi ro cao nhất — phải thành risk có chủ,
hoặc thành câu hỏi cho người, KHÔNG được lấp bằng suy đoán.>

| Vùng chưa phủ | Vì sao không có nguồn | Xử lý (hỏi ai / giả định [ASSUMED] + risk) |
|---|---|---|

## 5. Kết luận cho Gate B

- AS-IS dựng từ những nguồn nào: …
- Khẳng định nào là `[INFERRED]` (suy luận, chưa có nguồn trực tiếp): …
- Điều người duyệt cần xác nhận: …

## Changelog
- v1: bản đầu
