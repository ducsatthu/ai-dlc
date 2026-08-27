# Anthropic "AI-Native SDLC playbook" đối chiếu với gói `ai-dlc` — và áp dụng gì vào 6.x / 7.0.0

> Trạng thái: **PHÂN TÍCH + ĐỀ XUẤT — chờ chủ gói chọn** · Ngày: 2026-08-27
> Nguồn: <https://claude.com/blog/the-ai-native-sdlc-playbook> (Louis Claxton, Applied AI · 2026-08-21 · 46 phút đọc), đọc toàn văn 6 stage · 15 play. Đây là **playbook thực hành** của đội Applied AI Anthropic, không phải phương pháp có phân cấp/artefact chuẩn như AWS AI-DLC — nên đối chiếu ở mức *cơ chế* và *chỗ đặt con người*, không đối chiếu stage-với-stage.
> Tài liệu chuẩn của gói vẫn là `whitepaper-ai-dlc-vi.md` (v2 Human-Lead). Bản đối chiếu AWS `aidlc-workflows` v2 ở `aws-aidlc-workflows-v2-vs-ai-dlc.md` — file này **không nhắc lại** 8 cơ chế đã đề xuất ở đó, chỉ trỏ tới khi trùng.
> File này trả lời ba câu: *playbook nói gì · nó xác nhận hay phản bác white paper v2 chỗ nào · lấy gì vào gói, làm ngay trên 6.x được gì.*

---

## 0 · Kết luận một trang

1. **Playbook và white paper v2 cùng một chẩn đoán, cùng một thuốc.** Playbook: *"Build is no longer the constraint — the human-speed steps around it are"*; *"Reviewing each line by hand … can't keep up once agents write most of the diff"*; *"an approval prompt during the build puts a person back on the critical path of all the sessions running in parallel"* → hook hỏi người **chỉ đặt ở Deploy**. White paper §0: *"chờ người là đường găng"* → một chốt chặn thật (Gate R) + Ranh đỏ. Đây là **bằng chứng ngoài** thứ hai (sau LL-002 của PILOT) cho quyết định 7.0.0 ở `plugin-transition-plan.md` §1 — và ngược chiều với AWS v2 (gate mỗi stage).
2. **Playbook đặt con người ở 6 chỗ, gần như trùng bốn điểm dừng của v2** (bảng §3). Khác biệt: playbook *không có* Showcase và Sổ giả định (open questions chỉ "carried forward" trong `intent.md`/`spec.md`, không có `default_if_silent`) — v2 đi xa hơn ở hai chỗ này, **giữ nguyên**. Playbook có thứ v2 *chưa có*: **vòng Maintain → `intent.md` kế** (đóng loop) và **evals cho cấu hình agent**.
3. **"Đơn vị chảy" của playbook là một thay đổi = một PR** (`intent.md` → `spec.md` → `plan.md` → diff). Intent của PILOT là 30 Unit. Playbook không mâu thuẫn với §4.9 (Unit `releasable` + `session_fit`) mà **xác nhận** nó: Unit của mình ≈ một "change" của playbook; Intent của mình ≈ một chuỗi change có chung đích.
4. **Playbook mạnh ở tầng máy Claude Code nguyên bản** (plan mode, hooks, skills, subagents, worktree, `claude -p` headless, `claude-code-action`, managed settings, OpenTelemetry) — gói mình đang **tự dựng lại** một phần bằng HOF/tower/gate_guard. Không phải thay, nhưng vài chỗ nên **dùng máy sẵn thay vì luật viết tay** (mục 4).
5. **Khuyến nghị**: không đổi lộ trình A/B/C. Lấy **10 cơ chế** (mục 4), trong đó **5 cái làm được ngay trên 6.x không đổi luật gate** (red-line guard bổ sung · evals cho gói · khoá file test khi sửa lỗi · verifier tươi context · kiểm trôi plan). Cái đáng làm nhất và mới nhất: **evals cho chính gói** — vì "luật không kiểm được là luật sẽ trượt" (§4.15/§IX) hiện chỉ áp cho dự án, chưa áp cho plugin.

---

## 1 · Playbook nói gì (tóm tắt đủ để quyết)

### 1.1 Khung

- **6 stage phi tuyến** Plan → Design → Build → Test → Deploy → Maintain, thành **vòng lặp**: Maintain viết `intent.md` kế.
- **Sợi chỉ xuyên suốt = artefact commit vào git**: mỗi stage kết thúc bằng commit một artefact, stage kế bắt đầu bằng đọc nó. `intent.md` → `spec.md` → `plan.md` → diff + test → PR + review findings → incident record. *"The chain of commits is also the audit trail: who asked for what, what the agent produced, and who approved it."* **Commit/merge = quyết định** — không có file DEC riêng.
- **Mỗi play** có 5 mục cố định: *What changes · Getting started (Prerequisites/Infrastructure) · How to execute · Governance (enforced / evidence / logged where / who approves) · How to measure (leading / lagging)*. Chỉ số **đọc từ git/PR metadata/OTel**, không tự khai.
- Lộ trình: *"First, you prompt each step by hand with the end state being a loop in which each accepted artifact fires the next gate."*

### 1.2 15 play, một dòng mỗi play

| Stage | Play | Cốt lõi | Người quyết |
|---|---|---|---|
| 1 Plan | **Capture as `intent.md`** | Người khởi xướng brainstorm với Claude (claude.ai/Cowork, không cần git) → `intent.md` theo template tổ chức (problem · outcome · affected · constraints · open questions) → commit vào `intent/` | PO accept = merge |
| 2 Design | **Requirements + design một phiên** | Claude đọc `intent.md` + skills (brand/security/compliance/UX) → `spec.md` có **flagged concerns**; PO giải quyết concern với policy owner trước khi eng thấy. Sau này: merge `intent.md` tự bắn job sinh `spec.md` thành PR | PO ký spec, hỏi tech lead nếu rủi ro cao |
| 3 Build | **Plan mode mặc định** | Eng vào plan mode với `spec.md`, bắt Claude phỏng vấn; "interrogate": vỡ gì · bước nào rủi ro nhất · phương án nào không chọn; iterate tới khi *người chưa đọc hội thoại vẫn làm được từ plan* → commit `plan.md`. Lệch plan ⇒ sửa `plan.md` cùng commit, **hook ép đồng bộ** | Eng accept plan; tech lead/architect nếu rủi ro cao |
| 3 | **Auto mode** | Khi guardrail chín (CLAUDE.md, skills, hooks, test suite): auto-accept cho việc thường; người review **artefact sau phiên dài**, không xem từng edit | — |
| 3 | Sidebar **legacy = source of truth** | Mỗi artefact khai **một** SoT (repo / Jira-ServiceNow / linkage tối thiểu: record ID ↔ commit SHA) | — |
| 3 | **CLAUDE.md** | < 1 trang; *"When Claude makes a mistake twice, the correction goes into CLAUDE.md"*; KPI: lặp lỗi CLAUDE.md đáng lẽ bắt được | code owner duyệt PR sửa |
| 3 | **Skills = tri thức tổ chức** | Một policy có chủ · một SoT → SKILL.md; *"A skill is an advisory control … the hook makes them close to impossible"*; test skill có trigger | policy owner ký đổi skill |
| 3 | **Hooks = guardrail lúc build** | Chặn path bảo vệ · chạy lint/format sau edit · giữ credential ngoài diff · **backing** cho skill bắt buộc. Hook *hỏi người* **không** đặt ở build | — |
| 3 | **Parallel sessions + subagents** | `claude --worktree` mỗi task; 2–3 phiên; trần = *review theo kịp*; subagent cho việc lặp (verifier · simplifier · researcher), khai `.claude/agents/*.md` | — |
| 4 Test | **Feedback loop** | `make test` một lệnh + đích định lượng trong prompt; sửa lỗi = **viết test fail trước, commit, rồi hook cấm sửa file test** (*"an agent fixing code must not be able to weaken the check"*); UI = screenshot vs mock; "done" = đã chạy test và dán output. **Verifier subagent** = context tươi, *"so the verdict is not colored by the assumptions that produced the code"* | code owner ở PR |
| 4 | **Continuous evals in CI** | 20–50 task thật + check → chạy `claude -p` non-interactive **on schedule + on any change to CLAUDE.md / skills / hooks**; pass-rate là merge check; **mỗi incident production thành một eval** | đội sở hữu config |
| 5 Deploy | **AI trong vòng PR review** | Claude review mọi PR theo `REVIEW.md` (passes: bugs · security · **compliance vs `spec.md` + `plan.md`** · Important vs Nit · cap nit · exclusions) và tự sửa comment `@claude`; người review **intent + risk**; finding lặp lần 2 → CLAUDE.md ngay trong review; tech lead tune hàng tháng | code owner qua branch protection (finding không tự approve/block) |
| 5 | **Hooks = cổng duyệt** | Gate người phải sống (change mgmt, release auth, protected path) → hook `allow/ask/block`; team hooks trong `.claude/settings.json`, **non-negotiable trong managed settings** (không tắt được); block phải nói lý do + đường xin duyệt. Ví dụ `production-gate.sh`: `deploy`+`production` mà thiếu `RELEASE_APPROVAL` ⇒ exit 2 | release manager |
| 5 | **CI/CD** | `claude -p` cho bước cần phán đoán (triage build hỏng, changelog); sandbox + token ngắn hạn; deploy/status/rollback qua MCP có allowlist; **tier tự trị theo môi trường** (dev tự do · staging giữa · prod chuẩn bị rồi người ký); *"The agent may act up to the production gate and cannot pass it"*; rollback là đường **tập nhiều nhất** | — |
| 6 Maintain | **Closing the loop** | Script **tất định** (mean/σ rolling, Western Electric) theo dõi một metric; `bands.yaml`: 1σ log · 2σ Claude read-only chẩn đoán · 3σ Claude **đề xuất** (PR vào review gate / runbook pre-approved); kết quả viết thành `intent.md` format Stage 1 → vào pipeline; dismiss tune band; fix xong → thêm eval | service owner triage |
| 6 | Recurring scans (Claude Security) | Scan định kỳ, finding có confidence; vừa một PR → review gate; lớn hơn → `intent.md` | security lead |
| 6 | On-call qua Claude Tag (Slack) | Incident vào channel → Claude first responder; post-mortem ghi vào lessons file version-controlled | người trong channel |

### 1.3 Điểm playbook nhấn mạnh mà mình hay bỏ qua

- **Đo từ máy, không tự khai**: *time intent→spec* = hai git timestamp; *rework* = số commit `spec.md` sau commit `plan.md` đầu; *first-pass merge rate* từ PR metadata; hook wait từ OTel. KPI §IX của mình có `showcase.lead_minutes` (tự khai) — playbook sẽ không chấp nhận.
- **Skill là advisory, hook là deterministic** — *hai lớp*, không chọn một. Gói mình có checklist (advisory) và một hook (`gate_guard`), nhưng chưa nối "checklist nào bắt buộc thì hook nào đứng sau".
- **Loop tự đóng chỉ khi rollback đã tập** — Gate R mục 7 (đường lùi) của mình khớp, nhưng mình chưa có "3σ ⇒ rollback" vì chưa có stage Maintain sinh intent.

---

## 2 · Ánh xạ thuật ngữ và cơ chế

| Playbook | Gói `ai-dlc` (6.1.1 / v2 white paper) | Ghi chú |
|---|---|---|
| `intent.md` (problem · outcome · affected · constraints · open questions) | `intent-plan.md` phần 1 Intent (+ Source Reading Plan + Provisional Unit Map) · `CP-01` v2 | Mình nặng hơn (3 phần) vì brownfield; playbook không có Source Reading Plan — §4.8 No-unread-source là điểm mình hơn |
| `spec.md` + flagged concerns | AS-IS (stage 2) + `open-questions-*.md` (stage 3–4) → v2: Sổ giả định `ASM` | "flagged concern → PO resolve với policy owner" ≈ `OQB` có người trả lời cụ thể (§4.10). v2 thêm `default_if_silent` — playbook không có |
| `plan.md` (files · order · risks · proof) | Bolt: Logical Design + ADR + `tasks.md` (§1.0) | Playbook có mục **Proof** (test nào chứng minh) và **"options not chosen"** — `unit-spec.md`/ADR của mình chưa bắt buộc hai mục này |
| Plan mode → accept → implement | Gate D → Bolt (6.x) · `CP` thứ tự Unit → Bolt (v2) | Plan mode là **cơ chế máy** cấm edit trước khi accept — đúng vai `gate_guard.py` hiện tại, nhưng ở mức phiên, không cần hook |
| Auto mode sau khi guardrail chín | `leadership.mode: lead` (phương án B) | Playbook nói rõ **điều kiện** để auto: CLAUDE.md tuned · skills · hooks · test suite chạy được. Nên thành checklist "đủ điều kiện `lead`" |
| CLAUDE.md < 1 trang, "sai hai lần → vào" | `governance/` nạp qua SessionStart + `LL` qua Gate G | Mình đi đường retro (chậm, đúng kỷ luật); playbook đi đường liên tục. Xem #3 mục 4 |
| Skill có chủ + SoT | `skills/checklists/*.md` có `version` + changelog | Trùng ý; thiếu **test skill có trigger** và thiếu "policy owner ký" |
| Hook build-time (protected path · lint · credential) | `gate_guard.py` chặn code roots trước Gate D | Playbook dùng hook cho **an toàn** không cho **quy trình**; v2 §XII đã quyết chuyển `gate_guard` → red-line guard — playbook cho hình mẫu (#1) |
| Hook `ask` = cổng duyệt production (`production-gate.sh`) | Ranh đỏ #1 (deploy) · Gate R | Trùng gần như nguyên văn với transition plan §2.2 |
| Managed settings (không tắt được) | `AI_DLC_GUARD=off` tắt được | Ranh đỏ mà tắt được bằng env thì không phải ranh đỏ — xem #1 |
| Verifier subagent (context tươi, report-only) | §9.6 `result_check` do người giao · `self_verify` tier `none` | Cùng mục đích; playbook nói lý do **tại sao phải tươi context** — mình chưa ghi và chưa có agent riêng (#5) |
| Feedback loop + khoá file test khi fix | §4.15 ca đối chứng + mutation test | Mình đo *sau*; playbook **chặn trước** (#5) |
| Evals cho CLAUDE.md/skills/hooks | — **không có** | Gói sửa checklist/agent/hook qua CHANGELOG + LL, **không có regression test** (#4) |
| `REVIEW.md` (3 pass · Important/Nit · cap · exclude) | §4.17 tầng `none/peer/specialist` + checklist BE/FE/security/tech-lead/qa | Mình thiếu pass **compliance vs spec + plan** và thiếu cap nit (#7) |
| PR review bằng Claude + code owner | tier `peer` = dev còn lại trong bolt | Playbook thay "người thứ hai" bằng "máy + code owner" (#7) |
| Worktree mỗi phiên song song | — (đề xuất AWS #8) | Trùng — không nhắc lại |
| `claude -p` trong CI · tier tự trị theo môi trường | — | Stage 8 của mình chưa có hình dạng máy (#8, #9) |
| `bands.yaml` → `intent.md` kế | Stage 8 "telemetry, runbook chờ Lead" (protocol §1) · v2 §VIII `TM → RT` | Mình dừng ở retro; playbook **tự sinh intent kế** (#8) |
| Leading/lagging từ git · PR · OTel | KPI §IX (một phần tự khai) · tower KPI | (#10) |
| Legacy SoT (repo / Jira / linkage) | `workspace-map.md` + `pinned/` | Mình chưa có khai báo "SoT của artefact X là đâu" — PILOT có Jira? nếu có, cần một dòng linkage |

---

## 3 · Chỗ đặt con người — so trực tiếp với v2

| # | Playbook: người quyết ở đâu | Cơ chế | v2 white paper | Nhận xét |
|---|---|---|---|---|
| 1 | PO **accept `intent.md`** | merge PR | `CP-01` Mốc chờ (đích) | trùng; playbook không có "im lặng = mặc định" |
| 2 | PO **ký `spec.md`**, hỏi tech lead nếu rủi ro cao | merge; concern giải với policy owner | Sổ giả định: đảo rẻ → `ASM` đi tiếp; đảo đắt → Mốc chờ; chạm ranh đỏ → dừng | v2 **mịn hơn** — playbook vẫn là "PO đọc spec"; nhưng spec của playbook là **một change**, không phải 30 Unit, nên đọc được |
| 3 | Eng **accept `plan.md`** (plan mode) | máy cấm edit trước accept | Mốc chờ thứ tự Unit + Team Agreement trong đội | v2 bỏ người khỏi design nội bộ (E(a)); playbook giữ eng accept — nhưng eng *là* người chạy phiên, không phải người thứ hai ⇒ tương đương "trưởng ca chốt" |
| 4 | — | — | **Showcase** `SC` + `FB` | playbook **không có**; gần nhất là "screenshot matches mock" trong feedback loop. Giữ của mình |
| 5 | Code owner **approve PR** (findings không tự quyết) | branch protection | Gate R mục 4–6 | trùng một phần; Gate R rộng hơn (ledger · soak · rollback · notes) |
| 6 | Release manager **ký production** | hook `ask`/`block` | Ranh đỏ #1 → `DEC` | trùng nguyên văn |
| 7 | Service owner **triage** finding Maintain | queue | Retro → LL Mốc chờ | v2 chưa có triage queue từ production |

Kết luận mục này: playbook **không phản bác** điểm nào của v2; **xác nhận** §0, §II, §V, §VI; **bổ sung** cho v2 hai lỗ: (a) Maintain sinh intent kế, (b) cấu hình agent phải có regression test.

---

## 4 · Mượn gì — theo thứ tự "làm được trên 6.x trước, đổi luật sau"

Mỗi dòng: cơ chế playbook → hình dạng trong gói → trả nợ gì → cỡ. Không trùng với 8 cơ chế AWS (trỏ khi liên quan). Giữ Python.

### 4.1 Làm ngay trên 6.x — không đổi luật gate, không phụ thuộc A/B/C

| # | Cơ chế | Trong gói | Trả nợ | Cỡ |
|---|---|---|---|---|
| **1** | `production-gate.sh` + managed settings | Thêm hook `red_line_guard.py` (PreToolUse `Bash`) **song song** `gate_guard.py`: chặn lệnh khớp `deploy.*prod\|DROP\|TRUNCATE\|DELETE (không WHERE)\|gh pr create\|slack\|mail` khi không có `DEC` mới nhất trỏ `RED-NN` cùng loại; stderr = lý do + đường xin (`/ai-dlc:dlc-revise RED-NN`). **Không có** `AI_DLC_GUARD=off` cho hook này — kill switch chỉ giữ cho `gate_guard`. Ghi `docs/` một trang "managed settings khuyến nghị cho tổ chức" (deny `Read(.env*)`, `allowManagedHooksOnly`) — ngoài phạm vi plugin, nhưng PILOT nên biết | v2 §VI, transition plan §2.2 — làm trước, 7.0.0 chỉ còn gỡ `gate_guard` | 0.5–1 ngày |
| **2** | Evals on change to CLAUDE.md/skills/hooks; incident → eval | `plugin/evals/<LL>.json` = prompt + check script; **mỗi LL đã qua Gate G thành một eval**: `LL-001` (hỏi thứ có sẵn trong nguồn) · `LL-002` (unit đóng không RV) · `HOF-0039` (heartbeat placeholder) · §4.11 (tower khai version chết). Chạy bằng `claude plugin eval` (nếu bật early-access) hoặc vòng `claude -p --allowedTools` như YAML playbook, trên PR chạm `plugin/**` + lịch. Pass-rate là điều kiện merge; CHANGELOG entry phải link **cả LL lẫn eval** | Quy ước "sửa gói phải từ LL" hiện chỉ kiểm bằng mắt; §4.15 chưa áp cho chính gói; nợ `LL-004` (4.1.0) có chỗ trả bằng máy | 2 ngày khởi tạo, 0.5 ngày/LL |
| **3** | Khoá file test khi sửa lỗi; verifier tươi context | (a) HOF có `kind: fix` ⇒ `gate_guard.py` (hoặc hook mới) chặn Write/Edit vào path test của code root (đọc pattern từ `workspace-map.md`, mặc định `test*/`, `*_test.*`, `*.spec.*`); bolt-coordinator bắt "test fail trước, commit, rồi sửa". (b) Agent `dlc-verifier` (Bash · Read, *report only, do not fix*, "chạy app + 2 flow lân cận, đối chiếu DoD lượt") — §9.6 người giao gọi nó **trước** khi ghi `result_check` | §4.15 (đo *sau* → chặn *trước*), §9.6 có mắt thứ hai thật cho tier `none` | 1 ngày |
| **4** | `plan.md` drift hook + "interrogate the plan" | (a) Stop/PostToolUse trên bolt: file trong diff ∉ `tasks.md` ⇒ WARN vào `escalations/` (§4.13), không chặn. (b) Template `unit-spec.md`/ADR thêm 2 mục bắt buộc: **Proof** (test nào chứng minh AC nào) · **Phương án không chọn**; doctor WARN thiếu | §4.12/4.13; LL-003 (unit không bolt, không evidence) | 0.5 ngày |
| **5** | "Sai hai lần → CLAUDE.md" | Không đổi luật LL (vẫn Gate G / Mốc chờ). Thêm: `escalations/` và `RV` có trường `repeat_of:`; doctor đếm — lần 2 cùng mã ⇒ tự sinh **ứng viên LL** vào `retro/candidates.md` (trùng cơ chế AWS #5 `surface`); `session_start.sh` in mục *"Điều AI hay sai ở dự án này"* = LL đã qua gate, ≤ 10 dòng, thay vì nạp cả governance | LL không phải "nhớ lại" ở retro; ngân sách context §10 | 0.5 ngày |

### 4.2 Vào 7.0.0 — cùng lượt với phương án B

| # | Cơ chế | Trong gói | Trả nợ | Cỡ |
|---|---|---|---|---|
| **6** | Commit = quyết định; audit trail = git | `dlc_state.py` (AWS #2) **commit `.ai-dlc/`** tại mỗi `CP`/`SC`/`GATE-R`/`RED` với message có mã; `DEC` chỉ còn ở Gate R/RED/patch gói (đã quyết ở transition plan §2.1). Tower đọc `git log` để tính thời gian, không đọc `heartbeat:` | KPI `lead.wait_hours` từ timestamp máy; §4.11 số truy được | 0.5 ngày (trên AWS #2) |
| **7** | `REVIEW.md` + review máy + code owner | `templates/governance/review.md` (3 pass · Important/Nit · cap 5 · exclude) cho peer/specialist đọc; tier **`peer` được thoả bằng review máy có receipt** (AWS #1 fingerprint) + `result_check` của người giao — không bắt dev thứ hai; `specialist` giữ người. Pass *compliance* đối chiếu `unit-spec.md` + design của Bolt | RV-019/020 kiểu "không ai rảnh review"; §4.17 | 1 ngày |
| **8** | Closing the loop: Maintain → intent kế | `dlc-intent --from <file>` nhận `incident.md`/`finding.md` format Stage 1 (anomaly + evidence · outcome · affected · open questions → `ASM`); `templates/governance/bands.md` (metric · baseline · 3 tier: log / diagnose read-only / propose PR-only) — **script phát hiện là của dự án**, gói chỉ định format và tier; tier 3 luôn dưới Ranh đỏ #1 | v2 §VIII `TM → RT` mới có retro, chưa có intent kế; Gate R mục 7 rollback có người dùng | 1 ngày |
| **9** | `claude -p` trong CI + tier tự trị theo môi trường | `governance/leadership.md` thêm `autonomy: {dev: free, staging: propose, prod: ask}`; skill `dlc-brief`/`dlc-doctor` chạy được non-interactive (`claude -p "/ai-dlc:dlc-doctor" --output-format json`) để CI/cron gọi | Doctor chỉ chạy khi người nhớ; Bản tin ca có thể sinh theo lịch | 0.5 ngày |
| **10** | Leading/lagging từ máy | Tower KPI: bỏ trường tự khai (`showcase.lead_minutes` → đo từ mtime `feedback.md` − mtime `README.md` của SC, hoặc từ inbox json); thêm `first_pass_merge_rate` (Bolt không có `-fix`), `rework` (ASM overridden sau SC), `hook_wait` (thời gian giữa `RED` mở và `DEC`) | §IX "luật nào không có KPI thì không vào gói" — áp ngược: KPI nào không đo từ máy thì không tin | 0.5 ngày |

Cộng: 4.1 ≈ 4.5–5 ngày (độc lập), 4.2 ≈ 3.5 ngày chồng lên phương án B + AWS #1–#3.

### 4.3 Không mượn (có lý do)

- **Claude Security / Claude Tag / Claude Design / claude.ai + Cowork cho intent** — sản phẩm hosted, gắn Enterprise/Slack; ngoài phạm vi plugin. *Riêng* "PO viết intent không cần git" là nhu cầu thật của PILOT (BA/PO không dùng Claude Code) — ghi thành câu chốt #4 mục 6, không vào gói.
- **Managed settings** — cấp tổ chức/IT, plugin không cài được; chỉ viết một trang khuyến nghị (#1).
- **Gỡ Showcase/ASM để giống playbook** — không; playbook thiếu hai cái này và là chỗ v2 hơn.
- **Bỏ Source Reading Plan / source-ledger** vì playbook không có — không; playbook viết cho greenfield-ish, PILOT là brownfield, LL-001 là lý do §4.8 tồn tại.
- **Thay HOF bằng subagent thuần** — không; HOF là file để tower nhìn và để phiên sau `dlc-resume`; subagent của playbook mất context khi phiên tắt (đúng lý do §9.5 không dùng teammate thay HOF). Nhưng #3(b) verifier **là** subagent — đúng chỗ playbook dùng.

---

## 5 · Đối chiếu ba nguồn — AWS v2 · playbook · white paper v2

| Câu hỏi | AWS `aidlc-workflows` v2 | Playbook Anthropic | White paper v2 (mình) |
|---|---|---|---|
| Người dừng ở đâu | mọi stage trừ init (~23–30 gate) | 6 chỗ, đều là *commit/merge/accept*, hook `ask` chỉ ở prod | `CP-01` · Mốc chờ thứ tự Unit · Showcase · Gate R · Ranh đỏ |
| Quyết định = gì | receipt do tool ghi + gate của engine | commit trong git | `DEC` (Gate R/RED) + `ASM`/`FB`/`STR` có ID |
| Không biết thì | Request Changes / Accept as-is vòng 3 | open questions carried forward | `ASM` có `default_if_silent` |
| Kiểm cấu hình agent | 443 test cho engine, không eval LLM | **evals CI on change** | **chưa có** |
| Đóng loop production | Operation phase 4.x CONDITIONAL | `bands.yaml` → `intent.md` | retro → LL, dừng |
| Đo | audit event 87 loại, ledger USD | git/PR/OTel, leading+lagging | KPI §IX, một phần tự khai |
| Nên lấy | máy kiểm được (#1–#8 file AWS) | hook prod · evals · verifier · plan drift · loop Maintain (#1–#10 file này) | giữ mô hình dừng |

---

## 6 · Việc cần chủ gói chốt (bổ sung vào §5 transition plan)

1. **Làm 4.1 (#1–#5) ngay trên 6.x** — bump 6.2.0 (minor: thêm hook + agent), CHANGELOG ghi "quyết định chủ gói, căn cứ playbook Anthropic 2026-08-21 + LL-001/002", nợ LL như 5.0.0/6.0.0 — hay chờ chọn A/B/C rồi làm một lượt?
2. **Evals cho gói (#2)**: chấp nhận chi phí token chạy `claude -p` trên mỗi PR chạm `plugin/**`? Ngưỡng pass-rate chặn merge bao nhiêu (đề xuất 100% cho eval từ LL đã qua Gate G, vì đó là regression)?
3. **Tier `peer` = review máy + receipt** (#7): có bỏ yêu cầu "dev còn lại trong bolt" không? Đây là đổi §4.17 ⇒ major, đi cùng 7.0.0.
4. **Intent từ PO không dùng git** (claude.ai/Cowork + connector GitHub như playbook): PILOT có cần không, và ai dựng "intent home"? Ngoài gói, nhưng quyết định này đổi cách `dlc-intent` nhận đầu vào (`--from <file>` của #8 dùng chung được).
5. **Ranh đỏ không có kill switch** (#1): đồng ý bỏ `AI_DLC_GUARD=off` cho red-line guard? Nếu tắt được thì không gọi là ranh đỏ.

---

## Phụ lục · Trích dẫn giữ nguyên văn (để CHANGELOG/white paper trích khi cần)

- *"Build is no longer the constraint — the human-speed steps around it are. Human-speed stages keep their length while build collapses to hours."*
- *"A hook that asks a human for approval belongs with the gates in Stage 5: Deploy, because an approval prompt during the build puts a person back on the critical path of all the sessions running in parallel."*
- *"The agent does everything up to the production gate and nothing past it."*
- *"A skill is a control, though an advisory one … The skill makes violations rare and the hook makes them close to impossible."*
- *"When Claude makes a mistake twice, the correction goes into CLAUDE.md."*
- *"An agent fixing code must not be able to weaken the check on that code."*
- *"[The verifier runs in] a fresh context window once the session believes the work is done. This way the verdict is not colored by the assumptions that produced the code."*
- *"[Evals run] on any change to CLAUDE.md, skills or hooks, since that configuration steers the agent and deserves the regression testing that code gets."*
- *"Each stage ends by writing one [artifact] to version control … The chain of commits is also the audit trail: who asked for what, what the agent produced, and who approved it."*
- *"Human attention concentrates at the gates, reviewing what the agent flagged rather than starting each stage from scratch."*
