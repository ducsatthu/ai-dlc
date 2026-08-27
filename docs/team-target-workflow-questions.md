# Câu hỏi làm rõ với team về workflow đích (Intent · Plan · Execution · Verify)

> Gửi: team vẽ `docs/techtus-aidlc-workflow-viewer.html` (2026-08-27) · Từ: chủ gói `ai-dlc` · Ngày: 2026-08-27
> Bản đối chiếu đầy đủ: `docs/team-target-workflow-vs-ai-dlc.md`. File này chỉ gom **câu hỏi** — mỗi câu có *quan sát trên hình* (số bước), *vì sao phải hỏi*, và *đề xuất* để team phản biện. Trả lời ngắn vào ô **Trả lời** là đủ; câu nào team thấy hình đã đúng thì ghi "giữ" kèm một dòng lý do.
>
> Trước hết, ba điều tôi thấy **đúng và muốn giữ**: rút còn 3 gate người (thay vì 7 của gói hiện tại) · Gate 3 là *tự dùng thử trên hệ thống* chứ không phải đọc diff · **Preview → Confirm → Publish** cho mọi lần ghi ra Backlog. Các câu dưới là để làm workflow này chạy được thật, không phải để kéo về mô hình cũ.

---

## A · Điểm dừng — ai chờ ai, và chờ khi nào

### A1. Gate 3 đặt sau *tất cả* unit — Lead nhìn thấy sản phẩm lần đầu khi nào?
- **Quan sát**: bước 11 (Execution UNIT) lặp cho từng unit → bước 12 Gate 3 *Integrated Outcome* một lần. Với intent 10–30 unit, người chỉ "self testing trên outcome hệ thống" khi mọi thứ đã xong.
- **Vì sao hỏi**: đây đúng ca INT-001 của PILOT — 17 unit đi qua điểm demo mà không ai dừng; phản hồi dồn về cuối thì sửa đắt nhất. Bài này là lý do white paper v2 tách *Điểm nhìn (Showcase)* per unit khỏi *chốt chặn* cuối.
- **Câu hỏi**: Team có chấp nhận **mỗi unit xong ra một bản "bấm thử" ≤ 10 bước** (không chặn, Engineer/BA xem khi rảnh, phản hồi từng dòng), và Gate 3 chỉ mở khi mọi phản hồi "đổi/làm lại" đã đóng? Hay dự án đích có lý do để chỉ nhìn một lần (ví dụ unit không chạy độc lập được)?
- **Đề xuất**: giữ Gate 3 làm chốt chặn duy nhất; thêm điểm nhìn per unit, không thêm gate.
- **Trả lời**:

### A2. Gate 2 "duyệt unit trước execution" — duyệt *gì* trên bảng unit?
- **Quan sát**: bước 08 chặn cứng; bước 07 sinh unit có role, owner, dependency, AC, verification, halting condition.
- **Vì sao hỏi**: Gate D của PILOT INT-003 duyệt 30 unit · 113h bằng một file — không ai đọc nổi từng dòng, kết quả là approve mù hoặc đứng im. Gate chặn cứng chỉ có nghĩa khi người thực sự quyết được thứ trên bàn.
- **Câu hỏi**: Ở Gate 2 người quyết cái gì cụ thể — (a) *thứ tự* unit và unit nào ra bấm thử trước, (b) *từng* unit đúng/sai, hay (c) chỉ *tổng* phạm vi? Nếu là (a), Gate 2 có thể là "mốc chờ có hạn" (im lặng N giờ = đi theo thứ tự AI đề xuất) thay vì chặn cứng không?
- **Trả lời**:

### A3. Bước 13 "Agents Gate security, Quality" chạy *sau* Gate 3 người
- **Quan sát**: mũi tên 17 → 13 → 18; vòng đỏ "Back to fix security & quality" quay lại 11 **sau khi** người đã ký Gate 3 và đã comment lên Backlog (15).
- **Vì sao hỏi**: máy bắt sửa sau khi người ký ⇒ chữ ký vô hiệu, phải ký lại; và người đang review thứ máy chưa soát. Playbook Anthropic và §4.17 của gói đều đặt máy **trước** người để người chỉ còn xét *ý định + rủi ro*.
- **Câu hỏi**: Có lý do gì để 13 đứng sau 12 (ví dụ agents gate cần môi trường tích hợp chỉ có sau merge)? Nếu không, đảo 13 lên trước 12 được không? Và "agents gate plugins" cụ thể là gì — linter/SAST tất định, hay agent LLM đọc code? Hai loại này cần luật khác nhau (máy tất định có thể chặn; agent LLM chỉ được *đề xuất*).
- **Trả lời**:

### A4. Không có ranh đỏ — deploy, migration, public API nằm ở đâu?
- **Quan sát**: workflow kết thúc ở *Teams review & merge PR* + *Close backlog*. Không có hộp deploy, migration, hay "đổi contract có consumer ngoài đội".
- **Vì sao hỏi**: gate là nơi *người chờ AI xong*; ranh đỏ là nơi *AI phải dừng dù người không ở đó*. Không vẽ ⇒ AI có thể chạy migration phá dữ liệu trong bước 11 mà không ai chặn.
- **Câu hỏi**: Trong dự án đích, đội AI có được chạm (a) deploy môi trường có người dùng thật, (b) migration xoá/ghi đè dữ liệu, (c) public API/contract có consumer ngoài đội, (d) gửi thông tin ra ngoài (email/ticket khách)? Chỗ nào AI **phải dừng thật** kể cả khi chưa tới gate?
- **Đề xuất**: liệt kê ranh đỏ của dự án (gói có sẵn 9 dòng mặc định) — Preview→Confirm→Publish của Backlog chính là ranh đỏ (d) đã có hình.
- **Trả lời**:

---

## B · Câu hỏi làm rõ, giả định, nguồn

### B1. Assumption chưa có người trả lời thì flow làm gì?
- **Quan sát**: bước 03 câu trả lời thành `[ans:A1]`; Gate 1 kiểm "assumptions". Không thấy nhánh "chưa trả lời → ?".
- **Vì sao hỏi**: PILOT có 38 câu hỏi mở (5 chặn) ở một thời điểm; luật "hỏi rồi chờ" khiến AI hoặc đứng thật, hoặc *giả vờ hỏi rồi tự trả lời* (không truy vết được).
- **Câu hỏi**: Mỗi assumption có ghi **mặc định nếu im lặng** + **đảo lại tốn bao nhiêu** + **nhìn thấy ở đâu trong sản phẩm** không? Câu đảo rẻ ⇒ AI chọn mặc định, ghi lại, đi tiếp; câu đảo đắt ⇒ chờ có hạn; câu chạm ranh đỏ ⇒ dừng. Team có chấp nhận ba mức này không, hay muốn mọi assumption đều chờ người?
- **Trả lời**:

### B2. "Mỗi dòng mang tag chỉ về nguồn" — kiểm bằng gì?
- **Quan sát**: bước 02. Tag kiểu `[S3]`/`[ans:A1]`/`[assumption]`.
- **Vì sao hỏi**: luật không kiểm được là luật sẽ trượt. AWS có sensor `claim-sources` chạy lúc ghi file; gói có sổ cái nguồn (`source-ledger`) bắt mọi nguồn có trạng thái cuối.
- **Câu hỏi**: Tag phải resolve về **danh sách nguồn có trạng thái đã đọc** (ledger), hay chỉ cần có tag? Ai/máy nào kiểm trước Gate 1? Nguồn *lên kế hoạch đọc mà chưa đọc* có được chặn Gate 1 không (gói: có — "No-unread-source")?
- **Trả lời**:

### B3. "Một lựa chọn không được chọn thì không phải là loại trừ" — hiểu thế nào?
- **Quan sát**: bước 03.
- **Câu hỏi**: Nghĩa là phương án B/C không chọn vẫn được ghi lại và có thể quay lại (đúng tinh thần Sổ giả định), hay nghĩa là AI không được coi "không chọn" là "cấm"? Hai cách hiểu cho hai luật khác nhau — team ghi rõ được không?
- **Trả lời**:

---

## C · Plan và Work Unit

### C1. Work Unit thiếu hai điều kiện kích thước
- **Quan sát**: bước 07 có role, owner, dependency, AC, verification, halting condition — **không có** "xong unit này ra được sản phẩm không" và "một phiên có ôm nổi không".
- **Vì sao hỏi**: PILOT DEC-0052 từng tách unit chỉ để lọt trần giờ, hai mảnh phải ra chung mới có nghĩa. Unit không tự ra được sản phẩm thì bấm thử (A1) không có gì để bấm.
- **Câu hỏi**: Thêm `releasable: yes|no (+ ra chung với unit nào)` và `session_fit` có con số (mấy màn/endpoint/bảng, mấy nguồn) vào Work Unit được không? Và team **cắt dọc** (một unit chạm domain+api+web, ra được thứ để bấm) hay **cắt theo tầng** (u1-domain → u2-api → u3-web)?
- **Trả lời**:

### C2. Không có bước thiết kế (domain/logical/ADR) — cố ý hay bỏ sót?
- **Quan sát**: 07 chia unit → 11 code thẳng. Không có hộp design; ADR chỉ xuất hiện ở bước 14 "reconcile accepted knowledge and ADR" *sau merge*.
- **Vì sao hỏi**: ADR viết ngược từ code đã chạy là mô tả code đội lốt quyết định thiết kế. Gói bỏ *gate người* ở design (đúng hướng v2) nhưng vẫn giữ *chặng* design trong đội AI.
- **Câu hỏi**: Team bỏ hẳn design, hay design nằm ẩn trong "plan.md"? Nếu unit có quyết định kiến trúc (bảng mới, contract giữa area, pattern khác codebase), nó được ghi ở đâu **trước** khi code, và ai trong đội AI chốt?
- **Trả lời**:

### C3. `owner` của Work Unit là người hay agent?
- **Quan sát**: bước 07 "role, owner".
- **Câu hỏi**: owner = Engineer chịu trách nhiệm, hay agent thực thi? Nếu là người, một Engineer "own" bao nhiêu unit chạy song song thì review còn theo kịp (playbook: 2–3 phiên là trần)?
- **Trả lời**:

---

## D · Execution loop

### D1. "Tự sửa tối đa ba lần" — lần thứ tư thì sao?
- **Quan sát**: bước 10, 11, khung *max 3 times*; "halting condition" khai trong unit.
- **Vì sao hỏi**: đây là luật tốt, gói chưa có. Nhưng luật cần hậu quả: dừng rồi đi đâu?
- **Câu hỏi**: Hết 3 lần ⇒ (a) unit về trạng thái *chặn* + tạo escalation có chủ, (b) hỏi Engineer ngay trong phiên, hay (c) bỏ qua unit đó làm unit kế? "Halting condition" ngoài số lần còn gồm gì (test suite đỏ ở phần không liên quan? chạm file ngoài contract?)?
- **Trả lời**:

### D2. "Loop Verify follow AC" — ai verify, cùng context hay context tươi?
- **Quan sát**: bước 11 ↔ 11' "Agents Loop verify".
- **Vì sao hỏi**: agent vừa viết code tự chấm mình thì bị chính giả định của mình che mắt. Playbook: verifier chạy **context tươi**, report-only, không sửa.
- **Câu hỏi**: Loop verify là cùng agent chạy lại test, hay agent khác context mới đọc AC + chạy app? Evidence của verify ghi ở đâu để Gate 3 đọc (file evidence per unit, hay chỉ output test)?
- **Trả lời**:

### D3. AI được sửa file test khi đang fix không?
- **Quan sát**: không vẽ.
- **Vì sao hỏi**: agent sửa lỗi mà được sửa luôn test thì loop verify vô nghĩa ("fix the code, not the test").
- **Câu hỏi**: Với unit kind bugfix, có luật *viết test fail trước, commit, rồi cấm sửa file test trong lúc fix* không? Cấm bằng hook hay bằng review?
- **Trả lời**:

### D4. "Teams review & merge PR" là điểm dừng người hay không?
- **Quan sát**: nằm ở lane Git, không tô màu gate, đứng **trước** Gate 3.
- **Câu hỏi**: PR review có phải gate thứ tư không (người đọc diff)? Nếu có, Gate 3 còn cần đọc "evidence markdown" không, hay chỉ cần tự dùng thử? Nếu PR review là "máy review + code owner bấm approve" (playbook), team đã có công cụ review máy chưa?
- **Trả lời**:

---

## E · Backlog

### E1. Nguồn sự thật của cái gì nằm ở đâu?
- **Quan sát**: Story sync từ `intent.md` (06a); Work Unit *chỉ sống trong plan.md* (06b); commit `[TSD-158]`; comment evidence (15); close (16).
- **Vì sao hỏi**: hai bản (Backlog và repo) mà không khai bản nào là gốc thì sớm muộn lệch nhau — playbook gọi cấu hình này là "linkage": chấp nhận hai nguồn nhưng phải link hai chiều.
- **Câu hỏi**: Xác nhận: **repo là gốc** cho intent/plan/evidence, **Backlog là gốc** cho trạng thái và giao tiếp với PM/khách? Sửa `intent.md` sau khi Story đã publish ⇒ sync lại Story, hay chỉ comment? Ai sửa Story trên Backlog tay thì có sync ngược không (đề xuất: **không**)?
- **Trả lời**:

### E2. Ai bấm Confirm ở mỗi lần Preview → Confirm → Publish?
- **Quan sát**: 4 lần (05a Story · 05b child · 08 Units · 12 comment). Theo lane: BA&APM cho Story, Engineer cho Units/comment.
- **Câu hỏi**: Đúng như lane không? Confirm bấm ở đâu — terminal, hay màn hình (tower) có preview toàn văn? Có trường hợp nào AI được publish **không** cần confirm (ví dụ comment tiến độ)? Đề xuất: không — mọi ghi ra Backlog là ranh đỏ, luôn có người bấm.
- **Trả lời**:

### E3. Work Unit → task Backlog cho mọi loại, hay chỉ feature?
- **Quan sát**: 09 tạo task; nhưng 06b nói bugfix/refactor "Work Units chỉ sống trong plan.md".
- **Câu hỏi**: Feature/infra ⇒ mỗi unit một task; bugfix/refactor ⇒ không task, chỉ một child issue — đúng không? Task có cần cập nhật trạng thái theo unit (in-progress/done) hay chỉ tạo rồi đóng cùng Story?
- **Trả lời**:

### E4. Backlog MCP — có sẵn chưa, ai vận hành?
- **Câu hỏi**: MCP server cho Nulab Backlog là bản có sẵn hay team tự dựng? Quyền ghi của MCP giới hạn ở project `TSD`? Token đặt ở đâu (không nằm trong repo)? Nếu Backlog tắt ("nếu Backlog enabled"), phần nào của workflow đổi?
- **Trả lời**:

---

## F · Verify, học, và workspace

### F1. "Human accepts memory changes" — đọc gì để chấp nhận?
- **Quan sát**: bước 14 propose/reconcile knowledge + ADR; human accepts.
- **Vì sao hỏi**: memory là luật cho mọi intent sau; chấp nhận mù còn tệ hơn không có. Gói bắt lesson learned đi qua retro + gate riêng.
- **Câu hỏi**: Đề xuất memory update hiện ở dạng gì (diff của `memory/rules/*.md`?), ai duyệt (Engineer làm unit đó, hay tech lead), và có phân biệt *rule bắt buộc* (memory) với *tham khảo* (knowledge) khi đề xuất không? Rule sai hai intent liên tiếp thì ai gỡ?
- **Trả lời**:

### F2. "Mark affected codekb STALE" — rồi ai/khi nào làm tươi lại?
- **Quan sát**: bước 14 chỉ đánh dấu STALE.
- **Câu hỏi**: Intent kế gặp STALE thì quét lại toàn bộ hay chỉ delta (file đổi từ commit gần nhất)? Ai quyết reuse/rescan — người ở Gate 1 hay AI tự (gói 6.2.0: AI so HEAD, ghi quyết định vào sổ cái nguồn để người thấy ở Gate 1)? `codekb` chia theo area (`backend`, `infra`) — một repo nhiều area thì fingerprint tính theo gì?
- **Trả lời**:

### F3. Cây `/docs/…` — commit vào repo sản phẩm, hay repo riêng?
- **Quan sát**: `/workspace/docs/{intents,memory,knowledge,codekb}` + `/sources`.
- **Câu hỏi**: `/docs` nằm trong repo chứa `/sources` (cùng PR), hay repo riêng? `knowledge/documents` chứa raw từ khách (PDF, backlog export) — có dữ liệu cá nhân/hợp đồng không, có được commit không? `documentkb` ("document index convert") là tool nào sinh ra? Team muốn thư mục **nhìn thấy** (`/docs`) thay vì ẩn (`.ai-dlc/`) vì lý do gì — để PM đọc, hay để commit chung?
- **Trả lời**:

### F4. Một space hay nhiều?
- **Câu hỏi**: Dự án đích có một đội duyệt cho cả `backend` và `infra`, hay hai đội (dev và platform) với approval riêng? Câu này quyết có một hay hai `/docs` (Atlas tuần trước: "team ổn định → space").
- **Trả lời**:

---

## G · Engine, harness, vai trò

### G1. Chạy trên gì? — câu quyết mọi câu còn lại
- **Quan sát**: lệnh `/aidlc start <business outcome>`, từ `intent.md`/`plan.md`/Work Unit/codekb STALE/`[ans:A1]` là từ vựng **AWS aidlc-workflows v2**; nhưng 3 gate + Backlog + Codex là của team; và AWS v2 **không tắt được gate mỗi stage** (đã kiểm — `aws-aidlc-workflows-v2-vs-ai-dlc.md` §3.2).
- **Câu hỏi**: Team định (a) chạy trên gói `ai-dlc` (sẽ thêm Backlog, `kind`, trần 3 lần…), (b) cài AWS v2 nguyên bản (thì 3 gate không giữ được), hay (c) viết plugin `/aidlc` mới theo đúng hình? Nếu (c), phần nào của gói hiện tại muốn tái dùng (tower, handoff file, sổ cái nguồn, doctor)?
- **Trả lời**:

### G2. Codex
- **Quan sát**: lane "AI agents Claude Code & Codex".
- **Câu hỏi**: Codex làm việc gì trong flow — thực thi unit song song, review chéo, hay chỉ là "có thể dùng"? Gói `ai-dlc` chỉ có hook/skill/tower cho Claude Code; Codex đọc được file `.ai-dlc/` nhưng không có hàng rào. Nếu Codex thực thi unit, ranh đỏ và guard áp cho nó bằng gì?
- **Trả lời**:

### G3. BA/APM và Engineer — ai là "Lead" của một intent?
- **Quan sát**: BA&APM *leading* Intent; Engineer *leading* Plan/Execution; Gate 3 Engineer ký.
- **Vì sao hỏi**: outcome là của BA/PO; người ký "đã đạt outcome" mà không phải người đặt outcome thì Gate 3 đo cái gì?
- **Câu hỏi**: Gate 3 ai ký — Engineer, BA/APM, hay cả hai (Engineer: evidence/kỹ thuật; BA: tự dùng thử theo outcome)? Bẻ lái giữa chừng (đổi scope khi đang execution) ai được quyền, ghi ở đâu?
- **Trả lời**:

---

## Tóm tắt — điểm cần cải thiện, xếp theo mức ảnh hưởng

| # | Điểm | Ảnh hưởng nếu không sửa | Câu |
|---|---|---|---|
| 1 | Chốt **engine** (gói / AWS v2 / plugin mới) và vai Codex | mọi việc build tiếp có thể sai địa chỉ | G1, G2 |
| 2 | Gate 3 sau mọi unit — thêm điểm nhìn per unit, không thêm gate | phản hồi dồn cuối, sửa đắt (ca INT-001) | A1, C1 |
| 3 | Agents gate (13) chạy **trước** Gate 3; tách máy tất định vs agent LLM | chữ ký người vô hiệu | A3 |
| 4 | Ranh đỏ của dự án (deploy/migration/contract/ghi ra ngoài) | AI làm việc không đảo được mà không ai chặn | A4 |
| 5 | Assumption có mặc định-nếu-im-lặng + chi phí đảo; tag nguồn kiểm được | AI đứng chờ hoặc tự trả lời thầm | B1, B2 |
| 6 | Hậu quả của "max 3 lần"; verify context tươi; cấm sửa test khi fix | loop verify thành hình thức | D1–D3 |
| 7 | Backlog: SoT, ai confirm, task cho kind nào, MCP | hai nguồn sự thật lệch nhau; publish không người | E1–E4 |
| 8 | Memory update ai duyệt; codekb STALE ai làm tươi; `/docs` commit ở đâu | luật sai lan sang intent sau; docs chứa dữ liệu khách | F1–F3 |
| 9 | Work Unit thêm `releasable`/`session_fit`; design ghi trước code | unit không ra được sản phẩm; ADR viết ngược | C1, C2 |
| 10 | Ai ký Gate 3, ai được bẻ lái | gate đo sai người | G3 |
