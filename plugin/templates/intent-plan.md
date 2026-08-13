---
type: intent-plan
id: INT-NNN
title: <tên intent>
gate: A
version: 1
created: <ngày>
authors: [dlc-intent-analyst, dlc-source-planner]
sources_planned: 0
units_proposed: 0
total_estimate_hours: 0
---

# INT-NNN · <tên intent> — Kế hoạch Intent (tài liệu Gate A)

> Tài liệu này **tự đủ**: người duyệt đọc xong quyết được mà không cần mở file khác.
> Duyệt tài liệu này = đồng ý cả ba: (1) đích đến, (2) **sẽ đọc những nguồn nào để hiểu bối cảnh**,
> (3) trục phân rã Unit và khối lượng dự kiến. Chưa duyệt → không agent nào được chạy stage 2.

---

## PHẦN 1 — INTENT (đích đến)

### 1.1 Problem — đang đau gì
<Mô tả nỗi đau thật, đo được nếu có. MỖI khẳng định kèm nguồn dạng `(nguồn: path#section)`.>

### 1.2 Outcome — đo bằng gì
<Kết quả quan sát được sau khi xong. KHÔNG viết giải pháp. Dạng: "Ai làm được gì / chỉ số nào đổi từ X → Y".>

- [ ] O1: …
- [ ] O2: …

### 1.3 Ngoài phạm vi (out of scope)
<Cái người ta dễ tưởng có trong đợt này nhưng KHÔNG có. Ghi rõ để tránh scope creep ngầm.>

### 1.4 Priority & lý do
<P0/P1/P2 + căn cứ (quyết định nào, ngày nào, ai).>

### 1.5 Brownfield type
`add-feature | optimize-nfr | tech-debt | fix-defect | green-field`

### 1.6 Vùng ảnh hưởng (theo workspace-map — không đoán path)
| Vùng | Path (từ workspace-map) | Dự kiến đụng tới |
|---|---|---|
| backend | | |
| frontend | | |
| docs/wiki | | |
| dữ liệu / hệ ngoài | | |

### 1.7 Mâu thuẫn & điểm phải confirm tại Gate A
<Chỗ tài liệu đá nhau, chỗ quyết định nằm ngoài repo, chỗ agent KHÔNG được tự chọn một bên.
Mỗi mục: mâu thuẫn gì · hai bên nói gì · ai chốt được · hệ quả nếu chọn sai.>

1. [CONFLICT] …
2. [OPEN] …

---

## PHẦN 2 — SOURCE READING PLAN (sẽ đọc gì, ở đâu, lấy thông tin gì)

> Bảng này do `dlc-source-planner` dựng bằng cách **quét thật** workspace (Glob/Grep theo workspace-map),
> không liệt kê theo trí nhớ. Nguồn không tồn tại vẫn phải có dòng, trạng thái `missing`.
> Sau Gate A, mọi nguồn ở đây phải có trạng thái cuối trong `as-is/source-ledger.md` — còn `planned` là
> CẤM mở Gate B (protocol §4.8).

### 2.1 Bảng nguồn

| # | Nguồn (path/địa chỉ) | Loại | Vì sao cần cho intent này | **Thông tin cụ thể phải lấy ra** | Ai sở hữu | Ưu tiên | Rủi ro nếu bỏ qua | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| S1 | wiki/docs/… | doc-SSOT | | | | P0 | | planned |
| S2 | app-be/…/models/ | code | | | | P0 | | planned |
| S3 | swagger/… | api-spec | | | | P1 | | planned |
| S4 | app-fe/…/app/ | code | | | | P1 | | planned |
| S5 | tests/… | test | | | | P2 | | planned |
| S6 | DB schema / migration | schema | | | | P1 | | planned |
| S7 | ticket/tracker … | tracker | | | | P2 | | planned |
| S8 | <hệ ngoài / người> | external | | | | P1 | | missing |

*Loại*: `doc-SSOT` · `doc-phụ` · `code` · `api-spec` · `schema` · `test` · `tracker` · `decision` · `runtime-log` · `external`.
*Trạng thái ban đầu*: `planned` (sẽ đọc) hoặc `missing` (biết là không có → phải hỏi người).

### 2.2 Thứ tự đọc & lý do
<Đọc SSOT trước, quyết định đã chốt kế tiếp, rồi code, rồi test, rồi schema. Nêu rõ chỗ nào phải đọc
trước vì nó quyết định cách hiểu chỗ sau.>

### 2.3 Nguồn KHÔNG đọc (và vì sao)
<Chống "đọc cho đủ": nêu vùng cố tình bỏ + lý do. Nếu sau này phát hiện phải đọc → thêm `[ADDED]` vào ledger.>

### 2.4 Câu hỏi chỉ người trả lời được (không có trong repo)
| # | Câu hỏi | Ai trả lời | Deadline | Ảnh hưởng nếu không có câu trả lời |
|---|---|---|---|---|
| Q1 | | | | |

### 2.5 Coverage tự đánh giá
- Nguồn P0 đã liệt kê hết chưa? Căn cứ nào để nói "hết"? <ghi câu lệnh quét đã chạy, ví dụ `glob app-be/**/models/*.py`>
- Vùng nào của intent hiện **chưa có nguồn nào phủ**? → đó là rủi ro lớn nhất, ghi vào 3.x của Unit liên quan.

---

## PHẦN 3 — PROVISIONAL UNIT MAP (phân rã dự kiến)

> Dự kiến, sẽ refine sau khi đọc AS-IS và chốt lại tại Gate D bằng `unit-plan.md`.
> **Luật cứng: mỗi Unit ≤ 5 giờ elapsed cho toàn vòng đời (design + code + test + review + fix).**
> Unit >5h phải tách ngay tại đây, không để tới Gate D.

### 3.1 Trục phân rã đã chọn
<Chia theo cái gì: theo actor / theo luồng nghiệp vụ / theo trạng thái dữ liệu / theo happy-path trước.
Nêu 1 trục đã loại và vì sao — cho người duyệt thấy đây là lựa chọn, không phải mặc định.>

### 3.2 Bảng tổng quan Unit

| Unit | Tên (capability quan sát được) | Est (h) | Bolt dự kiến | Phụ thuộc | Nguồn chứng minh |
|---|---|---|---|---|---|
| UOW-01 | | 4.0 | 1 | — | S1, S2 |
| UOW-02 | | 4.5 | 2 | UOW-01 | S1, S4 |
| | **Tổng** | **0.0** | | | |

### 3.3 Chi tiết từng Unit

#### UOW-01 · <tên>
**Mô tả (observable outcome)**: <xong rồi thì ai nhìn thấy cái gì khác đi>

**User Story**
> Là **<vai trò>**, tôi muốn **<hành động>**, để **<giá trị nghiệp vụ>**.

Acceptance Criteria (đo được, trace về outcome O_x):
- [ ] AC1 — …
- [ ] AC2 — …

**NFR** (chỉ ghi cái thật sự ràng buộc Unit này, có ngưỡng số)
| Loại | Yêu cầu | Ngưỡng | Đo bằng |
|---|---|---|---|
| performance | | | |
| security | | | |
| khả dụng/lỗi | | | |

**Rủi ro**
| ID | Rủi ro | Mức | Trigger (dấu hiệu sớm) | Giảm thiểu | Chủ |
|---|---|---|---|---|---|
| R1 | | high/med/low | | | |

**Ước lượng ≤5h — breakdown**
| Hạng mục | Giờ | Căn cứ |
|---|---|---|
| domain + logical design | | |
| code BE | | <mấy endpoint / bảng> |
| code FE | | <mấy màn / component> |
| test | | |
| review + fix | | |
| **Tổng** | **≤5.0** | |

**Nguồn cần đọc trước khi làm Unit này**: S1, S2 (từ bảng 2.1)

<lặp khối trên cho UOW-02, UOW-03, …>

### 3.4 Unit đã cân nhắc rồi loại / defer
| Ứng viên | Vì sao loại/defer | Điều kiện để đưa lại vào |
|---|---|---|

---

## QUYẾT ĐỊNH CẦN Ở GATE A

1. **Đích đến** — Outcome ở 1.2 đúng cái bạn muốn?
2. **Nguồn** — Bảng 2.1 đã đủ chưa? Có nguồn nào bạn biết mà agent chưa liệt kê? (đây là chỗ hay thiếu nhất)
3. **Mâu thuẫn** — các mục ở 1.7 chốt theo bên nào?
4. **Phân rã** — trục ở 3.1 và khối lượng ở 3.2 hợp lý?

**Khuyến nghị của AI**: <1–3 câu, nêu rõ khuyến nghị gì và vì sao>

**Nếu duyệt**: stage 2 chạy đúng theo bảng 2.1, sinh `as-is/source-ledger.md`.
**Nếu cần sửa**: bấm *Yêu cầu chỉnh sửa* trên Control Tower — ghi rõ phần nào (1.x / 2.x / 3.x); bản mới sẽ bump version và ghi changelog dưới đây.

## Changelog
- v1: bản đầu
