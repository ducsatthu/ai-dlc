# Engine `docs/intents/` của template đội so với gói `ai-dlc` 6.5.0: gói chạy được chưa, và 7.0.0 phải nhắm vào đâu

> Trạng thái: đã chốt 2026-10-16, bốn câu ở §6 do chủ gói trả lời trực tiếp. Lát a và a-3 làm cùng ngày (xem `CHANGELOG` *Unreleased 7.0.0-a*).
> Nguồn: `project-starter-template-ai` @ `c75f50d` (2026-10-14, nhánh `main`, remote Bitbucket `nal-solutions`). Đã đọc `AGENTS.md`, `docs/intents/README.md`, `.agents/skills/aidlc/{SKILL.md,references/*,scripts/*}`, `docs/intents/_templates/*`, `REVIEW.md`, `.claude/settings.json`, `.agents/hooks/*`. Đã chạy `validate_workflow.py --help`, `approvals.py --help`, `start_change.py --help` và self-test (100 ca OK). Phía gói: `layout.py --explain` chạy trên template, `session_start.sh`, `gate_guard.py` với payload Write giả, `python3 -m unittest discover -s tests`.
> Ba bản đối chiếu trước: engine AWS (`aws-aidlc-workflows-v2-vs-ai-dlc.md`), playbook Anthropic, workflow đích của team (`team-target-workflow-vs-ai-dlc.md`, 2026-08-27). File này trả lời câu thứ tư: team đã đóng workflow đích thành engine của riêng họ, gói đứng ở đâu so với nó.

## 0. Kết luận một trang

1. Tiền đề của kế hoạch 7.0.0 đã lỗi. `plugin-7-policy-layer-plan.md` (chốt 2026-09-28), `aws-v2-workspace.md`, `tower_aws_v2.py`, `tower_approve.ts`, `aws_v2_write_receipt.ts` đều nhắm vào template chạy AWS `aidlc-workflows` v2 2.5.75 (`aidlc/spaces/`, `.claude/tools/aidlc-audit.ts`, `upstream-lock.json`). Template ở HEAD không còn file nào trong số đó. Thay vào là engine tự viết của team: skill `.agents/skills/aidlc/` (Python stdlib, 100 self-test, CI `aidlc-validate.yml`), state tại `docs/intents/NNNN-name/` với đúng bốn file. Dòng commit: 2026-08-20 "grounded Intent contract", 09-30 `approvals.py` (hash-bound) và nested repo, 10-03 Knowledge impact, 10-04 multi-repo. Spike 2026-09-03 của gói chạy trên bản copy cũ; team đổi engine ngay sau đó.
2. Hôm nay gói chạy được 0% trên template và im lặng hoàn toàn. `layout.py --explain` trả `engine: none`, nên `session_start.sh` không in gì, `gate_guard.py` cho qua, `tower_generate.py` từ chối sinh. Không hại, không ích. Chạy `/ai-dlc:dlc-init` ở đó sẽ tạo `.ai-dlc/context-memory/` song song với `docs/intents/`, đúng phương án C mà `multi-user-shared-space.md` §2.1b đã bác vì hai nguồn sự thật.
3. Engine của team là bản "workflow đích" đã đóng, và nó hấp thụ khoảng 70% điều gói từng khuyên: ba gate người (Intent, Plan, Outcome; bugfix và refactor gộp Intent với Plan), tự sửa tối đa ba lần rồi dừng, tag `[gate]`, `[owner:]`, `[repo:]` trên Work Unit, Proof là lệnh chính xác, REVIEW.md ba pass chạy trước Outcome (đúng đề xuất §3.2 của file 08-27), ranh đỏ "external, production, destructive, security authorization halts", Backlog Preview rồi Confirm rồi Publish (`.plugins/backlog-sync`), codekb fingerprint CURRENT/STALE, Knowledge impact thành unit `[knowledge]` trên cùng PR, Ideation `/idea`. Team có bốn thứ gói không có: sổ duyệt băm SHA-256 (`approvals.json`, append-only, đổi byte là mất duyệt), validator chạy trong CI của PR (`validate_pr.py`, bốn stage), evidence gắn `<repo>@<sha>`, và chạy được trên Codex vì `AGENTS.md` là canonical.
4. Thứ team không có mà gói có chính là "lớp chính sách + tower" 7.0.0 đã định làm, chỉ cần đổi engine đích: tower decision-first và bản mô hình cho người (§2.4), Source Reading Plan và No-unread-source, open questions tách business/tech có cột *Nếu im lặng*, Unit `releasable` và `session_fit`, tầng review §4.17, self-verify có con trỏ cùng §4.15, HOF và heartbeat, escalation, retro thành LL qua Gate G, doctor. Template viết "Read memory, knowledge, fresh codekb and actual source" nhưng không có sổ cái nào chứng minh đã đọc; `## Open questions` là chữ tự do, không có mặc định; không có dashboard; không có vòng LL.
5. Một xung đột luật phải chốt trước khi code: autopilot và "Never infer approval". Template cấm tuyệt đối: *"Never run the helper because a test passed or a person stayed silent"*; `approvals.py` đòi `--by <tên người đã xác nhận>`. Autopilot §2.3 tự quyết gate vi phạm trực tiếp. Lối ra đã có trong gói: §9.3 dòng aws-v2 chốt "soạn sẵn, người bấm một nút". Áp đúng cái đó cho engine này (§6 câu 2).
6. Khuyến nghị: 7.0.0 là lớp chính sách + tower trên engine `docs/intents/` của team. Kiến trúc giữ nguyên phương án A, đổi đích. Lát a (máy móc, không luật mới): engine thứ ba trong `layout.py` và `layout.ts`, `contracts_brief.py`, nhánh `dlc-status`, `dlc-resume`, `dlc-doctor` đọc bốn file và gọi `validate_workflow.py`. Lát b (luật, mức WARN): sổ cái nguồn, OQ có mặc định, sizing, tầng review, LL, ghi vào chỗ template cho phép và không sửa template. Nhánh AWS v2 vào `archive/` vì không còn dự án nào chạy nó. Chi tiết ở §5.

## 1. Engine của template nói gì

Nguồn: `docs/intents/README.md`, tự nhận là "canonical definition".

### 1.1 Một change là một thư mục, bốn file, một PR

```
docs/intents/NNNN-change-name/
├── intent.md        # Scope · Owner · Implementation repository · Backlog · Security triggers ·
│                    # Problem · Proposed outcome · Affected users/systems · Constraints · Open questions ·
│                    # Success criteria (AC-* | Criterion | How to verify) · Knowledge impact (Target | Change)
├── plan.md          # Scope · Owner · Implementation repository · Branch · Files that change ·
│                    # Order of work (N. U-00N — step (AC-*) [gate] [owner:] [repo:] [knowledge]) · Risks · Proof (AC | Check)
├── approvals.json   # {"version":1,"events":[{gate, decision, by, at, source:"chat", files:{name: sha256}}]}
└── evidence.md      # Work Units (Unit|AC|Result|Check|Commit|Evidence) · Acceptance evidence · Outcome
```

Markdown không có `Status` hay `Approved by`. Duyệt chỉ sống trong `approvals.json`, băm toàn bộ byte của file. Ideation (`/idea`) ghi vào `docs/intents/ideation/`: không số, không validate, không duyệt.

### 1.2 Gate và đường duyệt

| Scope | Gate | Branch | Backlog |
|---|---|---|---|
| feature, infra | `intent` rồi `plan` rồi `outcome` | `feat/`, `chore/` | none (mặc định) hoặc story |
| bugfix, refactor | `contract` (Intent và Plan một lần) rồi `outcome` | `fix/`, `chore/` | none hoặc `child:<KEY>` |

Gate nào băm file nào: `intent` băm intent.md; `plan` băm intent.md và plan.md; `contract` băm cả hai; `outcome` băm cả ba kể cả evidence.md. Đổi Intent thì mất Intent và Plan. Đổi Plan thì mất Plan. Đổi output hoặc evidence thì mất Outcome. Merge không phải quyết định chat: người review bấm trên Bitbucket hoặc GitHub, agent không merge trừ khi được bảo.

### 1.3 Máy kiểm, thứ gói chưa từng có

```
validate_workflow.py <dir> --stage draft    # PR draft CI: cho phép contract dở, chỉ WARN
                           --stage execute  # trước khi chạy unit: cần duyệt hiện hành và cấu trúc đủ
                           --stage outcome  # cần evidence pass, quality/review/security, output không trôi so với commit đã verify
                           --stage merge    # PR review-ready CI: cần Outcome approval hiện hành
validate_pr.py "$GITHUB_EVENT_PATH" [--workspace-root --implementation-root]   # chạy trong CI, fail-closed
approvals.py <dir> --gate … --decision approve|request-changes --by "<tên người>"  # validate rồi append atomic
start_change.py <slug> --scope … --branch … [--implementation-repository sources/x …]  # copy 4 template, không git
```

Drift check: mọi thay đổi tracked, staged, hoặc untracked không ignore, ngoài `approvals.json`, `evidence.md`, `.backlog-sync.json` của chính change đó, đều là output và phải nằm trong `Files that change`. Spike ngày 2026-10-16 (clone template, `start_change.py`, thêm `sources.md` vào thư mục change) cho thấy `--stage draft` và `--stage execute` không phạt file lạ, kể cả sau khi approve intent và plan. Chỉ `outcome` và `merge` kiểm drift so với implementation commit đã verify (`verify_snapshot`). Vậy file gói ghi thêm vào `docs/intents/NNNN/` phải được commit trước implementation commit của Outcome, hoặc khai vào `Files that change` (§6 câu 3).

### 1.4 Luật vận hành gói phải tôn trọng

Từ `AGENTS.md`, `ai-agents.md`, `CONTRIBUTING.md`:

- Không co-author hay generated-by AI trong commit. Không commit trên `main` hoặc `develop` (hook `git-guardrails.sh` chặn). Không force-push.
- Không đọc hay ghi `.env*` và key (hook `secret-guardrails.sh` và `permissions.deny`).
- `memory/` áp luật. `knowledge/` giữ sự thật đã chấp nhận. `codekb/` là quan sát, có thể cũ. `intents/` cho một change. Không ghi luật vào knowledge hay codekb; không ghi scan vào knowledge.
- Codex đọc `AGENTS.md` trực tiếp; skill ở `.agents/skills/` (symlink `.claude/skills`). Gói chỉ có Claude Code, nên mọi thứ gói thêm phải là file người và Codex đọc được, không chỉ hook.

## 2. Ánh xạ khái niệm: cùng tên, khác hình

| Khái niệm | Template (engine team) | Gói `ai-dlc` 6.5.0 | Nhận xét |
|---|---|---|---|
| Đơn vị thay đổi | `docs/intents/NNNN-name/` (4 file) | `.ai-dlc/context-memory/intents/INT-NNN/` (~15 file và `units/UOW-NN/bolts/`) | gói nặng gấp khoảng 4 lần; team cố ý nhẹ ("Keep each section to a few lines") |
| Mô tả đích | `intent.md` 6 mục và bảng AC | `intent-plan.md` 3 phần (Intent, Source Reading Plan, Provisional Unit Map) | team không có kế hoạch đọc nguồn và không có unit map ở Intent |
| Kế hoạch | `plan.md`: Files, `U-*` thứ tự, Risks, Proof là lệnh | `unit-plan.md` và `spec.md` (`releasable`, `session_fit`, `areas`, `review`) và Bolt 4 chặng | team có `[owner:]`, `[repo:]`, Proof; gói có sizing, tier, bolt. Team không có Bolt, unit đi thẳng code |
| Quyết định người | `approvals.py --by` ghi `approvals.json` băm SHA-256 | tower ghi `inbox/gate-*.json` (`previewed:true`) rồi DEC prose trong `decisions-log.md` và `status.md` | gói kiểm "đã xem", team kiểm "đúng byte". Hai cái bù nhau |
| Số gate | 3 (hoặc 2) và người merge PR | A đến G, thêm E(a)/E(b) mỗi bolt | khoảng cách đã thấy ở file 08-27, nay team đã chốt 3 |
| Tự sửa | tối đa 3 lần rồi dừng (unit-loop.md §4) | `max_self_fix: 2` (autopilot.md) | cùng ý, con số khác |
| Review | REVIEW.md 3 pass trước Outcome; `security-review` theo `Security triggers` | tầng `none/peer/specialist` §4.17; self-verify §4.15 | team có pass nhưng không có tầng; gói có tầng nhưng không có checklist pass chuẩn. Ghép được: trigger của gói với `Security triggers` của team |
| Bằng chứng | `evidence.md` bảng Unit/AC, `<repo>@<sha>`, Outcome | `bolts/*/evidence/`, `self-verify.md`, `acceptance.md` | team bắt SHA thật và validator kiểm reachable; gói chỉ khuyên |
| Kiểm máy | validator 4 stage và CI | `dlc-doctor` (prose 159 dòng), `autopilot_check.py`, `human_view_check.py` | gói không có gì trong CI |
| Open questions | `## Open questions` chữ tự do, chặn Gate 1 | 2 file B/T; mỗi câu có người, phương án kèm giá, *Nếu im lặng*, *đã soát nguồn* | gói hơn hẳn; đúng điểm §3.4 file 08-27 team chưa sửa |
| Nguồn đã đọc | "Read memory, knowledge, fresh codekb and actual source", không sổ | `source-ledger.md` read/missing/deferred kèm evidence; `planned` chặn Gate B/D | khoảng trống lớn nhất của team về truy vết |
| codekb | `docs/codekb/<source>/` 9 file, `codekb.py` fingerprint `git ls-files` ra CURRENT/STALE | `codekb/<repo>/freshness.md` `git_head` | cùng ý; team có script, gói có luật "reuse vẫn qua ledger" |
| Knowledge | `docs/knowledge/` và Intent `## Knowledge impact` thành unit `[knowledge]` cùng PR | `governance/` (luật), không có lớp knowledge rõ | team hơn |
| Luật | `docs/memory/{org,team,project}.md`, `rules/`, `phases/` | `governance/{dor,dod,sizing,autopilot}.md`, `overrides/` | team: luật là tài liệu người đọc, Codex cũng đọc. Gói: luật nằm trong protocol.md 938 dòng và hook |
| Backlog | `.plugins/backlog-sync`, Preview rồi Confirm rồi Publish, `Backlog: none|story|child:` | không có | team có, gói chưa bao giờ làm `dlc-backlog` |
| Ideation | `/idea` Spark, Flame, Forge ra Concept Brief | không có | team có |
| Dashboard | không có | Control Tower LIVE, bản mô hình SVG, thẻ *Cần tôi quyết*, Đảo | gói có, team không. Giá trị lớn nhất gói mang được |
| Handoff | không có (spawn bằng prompt) | HOF, heartbeat, §9.6 nghiệm kết quả | gói có; team không, nhưng team chạy một agent tuần tự nên nhu cầu thấp hơn |
| Học | `docs/knowledge/technical/decisions/` ADR; không có "sai hai lần" | LL qua Gate G rồi patch gói | gói có vòng học; team không |
| Harness | Claude Code và Codex | Claude Code | gói thiếu |
| Nested repo | contracts khai `Implementation repository: sources/a, sources/b`; mỗi repo một PR; CI hai checkout | `workspace-map.md` `repos:` và `areas:` | cùng bài toán, team đã có CI thật |

## 3. Gói chạy được bao nhiêu trên template, đo thật

| Thành phần gói | Trên template @HEAD | Lý do |
|---|---|---|
| `layout.py --explain` | `engine: none` | tự dò chỉ biết `.ai-dlc/context-memory` và `aidlc/spaces` kèm `.claude/tools/aidlc-audit.ts` |
| `session_start.sh` | im lặng | engine none |
| `gate_guard.py` | exit 0 | engine khác ai-dlc |
| `aws_v2_write_receipt.ts` | no-op | không có `aidlc/` |
| `tower_generate.py`, `dlc-tower serve` | từ chối sinh | engine none |
| `tower_aws_v2.py`, `tower_approve.ts` | "không phải workspace AWS v2", exit 1 | 441 và 229 dòng không có đích nào còn tồn tại |
| `dlc-init` | sẽ tạo `.ai-dlc/context-memory/` cạnh `docs/intents/` | bước 0 chỉ nhận ra aws-v2, nên rơi xuống nhánh tạo state riêng: hai nguồn sự thật |
| `dlc-intent` đến `dlc-accept` | tạo INT-NNN trong `.ai-dlc/`, bỏ qua `start_change.py` và `approvals.py` | ghi state ngoài validator và CI của team; PR của team không thấy gì gói làm |
| `dlc-status`, `dlc-resume`, `dlc-doctor` | "chưa init" | đọc `session_brief.py` nhánh ai-dlc |
| `dlc-retro`, `dlc-contribute` | chạy được về cơ học nhưng không có `comms/` hay `handoffs/` để đọc | |
| Tests 118 ca | 117 pass, 1 fail (WIP `tower_generate.py` chưa commit) | không liên quan template; ghi để chủ gói biết trước khi cắt lát |

Tổng: không lệnh nào của gói làm được việc có ích trên template mà không tạo ra nguồn sự thật thứ hai.

## 4. Ba lựa chọn, và vì sao vẫn là A

| | A. Gói là lớp chính sách + tower trên engine `docs/intents/` của team | B. Gói thay engine trong template | C. Hai engine song song |
|---|---|---|---|
| Cách làm | engine thứ ba trong `layout.py`; tower đọc 4 file, git, PR; nút quyết gọi `approvals.py` của team với tên git user; luật gói thành tài liệu trong `docs/memory/` (đề xuất, Lead chấp nhận) | bỏ `.agents/skills/aidlc`, đặt `.ai-dlc/` và 16 skill | `dlc-init` tạo `.ai-dlc/` cạnh `docs/intents/` |
| Được | giữ sổ băm, CI, Codex, Backlog, Ideation của team (họ vừa làm 2 tháng, 100 test); gói chỉ làm phần họ thiếu (§0.4) | đúng white paper v1 của gói | không phải chọn |
| Mất | gói phải bỏ 7 gate, HOF, bolt khi ở engine này vì những luật đó không có chỗ cắm; autopilot bị cấm (§5.3) | mất toàn bộ máy móc team; không khả thi về chính trị | hai nguồn sự thật, §2.1b đã bác |
| Khớp kế hoạch 7.0.0 | y nguyên kiến trúc, đổi đích từ `aidlc/spaces/` sang `docs/intents/` | ngược 7.0.0 | ngược 6.2.0 |

Khuyến nghị A. Khác lần trước (AWS v2 là engine của bên thứ ba, không sửa được), engine này là của chính đội, nên đề xuất sửa template là PR nội bộ. Kỷ luật cũ vẫn giữ: gói không sửa template; thứ gì muốn team đổi thì ghi thành đề xuất ở §7.

## 5. Kế hoạch 7.0.0 nhắm lại: lát, loại, nợ

### 5.1 Lát a, máy móc, không luật mới (đã làm 2026-10-16)

| Việc | Chi tiết | Kiểm bằng |
|---|---|---|
| Engine `contracts` trong `layout.py` và `layout.ts` | tự dò bằng đúng bộ ba `start_change.py` dùng: `.agents/skills/aidlc/SKILL.md`, `docs/memory/project.md`, `docs/intents/_templates/intent.md` cùng thư mục; `state` là `docs/intents`; `governance` mặc định `.ai-dlc/governance/` (gói ghi) trong khi `docs/memory` là luật đội (đọc); `tower.port` 8644 | fixture mới trong `tests/test_layout.py`: template thường, từ thư mục con, config đè, hai engine cùng chỗ |
| `session_start.sh` nhánh `contracts` | banner ngắn: engine team giữ lifecycle, gói là brief và doctor; rồi `contracts_brief.py --short` | `bash -n` và chạy trên template |
| `gate_guard.py` | cho qua ở engine `contracts` vì template có hook riêng | test hiện có |
| `contracts_brief.py` | đọc mỗi `docs/intents/NNNN-*/{intent,plan,approvals.json,evidence.md}`, git, và chạy `validate_workflow.py` ở stage suy ra. Gate đang chờ là gate kế tiếp chưa có event hiện hành. `--doctor` mã `D01` đến `D21` | `tests/test_contracts_brief.py` |
| `dlc-status`, `dlc-resume`, `dlc-doctor` nhánh `contracts` | chuyển sang `contracts_brief.py`; doctor chép nguyên mã D | chạy trên template |
| `dlc-init` nhánh `contracts` | không tạo `.ai-dlc/context-memory`; chỉ `.ai-dlc/governance/{raci,sizing,autopilot}.md` với autopilot `mode: lead` (§5.3); gitignore `.ai-dlc/tower/` | idempotent |
| Gỡ đích AWS v2 | `tower_aws_v2.py`, `tower_approve.ts`, `aws_v2_write_receipt.ts`, `references/aws-v2-workspace.md` vào `docs/archive/aws-v2/`; `layout.py` giữ autodetect `aws-v2` nhưng `notes` ghi "đã archive" | tests `test_layout` aws-v2 fixture giữ |

Chưa làm trong lát a: `tower_contracts.py` có nút Duyệt gọi `approvals.py` (lát a-2), bản mô hình `views/` cho `intent.md` và `plan.md`.

### 5.2 Lát b, luật gói đọc được bởi người và Codex, mức WARN cho tới khi có LL (3 đến 4 ngày)

Cách duy nhất để luật gói tới được agent của team (Claude và Codex) là tài liệu trong `docs/memory/`, không phải hook. Gói sinh một file đề xuất, Lead chấp nhận bằng PR, đúng luật "Humans (AI proposes)" của template.

| Luật gói | Đưa vào template bằng | Doctor kiểm (WARN) |
|---|---|---|
| No-unread-source §4.8 | đề xuất mục `## Sources` trong `intent.md` (team từng vẽ `[ans:A1]` ở workflow đích nhưng template chưa có) hoặc file `sources.md` cạnh (§6 câu 3) | AC không trỏ nguồn; nguồn `planned` khi gate `plan` |
| Open questions có *Nếu im lặng* và *đã soát* §4.10 | đề xuất format bảng cho `## Open questions` | câu không có mặc định khi gate `intent` mở |
| Unit `releasable`, `session_fit` §4.9 | tag `[releasable:…]`, `[fit:…]` trên dòng `U-*` của `plan.md` (cùng kiểu `[owner:]`) | thiếu thì WARN |
| Tầng review §4.17 | ánh xạ: `Security triggers` khác none thì specialist(security); `Implementation repository` từ 2 repo thì peer; còn lại none với self-verify | REVIEW.md pass có mà tầng không khai |
| §4.15 ca đối chứng và mutation | mục trong `docs/memory/rules/testing.md` (đề xuất) | Proof không có ca đối chứng |
| LL qua Gate G | `dlc-retro` đọc `evidence.md`, `approvals.json` (request-changes là tín hiệu), log máy ghi, PR comment; ra `LL-NNN` trong `.ai-dlc/governance/lessons-learned/`; patch gói qua `dlc-contribute` | |
| RACI | `.ai-dlc/governance/raci.md` cột gate là `intent|plan|contract|outcome`; tower chỉ hiện thẻ cho đúng người | |

### 5.3 Autopilot trên engine `contracts`: chỉ một chế độ hợp lệ

Template viết: *"Never infer approval. Never run the helper because a test passed or a person stayed silent."* `approvals.py --by` phải là người. Vậy `mode: autopilot` không được gọi `approvals.py`. Áp đúng quyết định §9.3 dòng aws-v2, "soạn sẵn, người bấm một nút": orchestrator vẫn chạy block check sáu điều kiện, ghi DEC đề xuất (Chọn, Bỏ, Đảo bằng, Hiện ở) vào `.ai-dlc/governance/decisions-log.md`, tower hiện thẻ một nút kèm đề xuất, người bấm thì `approvals.py` chạy với tên người. Im lặng thì không áp gì, chỉ hiện thẻ quá hạn. Muốn hơn thế phải team đổi luật template (§7), không phải việc của gói.

### 5.4 Thứ của gói không có chỗ cắm ở engine này

Bolt 4 chặng, Gate B, C, E(a), E(b), HOF và heartbeat và §9.6, `units/_trash`, escalation file, `comms/`. Tất cả giả định state `.ai-dlc/` và nhiều agent song song. Team chạy tuần tự, một PR, một agent. Giữ chúng cho engine `ai-dlc` (đóng băng như 7.0.0 §5). Ở engine `contracts` chúng không tồn tại và doctor không kiểm. Ghi thành `ASM-PKG-03`.

## 6. Việc chủ gói cần chốt (mỗi câu có mặc định nếu im lặng)

| # | Câu | Phương án và giá | Mặc định nếu im lặng |
|---|---|---|---|
| 1 | Nhắm lại 7.0.0 vào engine `docs/intents/` của team, gỡ đích AWS v2 vào `archive/`? | Có: 7.0.0 có đích thật đang chạy. Không: giữ AWS v2 mà không còn workspace nào để thử | Có |
| 2 | Autopilot ở engine này: (a) soạn sẵn, người bấm, tôn trọng "never infer approval"; (b) cho `approvals.py --by autopilot`, phải xin team đổi luật template trước | (a) chậm hơn, hợp luật. (b) đúng tinh thần 6.4.0 nhưng phá luật của người khác | (a) |
| 3 | Artefact gói per change (`sources.md`, `views/*.view.json`, self-verify) đặt trong `docs/intents/NNNN/` hay mirror `.ai-dlc/intents/NNNN/`? | trong: một chỗ, Codex thấy, nhưng phải commit trước implementation commit của Outcome. mirror: không chạm validator, hai chỗ | spike nửa ngày, mặc định mirror nếu validator từ chối |
| 4 | Tên engine trong config và `layout.py`: `contracts`, `aidlc-skill`, `team` | chữ chỉ để đọc; `contracts` tả đúng thứ nó đọc | `contracts` |

Hạn 2026-10-20. Quá hạn thì áp mặc định và ghi `CHANGELOG` *Unreleased* "chốt theo mặc định vì im lặng quá hạn".

### 6.1 Đã chốt 2026-10-16, chủ gói trả lời trực tiếp

| # | Chốt | Ghi chú thực thi |
|---|---|---|
| 1 | Có, nhắm lại và archive AWS v2 | làm trong lát a: 4 file vào `docs/archive/aws-v2/`, hook PostToolUse receipt gỡ, `layout.py` vẫn dò ra để báo |
| 2 | (a) soạn sẵn, người bấm | `dlc-init` nhánh contracts seed `autopilot.md` `mode: lead`; `contracts_brief.py` không có đường gọi `approvals.py`; banner nói rõ *never infer approval* |
| 3 | Luôn trong `docs/intents/NNNN/` (chủ gói chọn phương án mạnh hơn mặc định) | spike đã chạy, kết quả ở §1.3: draft và execute không phạt, outcome và merge kiểm drift. Artefact gói phải commit trước implementation commit của Outcome hoặc khai vào `Files that change`. Doctor `D16` nhắc đúng điều đó. Đề xuất §7.1 vẫn nên gửi team để bỏ ràng buộc này |
| 4 | `contracts` | |

Lát đầu chốt là lát a đọc-only, đã làm. Cùng ngày làm thêm lát a-3 (log máy ghi và retro, §9).

## 7. Đề xuất gửi team về template

Không phải việc của gói, nhưng gói sẽ dễ hơn nếu có:

1. `docs/intents/README.md` thêm `.ai-dlc/` (hoặc tên khác) vào audit exceptions cạnh `.backlog-sync.json`. Một dòng, mở đường cho §6 câu 3 phương án "trong".
2. `intent.md` thêm `## Sources` (bảng `S-NN | nguồn | vùng đã đọc | rút ra`). Team đã vẽ nó ở workflow đích 08-27 dưới tên `[ans:A1]`.
3. `## Open questions` thành bảng có cột *Nếu không trả lời trước hạn*, chính điểm §3.4 file 08-27.
4. `plan.md` cho phép tag `[fit: …]` trên `U-*` như `[owner:]`, không đổi validator.

## 8. Việc phải sửa ở tài liệu gói khi file này được chốt

- `plugin-7-policy-layer-plan.md`: dòng đầu "tiền đề AWS v2 lỗi từ 2026-10; kế hoạch hiện hành: `template-contracts-engine-vs-ai-dlc.md` §5".
- `references/aws-v2-workspace.md` vào `docs/archive/`; `references/layout-config.md` §4 ví dụ "Template đội (AWS v2)" đổi sang engine `contracts`. Đã làm.
- `CLAUDE.md` gói: bảng `docs/` thêm file này; dòng "Layout cấu hình được" thêm engine thứ ba. Đã làm.
- `MIGRATION.md` 7.0.0: engine `ai-dlc` đóng băng, engine `contracts` mới, `aws-v2` archive. Đã làm.
- Sửa test đang đỏ `test_apply_line_on_the_views_own_decision_id`. Đã làm 2026-10-16: `make_resolver` so theo gate của tài liệu thay vì một id DEC (gate A có thể có nhiều DEC; điểm chưa bị đảo vẫn là đúng mặc định đang vẽ). 161 test xanh.

## 9. Log máy ghi, profile tối giản, và evals cho model mới (chốt 2026-10-16, cùng ngày)

Ba câu chủ gói đặt sau khi lát a xong. Trả lời ngắn: chưa có hook nào ghi log để đánh giá lại; cắt skill cho model mới nên làm hai bước; cả hai việc cần chung một nền là dữ liệu do máy ghi.

### 9.1 Trước đó chưa có log máy ghi

Vòng học của gói (`dlc-retro`, `LL`, Gate G) đọc HOF, REV, MSG, SES. Tất cả do agent tự viết. Hook của gói chỉ nạp luật (`SessionStart`) và chặn (`PreToolUse`). Hook của template cũng chỉ chặn. Dấu vết máy duy nhất từng có là audit shard của AWS v2, nay archive.

Lát a-3 (đã làm) bù chỗ đó bằng `hooks/observe.py` và `scripts/contracts_retro.py`. Hook ghi sự kiện có cấu trúc vào `.ai-dlc/log/`; retro đếm mẫu lặp và sinh `candidates.md`. Người vẫn là người viết LL và ký. Chi tiết trong `CHANGELOG` *Unreleased 7.0.0-a*.

Hai luật tự đặt cho log: không ghi nội dung (file, stdout, câu lệnh đầy đủ) và không ghi tên người (tên đã nằm trong `approvals.json`). Lệnh shell thường không ghi gì. Nhờ vậy log commit được cùng repo mà không kéo theo bí mật.

### 9.2 Cắt skill cho model mới: hai bước

Phần lớn giàn giáo của gói sinh ra để bù lỗi của model yếu hơn: LL-001 (hỏi thứ có sẵn trong nguồn), LL-002 (khai xong không bằng chứng), HOF-0039 (heartbeat bịa). Model mạnh hơn có thể không cần một phần. Cắt theo cảm giác thì lặp lại đúng lỗi "luật không kiểm được".

Bước 1, không cần bằng chứng thêm, đã làm: ở engine `contracts` 9 skill không có việc và nay tự nói điều đó khi được gọi. Profile còn lại:

| Giữ | Việc |
|---|---|
| `dlc-status`, `dlc-doctor`, `dlc-resume` | đọc 4 file và validator của đội |
| `dlc-retro`, `dlc-contribute` | vòng học trên log máy ghi |
| `dlc-init`, `dlc-tower` | seed governance; tower là lát sau |
| agent `retro-keeper` (và `modeler` khi có `views/`) | hai agent, không phải mười bảy |

Bước 2, chưa làm: mỗi LL đã qua Gate G thành một eval (`plugin/evals/LL-NNN/`: prompt tái hiện tình huống và script kiểm). Chạy bằng `claude -p` trên model đích. Luật nào model pass mà không cần luật thì hạ xuống WARN rồi gỡ ở 8.0.0; luật nào vẫn fail thì giữ. Nguồn eval mới là `candidates.md` từ 9.1. Đây là cách duy nhất để nói "model mới không cần X" bằng con số.

Agent khai `model:` bằng alias (`opus`, `sonnet`, `haiku`) nên tự trỏ model mới nhất; không cần sửa frontmatter.

### 9.3 Cách trình bày

Từ 2026-10-16 tài liệu của gói viết theo hướng dẫn humanizer: câu ngắn, không gạch ngang dài, không chữ đậm trang trí, kết luận đứng trước lý do. Bảng giữ dấu `·` khi cần gọn. Tài liệu cũ sửa khi chạm vào.
