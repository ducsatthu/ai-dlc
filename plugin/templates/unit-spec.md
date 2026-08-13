---
id: UOW-NN
intent: INT-NNN
title: <tên capability>
status: proposed        # proposed → in-bolt → done|approved (đồng nghĩa) · descoped nếu ra ngoài phạm vi
                        # obsolete = đã chuyển vào units/_trash/ kèm TOMBSTONE.md (protocol §4.14)
estimate_hours: 0.0
bolts: 1
depends_on: []
sources: [S1, S2]
stories: 0
nfrs: 0
risks: 0
# Một trong hai dòng dưới BẮT BUỘC có trước khi được `done` (protocol §4.12 · DoD v3).
# Thiếu cả hai = unit tự khai hoàn thành, không phải được người thứ hai soát.
reviewed_by:            # <agent> — kèm rv: RV-NNN có thật, `re:` khớp unit này
rv:                     # RV-NNN
review_waived_by:       # DEC-NNNN — nếu cố ý bỏ review lượt này, phải nói vì sao trong DEC đó
tests:                  # [đường dẫn file test phủ unit này] — hoặc đặt tên *.uowNN.test.*
---
# Unit — <tên>

## Mô tả (observable outcome)
<Xong rồi thì ai nhìn thấy cái gì khác đi. Không mô tả kỹ thuật ở đây.>

## Acceptance Criteria (đo được, trace về intent)
- [ ] AC1 — … *(trace: outcome O1)*
- [ ] AC2 — …

## Ước lượng — BẮT BUỘC ≤5.0h (protocol §4.9)
| Hạng mục | Giờ | Căn cứ (con số thật: mấy endpoint/màn/bảng) |
|---|---|---|
| domain + logical design | | |
| code BE | | |
| code FE | | |
| test | | |
| review + fix sau review | | |
| **Tổng** | | |

>5h → phải tách Unit. Tách xong vẫn phải là capability quan sát được, không phải "Update DB".

## Dependency (Units khác)
| Unit | Cần gì từ nó | Chặn hay chỉ thứ tự |
|---|---|---|

## Nguồn đã đọc để viết Unit này (theo source-ledger)
| # | Nguồn | Dùng để kết luận điều gì |
|---|---|---|

## Bolt đề xuất
| Bolt | Phạm vi | Est (h) | Song song/tuần tự | Contract cần freeze |
|---|---|---|---|---|

## Liên kết bắt buộc
- User Story → `user-stories.md`
- NFR → `nfr.md`
- Rủi ro → `risks.md`

Thiếu bất kỳ file nào trong ba file trên → Unit KHÔNG đạt DoR, không vào Bolt.
