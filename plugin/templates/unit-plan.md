---
type: unit-plan
id: INT-NNN
title: <tên intent>
gate: D
version: 1
created: <ngày>
authors: [dlc-unit-planner]
based_on: intent-plan.md v<N>
dor_version: 1
dod_version: 1
units_total: 0
total_estimate_hours: 0
---

# INT-NNN · Unit Plan (tài liệu Gate D)

> Bản chốt của phân rã Unit — refine từ Provisional Unit Map (`intent-plan.md` phần 3) **sau khi đã đọc
> AS-IS**. Duyệt tài liệu này = mở khóa Construction cho các Unit trong bảng, **và duyệt cả bảng tầng
> review** — cột Review chính là "unit nào sẽ chạy không reviewer" (§4.17); muốn nâng tầng unit nào thì
> request-changes đúng dòng đó.
> Luật cứng: mỗi Unit đủ **User Story · NFR · Rủi ro**, khai `releasable` + `session_fit` có con số (§4.9 v5)
> và `review:` tầng kèm căn cứ trigger (§4.17). Không còn trần giờ.

## 1. Đã đổi gì so với provisional (đọc trước tiên)

| Unit provisional | Sau khi đọc AS-IS | Vì sao đổi | Nguồn (ledger) |
|---|---|---|---|
| UOW-01 (4h) | tách thành UOW-01 + UOW-04 | bảng `xxx` đã có sẵn cột → bớt việc; nhưng luồng duyệt có 2 trạng thái ẩn | S2, S6 |
| — | UOW-05 (mới) | phát hiện job cron cũ phải sửa cùng lúc | S9 [ADDED] |

Nếu không đổi gì: ghi rõ "không đổi — AS-IS xác nhận đúng giả định ban đầu" (kèm dòng ledger chứng minh).

## 2. Coverage nguồn (điều kiện tiên quyết)

| Chỉ số | Số |
|---|---|
| Nguồn đã lên kế hoạch (intent-plan 2.1) | |
| Đã đọc (`read`, có evidence) | |
| Thiếu (`missing`) — đã hỏi người chưa? | |
| Hoãn (`deferred`) — ai chịu, tới khi nào | |
| Bổ sung ngoài plan (`[ADDED]`) | |
| Mâu thuẫn chưa chốt (`[CONFLICT]`) | |

Còn nguồn `planned` chưa xử lý → **không được trình Gate D** (protocol §4.8).

## 3. Bảng Unit

| Unit | Capability | Est (h) | Bolt | Song song/tuần tự | Phụ thuộc | US | NFR | Risk | Review (§4.17 — vì sao) | DoR |
|---|---|---|---|---|---|---|---|---|---|---|
| UOW-01 | | 4.0 | 1 | // với UOW-02 | — | 2 | 3 | 1 | `specialist(security)` — chạm role-matrix | ✅ |
| UOW-02 | | 3.0 | 1 | | — | 1 | 2 | 1 | `none` — vùng quen, không trigger | ✅ |
| | **Tổng** | **0.0** | | | | | | | | |

## 4. Chi tiết từng Unit

### UOW-01 · <tên>
`spec.md` · `user-stories.md` · `nfr.md` · `risks.md`

**Observable outcome**: …

**User Story chính**
> Là **<vai trò>**, tôi muốn **<hành động>**, để **<giá trị>**.

**Acceptance Criteria** (trace: AC → outcome O_x → intent)
- [ ] AC1 …
- [ ] AC2 …

> **Luật đường nối** (protocol §4.13 · LL-001 P-1): AC nào ghi *"X thuộc unit khác"* thì **bắt buộc** có
> một AC — ở unit này hoặc ở unit kia, ghi rõ ở đâu — nói *"nối X vào Y"*. Cắt việc theo trục "ai sở hữu
> component nào" là đúng để chạy song song, nhưng nó sinh ra mẩu việc *nối hai mảnh lại* mà không unit nào
> nhận: mỗi unit đạt AC của mình, đường nối không có trong AC của ai, và người dùng nhận một nút bấm không
> ra gì. Không được để trống ô này.

**Đường nối với unit khác** *(bỏ trống nếu unit này không phụ thuộc phần việc của unit khác)*
| Mảnh của unit khác | Ai nối | AC nào ghi việc nối | Nghiệm thu bằng gì |
|---|---|---|---|

**NFR ràng buộc**
| Loại | Ngưỡng | Đo bằng | Nguồn ngưỡng |
|---|---|---|---|

**Rủi ro**
| ID | Rủi ro | Mức | Trigger | Giảm thiểu | Chủ |
|---|---|---|---|---|---|

**Ước lượng (breakdown bắt buộc — §4.9 v5, không còn trần giờ)**
| Hạng mục | Giờ | Căn cứ (con số thật từ AS-IS) |
|---|---|---|
| **Tổng** | | |

**Tầng review** (§4.17): `<none|peer|specialist(vai)>` — căn cứ: *đã đối chiếu trigger nào, dính/không dính cái gì*.

**Nguồn đã đọc để viết Unit này**: S1 (read), S2 (read), S6 (read)

**Bolt plan**
| Bolt | Phạm vi | Est (h) | Contract cần freeze | Checkpoint Gate E |
|---|---|---|---|---|

## 5. Thứ tự thực thi & đường găng

```
UOW-01 ──┬─► UOW-03 ─► UOW-05
UOW-02 ──┘
```
Đường găng: … · Unit chạy song song được: … · Nút thắt tài nguyên: …

## 5b. Pre-flight (tự đối chiếu checklist — §4.17.4, thay cho review board mặc định)

| Checklist | Mục | Đạt? | Con trỏ bằng chứng |
|---|---|---|---|
| pm-po v4 | … | | |
| qa v5 (DoR) | … | | |

Mục nào không đạt thì sửa trước khi trình gate — pre-flight có mục fail mà vẫn mở gate là vi phạm.

## 6. Điều kiện DoR/DoD áp dụng
- DoR version: `v<N>` — Unit nào chưa đạt và thiếu gì.
- DoD version: `v<N>` — điều khoản nào đặc biệt áp cho intent này.

## 7. Trade-off cần người quyết tại Gate D
| Lựa chọn | Phương án A | Phương án B | Khuyến nghị + lý do |
|---|---|---|---|

## Changelog
- v1: bản đầu, dựa trên intent-plan.md v<N>
