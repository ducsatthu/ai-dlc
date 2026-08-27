# AWS `aidlc-workflows` 2.0 đối chiếu với gói `ai-dlc` — và áp dụng gì vào 7.0.0

> Trạng thái: **PHÂN TÍCH + ĐỀ XUẤT — chờ chủ gói chọn** · Ngày: 2026-08-26
> Nguồn: checkout nhánh `v2` của <https://github.com/awslabs/aidlc-workflows> (HEAD `cb30d64`, 2026-08-26, `AIDLC_VERSION = 2.6.99`, README ghi "2.0 GA"), đọc toàn văn `docs/guide/`, `docs/harness-engineering/`, `docs/reference/`, `core/`, `dist/claude/`, spec PDF `assets/AI-DLC-Workflows-2.0-Specification.pdf`. Nhánh `main` của repo đó vẫn là **v1** (`aidlc-rules/` markdown, 1.0.1) — v2 chỉ sống trên nhánh `v2`, chưa có GitHub Release.
> Tài liệu chuẩn của gói mình vẫn là `whitepaper-ai-dlc-vi.md` (v2 Human-Lead). File này trả lời ba câu: *AWS v2 là gì · nó khác gói mình chỗ nào · lấy gì, bỏ gì, theo lộ trình nào.*

---

## 0 · Kết luận một trang

1. **AWS v2 không phải "phiên bản mới của white paper" mà là một engine khác hẳn**: 5 phase / 33 stage · 14 agent · 11 scope · 6 sensor · 17 hook · 87 loại audit event · 72 655 dòng TypeScript chạy bằng `bun`, phát hành cho 7 harness từ một `core/`. Cài vào Claude Code là **copy 266 file (4.9 MB) vào `.claude/` của project** — không phải plugin marketplace.
2. **Về gate, hai bên đi ngược chiều.** Spec AWS §6.4: *"non-bootstrap stages require explicit approval"* — mọi stage trừ 3 stage khởi tạo đều có gate người duyệt (scope `feature` ≈ 30 gate, `classic` ≈ 23). White paper v2 của mình rút từ PILOT: *"chờ người là đường găng"* → 1 chốt chặn thật (Gate R) + Ranh đỏ + Showcase. AWS có nới ở Construction (`Construction Autonomy Mode: autonomous` sau walking skeleton) và "Accept as-is" sau 3 vòng reject, nhưng Ideation/Inception vẫn là "duyệt markdown từng stage" — đúng cái §0 white paper mình mô tả là không chạy được (Gate D 30 Unit/113h, 17 Unit đi qua 4 điểm dừng không dừng).
3. **Về máy móc kiểm được, AWS v2 đi xa hơn mình rất nhiều** — và trúng đúng các LL của PILOT:
   - **Review receipt có fingerprint** (`REVIEW_REQUESTED`/`REVIEW_COMPLETED` do tool ghi, artifact đổi byte sau review ⇒ receipt vô hiệu, gate từ chối) → đây chính là thứ LL-002 thiếu (13 review-request / 0 verdict / 17 unit vẫn đóng).
   - **State do tool ghi, LLM bị hook chặn sửa tay** (`aidlc-state-transition-guard.ts`) → chống "18 unit `approved` tự khai", "4 unit chưa xây vẫn approved".
   - **`HUMAN_TURN` seam**: gate không đóng được nếu chưa có một lượt người thật kể từ gate trước → phiên bản deterministic của luật `previewed: true` trên tower mình.
   - **Sensor** deterministic bắn lúc ghi file / lúc mở gate (advisory hoặc blocking) → doctor của mình chạy sau; sensor chạy ngay.
   - **Diary `memory.md` per stage + learnings ritual** (Interpretations · Deviations · Tradeoffs · Open questions → người tick → ghi thành rule ở `project.md`/`team.md`) → nguồn nguyên liệu tự nhiên cho Sổ giả định `ASM` và cho vòng LL của mình.
4. **Không thể "cài AWS v2 rồi bồi luật Human-Lead lên trên"**: plugin mechanism của AWS là **additive-only** (không xoá stage, không tắt gate, `when:` chưa được evaluate), gate là quyết định của engine, không có field nào tắt được. Muốn đổi mô hình dừng là phải fork 72k dòng TS. ⇒ **Phương án "dùng AWS v2 làm lõi" bị loại.**
5. **Khuyến nghị**: giữ gói `ai-dlc` + lộ trình 7.0.0 phương án B (`leadership.mode`), **mượn 8 cơ chế máy của AWS v2** (mục 5) theo thứ tự trả nợ LL — receipt review và state-do-tool-ghi làm trước. Song song, **chạy AWS v2 nguyên bản trên một repo nhỏ ngoài PILOT** (scope `poc`/`express`, 8–10 stage, 1 ngày) để có ca đối chứng thật thay vì tranh luận trên giấy.

---

## 1 · AWS AI-DLC Workflows 2.0 là gì (tóm tắt đủ để quyết)

### 1.1 Kiến trúc

| Lớp | Nội dung |
|---|---|
| **Engine tất định** (TypeScript, `bun`) | `aidlc-orchestrate.ts` (4 lệnh `next / continue / report / park`) quyết định "bước kế tiếp" và phát **một Directive JSON** (`run-stage`, `ask`, `invoke-swarm`, `done`…). `aidlc-state.ts` sở hữu `aidlc-state.md`; `aidlc-audit.ts` sở hữu audit log; 43 tool `aidlc-*.ts`. |
| **Conductor** (LLM) | Skill `/aidlc` chỉ *thực thi* directive rồi `report` kết quả về engine. "Engine sở hữu routing; conductor sở hữu chất lượng thực thi." Hook `Stop` ép conductor không bỏ dở khi còn directive. |
| **14 agent** | 11 domain (product, design, delivery, architect, aws-platform, compliance, devsecops, developer, quality, pipeline-deploy, operations) + 2 reviewer (product-lead, architecture-reviewer) + composer. Agent **không được gọi agent khác** (`disallowedTools: Task`) — conductor là bus duy nhất. |
| **Stage = file markdown có frontmatter là graph node** | `slug · phase · execution · lead_agent · mode(inline/subagent/pipeline/mob) · reviewer · produces[] · consumes[] · requires_stage[] · sensors[] · scopes[]`; body cố định 3 mục `## Steps / ## Sensors / ## Learn`. Compile một lần thành `stage-graph.json`; artifact được consume phải có **đúng một** producer. |
| **Ba plane** | Control (stage/rules/sensors — compile lúc start) · Data (stage run, Bolt, audit) · Management (`--doctor`, ~30 check). |
| **Phát hành** | `core/` (SSOT) + `harness/<name>/manifest.ts` → `bun scripts/package.ts` sinh `dist/<harness>/`; CI drift-guard cấm sửa tay dist. |

### 1.2 Vòng đời: 5 phase · 33 stage

- **Initialization** (0.1–0.3, không gate, không LLM): scaffold · workspace-detection (greenfield/brownfield) · state-init.
- **Ideation** (1.1–1.7): intent-capture · market-research · feasibility · scope-definition · team-formation · rough-mockups · approval-handoff.
- **Inception** (2.1–2.9): reverse-engineering (brownfield, ghi `codekb/<repo>/` 9 file) · practices-discovery · requirements-analysis · user-stories (mob) · refined-mockups · domain-design · **units-generation** (DAG phụ thuộc Unit, `kind: service|spec|ui|packaging|library`) · contract-design · delivery-planning (`bolt-plan.md`).
- **Construction** (3.1–3.7): functional-design · nfr-requirements · nfr-design · infrastructure-design · **code-generation** (subagent per Unit, swarm) — chạy *per Unit*, mặc định **stage-major** (một stage cho mọi Unit rồi stage kế); build-and-test · ci-pipeline chạy một lần.
- **Operation** (4.1–4.7, đều CONDITIONAL): deployment-pipeline · environment-provisioning · deployment-execution · observability-setup · incident-response · performance-validation · feedback-optimization.
- Giữa phase có **Verification Gate tự động** (traceability check → `verification/phase-check-<phase>.md`).

### 1.3 Scope · depth · test strategy · composer

11 scope tĩnh chọn tập stage: `enterprise` 33 · `feature` 33 · `classic` 26 (bỏ Ideation, **default**) · `workshop` 26 · `mvp` 23 · `infra` 13 · `express` 10 · `refactor` 10 · `security-patch` 10 · `bugfix` 9 · `poc` 8. Depth (Minimal/Standard/Comprehensive) chỉnh độ dày artifact; test strategy (Minimal = 1 test/requirement … Comprehensive) độc lập với depth. **Composer** (`/aidlc compose "<task>"`) ước lượng 5 thành phần "implementation entropy" → *Autonomy Risk Score* (advisory) → đề xuất grid EXECUTE/SKIP, người duyệt rồi mới ghi scope custom.

### 1.4 Gate và "verifiable, self-correcting"

- **Gate chuẩn** mọi stage trừ init: `(1) Approve — Continue to <next>` / `(2) Request Changes`; vòng 3 mở `(3) Accept as-is` (archive bản hiện tại, đi tiếp). Ở Ideation/Inception có thêm `Add <skipped stage>`.
- **Reviewer agent** chạy trước gate khi stage khai `reviewer:`: class `advisory` (1 pass) hoặc `adversarial` (Construction: builder sửa → reviewer soát lại, tối đa `reviewer_max_iterations` = 2). Reviewer **không bao giờ block** — người luôn quyết; nhưng **gate từ chối mở nếu thiếu receipt** ("hard on the review happening, soft on its verdict").
- **Review receipt**: `aidlc-log.ts review` ghi SHA-256 của artifact lúc dispatch; ghi artifact sau receipt ⇒ vô hiệu; cho đúng một lần recovery, lần hai phải Request Changes. Code-generation còn bind `source-manifest.json` + git fingerprint toàn workspace.
- **Hook đổi dòng chảy** (6/17): `plan-approval-guard` (không cho spawn developer khi chưa "Approve Plan" + fingerprint khớp) · `reviewer-scope` (reviewer per-unit không đọc unit anh em) · `review-freeze` (không ai ghi `produces[]` khi receipt còn fresh) · `state-transition-guard` (cấm gọi lifecycle verb trực tiếp) · `deliver-stage-rules` (chèn rule đúng nguyên văn vào brief subagent) · `continue-workflow` (Stop hook).
- **Sensor** (6): `claim-sources` (mọi đoạn văn có tag nguồn `[Q<n>]/[memory:<id>]/[assumption]` resolve được) · `required-sections` (heading theo template) · `upstream-coverage` (artifact phải nhắc mọi `consumes`) · `traceability` (JSON) · `linter` · `type-check`. Ship đều `advisory`; từ 2.6.72 có `fire_on: gate` + `default_severity: blocking` (fail-closed, override cần người ghi `DECISION_RECORDED`).
- **`HUMAN_TURN`**: hook mint từ prompt người/AskUserQuestion; gate đòi có một `HUMAN_TURN` sau lần giải quyết gate trước.
- **Construction Autonomy ladder**: sau gate đầu Construction (walking skeleton) hỏi đúng một lần `Continue autonomously / Gate every Bolt` → ghi `Construction Autonomy Mode` vào state. Autonomous: engine gom mọi batch rồi trình **một** gate code-generation; lỗi build vẫn **halt-and-ask** (retry/skip/abort).
- **Swarm** (code-generation, autonomous): một git worktree per Unit (`.aidlc/worktrees/bolt-<slug>/`), referee `aidlc-swarm.ts` stateless: `prepare → check (test xanh + spec không bị sửa) → finalize` (re-check mọi unit claimed, đòi receipt review per unit, merge tuần tự HOLD-MERGE, không auto-resolve conflict).

### 1.5 Rule, learning loop, knowledge, workspace

- Workspace `aidlc/spaces/<space>/` (commit): `memory/{org,team,project}.md + phases/*.md` (rule, **strict-additive**, không override) · `knowledge/` (tier 2 của team) · `codekb/<repo>/` · `intents/<YYMMDD>-<label>/` (record dir: `aidlc-state.md`, `audit/<host>-<clone>.md` append-only, artifact theo `<phase>/<stage>/`, `memory.md` diary mỗi stage).
- **Learnings ritual** trước mỗi gate: `aidlc-learnings.ts surface` in nguyên văn diary → người tick → LLM check xung đột với `org.md` → `persist` ghi dòng `- <text> (learned YYYY-MM-DD) <!-- cid:… -->` vào `project.md` (mặc định) hoặc `team.md` (promote); **không bao giờ ghi org**; áp cho workflow *kế tiếp*. Learning là "verification check" thì scaffold sensor mới + gắn vào stage.
- **Practices-discovery** (2.2, hub-and-spoke, 3 spoke "mù nhau") → `team-practices.md` → affirm → promote vào `team.md`.
- Knowledge 2 tầng: tier 1 của framework (`.claude/knowledge/`, đè khi upgrade) · tier 2 của team (`aidlc/.../knowledge/aidlc-shared/` + `<agent-slug>/`, nạp nguyên văn đầu stage). DocumentKB: `/aidlc knowledge onboard|sync|…`.
- Cost ledger (Claude-only): token/USD per stage/agent/model trên `STAGE_COMPLETED`, statusline `↑in ↓out $usd`.

### 1.6 Điều kiện vận hành (ràng buộc thật)

- `bun` bắt buộc trên PATH của shell non-interactive (máy này đã có 1.3.14).
- `settings.json` ship chạy **AWS Bedrock** (`CLAUDE_CODE_USE_BEDROCK=1`, pin Opus 4.8 `[1m]`, effort `xhigh`) — đổi được qua `settings.local.json`. README: "works better with Claude Opus 4.8… weaker models may skip reviewer pass, learnings ritual or rush approval gates".
- Toàn bộ prose tiếng Anh; agent `aws-platform`, MCP `aws-*` gắn AWS.
- Cài project-level `.claude/` (đè `.claude/settings.json`, `hooks`, `agents` của project) — không cài chung được với plugin khác có hook `Stop`/`PreToolUse` mà không merge tay.
- Roadmap tự khai còn dở: cyclic flow (chỉ Build&Test→CodeGen), traceability, stage-level rules, `when:` trên stage, Bolt chưa là runtime boundary, không có "verifier dùng LLM khác".

---

## 2 · Ánh xạ thuật ngữ và cơ chế

| Khái niệm | AWS v2 | Gói `ai-dlc` 6.1 (v1) | White paper v2 Human-Lead |
|---|---|---|---|
| Lần chạy vòng đời | `intent` = record dir `intents/<YYMMDD>-<label>/` | `INT-NNN` | giữ |
| Đơn vị việc | Unit of work + DAG `depends_on`, `kind` | `UOW-NN` + `releasable`/`session_fit` | giữ |
| Bolt | **lát kế hoạch** trong `bolt-plan.md` — engine *không* dùng để chạy | **vòng chạy** 4 chặng có dấu vết | giữ |
| Trạng thái | `aidlc-state.md` do tool ghi, hook cấm sửa tay | `status.md` do orchestrator (LLM) ghi | — |
| Nhật ký | `audit/` 87 event append-only | `comms/MSG`, `session/log/SES`, `decisions-log` | thêm `CP` |
| Điểm dừng người | gate *mọi* stage (≈30) + Accept-as-is vòng 3 | Gate A–G (7) + preview bắt buộc | `CP` không chờ · Mốc chờ `wait_until` · `SC` Showcase · Gate R · `RED` |
| Nới tự động | `Construction Autonomy Mode: autonomous` (chỉ Construction) | không | `leadership.mode: lead` (toàn flow) |
| Review | reviewer agent + **receipt fingerprint**, review-freeze | `RV-NNN` viết tay, §4.12 `rv:` phải tồn tại | tầng `none/peer/specialist` giữ |
| Bằng chứng người đã xem | `HUMAN_TURN` (hook) | `previewed: true` (tower) | giữ cho Gate R/RED |
| Kiểm máy | 6 sensor lúc ghi/lúc gate | `dlc-doctor` chạy sau, chỉ đọc | doctor thêm 6 kiểm ASM/Showcase |
| Câu hỏi/giả định | `<stage>-questions.md` (A–E + Other), sensor `claim-sources` tag `[assumption]` | `open-questions-business/tech.md`, §4.10.9 "đã soát nguồn nào" | **`ASM` ledger** với `default_if_silent`, `reversal_cost` |
| Học | diary `memory.md` → learnings ritual → `project.md`/`team.md` | `LL-NNN` qua Gate G → `overrides/` → contribute PR | LL là Mốc chờ, patch gói vẫn cần Lead ký |
| Brownfield | reverse-engineering → `codekb/` (9 file), sensor `upstream-coverage` | intent-plan §2 Source Reading Plan + `source-ledger.md` **No-unread-source** | giữ |
| Tuỳ biến | memory additive, plugin additive-only, `when:` chưa chạy | `overrides/` 3 lớp thắng gói, `pinned/` per intent | giữ |
| Song song | worktree per Unit + referee merge tuần tự | teammate/sub-agent, HOF, tin chết (RV-019/020) | giữ |
| Dashboard | statusline + `--status` + `--doctor --export` | Control Tower LIVE, decision-first | Bản tin ca + "Cần tôi quyết" |
| Chi phí | ledger USD per stage/agent | không | KPI §IX chưa có cost |

Điểm đáng chú ý: **AWS v2 không có "No-unread-source"** — `reverse-engineering` đọc theo scanner + `upstream-coverage` chỉ kiểm artifact có *nhắc tới* nguồn, không kiểm nguồn đã đọc hết. Đây là chỗ gói mình chặt hơn và nên giữ.

---

## 3 · Ba cách "áp dụng v2" — đánh giá

### 3.1 Cài AWS v2 nguyên bản cho PILOT, bỏ gói `ai-dlc`

| | |
|---|---|
| Làm gì | `cp -r dist/claude/.claude/ + dist/claude/aidlc/` vào PILOT, `settings.local.json` bỏ Bedrock, scope `classic` hoặc `feature`, Construction `autonomous`. |
| Được | engine + test suite (443 test) đã có; receipt/freeze/guard chạy ngay; audit 87 event; swarm worktree; cost ledger. |
| Mất | Control Tower tiếng Việt (Lead không dùng terminal) · HOF/heartbeat/`result_check` · No-unread-source · override/pinned per intent · toàn bộ LL-001..003 đã biến thành luật trong gói · tiếng Việt. |
| Điểm chết | **Gate mỗi stage** ở Ideation/Inception là mô hình §0 white paper mình đã bác bằng dữ liệu PILOT; không tắt được (mục 1.6). INT-003 đang stage 6 với layout `.ai-dlc/` không migrate được sang `aidlc/spaces/` (khác hoàn toàn). |
| Kết luận | **Không** cho PILOT. Chỉ hợp cho repo mới, đội nói tiếng Anh, chấp nhận duyệt từng stage. |

### 3.2 Dùng AWS v2 làm lõi, bồi Human-Lead lên bằng plugin/memory của AWS

Đã kiểm trực tiếp trong `docs/reference/18-plugin-mechanism.md` và `harness-engineering/`: contribution seam chỉ **set-union** `produces/consumes/sensors/scopes` và splice fragment vào `## Steps`; *"Additive only — invariant"*; không xoá stage, không đổi `lead_agent`, không tắt gate; `when:` parsed nhưng chưa evaluate; memory là strict-additive (không `overrides:`). Nới gate duy nhất là `autonomous` (Construction) và `review_cap: none`. ⇒ Mô hình `CP`/Mốc chờ/`ASM default_if_silent` **không biểu diễn được** mà không sửa `aidlc-orchestrate.ts` (6 514 dòng) — tức là fork và tự gánh 72k dòng TS + drift với upstream đang ra 2–5 bản/ngày (2.6.44→2.6.99 trong 5 ngày). **Loại.**

### 3.3 Giữ gói `ai-dlc`, mượn cơ chế máy của AWS v2 vào 7.0.0 (**khuyến nghị**)

Giữ: phương pháp (white paper v2 Human-Lead), layout `.ai-dlc/`, tower, HOF, override/pinned, tiếng Việt, plugin marketplace thật. Mượn: những gì làm cho luật **kiểm được bằng máy** — đúng nguyên tắc #9 "luật không kiểm được là luật sẽ trượt". Chi tiết ở mục 5. Đây cũng là câu trả lời cho mục 4 của transition plan ("7.0.0 nợ một LL"): mượn cơ chế nào thì phải nêu LL/KPI nào nó trả.

---

## 4 · Hai mô hình dừng — so bằng số, không bằng cảm tính

| | AWS v2 `feature` | AWS v2 `classic` + autonomous | Gói 6.1 (v1) | White paper v2 |
|---|---|---|---|---|
| Gate người trên một intent 30 Unit | ≈30 (mỗi stage; design stage gate một lần sau Unit cuối) | ≈20 (bỏ Ideation; Construction gom một gate) | 7 gate + E(a)/E(b) per Unit ⇒ 7 + 2×30 = **67** điểm dừng khai báo (17/30 đi qua không dừng — LL-002) | `CP-01` chờ đích + Mốc chờ thứ tự Unit + 30 Showcase (không chặn) + 1 Gate R/Unit hoặc 1/Intent |
| Cái người phải đọc ở gate | markdown artifact của stage | markdown artifact | gate_doc toàn văn (preview bắt buộc) | Showcase Pack ≤10 bước; hồ sơ Gate R 9 mục |
| Im lặng thì sao | flow đứng, `--doctor` cảnh báo gate >24h | flow đứng | flow đứng | `default_if_silent` áp sau `wait_until` (trừ Gate R/RED) |
| Máy kiểm trước gate | reviewer + receipt + sensor gate-fired + artifact guard + HUMAN_TURN | như trái | UI chặn approve mù; server kiểm `previewed` | + doctor 6 kiểm ASM |

Cả hai bên đồng ý một điểm mà spec AWS gọi là nguyên tắc 7 — *autonomy theo "safe increments", nới dần khi Compartment 2 (How do we know it's right) được máy hoá* — và white paper mình gọi là *"chỉ dừng khi đảo ngược đắt"*. Khác nhau ở **điểm xuất phát**: AWS xuất phát từ dừng-mọi-nơi rồi nới; mình xuất phát từ chạy-mặc-định rồi chốt chặn ở cuối. Dữ liệu PILOT (17 Unit đi qua 4 điểm dừng không dừng) là bằng chứng rằng dừng-mọi-nơi *trên giấy* không có nghĩa là dừng thật; AWS trả lời chính rủi ro đó bằng receipt/freeze/guard chứ không bằng thêm gate — và đó là phần đáng mượn.

---

## 5 · Mượn gì vào 7.0.0 — theo thứ tự trả nợ LL

Mỗi dòng: cơ chế AWS → hình dạng trong gói mình → LL/KPI nó trả → cỡ việc. Ngôn ngữ thực thi giữ **Python** (gói đang là Python, không thêm `bun` làm prerequisite cho người dùng gói).

| # | Cơ chế AWS v2 | Trong gói `ai-dlc` 7.0.0 | Trả nợ | Cỡ |
|---|---|---|---|---|
| **1** | Review receipt + fingerprint + review-freeze | Script `dlc_review.py request\|verdict` ghi `RV-NNN` **kèm SHA-256 của target lúc request**; `rv:` trên Unit chỉ hợp lệ khi verdict có, fingerprint khớp bản hiện tại; sửa target sau verdict ⇒ `rv` `stale`, doctor FIX, tower thẻ "cần soát lại". Hook PreToolUse chặn Write/Edit vào target khi review đang mở (`status: requested`). | **LL-002** (13 request / 0 verdict), KPI `units.reviewed` | 1 ngày |
| **2** | State do tool ghi + `state-transition-guard` | `dlc_state.py` là **nơi duy nhất** ghi `status.md` (`gates_passed`, `gate_open`, `stage`) và `units/UOW-NN/spec.md#status`; hook PreToolUse chặn Edit/Write trực tiếp vào hai chỗ đó (fail-open như `gate_guard.py`, tắt `AI_DLC_GUARD=off`). Orchestrator/skill gọi script thay vì sửa file. | LL-002 (unit `approved` tự khai, 4 unit chưa xây vẫn `approved`), LL-003 (`done` không evidence) | 1–2 ngày |
| **3** | `HUMAN_TURN` seam | `dlc_state.py gate close` từ chối nếu không có bản ghi người thật (`inbox/gate-*.json` với `previewed: true`, hoặc dòng `human_turn:` do hook `UserPromptSubmit` ghi vào `session/log/`) sau lần mở gate. Gate R/RED bắt buộc; `CP` không cần. | §2.1 preview thành luật máy ở cả CLI, không chỉ tower | 0.5 ngày |
| **4** | Sensor lúc ghi (advisory) | Chuyển 3 kiểm đọc-file của doctor thành **PostToolUse Write/Edit** trên `.ai-dlc/**`: `required-sections` (heading theo `templates/*.md` — đã có sẵn 24 template) · `claim-sources` = §4.10.9 `sources_checked` + §4.11 số trên tower truy được · `upstream-coverage` = unit-plan phải nhắc mọi nguồn `read` trong `source-ledger.md`. Kết quả ghi `evidence/sensors/<file>-<ts>.md`, tower gom vào Bản tin ca, **không chặn**. Doctor giữ vai kiểm sau. | LL-001 (hỏi thứ có sẵn), §4.11 (tower khai `5.0.0` chết hai bản major) | 1–2 ngày |
| **5** | Diary `memory.md` + learnings `surface` | Mỗi HOF/Bolt có `diary.md` 4 heading (Diễn giải · Lệch khỏi kế hoạch · Đánh đổi · Câu hỏi mở). `dlc-showcase` và `dlc-retro` chạy `dlc_learnings.py surface` in nguyên văn: **"Câu hỏi mở" → ứng viên `ASM`** (điền `default_if_silent`), **"Lệch"/"Đánh đổi" → ứng viên `LL`**. Người tick; không tick thì không thành gì. Không ghi rule tự động (giữ luật LL qua Gate G/Mốc chờ). | Nguyên liệu cho Sổ giả định §III và KPI `asm.*`; LL không còn phải "nhớ lại" ở retro | 1 ngày |
| **6** | `Construction Autonomy Mode` ladder | Chính là `governance/leadership.md` `mode: lead\|gatekeeper` của phương án B, nhưng lấy thêm hai ý: (a) ghi mode **vào `status.md` của từng intent** (pinned, không đổi giữa chừng) — AWS làm y hệt; (b) hỏi mode **đúng một lần** ở `CP-01` (sau khi đích được xác nhận), không hỏi ở `dlc-init`. | Transition plan §1 B, §3 INT-003 pin `gatekeeper` | 0.5 ngày (thuộc B) |
| **7** | Stage frontmatter `produces/consumes` + single producer + artifact guard | Mỗi skill `dlc-*` khai `produces:`/`consumes:` trong frontmatter SKILL.md; `dlc_state.py stage done` từ chối khi thiếu file `produces`; `workspace-map.md` chỉ còn khai code roots, đường dẫn artifact suy từ graph. Doctor 1d ("artifact tồn tại") đọc graph thay vì hard-code. | LL-003 (14/18 unit không bolt, 0 evidence), §4.12–4.14 | 1 ngày |
| **8** | Worktree per Unit + merge tuần tự | Tuỳ chọn cho Bolt song song: `dlc-bolt --worktree` tạo `.ai-dlc/worktrees/BOLT-NN/`, merge khi `result_check: pass`; conflict ⇒ `ESC`. Không referee riêng — bolt-coordinator giữ. | §9.5 teammate (RV-019/020) — cô lập file thay vì cô lập phiên | 1 ngày, làm sau |

Cộng: ≈7–9 ngày, chồng lên 4–5 ngày của phương án B. #1–#3 làm trước và **không phụ thuộc** việc chọn A/B/C — chúng chỉ làm luật đang có (§4.12, §2.1) thành luật máy.

**Không mượn** (có lý do):
- 33 stage / gate mỗi stage — ngược white paper §0.
- Reviewer agent bắt buộc trước gate — 6.0.0 đã gỡ Review Board vì LL-002; tầng `none/peer/specialist` §4.17 giữ. Receipt (#1) áp cho tầng `peer/specialist`, `self_verify` giữ cho `none`.
- Rule strict-additive không override — `overrides/` 3 lớp của mình cần override thật (dự án chịu quy định).
- `bun`/TypeScript — gói Python, người dùng gói không phải cài thêm runtime.
- Composer/ARS — `intent-plan.md` Provisional Unit Map + `sizing.md` đã đóng vai đó; ARS là advisory và priors do AWS chọn.
- Agent `aws-platform`, MCP `aws-*`, Bedrock pin.
- Learnings tự ghi thành rule sau khi tick — giữ kỷ luật LL qua Gate G/Mốc chờ + patch gói cần Lead ký (white paper §XI).

---

## 6 · Ca đối chứng rẻ: chạy AWS v2 nguyên bản một lần

Trước khi bỏ 7–9 ngày, nên có **số đo thật** thay vì so trên giấy — đúng §4.15 "phép đo phải có ca đối chứng".

- Chọn một repo nhỏ **ngoài PILOT** (ví dụ một repo phụ mới hoặc một feature nhỏ của repo khác), scope `express` (10 stage) hoặc `poc` (8 stage); `settings.local.json` tắt Bedrock, dùng model hiện có.
- Đo và ghi vào `docs/`: số gate người phải bấm · phút người đọc mỗi gate · số lần reviewer trả NOT-READY và có sửa thật không · số receipt bị stale · sensor bắn/pass/fail · USD từ ledger · learnings ritual có sinh rule dùng được không.
- Đối chiếu với cùng feature chạy bằng gói 6.1 (hoặc INT-004 ở mode `lead`) bằng bảng KPI §IX của white paper.
- Cỡ: 1 ngày. Kết quả là ca đối chứng cho CHANGELOG 7.0.0 và là dữ liệu trả nợ LL mà mục 4 transition plan đang treo.

---

## 7 · Việc cần chủ gói chốt (bổ sung vào mục 5 của transition plan)

1. Xác nhận **loại phương án 3.1/3.2** (thay gói bằng AWS v2, hoặc fork lõi AWS) — hay muốn thử 3.1 trên repo mới?
2. Duyệt danh sách mượn ở mục 5 — đặc biệt #1–#3 làm **trước** khi chọn A/B/C, vì không đổi luật.
3. Có chạy ca đối chứng mục 6 không, và trên repo nào.
4. Giữ Python cho engine gói, hay chấp nhận `bun` để copy thẳng một số tool AWS (`aidlc-log.ts review`, sensor `required-sections`) — MIT-0, copy được về license.

---

## Phụ lục · Con số kiểm được từ checkout

| | |
|---|---|
| Nhánh / commit | `v2` · `cb30d64` · 2026-08-26 · `AIDLC_VERSION 2.6.99` |
| `dist/claude/` | 266 file · 4.9 MB · `.claude/`: 14 agent, 18 hook, 58 tool (72 655 dòng TS), 43 skill, 59 knowledge, 6 sensor, 11 scope, 42 file `aidlc-common` (conductor + 8 protocol + 33 stage) |
| Test | 443 file `t*.test.ts`: smoke 14 · unit 245 · integration 109 · e2e 75 |
| Runtime | `bun` (máy này 1.3.14); tuỳ chọn `uv` (MCP AWS), git, eslint/tsc |
| License | MIT-0 |
| Nhánh `main` | v1: `aidlc-rules/` markdown, `VERSION 1.0.1` (2026-06-30), 3 phase Inception/Construction/Operations |
