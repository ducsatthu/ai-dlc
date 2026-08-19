---
unit: UOW-NN
bolt: BOLT-NN
by: <agent — chính dev làm unit>
checklist: <backend|frontend> v<N>          # bản trong pinned/ của intent
tier: none                                   # file này CHỈ hợp lệ khi spec.md khai review: none đã duyệt Gate D
date: <ISO>
---
# Self-verify · UOW-NN / BOLT-NN

> **Đây không phải danh sách dấu ✓.** Từng mục phải mang **con trỏ bằng chứng** mà người khác mở ra kiểm
> lại được — vì người giao SẼ mở 1–2 con trỏ trong file này khi nghiệm kết quả (§9.6), và doctor soi mục
> ✓ suông. Mục "n/a" phải có lý do. §4.15 bắt buộc ở tier này: ca đối chứng + mutation test.

## 1. Design (đối chiếu checklist tech-lead — mục design)

| Mục checklist | Đạt/n-a | Con trỏ bằng chứng (file:dòng · output · ADR) |
|---|---|---|
| | | |

## 2. Code + Test (đối chiếu checklist BE/FE — TỪNG mục, không bỏ dòng)

| Mục checklist | Đạt/n-a | Con trỏ bằng chứng |
|---|---|---|
| Khớp contract FROZEN | | `contract.md vN` · diff … |
| Tests: mỗi AC ≥1 test | | `AC1 → path/x.uowNN.test.ts:12` … |
| | | |

## 3. Phép đo tự chứng minh (§4.15 — BẮT BUỘC, vì không có người thứ hai)

- **Ca đối chứng** (một ca biết chắc kết quả ngược): làm gì · kỳ vọng gì · ra gì → kết luận công cụ đo tin được không
- **Mutation test** (bỏ nhánh được bảo vệ, test phải đỏ): sửa gì · test nào đỏ · đã revert

## 4. Trigger soát lại lần cuối

Đã grep lại diff theo bảng trigger §4.17 (auth/PII · migration/public API · NFR ngưỡng đo): **không dính**
— nếu dính thì file này vô hiệu, phải NÂNG tầng + MSG note, không được đóng unit bằng self-verify.
