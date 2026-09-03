# Nhiều người dùng chung một `.ai-dlc/` — sáu vai, ba loại thẻ, thang bậc 0 → 2

> Trạng thái: **PHÁC THẢO sau brainstorm — chờ chủ gói chốt hai câu treo rồi đưa đội** · Ngày: 2026-09-03
> Câu hỏi gốc: *gói chạy ổn với một người; làm sao cả đội dùng chung trên một dự án, và dùng thế nào để dự án thành công (release được cho khách), không phải để "ai cũng dùng plugin".*
> Bốn quyết định chủ gói chốt trong brainstorm: (1) đội đầu tiên = PM · Người dịch/APO · Team Lead · 2 Dev · Tester, tất cả dùng git · (2) mục tiêu **bậc 2 trở lên** · (3) thành công đo bằng **release một tính năng cho khách** · (4) **commit là quyết định** — markdown trong git trên một nhánh chính thức là nguồn sự thật, nhưng phải nhanh.
> Liên quan: `plugin-transition-plan.md` (7.0.0, chờ chọn A/B/C — file này thực chất là lý do để chọn), `team-target-workflow-questions.md` (câu G3 ai là Lead · F3/F4 docs commit đâu, một space), `workspace-knowledge-model-from-team-atlas.md` (mục 6 `governance/raci.md`), `anthropic-ai-native-sdlc-playbook-vs-ai-dlc.md` (khoá file test khi fix · verifier tươi context).

---

## 0 · Kết luận một trang

1. **Gói 6.2.0 là cockpit một ghế.** Bốn giả định ngầm "một người, một máy": `dlc-init` bước 4 gợi ý `.gitignore .ai-dlc/` · tower `localhost` + `inbox/*.json` trên máy người bấm · ID tuần tự `HOF-0042` · "tôi" trong *Cần tôi quyết* là một người. Muốn nhiều người thì gỡ bốn giả định này, không phải thêm tính năng. Kiến trúc markdown-first vốn hợp git — thiếu là **quy ước**, không phải công nghệ.
2. **Chỉ hai vai chạm Claude Code** (2 Dev, và Team Lead khi mở intent). Bốn vai còn lại (PM · APO · Tester · Team Lead khi duyệt) **không gõ lệnh** — chỉ chạm tower. Tower vì thế thành **cửa chính của đội**, với ba loại thẻ theo vai: *Cần tôi quyết* · *Cần tôi trả lời* · *Cần tôi kiểm*. Cùng một cơ chế phía sau: **một nút = một commit, một hạn giờ, một mặc định**.
3. **"Nhanh hơn" đến từ bốn chỗ**, xếp theo hiệu quả: không PR cho `.ai-dlc/` (repo control plane riêng, commit thẳng) · nút tower = commit + push, agent `git fetch` thay vì đọc inbox · im lặng quá hạn = mặc định + ASM · hook push gọi đúng người qua Slack/Nulab. Ca PILOT cho thấy chậm không ở agent mà ở **chờ người** (13 review request / 0 verdict). KPI tốc độ: **trung vị giờ từ thẻ xuất hiện tới commit DEC**.
4. **Bậc 2 (hai dev chạy bolt song song) chạm format bản ghi ⇒ 7.0.0.** Ba thứ phải đổi: ID theo intent + chữ cái đầu người tạo · file tổng hợp (`board.md`, `decisions-log.md`) chỉ sinh ra, cấm sửa tay · trường `by:` trên DEC/RV/HOF + mỗi Unit một nhánh/worktree. Bậc 0–1 làm được trên 6.x.
5. **Tester là vai duy nhất mà giá trị nằm ở sự độc lập**, và Tester **không viết gì**. Gói hiện không có chỗ cho Tester người (test toàn của dev/máy). Thêm hai tài sản: `governance/test-viewpoints.md` (bảng góc nhìn, bền vững, Tester bổ sung dần) và `units/UOW-NN/test-cases.md` (AI sinh, ngôn ngữ nghiệp vụ, mỗi dòng có con trỏ thực hiện). Tester chạm **2 lần/Unit**, đều đọc, đều có hạn — không gate mỗi Unit để không lặp ca 13/0.
6. **Thành công của pilot viết thành Gate R từ đầu**, sáu dòng (mục 6) — dòng quan trọng nhất: *≥3 người ngoài Team Lead có commit DEC hoặc câu trả lời*. Không có dòng đó thì gói vẫn một ghế, chỉ thêm khán giả.

---

## 1 · Sáu vai → vai trong white paper v2 → cái phải học

| Người | Vai v2 / RACI | Chạm flow ở đâu | Học gì | Lệnh |
|---|---|---|---|---|
| **PM** | Sponsor / PO | Gate A (intent-plan) · chốt phạm vi · ký Gate R mục giá trị | Đọc một trang, bấm duyệt | 0 |
| **Người dịch / APO** | Cầu nối khách; `owner:` của OQB và ASM | Trả lời câu hỏi nghiệp vụ, xác nhận giả định — tower ghi thành commit | Trả lời bằng lời trên thẻ | 0 |
| **Team Lead** | **Lead** (v2): dẫn flow, Gate D, Gate R, ranh đỏ, `specialist(tech-lead)` | Mở intent, duyệt bảng Unit, nghiệm kết quả (§9.6) | `dlc-intent` · `dlc-resume` · `dlc-tower` | 3 |
| **Dev 1, Dev 2** | Chạy bolt; **`peer` của nhau** (§4.17 "dev còn lại trong bolt" — khớp sẵn với đúng 2 dev) | Nhận HOF, chạy bolt trên nhánh Unit, review chéo | `dlc-resume` · `dlc-bolt` | 2 |
| **Tester** | Chủ tài sản kiểm thử; `specialist(qa)` khi Unit có NFR ngưỡng; ký Gate R mục testing posture | Duyệt `test-cases.md` sau Gate D · soát evidence tại Showcase · bổ sung góc nhìn | Đọc, bổ sung bằng lời | 0 |

Nguyên tắc giữ xuyên suốt: **người không cần lệnh thì không bao giờ phải mở terminal.** Muốn vậy tower phải làm được mọi hành động của bốn vai đó (mục 3).

---

## 2 · Bốn giả định "một ghế" và cách gỡ

| Giả định | Ở đâu | Vỡ thế nào | Gỡ |
|---|---|---|---|
| State trên một máy | `dlc-init` bước 4: `.gitignore .ai-dlc/` | B không thấy intent/HOF/DEC của A | `.ai-dlc/` vào git (mục 2.1); ignore phần sinh ra (`tower/`, `session/board.md`) |
| Người bấm nút là người duy nhất quyết | tower `localhost` · `inbox/*.json` | B duyệt trên máy B, agent của A không đọc được | Nút = commit + push; agent `git fetch` trước khi đọc trạng thái gate; `inbox/` chỉ còn là cache local |
| ID tuần tự không đụng | `HOF-0042`, `DEC-0053` | A và B cùng tạo `HOF-0042` trên hai nhánh | ID **theo intent + chữ cái đầu người tạo** (`HOF-0042-dt`); mỗi bản ghi = một file (đã vậy); file tổng hợp **chỉ sinh ra** |
| "Tôi" là một người | tower 6.1.0 *Cần tôi quyết* | PO, Lead, Dev cùng thấy một danh sách | `governance/raci.md` điền tên thật · trường `by:` lấy từ git user · tower lọc thẻ theo vai của người xem |

### 2.1 `.ai-dlc/` nằm đâu — phụ thuộc số repo code (câu treo #1)

| Đội có | Đặt `.ai-dlc/` ở | Commit thẳng được không | Ghi chú |
|---|---|---|---|
| **Một monorepo** | trong repo, thư mục gốc | Có, nếu bảo vệ nhánh cho phép path `.ai-dlc/**` không cần PR — GitHub rulesets làm được, GitLab push rules khó hơn | Đơn giản nhất; rủi ro: luật PR của repo code vô tình chặn commit quyết định |
| **Nhiều repo** | **repo control plane riêng** ở thư mục cha (`<team>-ai-dlc/`), repo code là thư mục con/sibling | Có — repo này **không bảo vệ nhánh** | Đúng luật 6.2.0 "một đội nhiều repo ⇒ `.ai-dlc/` ở cha"; hook tìm lên 2 cấp đã có. Khuyến nghị mặc định |

Repo control plane riêng còn có lợi thứ hai: repo code giữ nguyên luật PR/CI của khách, không phải xin đổi.

### 2.2 Cài gói cùng phiên bản

Commit `.claude/settings.json` của repo (code hoặc control plane) khai marketplace + bật `ai-dlc` — Claude Code nhắc mọi người cài đúng bản khi mở. `dlc-doctor` thêm một kiểm: version gói người chạy ≠ version ghi ở `governance/changelog.md` ⇒ WARN.

---

## 3 · Tower là cửa chính: ba loại thẻ, một cơ chế

| Thẻ | Cho ai | Hành động trên thẻ | Ghi thành | Mặc định khi im lặng quá hạn |
|---|---|---|---|---|
| **Cần tôi quyết** (đã có, 6.1.0) | PM · Team Lead | Approve / Yêu cầu chỉnh sửa / Reject | `DEC-…` + commit `by:` | Gate **không** có mặc định — gate là gate |
| **Cần tôi trả lời** (mới) | APO (và PM cho OQB, Team Lead cho OQT) | Trả lời bằng lời; chọn phương án có sẵn | `answer-…` → cập nhật OQB/OQT + ASM | Phương án "mặc định nếu im lặng" đã bắt buộc ở §4.10 → đi tiếp, ghi ASM có `owner:` |
| **Cần tôi kiểm** (mới) | Tester | Chấp nhận / bổ sung góc nhìn / trả lại `test-cases.md`; ghi nhận / trả lại evidence Showcase | `confirmed_by:` trên `test-cases.md` · RV tầng qa · `evidence/test-run-<ngày>.md` | Bản AI được dùng, ASM `owner: Tester` |

Cơ chế chung: nút → ghi file → `git commit` (author = git user người bấm) → `git push` lên nhánh chính control plane. Tower của mỗi người **poll bằng `git fetch`** (30s) thay vì mtime local. Hook sau push (CI của control repo) bắn một dòng lên Slack/Nulab: *"@<tên> · <loại thẻ> · INT-003 · hạn <giờ>"*. Tower tĩnh sinh bằng CI (GitHub/GitLab Pages nội bộ) cho ai chỉ muốn **xem**; muốn **bấm** thì chạy tower local (nút cần git credential của người bấm).

Không thay đổi luật gate: **Gate vẫn không có mặc định**. Chỉ câu hỏi và kiểm thử mới có "im lặng = mặc định" — và đây là câu treo #2 với PM/APO.

---

## 4 · Tester: hai tài sản, hai lần chạm, ba luật

### 4.1 Hai tài sản

| Tài sản | Ở đâu | Ai viết | Ai duyệt | Sống bao lâu |
|---|---|---|---|---|
| **Bảng góc nhìn kiểm thử** (test viewpoints) | `governance/test-viewpoints.md` | AI soạn lần đầu; Tester bổ sung dần; góc nhìn Tester nhắc ≥2 Unit ⇒ AI đề xuất promote | Tester | Bền vững, mọi intent |
| **Kịch bản test case** của Unit | `units/UOW-NN/test-cases.md` | AI sinh từ `user-stories.md` + bảng góc nhìn; **ngôn ngữ nghiệp vụ, cấm thuật ngữ code** (cùng luật OQB) | Tester (`confirmed_by:`) | Theo Unit |

Mỗi dòng `test-cases.md`: mã (`TC-NN`) · góc nhìn · tiền điều kiện · bước · kỳ vọng · AC tham chiếu · **cách thực hiện** (`auto` · `e2e` · `manual`) · **con trỏ thực hiện** (file test / kịch bản E2E / evidence chạy tay). Dòng không có con trỏ = dòng chưa làm, tower đếm được.

### 4.2 Hai lần chạm mỗi Unit

1. **Ngay sau Gate D, trước khi dev code**: AI sinh `test-cases.md` → thẻ *Cần tôi kiểm* → Tester chấp nhận / bổ sung / trả lại. Dev không bị chặn: quá hạn thì bản AI dùng, ASM ghi.
2. **Tại Showcase** (sản phẩm chạy được): thẻ thứ hai — Tester đọc evidence chạy thật, xem sản phẩm, ghi nhận hoặc trả lại. Bug ⇒ ESC hoặc task, không nằm trong comment.

Cố ý **không** đặt Tester thành gate mỗi Unit. Tester chạm bắt buộc ở Showcase + Gate R — trên sản phẩm, đúng tinh thần v2.

### 4.3 E2E và automation cắt thành Unit

- **Một Unit hạ tầng E2E làm sớm** (Unit 2–3 của intent đầu), khai `areas: [e2e]` trong `workspace-map.md`. Sản phẩm: khung chạy trên CI + một kịch bản smoke. Owner Tester (duyệt), dev viết, dev kia peer.
- **Sau đó mỗi Unit mang kịch bản E2E của mình** cho AC của nó, trong DoD. Tên file truy ngược về `TC-NN` — nối tiếp luật `*.uowNN.test.*`.
- Dòng `manual` mà Tester đánh dấu "lặp mỗi release" = ứng viên automation, gom thành Unit cuối intent hoặc đầu intent kế.

### 4.4 Ba luật mới — mỗi luật có trường để điền và doctor kiểm được

| Luật | Trường | Doctor |
|---|---|---|
| **Khoá file test khi fix**: agent dev đang fix Unit không sửa file test của Unit đó; muốn sửa ⇒ HOF riêng, Tester nhận | commit fix chạm `*.test.*`/kịch bản E2E của Unit | FIX (kiểm bằng diff) |
| **Test case có chủ** | `test-cases.md` frontmatter `owner:` · `confirmed_by:` hoặc ASM tương ứng | Unit `done` mà thiếu cả hai ⇒ FIX |
| **Kết quả chạy là bằng chứng, không phải lời khai** | `evidence/test-run-<ngày>.md` trỏ CI run / ảnh; KPI `units.tested` = Unit có evidence chạy thật / Unit đóng | WARN khi `units.tested` < `units.done` |

---

## 5 · Thang bậc — mỗi bậc một KPI máy đọc, và cần gói bản nào

| Bậc | Mô tả | Ai học gì | KPI chứng minh đã đạt | Cần gói |
|---|---|---|---|---|
| **0** | Một người chạy, cả đội **xem** | Không ai | tower tĩnh sinh từ control repo, ≥3 người mở | **6.x** (chỉ đổi `.gitignore` + CI sinh tower) |
| **1** | Một người chạy, người khác **duyệt/trả lời** | PM, APO, Tester: một nút | tỷ lệ DEC/answer có `by:` ≠ người tạo intent | **6.x** additive: `by:` (đọc git user), nút = commit, thẻ *trả lời*/*kiểm* |
| **2** | Nhiều người **chạy bolt** | Dev: `dlc-resume` + `dlc-bolt` | số HOF `accepted` bởi ≥2 git user khác nhau; 0 xung đột ID | **7.0.0**: ID mới, file tổng hợp chỉ sinh, nhánh/worktree per Unit |
| **3** | Nhiều intent song song | Team Lead | `intents.json` + `active-intent` | 7.0.0 (đã trong kế hoạch Atlas 4.4) |

Trình tự khuyến nghị: **bậc 0 → 1 trên 6.3.0** (không đổi luật gate, gộp với 5 việc playbook + `dlc-backlog` đã treo ở `team-target-workflow-vs-ai-dlc.md`) · **bậc 2 là lý do bump 7.0.0** — chọn phương án B (`leadership.mode`) trong `plugin-transition-plan.md` vì cùng lúc đổi luật gate và đổi format là quá nhiều cho một release có pilot đang chạy.

---

## 6 · "Thành công" của pilot — viết thành Gate R từ đầu

| # | Dòng Gate R | Đo bằng |
|---|---|---|
| 1 | Tính năng lên môi trường khách, khách xác nhận qua Showcase | DEC Gate R có `by:` PM + evidence Showcase |
| 2 | Không sự cố nghiêm trọng trong 14 ngày sau release | `risks.md` / ESC sau release |
| 3 | Mọi Unit đóng có `rv:` hoặc `self_verify:` thật | `units.reviewed` = 100% (PILOT INT-001: 0/17) |
| 4 | E2E xanh trên nhánh chính lúc release, **và lần đỏ gần nhất có bug thật đứng sau** | CI log + ESC/task trỏ tới lần đỏ |
| 5 | **≥3 người ngoài Team Lead có commit DEC hoặc câu trả lời** | `git log --author` trên control repo |
| 6 | Bug khách tìm ra sau release **không nằm trong bảng góc nhìn** | đếm; mỗi bug = một dòng mới cho `test-viewpoints.md` |

Hai KPI vận hành theo dõi suốt pilot: **trung vị giờ thẻ → commit** (tốc độ) · **số góc nhìn Tester phải bổ sung mỗi Unit** (giảm dần qua intent = bảng chung đang hoạt động; không giảm = AI không đọc bảng hoặc bảng viết không dùng được).

---

## 7 · Hai câu treo — chủ gói chốt trước khi đưa đội

| # | Câu | Quyết cái gì | Đề xuất |
|---|---|---|---|
| 1 | Đội có **mấy repo code**? | Mục 2.1: `.ai-dlc/` trong monorepo hay repo control plane riêng | Repo riêng, kể cả monorepo — tránh đụng luật PR của repo code |
| 2 | PM và APO có chấp nhận **"im lặng quá hạn = mặc định"** cho câu hỏi và test case (không áp cho gate)? | Núm tốc độ lớn nhất; cũng là chỗ dễ phản cảm với người quen mô hình phê duyệt | Có, với hạn **1 ngày làm việc** và tower hiện rõ "đã dùng mặc định" trên thẻ để rút lại được |

---

## 8 · Việc kế tiếp, theo thứ tự

1. **Chủ gói** chốt hai câu mục 7 (5 phút).
2. **Đưa đội** file này + `team-target-workflow-questions.md` trong một buổi 30 phút: mục tiêu là đội **đồng ý bảng vai (mục 1) và Gate R (mục 6)** — không bàn kỹ thuật.
3. **Chọn intent pilot** cùng đội: một tính năng nhỏ, có khách nhận, đủ để đi hết Gate R trong 2–3 tuần. Viết Gate R sáu dòng vào `intent-plan.md` **trước** khi làm gì khác.
4. **Chốt phương án 7.0.0** trong `plugin-transition-plan.md` (đề xuất B) — file này cung cấp lý do.
5. Khi đó mới sửa gói, theo lát: `.gitignore` + CI tower tĩnh (bậc 0, 1 ngày) → `by:` + nút = commit + thẻ *trả lời*/*kiểm* (bậc 1, 6.3.0) → ID mới + file tổng hợp sinh + nhánh/worktree (bậc 2, 7.0.0).

Kỷ luật vẫn áp: luật mới trong gói phải trả bằng LL của pilot này — sáu dòng Gate R chính là chỗ LL sẽ được viết ra.
