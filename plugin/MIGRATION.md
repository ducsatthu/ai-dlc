# MIGRATION — ai-dlc

## 4.x → 5.0.0 — trần 5h/Unit đã bỏ

**Đổi luật gate**: Gate D không còn chặn theo `estimate_hours`. Thay bằng hai điều kiện khai trong
`spec.md` (protocol §4.9 v5):

| | Trường mới | Chặn khi |
|---|---|---|
| Ra được sản phẩm một mình | `releasable: yes\|no` (+ `released_with:` khi `no`) | thiếu, hoặc `no` mà không nói ra chung với ai |
| Một phiên ôm nổi | `session_fit:` — **phải có con số** | thiếu, hoặc viết chung chung không con số |

`estimate_hours` **giữ nguyên** (đường găng, retro) nhưng không còn ngưỡng. Dự án muốn trần riêng thì đặt
`unit_max_hours` trong `.ai-dlc/governance/sizing.md` (template mới, mặc định `null`) — vượt chỉ WARN.

**Không phải làm gì với intent đã qua Gate D.** Tower/doctor/brief nhận diện kế hoạch cũ và **không** đòi
khai lại `releasable`/`session_fit` — dựng bù hồ sơ là thứ gói này cấm. Áp từ intent kế.

**Việc phải làm**: (1) intent đang ở stage ≤5 thì bổ sung hai trường cho mọi Unit trước khi trình Gate D;
(2) nếu muốn giữ trần cũ, tạo `governance/sizing.md` với `unit_max_hours: 5.0` + một DEC nói vì sao.

**KPI mới để đối chiếu**: `units.releasable` (khai lúc lập kế hoạch) và `units.oneSession` (đo sau bằng số
HOF trên mỗi Unit — lời khai lúc lập kế hoạch luôn lạc quan).

**Rollback**: hạ về 4.x thì hai trường mới bị bỏ qua và trần 5h sống lại; Unit >5h đã lập dưới 5.0.0 sẽ
hiện là vấn đề. Không có bước phá hủy.

## 3.x → 4.0.0 (review phải có địa chỉ · escalations/ · units/_trash/)

Nguồn: retro INT-001 của dự án PCT — `LL-001` + `LL-002` (Gate G · DEC-0027), thêm `LL-003` (chưa qua Gate G,
xem ghi chú cuối mục). Đây là **major** vì đổi điều kiện `done` của Unit và thêm hai thư mục vào layout.

### Có gì hỏng nếu bạn không làm gì?
**Không.** Intent đang chạy vẫn chạy: `escalations/` thiếu thì tower không hiện panel đó; unit không có `rv:`
thì tower hiện `units.reviewed = 0/N` **kèm cảnh báo** thay vì chặn. Không lệnh nào từ chối làm việc.
Cái đổi là: từ nay dashboard **nói ra** những gì trước đây im lặng.

### Việc nên làm, theo thứ tự rẻ → đắt
1. `mkdir -p .ai-dlc/context-memory/escalations` — chỗ cho phát hiện ngoài phạm vi unit (§4.13).
2. Chạy `/dlc-doctor`. Đọc hai dòng mới: unit `done` **không có** `rv:`/`review_waived_by:`, và unit `done`
   **không có** `bolts/`/`tasks.md`/`evidence/`. Đây là ảnh chụp nợ hiện tại, không phải lỗi mới sinh ra.
3. Với các unit đã đóng **không có review**: đừng đi tạo RV ngược. Ghi **một** `DEC` nói rõ "đợt này chạy
   không có reviewer độc lập cho N unit, vì <lý do>" rồi điền `review_waived_by: DEC-NNNN`. Một dòng sự
   thật đáng giá hơn N file RV dựng lại.
4. Unit lỗi thời (bị viết đè khi replan, hoặc trượt review mà không viết lại) → `units/_trash/UOW-NN/` +
   `status: obsolete` + `TOMBSTONE.md` (`templates/tombstone.md`). **Không xoá.** Mọi thống kê bỏ qua `_*`.
5. Áp DoD v3: `templates/dod.md` — dự án đang chạy nên áp qua `.ai-dlc/overrides/governance/dod.md`
   (`mode: patch`, `source: LL-002`) để giữ nguyên bản pinned của intent đang mở.

### Điều KHÔNG nên làm
**Đừng dựng bù hồ sơ.** Thiếu `bolts/*/design`, thiếu `evidence/` thì ghi khoảng trống vào LL. Design viết
sau khi code xong là mô tả code đội lốt quyết định thiết kế: người đọc sau tưởng những lựa chọn đó đã được
cân nhắc trước và được duyệt. Hồ sơ trống trung thực hơn hồ sơ dựng lại.

### Ghi chú provenance
`LL-001`/`LL-002` đã qua **Gate G (DEC-0027)** — đủ điều kiện sửa gói theo quy ước repo. `LL-003` (kiểm sự
tồn tại của artifact) **chưa qua Gate G**: INT-001 đã đóng nên nó chờ Gate G của intent kế. Phần đã áp từ
LL-003 trong 4.0.0 chỉ là **chẩn đoán** (doctor + KPI cảnh báo), không phải luật chặn gate — cố ý, để không
vượt mặt người duyệt.

## 2.2.x → 3.0.0 (open questions tách hai file)

Đổi **layout** (`open-questions.md` → `open-questions-business.md` + `open-questions-tech.md`) và **gate_doc
của C**. Fail-safe: file gộp cũ vẫn đọc được, tower hiện "bản gộp cũ" — **không có gì hỏng nếu bạn chưa làm gì**.

### Intent đã qua Gate C (khuyến nghị: để nguyên)
Không phải tách ngược. Câu hỏi cũ vẫn hiển thị, gate C đã đóng. Chỉ tách khi có vòng chỉnh sửa chạm chính
những câu đó — lúc đó tách luôn theo §4.10.

### Intent đang ở Gate C hoặc chưa tới stage 4
1. Spawn `ai-dlc:dlc-context-validator` với yêu cầu "tách `open-questions.md` theo protocol §4.10".
   Validator đọc file cũ, chia từng câu theo **người trả lời**, viết lại câu business bằng lời.
2. Đổi `status.md`: `gate_doc: open-questions-business.md`.
3. Câu kỹ thuật `CHẶN UOW-NN` còn treo → báo tech lead ngay; đó là thứ sẽ chặn Gate D.
4. `python3 <plugin>/scripts/tower_generate.py <root>` rồi mở lại tower.
5. Giữ file cũ hay xoá đều được — có bản tách thì generator bỏ qua bản gộp. Giữ lại thì truy vết dễ hơn.

### Dấu hiệu tách sai
- Câu business vẫn có `path/file.ts`, tên bảng, tên hàm → chưa dịch ra lời, `/dlc-doctor` sẽ báo FIX.
- Người trả lời ghi kiểu `BA/Tech Lead/Test Lead` → chưa biết hỏi ai; phải là **một** vai + tên người.
- Câu kỹ thuật mà quyết định cuối thuộc về kinh doanh → phải có **cặp** `OQT-NN` ↔ `OQB-NN`, không đẩy nguyên
  câu kỹ thuật ra Gate C.

### Rollback
Hạ về 2.2.x: gộp thủ công hai file thành `open-questions.md`, đổi `gate_doc` về file gộp. Không mất dữ liệu.

## 2.1.x → 2.2.0 (cộng thêm — chỉ cần khởi động lại server tower)

Chỉ thêm: `GET /state`, poll 5s ở UI, `heartbeat`/`progress` trong HOF, panel hoạt động.

- **Server tower đang chạy phải khởi động lại** để có `/state` (`/dlc-tower serve`). Token giữ nguyên trong
  `.ai-dlc/.tower-token` nên URL cũ vẫn dùng được. Không restart thì UI lặng lẽ chạy chế độ `TĨNH`.
- HOF cũ không có `heartbeat`/`progress` vẫn đọc được (hiện "chưa báo tiến độ"). Từ nay agent nhận việc phải
  đặt `accepted` + báo nhịp — xem protocol §9.4.
- Không cần regenerate tay nữa: server tự sinh lại khi `.ai-dlc/` đổi.

## 2.0.x → 2.1.0 (cộng thêm, không cần làm gì)

2.1.0 chỉ **thêm**: thư mục `context-memory/handoffs/` + `context-memory/session/`, lệnh `/dlc-resume`,
script `session_brief.py`. Không đổi gate, không đổi format file cũ.

- Dự án đang chạy: lần đầu chạy `/dlc-resume` (hoặc `/dlc-status`) sẽ tự tạo `session/board.md` và
  `session/INDEX.md`. Chưa có HOF nào thì board rỗng — bình thường.
- Từ 2.1.0, **mọi lần spawn agent phải có một file HOF** (protocol §9). Việc đang chạy dở bằng cách cũ
  (bối cảnh trong prompt) không phải viết bù HOF ngược — nhưng lần giao việc tiếp theo thì viết.
- `session/board.md` sinh ra từ `handoffs/`: đừng sửa tay, sửa file HOF rồi chạy lại
  `python3 <plugin>/scripts/session_brief.py <root> --board-only`.
- Thêm một dòng vào `session/INDEX.md` mỗi khi phải đi lục một thứ khó tìm — đó là cách phiên sau rẻ hơn.

---

# 1.x → 2.0.0

2.0.0 đổi **luật gate A**, **layout `.ai-dlc/`** và **format quyết định từ tower**. Dự án đang chạy 1.x không
tự hỏng (mọi thứ fail-safe), nhưng cần vài bước để dùng được phần mới.

## 1. Chuyện gì đổi

| Chủ đề | 1.x | 2.0.0 |
|---|---|---|
| Stage 1 | `intent.md` | `intent.md` + **`intent-plan.md`** (Intent + Source Reading Plan + Provisional Units) |
| Gate A duyệt | intent (thường qua brief) | **toàn văn `intent-plan.md`** trên tower |
| Stage 2 | AS-IS model | AS-IS model + **`as-is/source-ledger.md`** (mọi nguồn có trạng thái cuối + evidence) |
| Stage 5 | `units/UOW-NN/` | thêm **`unit-plan.md`** hợp nhất (gate_doc của D) |
| Unit | "khả thi trong giờ→ngày" | **≤5.0h/Unit** có breakdown; bắt buộc đủ US + NFR + Rủi ro |
| Verdict | approve / reject | approve / **request-changes** / reject; approve cần `previewed: true` |
| `status.md` | — | thêm `gate_doc`, `plan_version` |

## 2. Intent đang chạy dở (khuyến nghị: để nguyên)

Intent đã qua Gate A/B/C/D bằng 1.x **không phải làm lại**. Pinned snapshot của nó vẫn thắng (protocol §4.2),
nên checklist v1 và DoR/DoD v1 tiếp tục áp cho intent đó tới khi đóng. Cụ thể:

- Tower vẫn hiển thị được intent 1.x. Gate đang mở mà `status.md` chưa có `gate_doc` → generator suy ra mặc
  định (`A→intent-plan.md`, `B→as-is/source-ledger.md`, `C→open-questions-business.md` — không có thì lùi về
  `open-questions.md`, `D→unit-plan.md`); file không
  tồn tại thì màn duyệt báo "không tìm thấy tài liệu gate" và **không cho approve**.
- Muốn duyệt tiếp bằng UI mới: sinh tài liệu gate tương ứng (mục 3), hoặc quyết định trong terminal như cũ.

## 3. Nâng một intent đang mở lên 2.0.0

```
/dlc-doctor                     # xem thiếu gì
```
rồi theo thứ tự:

1. **Thêm `gate_doc` + `plan_version`** vào `status.md` của intent.
2. Chưa có `intent-plan.md`: chạy lại phần lập kế hoạch — spawn `dlc-source-planner` dựng Source Reading Plan
   từ intent hiện có, `dlc-intent-analyst` ghép phần 1 và 3. Không cần mở lại Gate A nếu scope không đổi;
   ghi một DEC "bổ sung tài liệu kế hoạch theo plugin 2.0.0".
3. Chưa có `source-ledger.md` mà đã qua stage 2: dựng ledger **hồi tố** từ những gì AS-IS đã trích dẫn, dòng
   nào không nhớ nguồn thì để `deferred` + ghi lý do — đừng đánh `read` cho có, vì đó chính là lỗi 2.0.0 muốn chặn.
4. Units hiện có: bổ sung `estimate_hours` + breakdown, và ba file `user-stories.md`/`nfr.md`/`risks.md`.
   Unit >5h — nếu **chưa vào Bolt** thì tách; nếu **đang chạy Bolt** thì giữ nguyên, ghi tech-debt "unit quá
   khổ" và tách ở intent sau (tách giữa chừng đắt hơn cái lợi).
5. `python3 <plugin>/scripts/tower_generate.py <project_root>` rồi mở lại tower.

## 4. Intent mới

Không phải làm gì — `/dlc-intent` đã theo 2.0.0. Governance mới (DoR v2/DoD v2, checklist v2) chỉ được pin vào
intent tạo **sau** khi nâng plugin.

Nếu project có `overrides/` cho `dor.md`/`dod.md`/checklist: kiểm lại bằng `/dlc-doctor` — nhiều override 1.x
đã được upstream vào bản v2, giữ lại là tự làm khó mình.

## 5. Nợ quy trình phải trả (bắt buộc)

Repo này quy định: sửa luật/checklist trong gói phải đi từ một LL đã qua Gate G của dự án thật. 2.0.0 sinh ra
từ phản hồi vận hành của chủ sở hữu chứ chưa qua retro chính thức, nên CHANGELOG ghi `LL-PENDING`.

**Dự án đầu tiên chạy 2.0.0** phải: mở LL trong retro (`/dlc-retro`) đánh giá ba luật mới (Intent Plan,
No-unread-source, Unit ≤5h) — thực tế có giảm lỗi "đọc thiếu nguồn" không, trần 5h có làm vỡ vụn Unit không —
rồi cập nhật link LL vào entry 2.0.0 của CHANGELOG.

## 6. Rollback

Không có bước phá hủy nào: 2.0.0 chỉ **thêm** file và field. Quay lại 1.x thì file mới bị bỏ qua, tower dựng
lại theo bản cũ. Riêng inbox JSON có `verdict: request-changes` sẽ không được server 1.x chấp nhận — drain hết
inbox trước khi hạ version.
