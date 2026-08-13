---
name: dlc-doctor
description: Audit sức khỏe AI-DLC của project — coverage nguồn (dòng planned còn treo), Unit thiếu điều kiện kích thước (releasable/session_fit) hoặc thiếu US/NFR/risk, nhịp HOF khai giả, teammate zombie, tin chết, gate thiếu gate_doc, override mồ côi, lệch version checklist, inbox tồn đọng.
---

Chỉ đọc + báo cáo (sửa gì phải được user đồng ý từng mục):

1. **Coverage nguồn (protocol §4.8)** — với mỗi intent đã qua Gate A:
   - `intent-plan.md` phần 2 có bao nhiêu nguồn; `as-is/source-ledger.md` đóng được bao nhiêu.
   - Dòng còn `planned` → **FIX** (chặn Gate B/D). Dòng `read` mà thiếu evidence → **FIX** (coi như chưa đọc).
   - `missing`/`deferred` chưa có chủ hoặc chưa thành risk → **WARN**.
   - `[CONFLICT]` chưa vào open-questions → **WARN**.
1b. **Open questions (protocol §4.10)** — với mỗi intent đã qua Gate B:
   - Còn `open-questions.md` gộp (không có bản business/tech) → **WARN**: tách ở vòng chỉnh sửa tới.
   - Câu trong `open-questions-business.md` chứa dấu vết kỹ thuật (`/`, `.md`, `.ts`, `.py`, `_id`, `()`,
     `snake_case`, tên bảng/cột) → **FIX**: người nghiệp vụ không trả lời được câu viết bằng ngôn ngữ code.
   - Câu thiếu **người trả lời cụ thể** (rỗng, "TBD", hoặc chuỗi vai chung chung kiểu `BA/Tech Lead/Test Lead`)
     → **FIX**. Câu thiếu cột *Nếu im lặng* (phương án mặc định) → **FIX** (§4.10.6).
   - Câu business không có phương án chọn sẵn (bảng A/B/C) → **WARN**: câu mở khó chốt tại Gate C.
   - `open-questions-tech.md` có câu `CHẶN UOW-NN` còn `open` mà intent đã ở stage ≥5 → **FIX** (chặn Gate D).
   - Mã *soi chiếu* trỏ tới mã không tồn tại ở file kia → **WARN** (cặp câu đứt).
1c. **Số liệu dashboard (protocol §4.11)** — chạy `tower_generate.py` rồi soi `metricsByIntent`:
   - Metric nào có `warnings` → in ra kèm cách sửa (thường là ô `Trạng thái` viết lạ, hoặc unit không khai
     `status`). Đây là chỗ dashboard đang **nói con số mà chính nó không chắc**.
   - `units.reviewed` < tổng unit đã đóng → **FIX**: số "unit đã xong" đang là **tự khai**; đừng dùng nó
     làm bằng chứng nghiệm thu ở Gate F mà không nói rõ điều đó.
   - `units.artifacts` < tổng unit đã đóng → **WARN** kèm danh sách unit thiếu bolt/tasks/evidence.
   - `sources.unknown` > 0 → **FIX**: sửa ô trạng thái trong sổ cái về từ khoá đọc được
     (`✅ đã đọc` · `read` · `⬜ chưa` · `missing` · `deferred` · `superseded`).
   - Sổ cái tồn tại mà `sources.read + planned = 0` → **FIX**: bảng thiếu cột `#`/`Nguồn`/`Trạng thái`
     nên không đếm được dòng nào.
   - Unit có thư mục + spec nhưng không nằm trong `unit-plan.md` và cũng không trong `DESCOPED.md` →
     **WARN** "thêm sau unit-plan": hợp lệ, nhưng nên ghi một DEC nói vì sao.
1d. **Artifact có TỒN TẠI không (protocol §4.12–§4.14 · LL-002 · LL-003)** — luật không kiểm được là luật
   sẽ trượt: một dự án thật đóng 17 unit với 0 review và 14/18 unit không có thư mục bolt nào, không ai nói
   dối, chỉ là không có lệnh nào đối chiếu. Kiểm **sự tồn tại**, không chỉ nội dung:
   - Unit `done`/`approved` mà **không có `rv:` trỏ một `reviews/RV-NNN.md` có thật**, và cũng không có
     `review_waived_by: DEC-NNNN` → **FIX**. `rv:` trỏ RV không tồn tại, hoặc `re:` của RV không khớp unit
     → **FIX** (tệ hơn thiếu: nó *trông như* đã review).
   - Unit `done` mà **không có `bolts/BOLT-NN/`** → **WARN**. Bolt có mà thiếu bất kỳ chặng nào trong sáu
     (`domain-design.md` · `logical-design.md` · `adr/` · `contract.md` · `tasks.md` · `evidence/`)
     → **WARN** kèm tên chặng thiếu — bolt là bốn chặng, không phải một thư mục rỗng (protocol §1.0).
   - Dự án **brownfield** mà thiếu `as-is/static-model.md` hoặc `as-is/dynamic-model.md` → **FIX**:
     đang thiết kế trên trí nhớ về hệ thống thay vì trên hệ thống (§1.0b). *Không đề xuất dựng bù*: design viết ngược từ code đã chạy là mô tả code đội lốt quyết
     định thiết kế — ghi nhận khoảng trống, đừng lấp bằng đồ giả.
   - `HOF-*.md` khai `scope: …/BOLT-NN` mà thư mục đó không tồn tại → **FIX** (tên bolt trong HOF là chuỗi
     tự do; đây là chỗ duy nhất đối chiếu nó với đĩa).
   - HOF `status: done` mà phần *Còn treo* ghi "chờ verdict" / "đã gửi review-request" → **FIX**: gửi review
     rồi đóng lượt trong cùng một nhịp là ca đã xảy ra 13 lần.
   - **Điểm dừng bị đi qua** (protocol §1.0c) — với mỗi Unit, đối chiếu năm điểm dừng với dấu vết thật
     (`reviews/` · `comms/` · `gates_passed` · `escalations/`). Unit đã đóng mà điểm dừng nào ở trạng thái
     *đã đi qua mà không dừng* → **FIX**, in ra đúng điểm nào. Điểm dừng `đang chờ NGƯỜI` quá 2 phiên
     → **WARN** kèm tên người/gate đang giữ — việc đứng ở người thì phải nhìn thấy được là đứng ở ai.
   - `escalations/ESC-*.md` `status: open` mà `owner:` trống → **WARN** (phát hiện không có chủ = phát hiện
     sẽ chìm). File `_trash/UOW-NN/` thiếu `TOMBSTONE.md` hoặc còn `status: approved` → **FIX**.
1e. **Nhịp sống có thật không (protocol §9.4)** — chạy `tower_generate.py` rồi soi `handoffHealth`:
   - Mỗi mục trong `suspect` → **FIX**, in nguyên câu `why`. Ba ca: `placeholder` (heartbeat đúng nửa đêm),
     `future` (nhịp ở tương lai), `drift` (file HOF được ghi muộn hơn nhịp khai > 30 phút). Cả ba đều nghĩa là
     **agent còn sống nhưng bảng đang nói sai** — nguy hơn không có số, vì người giám sát đi hỏi nhầm chuyện.
   - Mục trong `noHeartbeat` (đang `accepted` mà `heartbeat: -`) → **FIX**.
   - `trusted / accepted` < 100% → in tỉ lệ ở bảng tổng. Đây là KPI của §9.4; không có nó thì luật "báo còn
     sống" chỉ là lời khuyên.
1f. **Teammate (protocol §9.5)** — chỉ **WARN**, chưa phải luật chặn gate (chưa qua Gate G):
   - HOF `accepted` có `teammate:` trỏ tên không khớp quy ước `<vai>-<mã việc>` → WARN.
   - Đang chạy teammate mà HOF không khai `teammate:` → WARN: pane đang chạy và dòng trên board không ghép
     được với nhau. Đối chiếu bằng `~/.claude/teams/<team>/config.json` (thành viên ngoài `team-lead`).
   - Trong `comms/` có MSG kiểu "đã duyệt/OK" từ agent mà **không** có RV/DEC tương ứng → **FIX** (§9.5.3):
     tin nhắn giữa agent không đóng được gate.
   - `team.zombies` (§9.5.6) → **WARN** từng phiên: `zombie` = HOF của nó đã `done`/`returned` mà phiên còn
     sống → đề nghị lead tắt (gọi tên + yêu cầu shutdown, **không** giết pane — teammate được phép từ chối
     vì đang dở, và giết pane là mất phần *Đã làm* / *Còn treo*). `unknown` = phiên sống mà không HOF nào
     khai `teammate:` → hoặc bổ sung trường, hoặc tắt: một phiên không ai biết đang giữ việc gì thì lần sau
     không ai dám tắt nó, và nó sống mãi.
1g. **Tin chết (protocol §9.5.5)** — soi `team.deadLetters` từ `tower_generate.py`:
   - Hộp thư `~/.claude/teams/<team>/inboxes/<tên>.json` có tin mà `<tên>` **không** nằm trong `members`
     → **FIX**: spawn hỏng nhưng `SendMessage` vẫn báo "đã gửi". In tên + số tin + trích 1 dòng đầu, và
     nói rõ **việc đó chưa ai làm** — đừng để nó nằm trong đầu người giao dưới dạng "đã giao rồi".
   - Nếu tin đó là review-request → đối chiếu `reviews/`: không có RV tương ứng thì đây đúng là `LL-002`
     tái diễn (§4.12) — unit liên quan **không** được tính là đã review.
2. **Unit (protocol §4.9)** — với mỗi `units/UOW-NN/`:
   - `estimate_hours` = 0 hoặc thiếu → **FIX**; **không còn trần giờ** (§4.9 v5). Cả loạt Unit cùng một con
     số tròn → **WARN** (ước lượng lấy lệ). Dự án có đặt `unit_max_hours` trong `governance/sizing.md` mà
     Unit vượt → **WARN**, không chặn.
   - Thiếu `releasable`, hoặc `releasable: no` mà không có `released_with` → **FIX**: unit không có đường ra
     sản phẩm nào là pseudo-unit kỹ thuật. Thiếu `session_fit`, hoặc `session_fit` không có con số → **FIX**.
   - `session_fit` chép giống hệt nhau ở nhiều Unit → **WARN** (khai lấy lệ).
   - Đối chiếu `units.oneSession` trên tower: Unit đã đóng mà cần ≥2 HOF hoặc có HOF `returned` → **WARN**
     kèm tên — không phải để phạt, mà là dữ liệu cắt Unit cho intent kế.
   - Thiếu/rỗng `user-stories.md` · `nfr.md` · `risks.md` → **FIX**.
   - `sources:` trỏ tới nguồn không có trong ledger, hoặc nguồn chưa `read` → **FIX**.
   - NFR không có ngưỡng số hoặc không có cách đo → **WARN**.
3. **Gate** — `status.md` có `gate_open` mà `gate_doc` null hoặc file không tồn tại → **FIX** (protocol §2.1).
   `revisions/REV-*.md` còn `status: open` quá 2 bản → **WARN** (nên escalation).
4. `.ai-dlc/overrides/**`: thiếu frontmatter reason/source → cảnh báo; nội dung ⊆ bản plugin hiện tại →
   "đã upstream, nên xóa"; xung đột bản mới → in diff.
5. So version checklist: pinned của intent đang chạy vs plugin hiện tại → liệt kê lệch (chỉ thông tin —
   pinned vẫn thắng trong intent đó). Intent tạo bằng plugin <2.0.0 → nhắc đọc `MIGRATION.md`.
6. `inbox/` có file chưa processed → nhắc drain. `workspace-map.md` mục null mà flow sắp cần → nhắc.
6b. **`.ai-dlc` rác** — quét cả repo: thư mục `.ai-dlc/` nào **chỉ có `tower/`**, không có
   `context-memory/`, là dashboard rỗng do chạy generator sai chỗ (trước 4.0.0 script nhận bừa `cwd`
   làm gốc dự án). → **FIX**: xoá; state thật chỉ nằm ở gốc. Cũng kiểm `.ai-dlc/` lồng trong `.ai-dlc/`.
   Nếu thấy nhiều hơn một `.ai-dlc/context-memory/` trong cùng repo → **hỏi người**, không tự xoá:
   đó có thể là hai dự án thật nằm chung repo.
6c. **Frontmatter có chú thích cuối dòng** (`gate_open: null  # A đã đóng bằng DEC-0031`) — hợp lệ và nên
   giữ, nhưng nếu `status.md` có `gate_open` không phải `A`–`G`/`escalation`/`null` sau khi cắt chú thích
   → **FIX**: tower coi như không có gate mở và in cảnh báo; giá trị lạ ở đây từng dựng ra một *gate ma*.
7. In bảng tổng: OK / WARN / FIX kèm hành động đề xuất.
