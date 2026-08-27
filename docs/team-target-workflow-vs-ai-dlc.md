# Workflow đích của team (Intent · Plan · Execution · Verify) đối chiếu với gói `ai-dlc`

> Trạng thái: **PHÂN TÍCH + ĐỀ XUẤT — chờ chủ gói chọn** · Ngày: 2026-08-27
> Nguồn: `docs/techtus-aidlc-workflow-viewer.html` (Excalidraw 8703×6369, team vẽ 2026-08-27 sáng) — 4 pha × 5 lane (Product Design (BA) & APM · AI agents Claude Code & Codex · Engineer · Backlog · Sources/Git) · 16 bước · 20 mũi tên có số · cây thư mục `/workspace`.
> Ba bản đối chiếu trước: AWS engine (`aws-aidlc-workflows-v2-vs-ai-dlc.md`), playbook Anthropic (`anthropic-ai-native-sdlc-playbook-vs-ai-dlc.md`), Phase Atlas của team (`workspace-knowledge-model-from-team-atlas.md`, đã chốt 6/6, ra 6.2.0). File này trả lời: *team định chạy thế nào · gói hiện chạy được bao nhiêu phần · phải thêm gì để chạy đúng — và chỗ nào workflow đích nên sửa trước khi đóng vào gói.*

---

## 0 · Kết luận một trang

1. **Workflow đích là thiết kế thứ ba, và là thiết kế gần v2 nhất từ trước tới nay.** Team tự rút từ 7 gate (v1) / ~30 gate (AWS) xuống **3 gate người**: Gate 1 *Intent approval* · Gate 2 *Plan — duyệt unit trước execution* · Gate 3 *Integrated Outcome approval* (đọc evidence + **tự dùng thử trên hệ thống**). Gate 3 chính là "phản hồi trên sản phẩm chạy được" của white paper §IV–§V. Bugfix/refactor duyệt Intent + Plan **một lần** tại Gate 1 — đúng quyết định `intent.kind` đã chốt hôm nay.
2. **Cái gói hoàn toàn chưa có: Backlog (Nulab) là hệ thống ghi nhận.** 7 điểm chạm: Story sinh từ `intent.md` (feature/infra) · child issue dưới Story cha (bugfix/refactor, hỏi key `TSD-142` → `TSD-158`) · task theo Work Unit · comment evidence · đổi trạng thái resolved/closed · mọi commit prefix `[TSD-158]` · **Preview → Confirm → Publish** cho mọi lần ghi ra Backlog. Câu cuối là **Ranh đỏ #5** (gửi thông tin ra ngoài đội) đã có hình dạng — team nghĩ ra trước khi gói kịp đặt tên.
3. **Ba luật ngầm đáng đưa thẳng vào gói**: (a) *tự sửa tối đa 3 lần rồi dừng* (halting condition — gói chưa có trần) · (b) *"một lựa chọn không được chọn thì không phải là loại trừ"* + câu trả lời thành entry `[ans:A1]` trong `## Sources` — chính là Sổ giả định `ASM` viết gọn · (c) *"chỉ nạp unit đó, làm trong đúng contract"* — §10 ngân sách context, nay thành luật của execution.
4. **Bốn chỗ workflow đích nên sửa trước khi đóng vào gói** (mục 3): Gate 3 đặt **sau mọi unit** ⇒ Lead nhìn sản phẩm muộn — nên tách Showcase per unit (không chặn) + Gate 3 = Gate R · *Agents Gate security/quality* (bước 13) chạy **sau** Gate 3 người — playbook và §4.17 đều đặt máy **trước** người · không có ranh đỏ production/migration (workflow dừng ở merge PR) · assumptions không có "mặc định nếu im lặng".
5. **Từ vựng và lệnh**: `/aidlc start <business outcome>`, `intent.md`, `plan.md`, Work Unit, `codekb STALE`, `[ans:A1]` là từ vựng AWS v2; nhưng 3 gate + Backlog + Codex là của team. Gói `ai-dlc` chạy được **~60%** workflow này bằng lệnh hiện có (bảng mục 5); phần thiếu là Backlog, `kind`, trần 3 lần, Gate 3 gộp, và **đa harness (Codex)** — gói chỉ có Claude Code. **Câu hỏi mở số 1** (mục 6): team định chạy trên gói `ai-dlc`, trên AWS v2, hay viết plugin `/aidlc` mới? Ba câu trả lời cho ba lộ trình khác nhau; file này giả định **gói `ai-dlc` là engine** và liệt kê phải thêm gì.

---

## 1 · Workflow đích nói gì

### 1.1 Bốn pha · 16 bước (theo số mũi tên 1→20)

| Pha | # | Bước | Lane | Artefact / hành động | Điểm dừng |
|---|---|---|---|---|---|
| **Intent** | 01 | Human states outcome — `/aidlc start <business outcome>`; *nói outcome, không cần viết sẵn spec* | BA & APM | — | |
| | 02 | AI chọn scope · soạn `intent.md` — đọc `memory · knowledge · codekb`; xác nhận scope (feature · bugfix · refactor · infra); outcome, in/out of scope, bảng `AC-*`; **mỗi dòng mang tag chỉ về nguồn** | AI | `intent.md` | |
| | 03 | Trả lời câu hỏi làm rõ — câu trả lời thành entry `[ans:A1]` trong `## Sources`; *"một lựa chọn không được chọn thì không phải là loại trừ"* | BA & APM | `intent.md ## Sources` | |
| | 04 | **Gate 1 · Intent approval** — kiểm outcome, scope, sources, assumptions, AC; **bugfix/refactor: duyệt cả Intent + Plan tại đây** | BA & APM | | ■ |
| | 05a | (feature/infra) AI draft `intent.md` — *Intent approved AND Backlog Story synchronized nếu Backlog enabled*; **Preview Story → Confirm → Publish Story** | AI | | ◇ confirm |
| | 06a | Backlog Story được tạo sau khi Intent duyệt — story detail with AC | Backlog | Story | |
| | 05b | (bugfix/refactor) AI hỏi **parent Story key** (`TSD-142`); verify tồn tại qua Backlog MCP; ghi `Backlog: child:TSD-142` vào `intent.md`; Preview child → Confirm → Publish child; nếu AI không có câu hỏi backlog ⇒ đi thẳng sang Plan | AI ↔ BA | | ◇ confirm |
| | 06b | Tạo **1 child issue** dưới Story cha (`TSD-158` ← 1 issue cho cả change); *Work Units chỉ sống trong `plan.md`; mọi commit dùng `[TSD-158]`* | Backlog | child issue | |
| **Plan** | 05 | Engineer start break plan — get story/intent/backlog, sources, docs (*pull documents*) | Engineer | | |
| | 06 | AI soạn `plan.md` | AI | `plan.md` | |
| | 07 | AI chia thành **Work Units** — role, owner, dependency, AC, verification, **halting condition** | AI | `plan.md` | |
| | 08 | **Gate 2 · Plan — duyệt unit trước execution**; Preview Units → Confirm → Publish Units | Engineer | | ■ |
| | 09 | Backlog task units create | Backlog | tasks | |
| **Execution** | 10 | Human work với AI start execution — dùng plugin chạy **từng unit hoặc danh sách unit**, self-verify, sửa tối đa ba lần | Engineer | | |
| | 11 | **Execution UNIT** — *chỉ nạp unit đó, làm trong đúng contract, chạy check đã khai, tự sửa tối đa ba lần*; code đi vào `sources/` ↔ **Loop Verify follow AC** (agents loop verify) — khung *max 3 times* | AI | code + evidence | |
| | — | Commit & Create pull request · Teams review & merge PR | Git | PR | (người review PR) |
| | 12 | **Gate 3 · Integrated Outcome approval** — review evidence markdown & self-testing kết quả AI sinh ra; **self testing trên outcome hệ thống**; Preview Outcome comment → Confirm → Publish comment | Engineer | | ■ |
| | 15 | Update backlog — comment evidence testing | Backlog | comment | |
| | 13 | **Agents Gate security, Quality** — agents loop verify các *agents gate plugins*; fail ⇒ *Back to fix security & quality* (quay lại 11) | AI | | máy |
| **Verify** | 14 | Verify Evidence & Update to finish Intent — **after merge**: propose/reconcile accepted knowledge + ADR · **Human accepts memory changes, if any** · **mark affected codekb STALE** | AI → Engineer | `memory/` `knowledge/` `codekb/` | ◇ accept |
| | 15' | Confirm close-out publication | Engineer | | |
| | 16 | Close Instant backlog — comment + status resolved/closed | Backlog | | |

(Số bước trong hình trùng: hai "05", hai "11", hai "15" — bảng gọi theo tên.)

### 1.2 Cây thư mục `/workspace`

```
/workspace
├── /docs
│   ├── /intents            # specs (feature, infra), bugfix, refactor
│   ├── /memory (rule)      # /rules: team rule, technical rule · /phases: phase rule implement
│   ├── /knowledge          # /business · /documentkb (index convert) · /documents (raw từ khách, backlog export) · /technical
│   └── /codekb             # /backend · /infra — component inventory, dependencies, technology-stack, architect
└── /sources                # /backend (source code) · /infra (IaC)
```

Hai điểm khác Atlas tuần trước: mọi thứ nằm **trong `/docs` nhìn thấy được**, không phải `.ai-dlc/` ẩn; `codekb` chia theo **code area** (`backend`, `infra`), không theo repo. Dự án ví dụ không có frontend (backend + IaC).

### 1.3 Ba luật ngầm (không có hộp riêng, nhưng lặp ở nhiều bước)

| Luật | Ở đâu | Gói đã có? |
|---|---|---|
| **Preview → Confirm → Publish** cho mọi lần ghi ra Backlog (05a, 05b, 08, 12) | 4 lần | Không có Backlog; nhưng cơ chế *preview bắt buộc rồi mới bấm* đã có ở tower (§2.1) |
| **Tự sửa tối đa 3 lần** rồi dừng (10, 11, khung *max 3 times*) — *halting condition* khai trong Work Unit | 3 lần | **Chưa có trần**; AWS `reviewer_max_iterations: 2`; §1.0c chỉ có "năm trạng thái" |
| **Tag nguồn trên mỗi dòng** + `[ans:A1]` + *"không chọn ≠ loại trừ"* | 02, 03 | §4.8 ledger + §4.10 open questions; chưa có tag inline; `ASM` (v2) có `default_if_silent` — team chưa có |

---

## 2 · Ánh xạ thuật ngữ

| Team | Gói 6.2.0 | White paper v2 | Ghi chú |
|---|---|---|---|
| `/aidlc start <business outcome>` | `/ai-dlc:dlc-intent "<yêu cầu>"` | như gói | một lệnh, không cần spec — trùng |
| "AI chọn scope (feature · bugfix · refactor · infra)" | — | `intent.kind` (quyết định #3, 7.0.0) | team đặt **AI chọn, người xác nhận ở Gate 1** — hợp lý hơn "người khai" |
| `intent.md` (outcome · in/out · `AC-*` · `## Sources` · assumptions) | `intent-plan.md` phần 1 + 2 (Source Reading Plan) | `CP-01` | team **không có** Provisional Unit Map ở Intent — phần 3 dời sang `plan.md`. Chấp nhận được: v2 chỉ chờ *đích* ở `CP-01` |
| `[ans:A1]` trong `## Sources` | bảng *Đã trả lời* của `open-questions-*.md` (§4.10) | `ASM` | team gọn hơn; thiếu `default_if_silent` và `reversal_cost` |
| Gate 1 · Intent approval | Gate A | `CP-01` Mốc chờ (chỉ đích) | team đọc cả sources/assumptions/AC — nặng hơn v2, nhẹ hơn v1 (không unit map) |
| `plan.md` + Work Unit (role · owner · dependency · AC · verification · halting condition) | `unit-plan.md` + `UOW-NN/spec.md` (`releasable` · `session_fit` · `areas` · `review`) + Bolt | như gói | team **không có Bolt** (Domain → Logical → Code); Work Unit đi thẳng code. Thiếu `releasable`/`session_fit`; có `owner`/`verification`/`halting` gói chưa có |
| Gate 2 · Plan, duyệt unit trước execution | Gate D | Mốc chờ *thứ tự Unit* | team giữ **chặn cứng** — giống AWS Plan Approval hơn v2 |
| Execution UNIT "chỉ nạp unit đó" · Loop verify AC · max 3 | HOF `read_first` (§9, §10) · `self_verify` (§4.15) | Team Agreement nội bộ | trần 3 lần là mới |
| Commit & PR · Teams review & merge | `rv:` tầng `peer` (§4.17) | như gói | team dùng **PR review của đội** làm peer — trùng playbook #7 |
| Gate 3 · Integrated Outcome approval (evidence + tự dùng thử) | Gate E(b) demo + Gate F UAT | **Showcase `SC` + Gate R** gộp | xem mục 3 |
| Agents Gate security, Quality (13) | `specialist(security\|qa)` theo trigger §4.17 · hook | Gate R mục 4–5 | team: máy chạy **sau** người |
| 14 propose/reconcile knowledge + ADR · human accepts memory · codekb STALE | `LL` qua Gate G · 6.2.0 `codekb/` promote + freshness | LL Mốc chờ · `codekb` | team "mark STALE khi merge" — 6.2.0 kiểm HEAD lúc intent kế, tương đương nhưng **muộn hơn**; thêm cờ STALE lúc merge là rẻ |
| Backlog Story / child / task / comment / close | **không có** | Ranh đỏ #5 cho mọi ghi ra ngoài | mục 4 |
| `/docs/{intents,memory,knowledge,codekb}` + `/sources` | `.ai-dlc/{context-memory,governance,codekb}` + `workspace-map` `areas` | như gói | `memory` = `governance`; `knowledge` 4 ngăn = 4.2 file Atlas (đổi tên ngăn theo team); `sources/` = `areas` |
| AI agents "Claude Code & Codex" | chỉ Claude Code | — | **gói không chạy trên Codex**; AWS v2 có dist cho 7 harness |

---

## 3 · Điểm dừng — team 3 gate so với v1 và v2, và bốn chỗ nên sửa

| | v1 (gói 6.x) | **Workflow đích của team** | White paper v2 |
|---|---|---|---|
| Đích | Gate A (intent-plan 3 phần) | **Gate 1** (intent.md: outcome · scope · sources · assumptions · AC) | `CP-01` Mốc chờ, chỉ đích |
| AS-IS / câu hỏi | Gate B · Gate C | — (câu hỏi làm rõ ở bước 03, không gate) | `CP` · `ASM` |
| Unit | Gate D | **Gate 2** (chặn cứng trước execution) | Mốc chờ thứ tự Unit |
| Design / code | Gate E(a) · E(b) per Unit | — (PR review của đội; AI loop max 3) | Team Agreement · Showcase `SC` per Unit |
| Trước release | Gate F | **Gate 3** Integrated Outcome (evidence + tự dùng) | **Gate R** 9 mục |
| Máy kiểm | doctor sau | Agents Gate security/quality (sau Gate 3) | trigger specialist (trước) · doctor |
| Học | Gate G | bước 14 "human accepts memory changes" | LL Mốc chờ |
| Ranh đỏ | escalation | — | 9 dòng `RED` |
| Bẻ lái | — | — | `STR` mọi lúc |

**Đồng hướng v2** ở ba chỗ lớn: bỏ gate AS-IS/câu hỏi · bỏ gate design per Unit · Gate cuối là "tự dùng thử trên hệ thống". Bốn chỗ nên sửa **trước** khi gói đóng luật theo:

1. **Gate 3 sau mọi unit ⇒ Lead nhìn sản phẩm lần đầu khi đã xong hết.** Đây đúng ca §0 white paper (Gate E(b) INT-001: 17 unit đi qua không dừng). Đề xuất: giữ Gate 3 là **Gate R** (ký một lần, 9 mục, tự dùng thử), nhưng thêm **Showcase per unit không chặn** ngay sau "Loop verify AC" — mỗi unit xong ra một `SC-NN` (≤10 bước bấm + giả định đang hiện hình), Lead phản hồi `FB` khi rảnh; Gate 3 chỉ mở khi mọi `FB đổi/làm lại` đã đóng. Không thêm gate, thêm **điểm nhìn**.
2. **Agents Gate security/quality (13) chạy sau Gate 3 người.** Người vừa ký xong thì máy bắt quay lại sửa ⇒ chữ ký vô hiệu, phải ký lại. Playbook: máy review trước, người "judge intent + risk" sau; §4.17: specialist theo trigger chạy trong Bolt. Đề xuất đảo 13 lên **trước** 12, và gắn vào tầng review (`none/peer/specialist`) thay vì chạy mọi unit như nhau.
3. **Không có ranh đỏ.** Workflow kết thúc ở merge PR + close backlog; deploy/migration/public API không xuất hiện. Nếu dự án đích chỉ merge (deploy do pipeline khác), vẫn cần **Ranh đỏ #2 (migration phá huỷ) · #3 (public API) · #5 (ghi ra Backlog — đã có Preview→Confirm→Publish)** — red-line guard 6.3 (playbook #1) phủ được.
4. **Assumptions không có "mặc định nếu im lặng" và chi phí đảo.** `[ans:A1]` chỉ ghi câu trả lời đã có; câu chưa trả lời thì đứng chờ ở Gate 1. Đề xuất: mỗi assumption trong `intent.md` = một `ASM` gọn 4 trường (giả định · mặc định nếu im lặng · đảo lại tốn bao nhiêu · nhìn thấy ở đâu) — chính bước 03 nhưng không chặn khi chưa có người trả lời.

---

## 4 · Backlog — thứ gói phải thêm, và luật đi kèm

Team dùng **Backlog (Nulab)** làm hệ thống ghi nhận cho PM/khách, `intent.md`/`plan.md` là bản làm việc — đúng cấu hình "**linkage tối thiểu**" của playbook (record ID ↔ commit SHA): Story/issue key trong `intent.md`, `[TSD-158]` trên mọi commit, Work Unit **không** sync ngược (chỉ sống trong `plan.md`), evidence sync bằng comment.

| Điểm chạm | Team | Trong gói (đề xuất `dlc-backlog`, 6.3.0 hoặc 7.0.0) |
|---|---|---|
| Bật/tắt | "nếu Backlog enabled" | `governance/backlog.md`: `enabled` · `mcp` (tên MCP server) · `project_key` (`TSD`) · `story_type` · `task_type` · `link_mode: linkage` |
| feature/infra → Story | 05a/06a, sau Gate 1 | `dlc-intent` sau DEC Gate A (7.0.0: sau `CP-01`): dựng **preview** Story từ `intent-plan.md` phần 1 (outcome + AC) → thẻ *Cần tôi quyết* trên tower (◇ confirm) → publish qua MCP → ghi `backlog: story:TSD-NNN` vào `status.md` |
| bugfix/refactor → child issue | 05b/06b, hỏi key cha | `dlc-intent --kind bugfix`: hỏi **một câu** "Story cha?" → verify qua MCP → preview child → confirm → publish → `backlog: child:TSD-158 (parent TSD-142)` |
| Work Unit → task | 09, sau Gate 2 | `dlc-units` sau Gate D: preview N task (tên Unit + AC) → confirm **một lần cho cả bảng** → publish; `spec.md` thêm `backlog: task:TSD-NNN`. Có thể tắt (`sync_units: false`) — team ghi "Work Units chỉ sống trong plan.md" cho bugfix, có task cho feature |
| Evidence → comment | 15, sau Gate 3 | `dlc-accept` sau Gate F/R: preview comment (link evidence, kết quả tự dùng thử) → confirm → publish |
| Close | 16 | `dlc-accept` stage 8: đổi status resolved/closed — **ranh đỏ #5**, cần DEC (chính là chữ ký Gate R) |
| Commit prefix | `[TSD-158]` | hook PostToolUse/`git commit` guard (6.3 red-line guard) WARN khi commit trong intent có `backlog:` mà message thiếu key |
| Preview → Confirm → Publish | 4 lần | **một cơ chế**: mọi ghi ra Backlog đi qua `inbox/` như gate — server chỉ xếp hàng, orchestrator publish sau khi thấy `confirmed`. Không có đường "AI tự publish" |

Luật máy: `dlc-doctor` FIX khi `status.md` có `backlog:` mà MCP không tìm thấy key; WARN khi Backlog `enabled` mà intent không có key sau Gate 1. KPI: `backlog.synced/intents`, `backlog.publish_without_confirm` = 0.

Điều **không** làm: sync ngược từ Backlog vào `intent.md` (SoT của intent là repo); sync Bolt/HOF/RV (nội bộ đội AI); để AI tự đóng issue.

---

## 5 · Gói chạy được bao nhiêu phần — và thêm gì

| Bước team | Gói 6.2.0 chạy được bằng | Thiếu | Bản |
|---|---|---|---|
| 01–02 `/aidlc start`, AI chọn scope | `dlc-intent` (intent-analyst + source-planner đọc `codekb/` từ 6.2.0) | AI **đề xuất `kind`**, người xác nhận ở Gate 1 | 7.0.0 (`kind`) |
| 02 tag nguồn mỗi dòng | §4.8 ledger, `sources:` per Unit | tag inline `[S3]`/`[ans:A1]` trong intent + sensor kiểm tag resolve được (AWS #4 `claim-sources`) | 6.3 |
| 03 câu hỏi làm rõ, `[ans:A1]`, "không chọn ≠ loại trừ" | §4.10 open-questions (đã có *phương án chọn sẵn* + *nếu im lặng*) | ghi thẳng vào `intent.md ## Sources` thay file riêng; `ASM` 4 trường | 7.0.0 (`ASM`) |
| 04 Gate 1; bugfix/refactor duyệt cả Plan | Gate A trên tower (preview bắt buộc) | route `kind`: bugfix gộp A+D | 7.0.0 |
| 05a/05b/06a/06b/09/15/16 Backlog | — | `dlc-backlog` + `governance/backlog.md` + MCP (mục 4) | **6.3.0** (không đổi gate) hoặc 7.0.0 |
| 05–07 `plan.md`, Work Unit có role/owner/dependency/AC/verification/halting | `dlc-units` → `unit-plan.md` + `spec.md` | `spec.md` thêm `owner:` · `verification:` (lệnh/đích định lượng — playbook "Proof") · `halting_condition:` · núm `max_self_fix: 3` trong `governance/sizing.md` | 6.3 (additive) |
| 08 Gate 2 | Gate D | — | có |
| 10–11 chạy từng unit / danh sách unit, chỉ nạp unit đó, loop verify AC max 3 | `dlc-bolt UOW-NN` + HOF `read_first` + `self_verify` | `dlc-bolt --units UOW-01,UOW-03` (danh sách) · bolt-coordinator đếm vòng sửa, **dừng ở 3** → `ESC` (§4.13) thay vì sửa tiếp · agent `dlc-verifier` tươi context (playbook #3) | 6.3 |
| Commit & PR, đội review | tầng `peer` §4.17 | `peer` = PR review của đội có receipt (AWS #1) — quyết định #3 file playbook | 7.0.0 |
| 12 Gate 3 evidence + tự dùng thử | Gate E(b)+F | Showcase Pack per unit (không chặn) + Gate R 9 mục có mục "Lead đã tự dùng" | 7.0.0 (`dlc-showcase`, `dlc-release`) |
| 13 Agents gate security/quality, loop back | `specialist(security\|qa)` theo trigger · checklists | REVIEW.md passes (playbook #7) · **chạy trước Gate 3** | 6.3 (review.md) |
| 14 propose knowledge/ADR, human accepts memory, codekb STALE | LL → Gate G · 6.2.0 promote codekb · ADR trong Bolt | `retro/candidates.md` từ `repeat_of` (playbook #5) · cờ `STALE` ngay khi merge chạm `areas_scanned` (thêm vào `dlc-accept` stage 8 — 5 dòng) | 6.3 |
| 15' close-out publication | `dlc-accept` publish docs theo `workspace-map docs:` | — | có |
| `/docs/…` nhìn thấy được thay `.ai-dlc/` | `.ai-dlc/` + publish sang `docs:` | tuỳ chọn `AI_DLC_DIR=docs/aidlc` (hook/script đọc env; mặc định `.ai-dlc`) — hoặc giữ `.ai-dlc/` và chỉ publish | 6.3 (nhỏ) — **cần chốt** |
| `knowledge/{business,documentkb,documents,technical}` | Atlas 4.2 đề xuất `shared/by-role/documents` | đổi tên ngăn theo team: `business/ technical/ documents/` (bỏ `documentkb` — không có engine ingest; `dlc-doctor` chỉ index) | 7.0.0 |
| Codex | — | gói chỉ Claude Code; Codex chạy được phần **đọc file** (`.ai-dlc/`, HOF, protocol là markdown) nhưng không có hook/skill/tower | **cần chốt** |

Ước lượng: 6.3.0 (Backlog · `max_self_fix` · Work Unit fields · `--units` · verifier · STALE-on-merge · tag sensor · review.md) ≈ 5–6 ngày, cộng 5 việc playbook đã treo ≈ 4–5 ngày; 7.0.0 giữ nguyên phương án B.

---

## 6 · Việc cần chủ gói chốt

1. **Engine**: team chạy workflow này trên **gói `ai-dlc`** (file này giả định), trên **AWS aidlc-workflows v2** (`/aidlc` là lệnh của họ; 3 gate không biểu diễn được — file AWS §3.2), hay **viết plugin `/aidlc` mới** theo đúng hình? Câu này quyết mọi câu sau.
2. **Gate 3**: giữ gộp (một lần cuối) hay tách **Showcase per unit không chặn + Gate R** (mục 3.1)? Khuyến nghị tách — đây là bài học đắt nhất của PILOT.
3. **Bước 13** (agents gate) đảo lên **trước** Gate 3? Khuyến nghị có.
4. **Backlog**: MCP server nào cho Nulab Backlog (có sẵn hay tự dựng)? Sync Work Unit → task cho mọi `kind` hay chỉ feature? Ai là người bấm *Confirm* — BA/APM (Story) và Engineer (Units/comment) như lane trong hình?
5. **`.ai-dlc/` hay `docs/aidlc/`**: giữ ẩn + publish, hay cho phép đổi thư mục qua env? Khuyến nghị giữ `.ai-dlc/` (hook/tower/doctor đều hard-code; đổi là major) và publish `intents/`, `codekb/` sang `docs/` ở stage 8 như hiện tại.
6. **Codex**: có cần gói chạy trên Codex không? Nếu có, đó là lý do duy nhất đủ nặng để cân nhắc lại câu 1.
7. **Ranh đỏ**: dự án đích có deploy/migration trong phạm vi đội AI không? Không thì red-line guard chỉ cần #2/#3/#5.

---

## Phụ lục · Workflow đích viết lại bằng từ của gói (nếu chọn engine = `ai-dlc`, sau 6.3 + 7.0.0)

```
/ai-dlc:dlc-intent "<outcome>"          # 01–02: AI đề xuất kind + intent-plan phần 1–2, tag nguồn, ASM gọn
  → CP-01 (Mốc chờ: đích)               # 04 Gate 1 — bugfix/refactor: CP-01 gộp thứ tự Unit
  → dlc-backlog story|child (preview → confirm trên tower → publish)     # 05a/05b/06a/06b
/ai-dlc:dlc-discover · dlc-validate     # codekb CURRENT ⇒ reuse; câu hỏi → ASM, không chặn
/ai-dlc:dlc-units                       # 06–07 plan: Unit có areas · owner · verification · halting · max_self_fix
  → CP (Mốc chờ: thứ tự Unit)           # 08 Gate 2
  → dlc-backlog tasks (confirm một lần)                                   # 09
/ai-dlc:dlc-bolt --units UOW-01,UOW-02  # 10–11: chỉ nạp unit đó, loop verify AC ≤ 3, verifier tươi context
  → specialist/peer theo trigger + review.md (máy TRƯỚC người)            # 13
  → dlc-showcase SC-NN (không chặn, Lead FB khi rảnh)                     # điểm nhìn mới
/ai-dlc:dlc-release                     # 12 Gate 3 = Gate R: evidence + Lead tự dùng + rollback + ledger ASM
  → dlc-backlog comment (confirm) · close (DEC = chữ ký Gate R)           # 15, 16
/ai-dlc:dlc-retro                       # 14: LL Mốc chờ, promote codekb + STALE các area chạm, publish docs/
```
