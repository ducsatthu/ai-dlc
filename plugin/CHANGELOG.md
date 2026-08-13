# Changelog — ai-dlc plugin

## 5.0.0 (2026-08-13) — Bỏ trần 5h/Unit: cắt theo đường ra sản phẩm, không theo đồng hồ

**Nguồn: quyết định của chủ gói, KHÔNG phải LL qua Gate G.** Ghi rõ để không tự lừa mình — đây là lần thứ
hai trong ngày một luật đổi mà chưa có retro chống lưng. Bù lại, ba căn cứ đều kiểm được:

1. **White paper (SSOT) không có trần 5h.** Nó nói chu kỳ tính bằng "**giờ hoặc ngày**" và bounded context
   "độc lập, **đúng kích thước**". Trần 5h là phát minh của gói ở v2 — **hẹp hơn** tài liệu gốc, tức là
   chính nó đang lệch SSOT.
2. **`MIGRATION.md` v2 đã tự đặt câu hỏi này**: *"trần 5h có làm vỡ vụn Unit không"* — treo từ đó tới nay.
3. **Ca thật**: `DEC-0052` của PCT tách một Unit thành 3.5h + 2.75h **chỉ để lọt trần**; hai mảnh phải ra
   chung mới có nghĩa. Trần đo sai thứ cần đo: nó bắt cắt theo *thời lượng* thay vì theo *đường ra sản phẩm*.

### Đổi luật gate (major)
- **protocol §4.9 viết lại**: Unit không còn ngưỡng giờ. Chặn Gate D theo **hai điều kiện**, cả hai là
  trường khai được và kiểm được:
  - `releasable: yes|no` (+ `released_with: UOW-NN` bắt buộc khi `no`) — *xong Unit này có ra được sản
    phẩm không*. Không khai được đường ra nào = pseudo-unit kỹ thuật, phải gộp hoặc cắt trục khác.
  - `session_fit:` **có con số** (mấy màn/endpoint/bảng · mấy nguồn phải đọc · vùng code quen hay lạ) —
    *một phiên có ôm nổi không*. Viết "vừa một phiên" không kèm số = chưa khai.
- `estimate_hours` **giữ** (đường găng + retro) nhưng không còn ngưỡng chặn; vẫn bắt buộc >0 và có breakdown.
- Trần giờ trở thành **núm của từng dự án**: `governance/sizing.md` → `unit_max_hours` (template mới, mặc
  định `null`). Có đặt thì vượt chỉ WARN — chặn gate vẫn là hai điều kiện trên.

### KPI mới (luật không kiểm được là luật sẽ trượt)
- `units.releasable` — bao nhiêu Unit khai đường ra hợp lệ (kiểm **lúc lập kế hoạch**).
- `units.oneSession` — bao nhiêu Unit đã đóng thật sự gọn trong **một chuỗi HOF** (kiểm **sau, bằng dấu
  vết**: cần ≥2 HOF hoặc có HOF `returned` nghĩa là thực tế to hơn `session_fit` đã khai). Không phải để
  phạt — là dữ liệu để intent sau cắt sát hơn. PCT/INT-001 khi đo lần đầu: **13/17**.

### Không dựng bù hồ sơ
Intent đã qua Gate D được lập dưới luật cũ → tower · `/dlc-doctor` · `session_brief` **không** đòi khai lại
`releasable`/`session_fit`, chỉ ghi một dòng WARN "kế hoạch cũ, áp §4.9 v5 từ intent kế". Kiểm trên PCT:
68 Unit của INT-001/002/003 **không** bị biến thành 68 lỗi giả.

### Kèm theo
`MIGRATION.md` mục 4.x→5.0.0 · template `sizing.md` + `unit-spec.md` (3 trường mới) · `/dlc-init` seed
`governance/sizing.md` · checklists `pm-po` v3 · `qa` v4 · `ba` v3 · agents `dlc-intent-analyst`,
`dlc-unit-planner`, `dlc-pm-po-reviewer`, `dlc-qa-reviewer`, `dlc-ba-reviewer`, `dlc-orchestrator` ·
`/dlc-doctor` mục 2 viết lại · KPI mới trên Mission Control + Dòng chảy.

## 4.1.0 (2026-08-13) — Nhịp sống phải kiểm chéo được · teammate vào giao thức

**Nguồn: quan sát hiện trường, KHÔNG phải LL đã qua Gate G.** Ca gốc là PCT · INT-003 · `HOF-0039` ngày
13/08, bắt được lúc agent đang chạy thật. Theo quy ước repo, luật chặn gate phải đi từ một LL qua Gate G —
nên bản này cố ý chia đôi: phần **đo nhịp** là siết một luật đã có (§9.4, đã có từ 1.0.0) nên kiểm ở mức
FIX; phần **teammate** (§9.5) là *hướng dẫn*, `/dlc-doctor` chỉ WARN, chờ Gate G ở retro INT-003 mới nâng
thành luật. Không ghi `LL-PENDING` cho phần này — nó phải trả bằng LL-004 hoặc bị gỡ.

**Ca gốc:** `HOF-0039` được agent ghi lúc 18:13, khai `heartbeat: 2026-08-13T00:00:00Z`, `progress` trễ ba
vòng so với việc nó đang làm. Tower hiện **"im lặng 1099 phút"** cho một agent đang chạy — và panel *Hoạt
động gần đây* (quét mtime) cùng lúc hiện file của chính nó vừa đổi **0 phút trước**. Hai con số cùng màn
hình chửi nhau mà không ai đối chiếu. Đây là §4.11 lặp lại ở tầng khác: **đọc lời khai như thể nó là dấu vết**.

### Siết luật đã có (§9.4 — nhịp là lời khai, mtime là dấu vết)
- `tower_generate` đối chiếu `heartbeat:` với **mtime của chính file HOF đó** và gắn bốn cờ:
  `placeholder` (đúng `T00:00:00`, mọi múi giờ) · `future` (> giờ máy + 5 phút) · `drift` (file ghi muộn hơn
  nhịp khai > 30 phút) · `unreadable` (không parse được ISO). Bị cờ thì **thôi hiện "im lặng N phút"** —
  mốc gốc đã sai thì con số dẫn xuất từ nó chỉ dẫn người giám sát đi sai hướng — thay bằng lý do + "file
  vừa đổi N phút trước".
- KPI mới `handoffHealth.trusted / handoffHealth.accepted` (trường để điền: `heartbeat:` · con số để đối
  chiếu: tỉ lệ này). PCT lúc phát hiện: **0/1**.
- `/dlc-doctor` mục **1e**: mỗi `suspect` → FIX; `accepted` mà `heartbeat: -` → FIX; in tỉ lệ ở bảng tổng.
- Template `handoff.md`: nói thẳng `heartbeat` phải là **giờ thật lúc ghi dòng đó** (`date -Iseconds`).

### Thêm (§9.5 — teammate/agent team, mức hướng dẫn)
- Bảng chọn **sub-agent vs teammate** theo tính chất việc, và **bốn ràng buộc không nới**: teammate không
  thay HOF (hộp thư của team bị xoá khi phiên kết thúc — cái gì chỉ nằm trong hộp thư coi như chưa xảy ra) ·
  đặt tên `<vai>-<mã việc>` + khai `teammate:` trong HOF · tin nhắn giữa agent **không** đóng được gate
  (chỉ RV/DEC mới đóng) · kết tinh trước khi tắt teammate.
- Trường frontmatter mới **`teammate:`** (không bắt buộc) — chỗ duy nhất nối pane đang chạy với dòng trên
  board. Tower hiện chip `⧉ <tên>` ở vị trí đó.
- `/dlc-doctor` mục **1f** (WARN): teammate sai quy ước tên · đang chạy teammate mà HOF không khai · MSG
  kiểu "đã duyệt" không có RV/DEC kèm theo (mục này FIX — nó thuộc §4.12 đã qua Gate G).

### Thêm (§9.5.5 — "đã gửi" ≠ "có người nhận")
- Ca thật cùng ngày: 5 lần spawn teammate hỏng vì tmux (`respawn pane failed: fork failed: Device not
  configured`) — nhưng `SendMessage` **vẫn báo thành công**, vì nó chỉ ghi file hộp thư. Hai review-request
  (`MSG-0033`, `MSG-0034`) và hai yêu cầu Review Board (`RV-019`, `RV-020`) nằm im trong hộp thư của
  `pmpo-INT003` · `pmpo2-INT003` · `qa-INT003` · `rv019` · `rv020` — những agent chưa bao giờ tồn tại.
  `reviews/` không có RV-019/RV-020. **`LL-002` lặp lại ở tầng team**, và lần này cái làm nó vô hình là
  một *thông báo thành công*.
- `tower_generate.scan_team()` đọc `~/.claude/teams/*/config.json` của **đúng dự án này** (khớp `cwd` của
  lead, chấp nhận lồng nhau vì lead hay ngồi ở gốc monorepo) → `data.team`: thành viên thật (ghép pane với
  dòng trên board) + **`deadLetters`**: hộp thư mang tên không có trong `members`. Panel đỏ trên Mission
  Control + cảnh báo stderr. `/dlc-doctor` mục **1g** (FIX, vì nó rơi vào §4.12 đã qua Gate G: unit có
  review-request chết thì **không** được tính là đã review).

### Thêm (§9.5.6 — vòng đời teammate = vòng đời HOF của nó)
- Luật: HOF `done`/`returned` → **tắt teammate ngay**; cần lại thì spawn phiên mới bằng HOF mới. Lý do
  không phải token (phiên rảnh không gọi API, không tốn gì) mà là **bối cảnh cũ**: một phiên sống qua vài
  gate vẫn nhớ `unit-plan` v3 trong khi đĩa đã v4 — nguồn sự thật thứ hai, đúng thứ §9.3 cấm với `board.md`.
  Kèm: gọi lại đắt hơn spawn mới (prompt spawn chỉ là một dòng trỏ HOF), và mỗi phiên giữ một pty — cạn
  pty chính là thứ vừa sinh ra 5 tin chết ở §9.5.5.
- **`/compact` cho teammate gần như luôn sai**: nó tốn token để tạo ra một bản tóm tắt kém hơn bản đã nằm
  trên đĩa (HOF · MSG · artifact). Chỉ dùng khi agent đang giữa chừng một HOF dài và sắp chạm trần context.
- Tower đối chiếu `members` (phiên đang sống) với `teammate:` trong HOF → ba trạng thái `working` /
  `zombie` (HOF đã đóng mà phiên còn sống) / `unknown` (không HOF nào khai tên nó), panel **"Agent team —
  phiên đang sống"** + cảnh báo stderr + `team.zombies`. `/dlc-doctor` 1f và `dlc-orchestrator` bước 5d
  nhắc tắt **bằng shutdown request, không giết pane** — teammate được phép từ chối vì đang dở, và giết
  pane là mất phần *Đã làm* / *Còn treo* chưa kịp ghi.

### Sửa
- **Nhịp có múi giờ làm sập generator**: `heartbeat: …+07:00` ở một HOF `accepted` gây
  `TypeError: can't subtract offset-naive and offset-aware datetimes` (chỉ bắt `ValueError`). Cùng họ với
  lỗi đã sửa ở `session_brief.py` bản trước — nay dùng chung `parse_iso_local()` quy về giờ máy.

## 4.0.0 (2026-08-12) — Luật kiểm được, và nợ LL-PENDING đã trả

**Nguồn (hết `LL-PENDING`):** retro thật đầu tiên — `LL-001` + `LL-002` của INT-001 dự án PCT, **đã qua
Gate G (DEC-0027)**; thêm `LL-003` (chưa qua Gate G — xem mục *provenance* dưới). Mọi thay đổi trong bản này
truy được về một trong ba file đó. Các mục 2.0.0–3.1.0 mang `LL-PENDING` nay coi như đã có nguồn: đây chính
là dự án đầu tiên chạy plugin qua trọn vòng đời tới Gate G.

**Phát hiện lớn nhất của retro:** DoD v1 — có từ ngày `/dlc-init`, seed từ chính gói này — đã ghi *"Quality
gate: reviewer BE/FE approve"*. Dự án vẫn đóng **17 unit code liên tiếp** với **13 review-request gửi đi và
0 verdict quay lại**, cả 18 unit mang `status: approved` do **chính agent làm unit tự đặt**. Không ai nói
dối. Luật không thiếu — **luật không kiểm được**: "reviewer approve" là một câu chữ, không có trường nào bắt
điền và không lệnh nào đối chiếu, nên nó trượt 17 lần mà không ai nhận ra.

### Luật mới (major — đổi điều kiện `done` và layout `.ai-dlc/`)
- **protocol §4.12 — review phải có địa chỉ**: Unit chỉ được `done` khi `spec.md` có `reviewed_by:` + `rv:`
  trỏ một `reviews/RV-NNN.md` **tồn tại thật**, hoặc `review_waived_by: DEC-NNNN`. Gửi review-request rồi
  đóng HOF trong cùng lượt là vi phạm — "đã gửi, chờ verdict" là *đang chờ*, không phải *xong*.
- **protocol §4.13 + `escalations/ESC-NNN.md`** (layout mới): phát hiện ngoài phạm vi Unit phải thành **việc
  có hàng đợi**, không thành ghi chú trong HOF. *(Cùng một lỗi id-space được 4 HOF ghi nhận rồi vẫn tới tay
  người dùng dưới dạng link 404 — HOF đóng lại là phát hiện chìm theo.)*
- **protocol §4.14 + `units/_trash/UOW-NN/` + `TOMBSTONE.md`** (layout mới): unit lỗi thời chuyển vào đây,
  hạ `status: obsolete`, **không xoá** — retro sống bằng chính đống dấu vết đó. Mọi thống kê bỏ qua `_*`.
  *(4 unit chưa bao giờ được xây vẫn đeo `approved` suốt cả intent.)*
- **protocol §4.15 — phép đo phải tự chứng minh**: chạy một ca đối chứng đã biết chắc kết quả ngược lại
  trước khi tin; test bảo vệ phải mutation-test. *(4 lần đo hỏng cho kết quả NGƯỢC, 3 lần suýt báo ra ngoài.)*
- **protocol §4.16 — thu hẹp union ⇒ grep mọi so sánh bằng**. *(Xoá một persona làm điều kiện thi hành một
  business rule ở file khác vĩnh viễn sai; TypeScript im, test im.)*
- **protocol §4.10.9–11 — không hỏi trước khi đọc**: mỗi câu trong `open-questions-*.md` bắt buộc có dòng
  *"đã soát X, Y, Z — không thấy đáp án"*; câu về màn `SCR-*` phải trích spec màn đó; câu về **hiện trạng**
  phải grep code trước; cấm bịa nhãn. *(8 lần hỏi thứ đã có sẵn đáp án; lần tệ nhất người trả lời phải đi
  sửa lại câu hỏi trước khi trả lời được.)*
- **DoD template v3** (9 mục mới, mỗi mục ghi rõ nó chữa ca nào) · **unit-spec** thêm `reviewed_by`/`rv`/
  `review_waived_by`/`tests` · **unit-plan** thêm bảng *Đường nối với unit khác* (AC ghi "X thuộc unit khác"
  thì bắt buộc có AC nói ai nối X vào Y) · checklist **frontend v2** (không nút chết, bấm thử), **backend v2**
  (grep enum, luật trỏ được về nguồn), **qa v3** (ca đối chứng, mutation test, chặn `done` thiếu review).

### Control Tower — đo được những gì luật vừa đòi
- **KPI `units.reviewed`** — "unit đã xong CÓ người thứ hai ký". Trên PCT: **0/17**, kèm cảnh báo *"con số
  unit đã xong ở trên là TỰ KHAI"*. Đây là LL-002 §1 tự hiện ra trên dashboard thay vì phải đọc retro.
- **KPI `units.artifacts`** — unit đã đóng có đủ `bolts/` · `tasks.md` · `evidence/`. Trên PCT: **0/17**
  (14 unit không có thư mục bolt nào, 0 unit có `evidence/`) — đúng con số LL-003 đo tay.
- **Panel "Phát hiện ngoài phạm vi — chờ người nhận"** đọc `escalations/`; mục `open` không có `owner` được
  tô hổ phách: đó chính là mục sẽ chìm nếu chỉ nằm trong HOF.
- **`units/_trash/` không còn bị đếm là Unit** (trước 4.0.0 nó hiện thành một unit tên `_trash`, làm sai mọi
  thống kê của intent); sidebar hiện "+N unit lỗi thời" riêng.
- **Bolt đọc từ chính Unit, và hiện đủ bốn chặng** (`unit.boltDetails`): mỗi bolt hiện chuỗi
  `Domain Design → Logical Design + ADR → Contract → Task board → Evidence` với trạng thái **có/không đọc
  thẳng từ đĩa**, bấm vào chặng có thật là mở tài liệu. Unit không có bolt thì nói thẳng "các chặng đó
  không xảy ra", không mượn số của unit khác. Trên PCT: UOW-06/11/13 **4/6 chặng**, UOW-16 **1/6**,
  14 unit **0 bolt** — đúng con số LL-003 đo tay.
  *(Bug đã sửa cùng lúc, do người dùng bắt được: bảng task tra theo mã unit trần nên INT-001/UOW-01 hiện
  task của INT-002/UOW-01 — hai intent có thể cùng có `UOW-01`. Nay bolt/task nằm trong chính object unit,
  không có khoá toàn cục để đụng nhau.)*
- **Điểm dừng trong Bolt được vẽ ra** (protocol §1.0c): năm điểm dừng — review thiết kế · freeze contract ·
  Gate E(a) · review code · Gate E(b) — cộng escalation và câu hỏi `CHẶN UOW-NN`, mỗi điểm ghi rõ **ai giữ**
  (agent hay NGƯỜI) và ở một trong năm trạng thái: *chưa tới · đang chờ agent · **đang chờ NGƯỜI** · bị trả
  lại · **đã đi qua mà không dừng***. Trạng thái suy từ `reviews/` · `comms/` · `escalations/` · `gate_open`,
  **không** từ trạng thái tự khai. Bolt board vẽ xen kẽ chặng → điểm dừng trên cùng một mạch; Dòng chảy hiện
  dãy chấm điểm dừng cho từng Unit và nói *"đang chờ NGƯỜI"* khi việc đứng ở người.
  Trên PCT: mỗi unit **4 điểm dừng bị đi qua** — đây là LL-002 §1 hiện thành hình, không phải thành chữ.
- **Brownfield có chặng riêng ở đầu Inception**: `as-is/static-model.md` + `as-is/dynamic-model.md` hiện
  trong Dòng chảy **chỉ khi** intent khai `brownfield_type` — greenfield không hiện (bịa việc cũng là nói dối).
- Dòng chảy nói rõ *"N bolt / M unit · X unit CHƯA có bolt nào"* thay vì chỉ đếm bolt.
- Bỏ nốt hai panel mock còn sót trong Bolt board (*API contract "GET/POST/PATCH /api/releases"*,
  *checkpoint "Demo SCR-REL-10/11"*) — thay bằng dữ liệu thật của unit + nguồn file.
- `lessons` đọc được LL viết tay (tiêu đề H1 khi không có dòng `Lesson:`, frontmatter tiếng Việt).

### Sửa (ba lỗi người dùng bắt được khi soi dự án thật)
- **Không còn đẻ ra `.ai-dlc/` rác.** `tower_generate` / `tower_serve` trước đây nhận **bừa `cwd`** làm gốc
  dự án và tạo `.ai-dlc/tower/` ở bất cứ đâu — chạy nhầm từ `app-fe/` hay từ trong `.ai-dlc/context-memory/`
  là sinh ra một thư mục `.ai-dlc` rỗng trông y như dự án thật (PCT có đúng hai cái như vậy). Nay:
  đường dẫn nằm trong một cây `.ai-dlc` thì **nhảy ngược ra gốc**; không thấy `.ai-dlc/context-memory/` thì
  **đi lên cha tìm**; tìm không ra thì **dừng và không tạo gì**, kèm câu hướng dẫn. `/dlc-doctor` có thêm
  bước quét `.ai-dlc` rác trong repo.
- **Chú thích cuối dòng trong frontmatter không còn bị nuốt thành giá trị.** `gate_open: null  # A đã đóng
  bằng DEC-0031` bị đọc thành *"có gate tên `null # A đã đóng bằng DEC-0031` đang mở"* → một **gate ma**
  trong hàng đợi, và cái nhãn dài 336px của nó **đẩy vỡ sidebar** khiến cây Intent không đọc được.
  Nay `fm()` cắt ` # …` trên giá trị không nằm trong nháy (cả `tower_generate` lẫn `session_brief`), và
  `gate_open` được chuẩn hoá về `A`–`G`/`escalation`/rỗng — giá trị lạ bị bỏ qua kèm cảnh báo ra stderr.
- **Sidebar không thể vỡ vì dữ liệu nữa**: `overflowX: hidden`, nhãn gate cắt cứng ở 12 ký tự / 54px.
  Nhãn điều hướng không được phép co giãn theo nội dung file.
- **`session_brief` hết sập và hết nói số rác**: (1) `closed:` có múi giờ (`…+07:00`) làm cả bản brief
  `TypeError` — nay bỏ tzinfo trước khi trừ; (2) đếm nguồn theo **vị trí cột** cho ra `0/0` và `79/0` trên
  dự án thật — nay đếm theo từ khoá trong dòng, gộp mọi bảng của cùng một mã, và **ưu tiên đúng con số
  Control Tower đang hiện** (`tower/data.js`) để hai màn hình không nói hai số khác nhau về cùng một thứ.

### Control Tower — thiết kế mới (Control Tower Design System, variant C)
- **Sidebar là cây Intent → Unit → Bolt**: nhánh đang chọn mở sẵn, chấm màu theo trạng thái unit, nhãn
  gate ở intent đang chờ người, "+N unit ngoài phạm vi / lỗi thời" đếm riêng. Vị trí trong cây trả lời
  "tôi đang ở đâu" mà không cần đọc breadcrumb.
- **Dải pha** trên Mission Control: Inception · Construction · Operations kèm số intent mỗi pha.
- **Nhớ chỗ đang đứng qua `localStorage`** (khoá theo tên project): theme sáng/tối, màn đang xem, intent và
  unit đang chọn, nhánh cây đang mở. F5 không còn ném bạn về màn mặc định; theme áp **trước** lần vẽ đầu
  tiên nên không nháy một nhịp màu sai.

### Provenance
`LL-001`/`LL-002`: **Gate G · DEC-0027** — đủ điều kiện sửa gói theo quy ước repo. `LL-003`: **chưa qua Gate
G** (INT-001 đã đóng, không mở lại gate đã duyệt) — phần áp từ nó trong bản này chỉ là **chẩn đoán** (doctor
+ KPI cảnh báo), không phải luật chặn gate. Nâng lên thành luật khi Gate G của intent kế duyệt.
Xem `MIGRATION.md` §3.x → 4.0.0.

## 3.1.0 (2026-08-12) — Mọi con số trên Control Tower đều truy được

**Vì sao (nguồn):** người dùng đọc dashboard PCT và không thể xác nhận số nào cả — *"Xem trong dòng chảy thì
có 13 mâu thuẫn nhưng tôi không tìm được ở đâu"*. Điều tra: generator đọc sổ cái **theo số thứ tự mục**
(§2 = bảng nguồn, §3 = mâu thuẫn). Sổ cái của PCT dùng §3 cho *"Nguồn code — hiện trạng FE/BE"*, nên 13 dòng
nguồn code bị đếm thành **13 mâu thuẫn**. Cùng nguyên nhân: cột `Trạng thái` bị lấy sai vị trí nên
27 nguồn đã đọc hiện thành **0/11**. `LL-PENDING` (chung với 2.0.0).

### Sửa (số liệu sai trên dashboard)
- **Sổ cái đọc theo tên, không theo vị trí**: nhận bảng bằng tên cột (`#` · `Nguồn` · `Trạng thái`), gộp
  MỌI bảng nguồn trong file (trước chỉ lấy một mục). Trên PCT: `0/11` → **27/28**.
- **Mâu thuẫn nhận bằng tên mục** ("Mâu thuẫn…"/"conflict") + dấu `[CONFLICT]` rải trong file, bỏ mục
  Changelog và câu phủ định ("không có `[CONFLICT]`"). Trên PCT: `13` → **0** (đúng: sổ cái không có mâu thuẫn nào).
- **Trạng thái viết tay được chuẩn hoá**: `✅ đã đọc` · `⬜ chưa` · `read` · `missing` · `deferred` ·
  `superseded`. Ô không hiểu được → `unknown` + cảnh báo, **không** âm thầm tính là 0. Có cả đường lùi khi
  hàng bị lệch cột do dấu `|` nằm trong inline code.
- **Descoped chỉ do `DESCOPED.md` quyết định.** Trước đây suy "không có trong `unit-plan.md` ⇒ ngoài phạm vi",
  khiến 5 unit sinh sau Gate D (UOW-15/19/20/21/22 của PCT, đã giao xong) bị loại khỏi mọi thống kê.
  18 unit / 67h thay cho "22 unit · 55h" — trước đó **đếm một tập, cộng giờ một tập khác**.
- **Bolt board**: bỏ nhãn cứng "UOW-01 · Bolt 1 — Release Planning" (di sản bản mock). Hiện đúng unit/bolt của
  file đang đọc, và cảnh báo khi task đang hiện thuộc unit đã ra ngoài phạm vi.
- **Trạng thái Unit chuẩn hoá từ vựng.** Trước đây chỉ đúng chữ `done` mới tính là xong, nên 21/22 unit của
  PCT ghi `status: approved` (đã duyệt = đã xong) hiện thành "chưa xong" trong khi intent đã ở Operations —
  người xem thấy mâu thuẫn mà không có cách nào tra. Nay `done` · `approved` · `accepted` · `completed` ·
  `closed` · `xong` · `đã nghiệm thu` đều là xong. Trên PCT: `1` → **18 unit đã xong**, khớp DEC-0014.
- Câu hỏi đã chốt: bảng điều phối chỉ có cột *"Chốt là gì"* (không có cột *Trạng thái*) nay được hiểu là
  **đã đóng** — trước đó 18 câu đã trả lời vẫn hiện là đang chờ.

### Thêm
- **`metricsByIntent`** — mỗi con số mang theo: *đếm cái gì* · *đọc từ file/mục nào* · *đúng những dòng đã đếm*
  · cảnh báo. Bấm vào bất kỳ KPI nào trên **Mission Control** hoặc **Dòng chảy 3 pha** → ngăn kéo
  *"Số này ở đâu ra?"*, mở được thẳng file gốc.
- KPI có ⚠ khi chính con số đó không đáng tin, ví dụ *"13 unit không khai `status` — đang tính là chưa xong"*
  hay *"không unit nào trong phạm vi có `tasks.md` — 0 task là do chưa lập file, không phải chưa làm việc"*.
- Mission Control nói rõ KPI là **tổng của N intent**, và bảng truy vết có thêm cột Intent.
- **protocol §4.11** — luật số liệu: số phải truy được · đọc bằng tên không bằng vị trí · không hiểu thì nói
  không hiểu · cùng một tập cho cùng phép đếm · phân biệt "đếm được = 0" với "không có gì để đếm".
- **Đối chiếu pha ↔ unit** (`phase.consistency`): pha hiển thị đến từ `stage:` trong `status.md` — một con số
  do orchestrator ghi — còn trạng thái unit đến từ N file `spec.md`, không có gì ràng buộc hai thứ. Từ nay
  `stage` ≥6 mà còn unit chưa đóng thì tower nói thẳng "stage 7 nhưng 5/18 unit chưa đóng hồ sơ", kèm danh
  sách unit và chữ thật trong từng `spec.md`.
- Từ vựng `status:` của unit ghi vào `templates/unit-spec.md` và protocol §4.11 điểm 7–8.
- `/dlc-doctor` mục 1c: soi `warnings` của metric, bắt ô trạng thái không đọc được và unit thêm sau unit-plan.

## 3.0.0 (2026-08-12) — Open questions tách theo NGƯỜI TRẢ LỜI

**Vì sao (nguồn):** vận hành thật trên PCT — `open-questions.md` gộp mọi câu vào một file có phân nhóm phạm vi
tốt, nhưng người nghiệp vụ đọc không trả lời được. Ví dụ `OQ-05` hỏi "BA/Tech Lead/Test Lead là vai gì?" kèm
`PctRole`, `QgParticipantRole`, `user.ts:5`: đúng về kỹ thuật, nhưng (a) người nhận là một chuỗi vai chung
chung nên **không ai thấy mình phải trả lời**, (b) muốn hiểu câu hỏi phải biết code. Câu hỏi nằm chết, Unit
treo theo. `LL-PENDING` (chung với 2.0.0).

### Đổi (BREAKING — layout + luật gate, xem MIGRATION.md)
- **Một file → hai file** (protocol §4.10): `open-questions-business.md` (gate_doc của **C**) và
  `open-questions-tech.md` (không ra Gate C; câu `CHẶN UOW-NN` là **điều kiện chặn Gate D**).
  Trục tách là **người trả lời**, không phải chủ đề.
- **Luật hai phút** cho file business: mỗi câu trả lời được trong ~2 phút, không mở file khác, không cần biết
  code. **Cấm** đường dẫn file · tên bảng/cột · tên lớp/hàm/kiểu · route trong file business — sự thật kỹ thuật
  phải dịch ra lời.
- **Cặp mã** khi quyết định chạm cả hai phía: `OQT-NN` giữ chi tiết + bằng chứng, `OQB-NN` là bản hỏi bằng lời,
  nối hai chiều bằng dòng *Soi chiếu*. Đây là lời giải trực tiếp cho ca `OQ-05`.
- **Mỗi câu là một quyết định**, bắt buộc: mã · nhóm · **người cụ thể** (vai + tên — chuỗi "BA/TL/Test Lead"
  bị coi là chưa biết hỏi ai) · hạn · ảnh hưởng · **phương án chọn sẵn kèm cái giá** · đề xuất của AI ·
  **phương án mặc định nếu im lặng**. Câu mở kiểu "X là gì?" bị cấm.
- Nhóm chuẩn: business **B1** phạm vi & ưu tiên · **B2** quy tắc nghiệp vụ · **B3** vai trò & quyền ·
  **B4** dữ liệu & nguồn sự thật · **B5** quy trình & vận hành · **B6** tuân thủ & rủi ro kinh doanh;
  tech **T1** kiến trúc · **T2** mô hình dữ liệu & migration · **T3** tích hợp & hợp đồng API ·
  **T4** phi chức năng · **T5** kiểm thử & môi trường · **T6** nợ kỹ thuật.

### Thêm
- Template `open-questions-business.md` + `open-questions-tech.md` (bảng điều phối mục 0 + thẻ câu hỏi).
- `dlc-context-validator` viết lại stage 4: phân loại theo người trả lời → tự kiểm luật hai phút → cặp mã.
- Generator: đọc bảng điều phối **theo tên cột** (không theo vị trí), gắn `audience`/`group`/`blocking`;
  Gate D nhận blocker từ câu tech `CHẶN` còn treo; dòng chảy Inception có hai chặng OQ riêng.
  Intent cũ còn `open-questions.md` vẫn đọc được, hiện "bản gộp cũ".
- Tower · tab Open Questions: hai khối riêng, cột *Ai trả lời* / *Nếu im lặng* thiếu thì tô đỏ.
- `/dlc-doctor` mục 1b: bắt câu business lẫn thuật ngữ code, câu không có người trả lời cụ thể, câu thiếu
  phương án mặc định, câu tech `CHẶN` còn treo ở stage ≥5, cặp *soi chiếu* đứt.

### Sửa
- Tower: link mở tài liệu ở đầu Intent Detail trỏ sai gốc (`INT-NNN/…` thay vì `context-memory/intents/…`)
  nên `/doc` trả 404 khi tài liệu không nằm sẵn trong `data.js`.

## 2.2.0 (2026-08-12) — Control Tower nhìn thấy agent đang chạy

**Vì sao (nguồn):** vận hành thật trên PCT — 4 `dlc-fe-dev` chạy song song mà tower không thể hiện gì.
Hai nguyên nhân: (1) tower là ảnh chụp, `data.js` nạp một lần lúc mở trang nên mọi thứ agent làm sau đó
không xuất hiện; (2) agent được giao HOF nhưng không tự đặt `accepted` và không báo tiến độ, nên board ghi
"chờ nhận" trong khi việc đã chạy 30 phút. `LL-PENDING` (chung với 2.0.0).

### Thêm
- **Tower tự cập nhật**: `tower_serve.py` thêm `GET /state` — trả phần state hay đổi (stations · handoffs ·
  activity · tasks · feed · gate keys) và **tự chạy `tower_generate.py` khi `.ai-dlc/` mới hơn `data.js`**
  (throttle 3s). Không ai phải nhớ chạy `/dlc-tower` sau mỗi thay đổi nữa.
- **UI poll 5 giây** + huy hiệu `LIVE · <giờ cập nhật>`; mở dạng `file://` thì tự lùi về `TĨNH — không tự
  cập nhật` (không báo lỗi). Hàng đợi gate đổi → banner "tải lại trang" (gate doc không nằm trong `/state`).
- **Nhịp sống của vị trí (protocol §9.4)**: HOF thêm `heartbeat` + `progress`. Agent nhận việc phải đặt
  `status: accepted` + `accepted:` **trước khi đọc `read_first`**, rồi cập nhật `heartbeat`/`progress` ở
  mỗi mốc. Board/tower hiện "nhịp 2 phút trước" hoặc "im lặng 25 phút" (>15 phút = đánh dấu).
- **Panel "Hoạt động gần đây — file thật vừa đổi"**: quét mtime trong `.ai-dlc/` + code roots (theo
  workspace-map, bỏ qua `node_modules`/`.git`/`dist`/…, trần 40k file, cửa sổ 2 giờ). Đây là lưới an toàn:
  agent quên cập nhật HOF thì file nó vừa ghi vẫn tố cáo là nó đang chạy. Đo trên PCT: 87ms/lần sinh.
- **Cảnh báo vị trí không khai báo**: HOF `open` mà vùng của nó vừa có file đổi → tower nói thẳng "nhiều khả
  năng agent đang chạy nhưng chưa đặt `status: accepted`".
- `session_brief.py` (`/dlc-resume`, `/dlc-status`): hiện `progress` + nhịp; cảnh báo HOF `accepted` chưa
  báo nhịp lần nào, im lặng quá lâu, hoặc `open` mà có thể đang chạy.

### Đổi
- `dlc-fe-dev` · `dlc-be-dev`: thêm mục "Nhận việc" đứng đầu định nghĩa agent (claim → heartbeat → đóng).

## 2.1.0 (2026-08-12) — Handoff bằng file · bảng vị trí · `/dlc-resume` gọn context

**Vì sao (nguồn):** yêu cầu vận hành của chủ sở hữu — vào lại dự án ở phiên mới đang phải nạp lại quá nhiều;
agent bị spawn mất bối cảnh khi phiên kết thúc vì bối cảnh chỉ nằm trong prompt; và không có dấu vết để
retro khi nhiều vị trí cùng làm. `LL-PENDING` (chung với 2.0.0 — xem `MIGRATION.md` §5).

### Thêm — hoàn toàn cộng thêm, không phá gì đang chạy
- **`/dlc-resume`** — vào lại một dự án đã có bằng phiên mới: chạy `session_brief.py`, thuật lại briefing,
  drain inbox, rồi tiếp tục từ đúng HOF đang treo. Có luật context riêng: chỉ được đọc stdout của script +
  tối đa 1 file HOF; cấm nạp toàn văn intent-plan/unit-plan/as-is.
- **`scripts/session_brief.py`** — làm toàn bộ phần quét bằng Python (frontmatter `status.md` · `handoffs/` ·
  `inbox/` · session log) rồi in ~30 dòng có tín hiệu cao: intent · gate chờ · vị trí đang làm việc · inbox ·
  cảnh báo (nguồn `planned`, unit >5h, HOF treo lâu, gate thiếu gate_doc) · việc kế tiếp.
  Cờ: `--open-session` · `--close-session SES-NNN` · `--board-only`.
- **Protocol §9 Handoff** — mọi lần spawn agent PHẢI có `handoffs/HOF-NNNN.md`; prompt spawn chỉ được là một
  câu trỏ tới file. HOF có vòng đời `open → accepted → done|returned|superseded`, `read_first` ≤8 mục dạng
  `path#mục` + vì sao (trỏ, cấm chép), DoD của lượt, và phần *Đã làm* / *Còn treo* do agent nhận điền.
  Phiên chết giữa chừng → HOF vẫn `accepted`, phiên sau tiếp tục từ chính file đó.
- **Protocol §10 Ngân sách context** — đọc theo tầng (frontmatter trước), tra qua `session/INDEX.md`, không
  nhắc lại nội dung tài liệu trong MSG/HOF, kết thúc lượt là ghi ra file.
- Layout mới: `context-memory/handoffs/` · `context-memory/session/{board.md, INDEX.md, log/SES-NNN.md}`.
- Template: `handoff.md` · `session-board.md` · `context-index.md` · `session-log.md`.
- `session/board.md` là **bản kết xuất từ `handoffs/`** (không sửa tay) — một nguồn sự thật duy nhất.

### Đổi
- `§4.5` "ghi chú bắt buộc" → **"đóng handoff bắt buộc"** cuối mỗi lượt.
- orchestrator + bolt-coordinator: giao việc bằng HOF, cập nhật board sau mỗi đổi trạng thái.
- `/dlc-retro`: chuỗi HOF là nguồn bằng chứng đầu tiên (ai giữ việc, mấy vòng, `returned` vì thiếu gì).
- `/dlc-status`: chạy `session_brief.py` thay vì tự đọc file; báo cáo thêm bảng vị trí.
- `/dlc-init`: seed `handoffs/`, `session/log/`, `session/INDEX.md`.
- SessionStart hook: nhắc `/dlc-resume` + liệt kê HOF còn `accepted`.
- Tower: panel **"Vị trí đang làm việc"** ở Mission Control (xanh = agent đang chạy · hổ phách = chờ nhận ·
  đỏ = trả lại) và tab **Handoff** trong Intent Detail; bấm vào mở toàn văn HOF.

## 2.0.0 (2026-08-12) — Intent Plan, luật nguồn, Unit ≤5h, gate duyệt bằng tài liệu

**Vì sao (nguồn):** phản hồi trực tiếp của chủ sở hữu từ vận hành thật — agent FE/BE làm sai vì khâu đầu
luồng **đọc thiếu nguồn / đọc sai nguồn**, sai lan xuống hạ nguồn và chỉ lộ ra lúc code; Unit quá lớn nên
không kiểm soát được; gate bị duyệt mà người duyệt chưa đọc tài liệu đầy đủ.
`LL-PENDING` — thay đổi này CHƯA đi qua Gate G của một dự án thật (xem `MIGRATION.md` §5): dự án pilot đầu
tiên chạy 2.0.0 phải mở LL retro và cập nhật link vào entry này.

### BREAKING
- **Gate A đổi luật**: duyệt `intent-plan.md` (Intent + Source Reading Plan + Provisional Unit Map), không
  còn duyệt `intent.md` trần. Không có `gate_doc` → không được mở gate (protocol §2.1).
- **Layout `.ai-dlc/` thêm bắt buộc**: `intents/INT-NNN/intent-plan.md`, `unit-plan.md`, `revisions/REV-NN.md`,
  `as-is/source-ledger.md`.
- **`status.md` thêm field** `gate_doc`, `plan_version`.
- **Inbox verdict**: `approve | request-changes | reject` (trước là approve|reject); `approve` bắt buộc cờ
  `previewed: true` — tower_serve trả 400 nếu thiếu.
- **DoR v2 / DoD v2**, checklist `ba` v2 · `pm-po` v2 · `qa` v2 (pinned của intent cũ vẫn thắng, không tự đổi).

### Thêm
- Agent `dlc-source-planner` (opus) — quét thật workspace để dựng Source Reading Plan; 18 agents.
- Skill `/dlc-revise` — xử lý vòng `request-changes`: ghi REV-NN, giao đúng agent, bump version tài liệu,
  trình lại gate; vòng 3 → escalation.
- Checklist `source-plan` v1 (plan-completeness ở Gate A · ledger-completeness ở Gate B).
- Template: `intent-plan.md`, `unit-plan.md`, `source-ledger.md`, `user-stories.md`, `nfr.md`, `risks.md`.
- Luật protocol §4.8 **No-unread-source**: mọi nguồn đã cam kết phải có trạng thái cuối + evidence; còn
  `planned` là chặn Gate B/D; agent chỉ được kết luận từ nguồn có trong ledger.
- Luật protocol §4.9 **Unit ≤5h**: ước lượng có breakdown, >5h phải tách; mỗi Unit bắt buộc đủ
  User Story · NFR · Rủi ro.

### Control Tower
- `GateReview` — đọc **toàn văn** tài liệu gate (markdown render tại chỗ, có mục lục), checkbox xác nhận đã
  đọc mới bật Approve; ba nút approve / yêu cầu chỉnh sửa / reject; hiện blockers và các vòng REV trước.
- Màn **Dòng chảy 3 pha** (`PhaseFlow`): Inception · Construction · Operations, mỗi khối có artefact + gate,
  kèm bảng "mạch từng Unit xuyên ba pha" và bảng coverage nguồn.
- `md.js` — renderer markdown tự chứa (không CDN ngoài), escape HTML, tô nhãn `[CONFLICT]/[ASSUMED]/…` và ID truy vết.
- `tower_generate.py` v3: nhúng toàn văn gate_doc vào `data.js`, parse coverage nguồn, dựng `flowByIntent`,
  Unit mang `estimate_hours`/US/NFR/risk và tự đánh dấu vi phạm.
- `tower_serve.py` v2: verdict thứ ba, chặn approve thiếu `previewed`, endpoint `GET /doc?path=` đọc markdown
  tươi trong `context-memory/`.
- Mission Control: gate không còn nút approve tại chỗ — chỉ có "Đọc tài liệu & quyết định".

## 1.1.0 (2026-08-11) — Control Tower Design System UI
- Tower UI làm lại hoàn toàn theo "Control Tower Design System" (user thiết kế): React ui-kit 6 màn (Mission Control · Intents · Intent Detail · Bolt/Task Board · Comms & Reviews · Governance & Learning), dark-first, sidebar + drawer + toast.
- tower_generate.py v2: copy runtime plugin/tower-ui/ + sinh data.js từ state .ai-dlc/ thật (intents, gates + decision brief parse, feed MSG/RV/DEC, reviews, decisions, risks, debt, lessons, governance, tasks).
- App.jsx patch: Approve/Reject POST thật về /decision → inbox durable (token giữ nguyên); reject bắt buộc lý do; "Cần thảo luận" hướng về phiên terminal.
- tower_serve.py: serve static toàn bộ tower/ (MIME jsx=text/babel), path-traversal guard, no-store.
- Nguồn LL: chưa — đây là thay đổi UI theo yêu cầu trực tiếp của user (chủ sở hữu), không qua retro.

## 1.0.0 (2026-08-11) — MVP
- 17 agents (9 pipeline · 7 review board · retro-keeper), model tiers opus/sonnet/haiku.
- 14 commands `dlc-*`; 7 checklists v1; templates (workspace-map, DoR/DoD v1, intent, unit, tasks, OVERRIDES).
- Gates A–G + gate động; protocol.md là luật chung.
- Control Tower: generator (Mission Control + Bản đồ AI-DLC theo Hình 1 white paper + task boards + comms) và serve 2 chiều (Approve/Reject → inbox durable, token localhost).
- Hooks: SessionStart (binding rules + drain inbox), PreToolUse gate guard (chặn code-write trước Gate D theo workspace map, fail-open).
- Cơ chế: overrides thắng plugin, pinned snapshot per intent, contribute → PR.
- Nguồn phương pháp: white paper AI-DLC bản dịch nội bộ (đã biên tập). Chưa có LL nào — thay đổi sau này bắt buộc link LL.
