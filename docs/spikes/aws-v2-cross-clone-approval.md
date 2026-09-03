# Spike · PM duyệt gate từ máy khác trên engine AWS `aidlc-workflows` v2

> Trạng thái: **XONG — kết luận có bằng chứng** · Ngày: 2026-09-03 · Chạy trên bản copy của `project-starter-template-ai` (upstream 2.5.75) trong scratchpad, ba clone giả lập ba máy, remote bare local. Không động template gốc.
> Câu hỏi: *một quyết định gate do người bấm trên tower (ngoài phiên Claude/Codex, trên máy khác) có được engine AWS v2 chấp nhận là gate-commit hợp lệ không?* — điều kiện tiên quyết của phương án **A** trong `../multi-user-shared-space.md` mục 2.1b.

## 0 · Kết luận

| # | Kết luận | Bằng chứng |
|---|---|---|
| 1 | **CÓ.** Máy B (PM, clone riêng, git user riêng) chạy `aidlc-orchestrate.ts report --stage intent-capture --result approved --user-input "Approve"` → engine ghi `GATE_APPROVED` + `STAGE_COMPLETED` vào **shard audit của B**, state `[x]`, `Current Stage` nhảy sang stage kế. Máy A pull về: `next` đi tiếp stage kế, `doctor` 49/49 pass. | log mục 3, bước 7–8 |
| 2 | **Blocker phải vá**: hook `aidlc-write-audit-log.ts` ghi trường `File` bằng **đường dẫn tuyệt đối** của máy ghi. Guard "artifact phải được ghi bằng tool harness sau khi người xác nhận tóm tắt" so `resolvePath(projectDir, File)` → trên clone khác không bao giờ khớp ⇒ approve bị từ chối. Guard đã chấp nhận đường dẫn tương đối, chỉ hook ghi sai. **Bản vá 4 dòng** (`aws-v2-write-audit-relative-path.patch`) → receipt tương đối, cross-clone qua. Consumer thứ hai (`producesArtifactUnit`) so bằng hậu tố nên không ảnh hưởng. | bước 5–6; patch kèm |
| 3 | **Điểm yếu**: guard "người có mặt" (`humanActedSinceGate`) là **toàn workflow, đọc mọi shard** — một `HUMAN_TURN` PM tạo trên B mở khoá approve cho **mọi** clone. Clone C (không có lượt người nào) approve cũng thành công. Engine kiểm *có người* chứ không kiểm *ai*; `GATE_APPROVED` không có trường actor. Định danh duy nhất là **tác giả commit git**. | bước 7: C và B cùng "Committed approve" |
| 4 | Shard audit theo clone-id **merge sạch** qua git (ba máy, ba file, không conflict). `aidlc-state.md` là một file ⇒ hai clone cùng approve rồi cùng push sẽ conflict — chấp nhận được vì gate tuần tự; tower phải `pull --rebase` ngay trước khi bấm và push ngay sau. | bước 7–8 |
| 5 | Để mở được gate, phía dev (trong phiên) phải qua **năm lớp guard theo thứ tự**: artifact tồn tại → xác nhận tóm tắt (decision với `[Answer]:` trống → người điền → answer; file bị khoá hash sau đó) → artifact được ghi lại **sau** xác nhận bằng tool harness → reviewer `REVIEW_REQUESTED`/`REVIEW_COMPLETED` → `awaiting-approval`. Tower chỉ lo bước cuối: approve. | bước 2–5 |

**Ý nghĩa cho phương án A**: khả thi. Tower = một script `bun` trên máy người duyệt làm bốn việc: `git pull --rebase` · ghi `HUMAN_TURN` (cùng seam với hook, kèm actor) · `report --result approved --user-input "<lựa chọn> — <tên> <email>"` · commit (author = git user người bấm) + push. Điều kiện: overlay bản vá hook vào template (và đề xuất upstream).

## 1 · Bố trí

```
scratchpad/spike/
├── remote.git      # bare, nhánh aidlc-v2
├── tpl/            # máy A — Dev A (deva@example.com), clone-id c6d529ca17b5
├── pmB/            # máy B — PM B  (pmb@example.com),  clone-id 6e505ccb2a37
└── devC/           # máy C — clone tươi, KHÔNG có HUMAN_TURN nào của chính nó
```

Intent `260903-spike-approve` (scope `feature`, 33 stage), gate thử: `intent-capture` (stage đầu sau init, có `summary_confirmation` và `reviewer: aidlc-product-lead-agent`). Không dùng biến bypass nào (`AIDLC_SKIP_*`).

## 2 · Cơ chế engine liên quan (đọc từ `aidlc-lib.ts` / `aidlc-state.ts` / hooks)

- `aidlc-state.ts approve|gate-start` bị chặn gọi trực tiếp — chỉ qua `aidlc-orchestrate.ts report --stage <slug> --result <…>`.
- **Presence guard**: approve chỉ qua khi có `HUMAN_TURN` **sau** resolution gần nhất (`GATE_APPROVED`/`GATE_REJECTED`/`QUESTION_ANSWERED`/`SUMMARY_CONFIRMATION_RECORDED`), xếp theo timestamp **trên mọi shard**; cùng giây khác shard ⇒ fail-closed. `HUMAN_TURN` do hook `UserPromptSubmit` ghi, là event **reserved** (CLI `aidlc-audit append` từ chối) nhưng hook chỉ gọi `appendAuditEntry("HUMAN_TURN", {}, pd)` — tower dùng cùng seam.
- **Artifact guard**: mọi `produces` phải tồn tại; với stage có xác nhận tóm tắt, mỗi artifact phải có `ARTIFACT_CREATED|UPDATED` (hook `PostToolUse` Write/Edit) **sau** `SUMMARY_CONFIRMATION_RECORDED`, và file câu hỏi bị **khoá hash** từ lúc xác nhận.
- **Reviewer guard**: stage khai `reviewer` cần cặp `REVIEW_REQUESTED` → `REVIEW_COMPLETED --verdict READY|NOT-READY --iteration n` (tool `aidlc-log.ts review`).
- Audit: một shard `audit/<host>-<clone-id>.md` mỗi clone; `aidlc/.aidlc-clone-id` mint lần đầu, gitignored.

## 3 · Log các bước (rút gọn, nguyên văn thông điệp engine)

| # | Máy | Lệnh | Kết quả |
|---|---|---|---|
| 1 | A | `aidlc-utility.ts intent-create --scope feature …` | `Intent created … First post-init stage: intent-capture` |
| 2 | A | tạo 3 artifact tối thiểu → `report --result awaiting-approval` | ✗ `must contain exactly one [Answer]: Looks correct in its Consolidated Summary Confirmation section` |
| 3 | A | thêm mục tóm tắt với `[Answer]:` trống → `aidlc-log decision --checkpoint summary-confirmation` → điền `Looks correct` → `HUMAN_TURN` (chạy hook) → `aidlc-log answer --details "Looks correct"` | `SUMMARY_CONFIRMATION_RECORDED` |
| 4 | A | `report awaiting-approval` | ✗ `has no recorded native-tool write after the human's consolidated summary confirmation` → chạy hook `aidlc-write-audit-log.ts` cho 3 file (không đổi nội dung file câu hỏi — đổi là ✗ `changed after the human confirmed its summary`) → ✓ `Recorded awaiting-approval`, state `[?]`. Push. |
| 5 | B | pull → `HUMAN_TURN` → `report --result approved --user-input Approve` | ✗ **`intent-statement.md has no recorded native-tool write after …`** — receipt của A ghi `File: /…/spike/tpl/aidlc/…`, trên B đường dẫn là `/…/spike/pmB/…` ⇒ không khớp. **Blocker #2.** |
| 6 | B | sửa `File:` trong shard của A thành tương đối (giả lập hook đã vá) → approve | ✗ chuyển sang guard kế: `declares a reviewer … but no fresh REVIEW_COMPLETED` ⇒ path guard đã qua |
| 7 | A → C, B | A: `aidlc-log review --iteration 1` rồi `--verdict READY`, push. C (không HUMAN_TURN riêng): approve → **✓ `Committed approve`**. B: approve → **✓ `Committed approve`**; shard B có `GATE_APPROVED · User Input: Approve` + `STAGE_COMPLETED`; state `[x] intent-capture`, `Current Stage: market-research`. B push. |
| 8 | A | pull → `next` → `{"kind":"load-steering","stage":"market-research"}` · `doctor`: `49 passed, 0 failed`, không còn `gate-unresolved`. `git log`: `PM B  decision: approve intent-capture` trên đầu. |
| 9 | A | vá hook thật (patch kèm), chạy lại hook cho một artifact | `File: aidlc/spaces/default/intents/…/intent-statement.md` (tương đối) |

## 4 · Việc rút ra cho gói `ai-dlc` (phương án A)

1. **Overlay bắt buộc**: áp `aws-v2-write-audit-relative-path.patch` vào `.claude/hooks/aidlc-write-audit-log.ts` (và bản `.codex/`) của template; ghi vào `sources/aidlc-integration/` như overlay đi cùng lock; gửi upstream `awslabs/aidlc-workflows` (một dòng, guard đã sẵn sàng nhận tương đối).
2. **Tower-approve script** (`bun`, chạy trên máy người bấm): `git pull --rebase` → kiểm gate còn `[?]` → ghi `HUMAN_TURN` qua `appendAuditEntry` **kèm trường `Actor: <tên> <email>`** (hook hiện ghi `{}`) → `report --result approved|rejected --user-input "<lựa chọn> — <tên>"` → commit + push; push bị từ chối ⇒ pull lại và kiểm gate còn mở rồi mới thử lại.
3. **Định danh là việc của tower, không phải engine**: tower đối chiếu git user với `governance/raci.md` (hoặc `memory/team.md`) **trước** khi hiện nút; engine không kiểm ai. Kết luận #3 phải ghi rõ trong tài liệu đội: *engine không chặn C dùng lượt người của B* — tower là nơi duy nhất giữ luật "đúng người".
4. **Xác nhận tóm tắt** (`Preview → Confirm` của team) là lượt người **thứ hai** trước gate, và khoá hash file: trong mô hình A nó thuộc **Team Lead trong phiên** (dev side); nếu muốn PM xác nhận từ tower thì cùng cơ chế với approve (decision → answer), nhưng file câu hỏi không được đổi sau đó.
5. **Không cần**: `.ai-dlc/` riêng, ID mới, file tổng hợp sinh — engine đã có shard per clone, worktree, swarm. Phần 7.0.0 "đổi format bản ghi" của `../multi-user-shared-space.md` mục 5 **bỏ**; thay bằng "tower đọc `aidlc-state.md` + audit".

## 5 · Chưa thử

- Gate ở stage **per-unit** Construction (`for_each: unit-of-work`, reviewer per unit, swarm/worktree) — cùng guard nhưng đường dẫn `construction/<unit>/…`; patch dùng `relative` nên kỳ vọng qua, chưa chạy.
- Hai người approve hai gate khác nhau cùng lúc rồi cùng push (conflict `aidlc-state.md`).
- Harness Codex (`.codex/hooks`) — cùng hook, chưa chạy.

## 6 · Bổ sung cùng ngày — `plugin/scripts/tower_approve.ts` chạy thử

Script bun trên máy người duyệt, đúng bốn bước ở mục 0 (+ kiểm gate `[?]` trước, kiểm `[x]` sau, retry push một lần sau `pull --rebase`). Thử trên clone mới `pmD` (git user "PM D") tại commit gate đang mở:

| Bước | Kết quả |
|---|---|
| `--dry-run` | `{"ok":true,"dryRun":true,…,"actor":"PM D <pmd@example.com>"}` — không ghi gì |
| chạy thật | `{"ok":true,"stage":"intent-capture","result":"approved","state":"x","commit":"cc06dd3","pushed":true}` |
| audit shard của D | `HUMAN_TURN` có **`Actor: PM D <…>` · `Source: tower` · `Stage`**; `GATE_APPROVED · User Input: Approve — nội dung intent đúng phạm vi — PM D <…>` |
| git | `cc06dd3 PM D <pmd@example.com> decision(260903-spike-approve/intent-capture): approved — PM D` |
| chạy lại | `Stage intent-capture đang ở [x], không phải [?] … không có gì để quyết` — chặn duyệt hai lần |
| clone khác pull | state `[x]`, `next` → `market-research`, doctor `49 passed, 0 failed` |

Điểm còn thiếu cho bản dùng thật: đối chiếu git user với RACI **trước** khi cho chạy (hiện chỉ bắt buộc có identity), và một bước "Actor có trong `memory/team.md`" — engine không kiểm nên script phải kiểm.
