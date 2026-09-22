# Kế hoạch gói `ai-dlc` 7.0.0 — lớp chính sách + tower TRÊN engine AWS `aidlc-workflows` v2 (phương án A)

> Trạng thái: **ĐỀ XUẤT — chờ chủ gói chốt 6 câu ở §7** · Ngày: 2026-09-22
> Thay cho §1–§4 của `plugin-transition-plan.md` (file đó tự tuyên bố là lịch sử từ 2026-09-03 và hứa "kế hoạch mới viết ở file riêng" — đây là file đó). Phần kiến trúc gói cũ (override 3 lớp, semver, contribute) vẫn đúng.
> Căn cứ: `multi-user-shared-space.md` §2.1b (A đã chốt) · `spikes/aws-v2-cross-clone-approval.md` · `plugin/references/aws-v2-workspace.md` · `aws-aidlc-workflows-v2-vs-ai-dlc.md` (đối chiếu engine — **viết trên 2.6.99, template đội pin 2.5.75**, xem §7 câu 4) · `whitepaper-ai-dlc-vi.md` (SSOT v2) · kiểm kê gói 2026-09-22 (16 agent · 16 skill · 3 hook · 7 script · 8 checklist · 27 template).
> Kỷ luật: file này **không thêm luật gate**. Mỗi lát ở §6 ghi rõ nó là *máy móc* (không cần LL) hay *luật* (phải trả bằng LL của pilot đội, hoặc gỡ).

---

## 0 · Kết luận một trang

1. **Dưới phương án A, gói không còn là engine.** Engine AWS v2 đã có 33 stage, `produces/consumes`, audit per clone, review receipt + fingerprint, worktree/swarm, doctor ~30 check. Gói `ai-dlc` chỉ còn **ba việc engine không làm**:
   - **(a) Cửa cho người không gõ lệnh** — tower ba loại thẻ (*quyết · trả lời · kiểm*) theo vai, nút = commit của đúng người (RACI), im lặng quá hạn = mặc định có ghi ASM. Engine chỉ kiểm *có người bấm*, không kiểm *ai*.
   - **(b) Luật v2 Human-Lead mà engine thiếu** — Sổ giả định `default_if_silent` · Gate R hồ sơ (6 dòng pilot / 9 mục white paper) · ranh đỏ có danh sách · Tester `test-viewpoints` + `test-cases` · No-unread-source · Unit `releasable`/`session_fit`.
   - **(c) Vòng học LL → luật gói qua Lead ký.** Engine có learnings ritual nhưng *tick xong tự thành rule, chỉ cộng thêm không override* — không mượn; retro của gói giữ.
2. **12/16 agent và 8/16 skill của gói bị stage AWS thay thế** (§3). Không gỡ ngay: PILOT INT-003 đang stage 6 với 30 Unit trên engine `ai-dlc`. **Đóng băng** engine `ai-dlc` ở 7.0.0 (chỉ sửa lỗi, không thêm), **gỡ ở 8.0.0** sau khi INT-003 đóng và retro trả LL.
3. **Phần "luật" của gói độc lập engine** — §4.8 · §4.9 · §4.12–§4.17 · §9.6 · LL. Chỉ đường dẫn artefact gắn `.ai-dlc/context-memory/`. 7.0.0 = tách luật khỏi đường dẫn: luật đọc state qua `layout.py`, viết vào chỗ engine cho phép (§4).
4. **Gate mọi stage của engine là khoảng cách gói KHÔNG đóng được ở 7.0.0** — plugin của engine chỉ additive, `when:` chưa được evaluate, không tắt được gate. Gói không sửa `aidlc-orchestrate.ts`. Cách hạ chi phí duy nhất: scope nhỏ (`classic` 26 / `poc` 8 stage) + tower làm mỗi gate rẻ (một nút, một commit). Phải **chốt chấp nhận** (§7 câu 1) và ghi thành ASM của chính gói, không né.
5. **Toàn bộ luật v2 chưa có dòng nào trong `agents/` hay `skills/`** (grep Gate R · ranh đỏ · Showcase · ASM · im lặng=mặc định · test-viewpoints = 0). Chúng chỉ sống trong `docs/`. 7.0.0 là lần đầu chúng thành code — và vì chưa có LL, chúng vào ở mức **WARN/đề xuất**, không chặn.
6. **Lộ trình bốn lát** (§6): 6.3.0 đóng *Unreleased* (máy móc, ½ ngày) → 7.0.0-a doctor/status/resume/init trên aws-v2 + `tests/` cho gói (máy móc) → 7.0.0-b ASM timeout · Tester assets · Gate R thẻ · red-line guard (luật, mức WARN) → 7.0.0 phát hành khi đội mở intent pilot đầu tiên → 8.0.0 gỡ engine cũ sau LL.

---

## 1 · Đề bài: "lớp chính sách" nghĩa là gì, và không phải gì

| Gói LÀ | Gói KHÔNG LÀ |
|---|---|
| Tower đọc `aidlc-state.md` + `audit/*.md`, sinh thẻ theo vai người xem | Engine chạy stage (đó là `aidlc-orchestrate.ts`) |
| Script quyết định = commit đúng người, kiểm RACI | Reviewer agent (engine đã có reviewer per stage) |
| Doctor đối chiếu luật gói với dấu vết engine | Sửa template / vendor của đội |
| Governance của đội: RACI · test-viewpoints · sizing · red-lines · LL | Nơi lưu artefact stage (đó là record dir của engine) |
| Retro: audit + diary → LL → Lead ký → patch gói/`team.md` | Learnings tự thành rule |

Nguyên tắc vận hành giữ nguyên từ `aws-v2-workspace.md`: **không sửa template**, mọi đường dẫn ghi vào audit **tương đối**, lifecycle chỉ qua `report`.

---

## 2 · Engine có gì, thiếu gì → gói cung cấp bằng gì

Nguồn: báo cáo đối chiếu 2026-09-22 trên `aws-aidlc-workflows-v2-vs-ai-dlc.md` + `aws-v2-workspace.md` + `whitepaper-ai-dlc-vi.md` §II–§IX.

| Khái niệm v2 | Engine AWS v2 | Gói 7.0.0 cung cấp | Lát | Loại |
|---|---|---|---|---|
| Mốc `CP` không chờ | **KHÔNG** — mọi stage gate, im lặng ⇒ flow đứng | **Không đóng được.** Chấp nhận; ghi `ASM-PKG-01` của gói. Giảm đau: tower thẻ một nút + scope nhỏ | — | chốt §7.1 |
| Mốc chờ + ASM `default_if_silent` | **KHÔNG** — nhưng có nguyên liệu: `<stage>-questions.md`, `aidlc-log.ts answer`, tag `[assumption]` | `scripts/asm_timeout.py`: câu hỏi quá hạn (từ `governance/sizing.md`) ⇒ ghi answer qua `aidlc-log.ts answer` với tiền tố `[assumed-by-timeout · phương án tốt nhất theo AI · ai lẽ ra trả lời · hạn · cách rút lại]`; tower thẻ *đã dùng mặc định* rút lại được. **Không áp cho gate** (chỉ `[?]` do người) | 7.0.0-b | luật (đã chốt 03/09, chưa LL) |
| Showcase `SC` | **KHÔNG** — chỗ người đọc ở gate là markdown | **Không làm ở 7.0.0** — engine không có chỗ treo sản phẩm chạy được. Gần nhất: gate 3.6 build-and-test có link preview do dev ghi tay. Ghi ASM | — | chốt §7.5 |
| Gate R | MỘT PHẦN — gate + reviewer + receipt + HUMAN_TURN | `scripts/gate_r_pack.py`: dựng hồ sơ 6 dòng (multi-user §6) từ audit/CI/`test-viewpoints` khi stage `4.3 deployment-execution` (hoặc stage cuối của scope) vào `[?]`; thẻ *quyết* của stage đó **hiện hồ sơ toàn văn**, không chỉ tên stage | 7.0.0-b | luật (Gate R 6 dòng đã chốt, chưa LL) |
| Ranh đỏ `RED` | MỘT PHẦN — build fail halt-and-ask; deploy là gate | `hooks/red_line_guard.py` (PreToolUse `Bash`): chặn `DROP|TRUNCATE|DELETE` không WHERE · deploy prod · `gh pr`/gửi ra ngoài khi không có `governance/red-lines.md` cho phép; **không chặn code**. Mức WARN tới khi có LL | 7.0.0-b | luật (playbook #1, chưa LL) |
| Bẻ lái `STR` | KHÔNG — chỉ Request Changes tại gate, `park` | Không làm. Bẻ lái = Request Changes tại gate kế + `park`. Ghi ASM | — | bỏ |
| Bản tin ca | MỘT PHẦN — statusline, `--status`, `--doctor --export` | `session_brief.py` nhánh aws-v2: một trang từ audit 24h (gate mở · quyết định đã ghi · mặc định đã áp · thẻ quá hạn) | 7.0.0-a | máy móc |
| Tester `test-viewpoints` / `test-cases` | KHÔNG | `governance/test-viewpoints.md` (template) + tower thẻ *kiểm* cho Tester ở stage 3.6; `test-cases.md` per unit do dev sinh dưới record dir Construction | 7.0.0-b | luật (multi-user §4, chưa LL) |
| LL / retro | MỘT PHẦN — diary → learnings tự thành rule | `dlc-retro` đọc `memory.md` diary + audit thay `comms/`; LL vẫn qua Lead ký; patch vào `team.md ## Mandated` (sinh) | 7.0.0-b | giữ luật cũ |
| No-unread-source | KHÔNG — gần nhất sensor `upstream-coverage` | Doctor gói: stage 2.1 reverse-engineering phải có `source-ledger.md` không còn `planned` (WARN) | 7.0.0-b | luật cũ §4.8 |
| Unit `releasable` / `session_fit` | MỘT PHẦN — DAG `depends_on`, `kind` | Doctor gói: units của stage 2.7 thiếu hai trường ⇒ WARN | 7.0.0-b | luật cũ §4.9 |
| RACI ai ký | KHÔNG — `GATE_APPROVED` không có actor | **ĐÃ CÓ**: `tower_approve.ts` + `governance/raci.md` + `HUMAN_TURN` có `Actor` | 6.3.0 | máy móc |
| Review tầng §4.17 | engine có reviewer agent per stage (không tắt) | Tầng chỉ còn dùng để quyết **người** nào nhận thẻ *kiểm* (RACI cột `kiểm`) | 7.0.0-a | thu hẹp luật |
| HOF / heartbeat §9.4 / nghiệm kết quả §9.6 | engine có Directive + audit + swarm referee | **Không áp** trên aws-v2 — không có HOF. Giữ cho engine `ai-dlc` (đóng băng) | — | chỉ engine cũ |

---

## 3 · Số phận từng thành phần gói

Ký hiệu: **GIỮ** = chạy trên cả hai engine · **ĐÓNG BĂNG** = chỉ engine `ai-dlc`, sửa lỗi không thêm, gỡ 8.0.0 · **CHUYỂN** = nội dung sống tiếp ở chỗ khác · **GỠ** = không có việc trên aws-v2 (vẫn đóng băng cho ai-dlc tới 8.0.0).

### 3.1 Agents (16)

| Agent | Stage AWS thay thế | Số phận | Phần luật mang đi đâu |
|---|---|---|---|
| `dlc-orchestrator` | `aidlc-orchestrate.ts` | ĐÓNG BĂNG | không có "trưởng ca" trên aws-v2; bản tin = script |
| `dlc-intent-analyst` | 1.1 intent-capture · 1.4 scope-definition | GỠ | outcome đo được → gợi ý trong thẻ quyết stage 1.1 |
| `dlc-source-planner` · `dlc-context-archaeologist` | 2.1 reverse-engineering (+ codekb của engine) | GỠ | No-unread-source → doctor WARN trên `source-ledger.md` |
| `dlc-context-validator` | 2.3 requirements + `<stage>-questions.md` | CHUYỂN | "Nếu im lặng" + "đã soát nguồn" → format answer của `asm_timeout.py` |
| `dlc-unit-planner` | 2.7 units-generation · 2.9 delivery-planning | GỠ | `releasable`/`session_fit` → doctor WARN |
| `dlc-bolt-coordinator` · `dlc-be-dev` · `dlc-fe-dev` | 3.1–3.5 per unit + swarm/worktree | GỠ | checklist BE/FE/tech-lead → `team.md ## Mandated` (§3.4) |
| `dlc-acceptance-recorder` | 3.6 build-and-test · 4.x · codekb engine | CHUYỂN | Gate R hồ sơ → `gate_r_pack.py` |
| `dlc-retro-keeper` | learnings ritual (không mượn) | **GIỮ** — đổi nguồn đọc | LL qua Lead ký |
| `dlc-ba-reviewer` · `dlc-pm-po-reviewer` · `dlc-qa-reviewer` · `dlc-security-reviewer` · `dlc-tech-lead-reviewer` | reviewer per stage của engine | GỠ | trigger specialist → cột `kiểm` RACI |

Kết quả trên aws-v2: **1 agent** (`retro-keeper`). Có thể thêm 0 agent — mọi việc khác là script.

### 3.2 Skills (16 → 9 trên aws-v2)

| Skill | Số phận | Ghi chú 7.0.0 |
|---|---|---|
| `dlc-init` | **GIỮ** | nhánh aws-v2 đầy đủ: `raci` · `test-viewpoints` · `sizing` · `red-lines` · `.gitignore .ai-dlc/tower/` · kiểm `upstream-lock.json` khớp bản gói hỗ trợ |
| `dlc-tower` | **GIỮ** | đã tự rẽ theo engine |
| `dlc-status` · `dlc-resume` · `dlc-doctor` | **GIỮ** — viết nhánh aws-v2 | đọc `aidlc-state.md` + audit qua `layout.py`; doctor kiểm bảng §2 |
| `dlc-retro` | **GIỮ** | nguồn: diary + audit |
| `dlc-contribute` | **GIỮ** | không đổi |
| `dlc-brief` (mới) | thêm | bản tin ca một trang; `dlc-resume` in nó đầu tiên |
| `dlc-ledger` (mới) | thêm | xem/lọc ASM (câu hỏi đã dùng mặc định), rút lại |
| `dlc-intent` · `dlc-discover` · `dlc-validate` · `dlc-units` · `dlc-bolt` · `dlc-accept` · `dlc-revise` · `dlc-tasks` | GỠ (aws-v2) / ĐÓNG BĂNG (ai-dlc) | engine: `/aidlc` + Request Changes tại gate |
| `dlc-map` | GỠ (aws-v2) / ĐÓNG BĂNG | engine: `repos.json` + `discoverSiblingRepos` |

Trên aws-v2, skill gọi khi engine ở stage nào thì **không chặn** engine; skill của gói chỉ đọc và ghi vào chỗ §4.

### 3.3 Hooks · scripts

| Thành phần | Số phận |
|---|---|
| `session_start.sh` | GIỮ — nhánh aws-v2 in bản tin ca thay banner |
| `gate_guard.py` | ĐÓNG BĂNG (chỉ engine ai-dlc, đã fail-open nơi khác) |
| `aws_v2_write_receipt.ts` | GIỮ |
| `red_line_guard.py` (mới, PreToolUse `Bash`) | thêm 7.0.0-b, WARN |
| `layout.py` / `layout.ts` | GIỮ — resolver duy nhất |
| `tower_aws_v2.py` · `tower_approve.ts` | GIỮ |
| `tower_generate.py` · `tower_serve.py` | ĐÓNG BĂNG (đã chuyển tiếp sang aws-v2) |
| `session_brief.py` | GIỮ — nhánh aws-v2 |
| `asm_timeout.py` · `gate_r_pack.py` · `doctor_aws_v2.py` (mới) | thêm 7.0.0-a/b |

### 3.4 Checklists (8) · templates (27)

- **Checklist**: `backend` · `frontend` · `tech-lead` · `security` → CHUYỂN thành mục trong `team.md ## Mandated` (sinh từ `.ai-dlc/governance/checklists/`, engine đọc additive — đây là cách duy nhất luật gói tới được agent của engine). `ba` · `pm-po` · `qa` · `source-plan` → ĐÓNG BĂNG.
- **Template GIỮ**: `ai-dlc.config.json` · `raci` · `sizing` · `OVERRIDES`. **Mới**: `test-viewpoints` · `red-lines` · `asm` (format answer) · `gate-r`. **ĐÓNG BĂNG**: 23 template còn lại (intent-plan, unit-plan, handoff, …).

### 3.5 `references/protocol.md` (818 dòng)

Tách hai: `protocol.md` giữ nguyên cho engine ai-dlc (đóng băng) · **`policy.md` mới ≤ 200 dòng** cho aws-v2: §4.8 · §4.9 · §4.15 · §4.17 (thu hẹp) · Gate R · ranh đỏ · ASM timeout · Tester · LL · RACI · bản tin. Mỗi mục **một trường để điền + một KPI** (§IX white paper), không có mục nào thiếu KPI.

---

## 4 · Gói đặt gì ở đâu trong workspace AWS v2

| Thứ | Chỗ | Ai commit | Engine thấy? |
|---|---|---|---|
| Governance của gói: `raci.md` · `test-viewpoints.md` · `sizing.md` · `red-lines.md` · `checklists/` · `lessons-learned/` | `<workspace>/.ai-dlc/governance/` | đội | không (đã loại khỏi sibling discovery) — đúng ý: đây là luật *người*, engine không cần |
| Luật engine phải đọc (checklist BE/FE, DoD) | `aidlc/spaces/<space>/memory/team.md` mục `## Mandated` — **sinh** từ governance bằng `dlc-init --sync-mandated`, có dấu `<!-- ai-dlc:generated -->`, cấm sửa tay | đội (qua lệnh) | có, additive theo thứ tự org → team → project → phase |
| Sensor/produces bổ sung (nếu cần) | `sources/aidlc-integration/plugins/ai-dlc/` | đội | có, additive — **không dùng để tắt gate** |
| Tower | `<workspace>/.ai-dlc/tower/` — gitignore | máy bất kỳ | không |
| Artefact gói per intent (ASM answer, Gate R pack, test-cases) | **chưa chốt** — xem §7 câu 3. Hai lựa chọn: (i) trong record dir `aidlc/spaces/<space>/intents/<id>/` cạnh artefact engine (receipt hook ghi được, nhưng có thể đụng guard `produces`) · (ii) `.ai-dlc/intents/<id>/` mirror (an toàn, nhưng hai chỗ) | | |
| Đường dẫn trong audit | luôn tương đối | | |

---

## 5 · Engine `ai-dlc` cũ: đóng băng thế nào

- `plugin.json` 7.0.0 mô tả: *"engine `ai-dlc` ở chế độ bảo trì cho dự án đang chạy; dự án mới dùng engine aws-v2"*. `dlc-init` trên thư mục trống **không tạo** `.ai-dlc/context-memory/` nữa nếu không có `engine: ai-dlc` tường minh trong config (§7 câu 2).
- INT-003 (PILOT) chạy tiếp tới stage 8 không đổi gì; retro INT-003 phải trả `LL-004` (nợ 4.1.0) và LL cho tầng review (nợ 6.0.0).
- 8.0.0: gỡ 12 agent · 8 skill · `gate_guard` · `tower_generate/serve` · 23 template · `protocol.md` → `archive/`. `MIGRATION.md` 8.0.0 chỉ có một dòng: "dự án còn `.ai-dlc/context-memory/` thì ở lại 7.x".

---

## 6 · Lộ trình lát — mỗi lát ghi loại và nợ

| Lát | Nội dung | Loại | Nợ LL / KPI | Cỡ |
|---|---|---|---|---|
| **6.3.0** | Đóng *Unreleased* nguyên trạng: receipt hook · `tower_approve` · `tower_aws_v2` · RACI · layout resolver. `MIGRATION.md`: không có gì phải làm (fail-open). Đổi `CHANGELOG` "nợ LL như 5.0.0/6.0.0/6.2.0" thành một dòng nợ tổng ở đầu file | máy móc | không (chỉ chạy khi engine aws-v2, dự án cũ không đổi) | ½ ngày |
| **7.0.0-a** | `tests/` cho gói (pytest: layout 14 ca · gate_guard · tower_generate trên `.ai-dlc/` mẫu · tower_aws_v2 + tower_approve dry-run trên workspace mẫu · receipt hook) · `dlc-doctor`/`dlc-status`/`dlc-resume`/`session_brief` nhánh aws-v2 · `dlc-init` aws-v2 đầy đủ + `--sync-mandated` · `policy.md` | máy móc + tách luật cũ | KPI máy đọc: `tower.median_hours_card_to_commit` · `handoff` → thay bằng `gate.open_over_24h` | 3–4 ngày |
| **7.0.0-b** | `asm_timeout.py` + `dlc-ledger` · `test-viewpoints` + thẻ *kiểm* Tester · `gate_r_pack.py` + thẻ Gate R toàn văn · `red_line_guard.py` (WARN) · `dlc-retro` đọc diary/audit · doctor WARN §4.8/§4.9 | **luật mới, chưa LL** ⇒ mọi thứ mức WARN/đề xuất, không chặn | KPI §IX: `asm.total/high` · `asm.overridden_after_release` · `red.count` · `gate_r.hold_rate`; multi-user §6 dòng 5 (≥3 người ngoài Lead có commit) | 3–4 ngày |
| **7.0.0** | Phát hành khi đội mở intent pilot đầu tiên trên workspace của họ (multi-user §8 bước 2–3 là việc của người, gói không thúc được). `MIGRATION.md` 7.0.0: engine ai-dlc đóng băng, config mẫu | — | Gate R sáu dòng viết vào intent-plan của pilot **trước** khi làm gì | — |
| **8.0.0** | Gỡ engine ai-dlc sau INT-003 đóng + retro LL; nâng WARN của 7.0.0-b lên FIX **chỉ mục nào có LL** | luật | LL-004 + LL của pilot đội | sau pilot |

Không làm ở bất kỳ lát nào: `dlc-backlog` · `dlc-showcase` · `dlc-steer` · `leadership.mode` (đều thuộc thế giới engine ai-dlc, xem `plugin-transition-plan.md` §2 — lịch sử).

---

## 7 · Câu chủ gói cần chốt (mỗi câu có mặc định nếu im lặng)

| # | Câu | Phương án + giá | Mặc định nếu im lặng |
|---|---|---|---|
| 1 | **Chấp nhận gate mọi stage của engine** ở 7.0.0, ghi thành `ASM-PKG-01` "khoảng cách với white paper §II không đóng được, giảm đau bằng scope nhỏ + tower"? | Có: đi được ngay · Không: phải fork engine hoặc quay về B của multi-user §2.1b (mất máy móc AWS) | **Có** |
| 2 | Engine `ai-dlc` ở 7.0.0: **đóng băng** (gỡ 8.0.0) hay **gỡ ngay** (INT-003 ở lại 6.3.0)? | Đóng băng: code hai nhánh thêm một chu kỳ, nhưng INT-003 retro được bằng gói hiện hành · Gỡ ngay: gói gọn, INT-003 kẹt ở 6.3.0 | **Đóng băng** |
| 3 | Artefact gói per intent đặt trong **record dir engine** hay **`.ai-dlc/intents/<id>/`**? | Record dir: một chỗ, cần spike guard `produces` · Mirror: an toàn, hai chỗ | **Spike ½ ngày trước, mặc định record dir nếu guard cho qua** |
| 4 | Gói target bản engine nào: **pin 2.5.75** (bản đội vendor) hay 2.6.99 (bản đã đối chiếu)? | 2.5.75: đúng thực tế, phải kiểm lại tính năng ghi trong `aws-aidlc-workflows-v2-vs-ai-dlc.md` (sensor blocking từ 2.6.72 chưa có) · 2.6.99: đội phải vendor lại | **2.5.75**; `dlc-init` đọc `upstream-lock.json` và WARN nếu khác bản gói đã thử |
| 5 | Showcase: **bỏ ở 7.0.0** (ghi ASM) hay ép vào gate 3.6 bằng link preview tay? | Bỏ: trung thực, mất điểm nhìn của v2 · Ép: có thứ để nhìn nhưng không phải Showcase Pack | **Bỏ**, ghi `ASM-PKG-02` |
| 6 | `tests/` cho gói là **điều kiện** của 7.0.0-a hay việc song song? | Điều kiện: chậm 1–2 ngày, mọi lát sau rẻ · Song song: nhanh nhưng lát b sửa tay lại | **Điều kiện** |

Hạn: 2026-09-29. Quá hạn ⇒ áp mặc định, ghi vào `CHANGELOG` *Unreleased* dòng "chốt theo mặc định vì im lặng quá hạn" — đúng luật gói tự đặt.

---

## 8 · Việc phải sửa ở tài liệu khác khi file này được chốt

- `plugin-transition-plan.md`: thêm dòng đầu "§1–§4 lịch sử; kế hoạch hiện hành: `plugin-7-policy-layer-plan.md`".
- `aws-aidlc-workflows-v2-vs-ai-dlc.md` §3 và §5: đánh dấu "khuyến nghị giữ gói làm engine đã bị quyết định A (03/09) thay; 8 cơ chế mượn nay có sẵn vì gói chạy trên engine". Ghi chú bản 2.6.99 ≠ 2.5.75.
- `whitepaper-ai-dlc-vi.md` §XII: bảng ánh xạ sang gói viết cho engine ai-dlc — thêm một dòng trỏ sang file này cho engine aws-v2. Không sửa §II–§XI.
- `CLAUDE.md` bảng `docs/`: thêm file này.
- `MIGRATION.md`: mục 7.0.0 theo §5.
