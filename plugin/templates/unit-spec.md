---
id: UOW-NN
intent: INT-NNN
title: <tên capability>
status: proposed        # proposed → in-bolt → done|approved (đồng nghĩa) · descoped nếu ra ngoài phạm vi
                        # obsolete = đã chuyển vào units/_trash/ kèm TOMBSTONE.md (protocol §4.14)
estimate_hours: 0.0     # vẫn cần cho đường găng — KHÔNG còn ngưỡng chặn (protocol §4.9 v5)
bolts: 1
# Hai điều kiện kích thước Unit (§4.9) — thay cho trần 5h cũ. Cả hai phải khai trước Gate D.
releasable: yes         # xong Unit này là ra được sản phẩm (có thể sau cờ tính năng)
release_note:           # cách đưa ra nếu cần cờ/route riêng
released_with:          # BẮT BUỘC khi releasable: no — ra chung với UOW nào. Không khai được = pseudo-unit
session_fit:            # "3 màn + 2 endpoint, đọc 4 nguồn (S12,S13), vùng code quen" — phải có CON SỐ
depends_on: []
sources: [S1, S2]
stories: 0
nfrs: 0
risks: 0
# Tầng review (§4.17) — BẮT BUỘC khai trước Gate D, kèm căn cứ trigger trong unit-plan.
# none = không dính trigger nào (mặc định) · peer = có contract FE↔BE / vùng code lạ / unit đầu chạm
# bounded context · specialist(security|tech-lead|qa) = trigger cứng (auth/PII · migration/public API/ADR
# trái pattern · NFR có ngưỡng đo). Người duyệt cả bảng tầng một lần ở Gate D.
review: none            # none | peer | specialist(<vai>)
# Một trong ba dòng dưới BẮT BUỘC có trước khi được `done` (protocol §4.12), ĐÚNG theo tầng đã khai.
reviewed_by:            # <agent> — kèm rv: RV-NNN có thật, `re:` khớp unit này (tier peer/specialist)
rv:                     # RV-NNN
self_verify:            # đường dẫn evidence/self-verify.md (CHỈ tier none — file thật, đủ mục, có con trỏ)
review_waived_by:       # DEC-NNNN — ngoại lệ ngoài bảng tầng, phải nói vì sao trong DEC đó
tests:                  # [đường dẫn file test phủ unit này] — hoặc đặt tên *.uowNN.test.*
---
# Unit — <tên>

## Mô tả (observable outcome)
<Xong rồi thì ai nhìn thấy cái gì khác đi. Không mô tả kỹ thuật ở đây.>

## Acceptance Criteria (đo được, trace về intent)
- [ ] AC1 — … *(trace: outcome O1)*
- [ ] AC2 — …

## Ước lượng — breakdown bắt buộc, không còn trần giờ (protocol §4.9 v5)
| Hạng mục | Giờ | Căn cứ (con số thật: mấy endpoint/màn/bảng) |
|---|---|---|
| domain + logical design | | |
| code BE | | |
| code FE | | |
| test | | |
| soát theo tầng + fix | | |
| **Tổng** | | |

Kích thước chặn bằng hai câu hỏi (§4.9): *tự ra được sản phẩm không* (`releasable`) và *một phiên có ôm
nổi không* (`session_fit` có con số) — không chặn theo đồng hồ. Tách thì mỗi mảnh vẫn phải là capability
quan sát được, không phải "Update DB".

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
