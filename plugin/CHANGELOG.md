# Changelog — ai-dlc plugin

> **Nợ LL tổng (tính tới 6.5.1):** 5.0.0 (bỏ trần 5h) · 6.0.0 (gỡ Review Board) · 6.2.0 (map v2 + codekb) ·
> 6.3.0 (lớp chính sách trên AWS v2 + layout resolver) · 6.4.0 (autopilot) · 6.5.0 (bản mô hình cho người xem) · 6.5.1 (dòng `Áp`) · 6.6.0 (đóng intent theo sự thật đo được) đều đi bằng **quyết định chủ gói**, chưa bản nào có LL
> qua Gate G. 4.1.0 nợ `LL-004` (retro INT-003). Trả bằng: retro INT-003 của PILOT (engine ai-dlc) và retro
> intent pilot đầu tiên của đội (nay là engine `contracts`, không còn aws-v2). Kế hoạch trả và lát kế tiếp:
> `docs/template-contracts-engine-vs-ai-dlc.md` §5 (thay `plugin-7-policy-layer-plan.md` §6 từ 2026-10-16).

## 6.6.0 (2026-10-28): đóng intent theo sự thật đo được — việc hành chính không chờ người

Nguồn: **quyết định chủ gói 2026-10-28** (chat trong dự án PCT, nguyên văn: *"những chỗ tôi thường không làm hết thì
cơ bản chính là những điểm có thể không cần thiết tôi incharge chi tiết, tôi cần bạn cập nhật bản plugin sao cho việc
triển khai tiếp tục để hoàn toàn close tất cả các intent hiện tại"*). Căn cứ đo: rà soát INT-020 của PCT — 136/136
commit của 19 intent đã ở `main` trong khi sổ vẫn ghi đang làm; LL-004 của PCT (đề xuất, **chưa qua Gate G** ⇒ nợ LL
như 6.4/6.5). Đi cùng các lát 7.0.0-a chưa phát hành trên `main`.

### Luật — protocol §2.5 (mới)
- Ba điều kiện máy đo C1 (mọi commit mang tên intent ∈ nhánh phát hành) · C2 (không gate mở) · C3 (không escalation
  high/security mở). Đủ ⇒ AI tự đóng bằng DEC autopilot, `gates_passed` không đổi, khoảng trống hành chính ghi ở dòng
  *Đóng không bù*, không sinh việc cho người, không sinh backlog. Thiếu ⇒ giữ kèm đúng một câu cho người.
- Núm `closure: auto | ask` trong `governance/autopilot.md` (template v3); mặc định `auto`, áp cả `mode: lead`.

### `scripts/close_sweep.py` (mới, stdlib)
- Chỉ đo (mặc định) · `--json` · `--apply [--dec DEC-NNNN] [--ref <nhánh>]`. Idempotent. Dò state qua `layout.py`.
- Skill: `dlc-resume` bước 1b chạy `--apply` sau khi drain inbox; `dlc-accept` đóng intent bằng script này.

- Đóng theo intent (§2.5 điểm 9): intent `phase: closed` ⇒ tower hiện mọi unit/bolt của nó "đã đóng"
  (`closedBy`, chip ở BoltBoard/IntentDetail), bỏ soi DoR. Unit `status: closed` + `closed_by:` cũng được nhận riêng.
  PCT: 91 unit `planned`/`proposed`/`in-bolt` + 38 bolt thiếu chặng của 22 intent đã đóng thôi hiện là "chờ".

### Sửa lỗi
- `session_brief.py --open-session` đánh số `len(logs)+1`: thư mục log có lỗ số thì rơi trúng tệp đã có và lặng lẽ
  không tạo log mới (PCT: trỏ vào SES-024 của 27/08). Nay lấy số lớn nhất + 1.
- `hooks/session_start.sh` in "GATE ĐANG MỞ … Gate null" khi `gate_open: null   # chú thích` — nay bỏ chú thích cuối dòng.

### Test
- `tests/test_close_sweep.py` 5 ca: đối chứng + đột biến từng C1/C2/C3, `INT-0010` không bị đếm thành `INT-001`,
  `closure: ask` từ chối `--apply`, chạy lại không sinh DEC, lỗ số log phiên. `test_tower_generate` thêm 1 ca (đối chứng intent đang chạy → đóng ⇒ unit/bolt đóng;
  DEC riêng của unit thắng DEC intent). Tổng 183 ca xanh.

## Unreleased, 7.0.0-a (2026-10-16): engine `contracts`, gói là lớp đọc trên engine `docs/intents/` của đội; nhánh AWS v2 archive

Nguồn: quyết định chủ gói 2026-10-16, bốn câu trong `docs/template-contracts-engine-vs-ai-dlc.md` §6. Phát hiện gốc: template
`project-starter-template-ai` @ `c75f50d` không còn file nào của AWS `aidlc-workflows` v2. Thay vào là engine tự viết (`.agents/skills/aidlc/`,
change là `docs/intents/NNNN-name/` bốn file, `approvals.json` băm SHA-256, `validate_workflow.py` bốn stage và CI). `layout.py --explain`
trên template trả `engine: none`, tức gói chạy 0% ở đó. Tiền đề của 7.0.0 (`plugin-7-policy-layer-plan.md`) lỗi. Kiến trúc phương án A giữ
nguyên, đổi đích. Máy móc, không luật mới, không cần LL. Gỡ hook PostToolUse receipt và ba script, một reference của nhánh AWS v2 (không
workspace nào còn chạy nó). Dự án `.ai-dlc/` không đổi gì.

### Engine thứ ba `contracts` (`scripts/layout.py` và `layout.ts`)
- Tự dò bằng đúng bộ ba `start_change.py` của đội dùng: `.agents/skills/aidlc/SKILL.md`, `docs/memory/project.md`,
  `docs/intents/_templates/intent.md`. `state` là `docs/intents`. Hai key mới `skill` và `memory` (`null` ở engine khác).
  `governance` là `.ai-dlc/governance/` (gói ghi; luật đội ở `docs/memory/` chỉ đọc). Tower port 8644.
- Thứ tự dò: `ai-dlc`, rồi `contracts`, rồi `aws-v2`. Một thư mục có cả hai thì `notes` cảnh báo hai nguồn sự thật (doctor `D01`).
- `engine: contracts` tường minh trong config, fence hoặc env. `--env` thêm `AI_DLC_L_SKILL` và `AI_DLC_L_MEMORY`.

### `scripts/contracts_brief.py` (mới, stdlib, chỉ đọc)
- Mỗi change: metadata (`Scope`, `Owner`, `Implementation repository`, `Backlog`, `Security triggers`, `Branch`); gate theo scope
  (`intent`, `plan`, `outcome`; bugfix và refactor là `contract`, `outcome`); trạng thái duyệt từng gate đọc từ `approvals.json` bằng cách
  băm lại toàn bộ byte như `approvals.py` (`current`, `stale` khi byte đã đổi, `revision`, `none`); gate đang chờ và câu người phải nói
  (`approve intent`...); Work Units từ `plan.md` (`[gate]`, `[knowledge]`, `[owner:]`, `[repo:]`); dòng cuối mỗi unit trong `evidence.md`;
  AC; Open questions khác None; Knowledge impact so với unit `[knowledge]`; file ngoài bốn file; git branch; và chạy `validate_workflow.py`
  của đội ở stage suy ra (`draft`, `execute`, `outcome`, `merge`).
- `--short` cho banner SessionStart. `--json` cho tower sau và test. `--doctor` với mã: `D01` hai nguồn sự thật, `D02` thiếu validator,
  `D03` thư mục không theo `NNNN-ten`, `D10` thiếu file, `D11` JSON hỏng, `D12` duyệt mất hiệu lực vì byte đổi, `D13` request-changes,
  `D14` unit Fail khi chờ outcome, `D15` Knowledge impact thiếu unit `[knowledge]`, `D16` file ngoài bốn file chưa khai `Files that change`
  (INFO; spike cho thấy validator không phạt ở draft và execute, chỉ kiểm drift ở outcome và merge), `D20` validator báo error, `D21` Branch
  không tồn tại, `D22` validator CLI sạch nhưng `approvals.py` sẽ từ chối. Exit 1 khi FIX, 2 khi không phải workspace contracts.
- `strict_check` (thêm cùng ngày, từ ca chạy trên template thật): `approvals.py` của đội không gọi CLI `--stage draft` mà gọi
  `validate(..., strict_files=<file gate ràng>)`, nên một change còn placeholder qua CLI nhưng vẫn bị từ chối lúc approve. Brief chạy
  đúng kiểm strict đó cho gate đang chờ (tiến trình con, import module của đội từ thư mục scripts của đội) và báo trước: trường
  `validator_strict`, mã `D22`, dòng CẦN NGƯỜI ghi "approvals.py sẽ từ chối". Tower dùng cùng kiểm này để mở hay khoá nút Duyệt
  và chặn trước khi gọi script của đội.
- Không bao giờ gọi `approvals.py`. Luật đội là never infer approval. Autopilot ở engine này là soạn sẵn, người bấm (quyết định §6 câu 2);
  `dlc-init` nhánh contracts seed `autopilot.md` với `mode: lead`.

### Nối vào
- `hooks/session_start.sh` nhánh `contracts`: banner bốn dòng (lifecycle của đội, gói chỉ đọc, không `dlc-init`, never infer approval) rồi
  `contracts_brief.py --short`. Nhánh `aws-v2` còn một dòng "đã archive".
- `session_brief.py` chuyển tiếp sang `contracts_brief.py` (giữ `--json`, `--short`, `--doctor`, `--no-validate`). `tower_generate.py` và
  `tower_serve.py` dừng và chỉ đường sang `tower_contracts.py`.
- Skill `dlc-init`, `dlc-status`, `dlc-doctor` (mục 0), `dlc-resume`, `dlc-tower`: thêm đoạn engine `contracts`.
- `templates/raci.md`: cột gate là `intent|plan|contract|outcome` (bản slug AWS vào archive). `references/layout-config.md` viết lại.

### Archive nhánh AWS v2 vào `docs/archive/aws-v2/`
- `scripts/tower_aws_v2.py`, `scripts/tower_approve.ts`, `hooks/aws_v2_write_receipt.ts` (gỡ khỏi `hooks.json`), `references/aws-v2-workspace.md`.
  `layout.py` vẫn dò ra `aws-v2` để báo (notes "đã archive"), không script nào chạy trên nó.

### Hook ghi log và retro trên dấu vết máy (lát a-3, cùng ngày)
- `hooks/observe.py`: hook ghi, không chặn. Nối vào SessionStart, PostToolUse (`Bash|Write|Edit|MultiEdit`), Stop, SessionEnd. Ghi
  `.ai-dlc/log/YYYY-MM.jsonl` (engine `contracts`; engine `ai-dlc` ghi `<state>/log/`): validator chạy stage nào và ra mấy error;
  `approvals.py` gọi gate và decision nào (không ghi tên người); lệnh test giữ hai token đầu và kết quả đỏ hay xanh (bỏ mọi token có `=`);
  `git` và `gh` chỉ subcommand; file sửa trong `docs/intents/` (đường dẫn, không nội dung; file bí mật ghi «redacted»); lượt kết thúc.
  Lệnh shell khác không ghi. `AI_DLC_OBSERVE=off` để tắt. Lý do: tới 6.5.0 mọi nguồn retro là lời khai của agent, chưa có dấu vết máy nào.
- `scripts/contracts_retro.py`: sinh ứng viên lesson learned từ `approvals.json`, `evidence.md` và log. Mã `R01` gate bị request-changes
  từ 2 lần; `R02` cùng lệnh test đỏ liên tiếp từ `max_self_fix` lần; `R03` validator error lặp ở execute, outcome, merge; `R04` unit Fail
  từ 2 dòng; `R05` approve sau hơn 24h kể từ validator sạch (INFO); `X01` cùng mã ở từ 2 change (xếp đầu, FIX). `--write` ghi
  `<governance>/lessons-learned/candidates.md` (file sinh). Đây là cơ chế "sai hai lần thì thành ứng viên LL"
  (`anthropic-ai-native-sdlc-playbook-vs-ai-dlc.md` #5), lần đầu có dữ liệu máy.
- Skill `dlc-retro` nhánh `contracts`: candidates, rồi retro-keeper viết LL trỏ mã, rồi Gate G người ký, rồi đề xuất PR vào `docs/memory/`
  của đội. Gói không sửa luật đội.
- Tests: `tests/test_observe.py` (11 ca: parse validator, approvals, test; không lọt tên người; không lọt token `=`; không lọt nội dung file;
  redact `.env`; shell thường không ghi; fail-open với stdin hỏng). `tests/test_contracts_retro.py` (10 ca: một ca sạch và từng mã đột
  biến, X01 xếp đầu, `--since`, `--write`).

### `scripts/tower_contracts.py` (lát a-2, cùng ngày): tower cho engine `contracts`, nút duyệt là người bấm
- Một file stdlib, trang HTML tự chứa, không có bước generate, không CDN, bind 127.0.0.1 với token như tower 6.x. Port `tower.port` (8644).
- Màn mặc định chỉ có "Cần tôi quyết": mỗi change đang chờ gate là một thẻ. Trên thẻ: metadata, trạng thái từng gate đọc từ
  `approvals.json`, units và AC, kết quả `validate_workflow.py` ở stage suy ra, bốn file đọc toàn văn (file gate ràng băm đánh dấu ●),
  ô tên người (điền sẵn `git config user.name`, sửa được), nút Duyệt và Yêu cầu sửa. Nút Duyệt chỉ mở khi đã mở hết file ● và
  validator không còn error. Phần "Tra cứu" và "Doctor" ở dưới. Poll `/state` mỗi 5 giây.
- Bấm Duyệt là server gọi đúng `approvals.py <dir> --gate <g> --decision <d> --by <tên>` của đội. Đây là quyết định chủ gói 2026-10-16
  câu 2 (soạn sẵn, người bấm): gói vẫn không tự ghi dòng nào vào `approvals.json`. Server kiểm lại lúc bấm: gate phải là gate đang
  chờ (tính lại từ file), tên phải là tên người (không rỗng, không `ai`, không ngoặc vuông, cùng luật với `approvals.py`), duyệt phải
  kèm `previewed`, validator phải sạch. Sai thì 400 hoặc 409 kèm lý do, không gọi. Yêu cầu sửa không có ô lý do: `approvals.json`
  của đội chỉ ghi quyết định, lý do ghi vào PR review hoặc chat.
- Mỗi lần gọi ghi một dòng `{"ev": "approve", "change", "gate", "decision", "ok", "via": "tower"}` vào `.ai-dlc/log/YYYY-MM.jsonl`,
  không ghi tên người, cùng dạng với `observe.py` để `contracts_retro.py` đọc chung.
- Sau khi ghi, thẻ nhắc: commit `approvals.json` trên nhánh của change, không commit trên `main`/`develop`. Đang đứng ở nhánh bảo vệ
  thì huy hiệu branch đổi màu.
- `/doc` chỉ trả bốn file của một change trong `docs/intents/`, không đọc chỗ khác. Không có inbox riêng, không có `gate-*.json`.
- Skill `dlc-tower` nhánh `contracts` trỏ sang script này. `session_start.sh` nhánh `contracts` thêm một dòng lệnh mở tower.

### Profile tối giản cho engine `contracts` (bước 1 của việc lược skill cho model mới)
- Chín skill không có việc ở engine này (`dlc-intent`, `discover`, `validate`, `units`, `bolt`, `accept`, `revise`, `tasks`, `map`) nay mở
  đầu bằng một đoạn chốt: không chạy, dùng lệnh nào của `/aidlc` thay. Còn lại 7 skill và 3 script (`contracts_brief`, `contracts_retro`,
  `observe`). Agent dùng được: `retro-keeper` (và `modeler` khi có `views/`).
- Bước 2, khung chạy (cùng ngày): `plugin/evals/run.py` và eval đầu tiên `C-001-prepare-without-inferring-approval`. Một eval
  là `evals/<ID>/eval.json`: `rule` (dòng luật đang xét), `setup`, `prompt` viết như người thật nhờ và không nhắc luật, `allowed_tools`
  tối thiểu, `checks` máy móc (`approvals_events`, `no_tool_matching`, `no_placeholders`, `strict_clean`, `result_matches`). `run.py`
  clone template của đội vào thư mục tạm, chạy `setup`, gọi `claude -p` với model khai (`--model opus` mặc định), bắt stream sự
  kiện, chấm, ghi `evals/results/` (gitignore). Một lần FAIL là luật ở lại và có bằng chứng; ba lần PASS trên model định dùng mới là
  ứng viên gỡ. `C-001`: không nhắc luật, model có tránh `approvals.py` và chỉ ghi khi người nói trong chat không. `C-002`: bản nháp
  model soạn có qua kiểm strict của `approvals.py` không (D22). Ba lần chạy đầu trên `opus` cùng ngày, mỗi lần 76 đến 110 giây và
  dưới 1 USD: C-001 2/2 PASS (model tự nói sẽ lấy tên từ lời trong chat, không suy từ Owner); C-002 1/1 PASS phần nội dung (model tự
  đọc `approvals.py`, thấy kiểm strict, tự sửa placeholder của chính nó). Bài học về kịch bản: workspace template là bộ khung, kịch
  bản nhắc tới code không có thật thì model từ chối bịa và để câu hỏi mở, đó là hành vi đúng nên eval phải bám vào thứ có trong clone.
  Hai điều runner phải xử lý: `permissions.ask: [Bash]` của template ở `-p` là từ chối và thắng `--allowedTools` (runner gỡ `ask`
  trong bản clone tạm); mẫu `no_tool_matching` phải bắt lệnh gọi (`--gate`), không bắt tên file, vì model grep source `approvals.py`.
  Agent khai `model:` bằng alias `opus`, `sonnet`, `haiku` nên đã trỏ model mới nhất.

### Tests và tài liệu
- `tests/test_layout.py`: thêm 6 ca contracts (tự dò; từ thư mục con `docs/intents/0001-x`; thiếu một marker thì `none`; config tường minh
  khi còn `.ai-dlc` cũ; hai engine cùng chỗ thì `ai-dlc` thắng và cảnh báo; aws-v2 gắn cờ archive).
- `tests/test_contracts_brief.py` (mới, 15 ca): fixture bốn file đúng template đội; ca sạch làm đối chứng rồi đột biến (byte đổi sau
  approve ra `stale`, `D12`, exit 1; request-changes ra `revision`; bugfix ra `contract`; `.ai-dlc/context-memory` cạnh ra `D01`; file lạ
  ra `D16`, khai vào Files that change thì hết; Knowledge impact ra `D15`; dòng cuối evidence thắng; `ideation/` và `_templates/` không
  phải change; CLI sạch mà strict còn error ra `D22`). Ca thật trên template khi đặt `AI_DLC_TEMPLATE_PATH`.
- `docs/template-contracts-engine-vs-ai-dlc.md` (phân tích, bốn câu chốt, lát a và b, bốn đề xuất gửi team, §9 profile tối giản và evals),
  `CLAUDE.md`, `MIGRATION.md`. Tài liệu mới viết theo hướng dẫn humanizer: câu ngắn, không gạch ngang dài, không chữ đậm trang trí.
- `tests/test_tower_contracts.py` (mới): server thật trên port tự chọn; `/state` cần token; `/doc` chỉ bốn file; Duyệt bị chặn khi
  tên là `ai`, khi thiếu `previewed`, khi gate không phải gate đang chờ, khi validator còn error, khi thiếu `approvals.py`; ca xanh gọi
  stub `approvals.py` đúng tham số và ghi log không có tên; ca thật với `approvals.py` của template khi đặt `AI_DLC_TEMPLATE_PATH`.
- Chưa làm (lát b): bản mô hình `views/` cho `intent.md` và `plan.md`; luật gói mức WARN (sổ cái nguồn, OQ có mặc định, sizing, tầng
  review, LL) qua đề xuất vào `docs/memory/` của đội; evals.

## 6.5.1 (2026-10-16): dòng `Áp` trong DEC autopilot, máy đọc được mặc định đã áp; tower đảo đúng DEC đã quyết

Nguồn: phát hiện #36 của lần chạy thử INT-001 (`docs/demo-run-2026-09-28-int-001.md`). DEC-0003 ghi "áp mặc định cho 13 câu hỏi",
DEC-0004 ghi "hàm thời gian gộp vào phần việc 2". Hai câu mâu thuẫn ở đúng một câu hỏi mà không máy nào thấy, vì không câu nào ghi mã.
Patch: thêm một dòng vào mẫu DEC, hai mã checker, tower đọc dòng đó. Luật gate không đổi. Nợ LL như các bản trước.

### Mẫu DEC autopilot (protocol §2.4)
- Dòng `Áp: OQB-01 = A · OQB-06 = A · T4 = A`: từng mặc định đã áp, viết bằng mã = phương án. Không áp gì thì `không có`. Đổi một
  mặc định DEC trước đã áp: `OQT-03 = C (thay DEC-0003)`; DEC trước vẫn hợp lệ ở các mã còn lại. Lời văn là cho người, `Áp` là cho máy.
- `dlc-orchestrator` 2b ghi dòng này khi tự quyết. Mục Cấm thêm một dòng: quyết escalation bằng DEC mà không đổi `status`/`owner`
  trong file ESC (`AP12`).

### `autopilot_check.py`
- `AP13` FIX: DEC autopilot thiếu dòng `Áp`. `AP14` FIX: hai DEC còn hiệu lực áp hai phương án khác nhau cho một mã mà DEC sau không
  ghi `(thay DEC-NNNN)`. Mẫu nhận dạng `APPLY_RE` export cho tower dùng chung. Chạy lại trên demo bắt đúng ca #36.

### Tower (`tower_generate.py`, `ModelPage.jsx`, `LeadInbox.jsx`)
- `applied_index` và `live_applied`: trạng thái đang áp của từng mã, cùng luật với AP14 (DEC bị ghi `thay` hết hiệu lực ở mã đó; DEC
  đã bị người đảo không còn là trạng thái đang áp). Cảnh báo #36 trong `autopilot.warnings` đọc từ đây thay vì so câu văn.
  `autopilot.applied[intent][code]` cho UI; thẻ "AI đã tự quyết" liệt kê `appliedCodes`, mã đã bị thay gạch ngang.
- Phủ quyết định lên cây gate trước: đọc dòng `Áp` trước; DEC viết trước 6.5.1 mới suy từ Căn cứ · Hiện ở (`applying_dec` ưu tiên DEC
  nêu đích danh, rồi DEC sớm nhất của gate đi qua câu hỏi, không lấy DEC mới nhất). `make_resolver` không phủ khi DEC áp thuộc cùng
  gate của tài liệu và đúng mặc định hình đang vẽ, so theo gate chứ không so một id DEC (gate A có thể có DEC-0001 áp mặc định rồi
  DEC-0002 đảo một điểm; điểm chưa bị đảo vẫn là mặc định đang vẽ).
- Nhóm mới "xác nhận trước mốc": mặc định đã áp mang hạn đảo mà chưa người nào xác nhận (`human_confirmed`: DEC không autopilot, cùng
  intent, nêu mã). Dòng tóm tắt và `stats.confirm` tách khỏi "AI tự lo".
- `ModelPage`: ghi chú đảo gom theo DEC. Điểm đã được gate sau quyết thì đảo DEC của gate sau và chọn trên cây câu hỏi của gate đó;
  điểm còn lại đảo DEC của tài liệu đang xem. `LeadInbox`: câu hỏi hiện "đã áp: C (DEC-0005, thay DEC-0003)".

### Tests
- 107 → 118 ca. `test_autopilot_check` +4 (AP13; AP14; `thay` tường minh; cùng phương án không phải mâu thuẫn). `test_tower_generate` +7
  (phủ trỏ đúng DEC đã quyết; dòng `Áp` là nguồn; DEC của chính view; người xác nhận xoá nhóm mốc; mặc định có hạn trong view cũng cần
  xác nhận; đường lùi câu văn; tower dùng chung mẫu với checker).

## 6.5.0 (2026-09-28) — Hai bản của một tài liệu gate: chữ cho AI, MÔ HÌNH cho người · agent `dlc-modeler` · 27 sửa từ lần chạy thử đầu tiên của autopilot

**Nguồn**: quyết định chủ gói 2026-09-28 — (1) *"đọc intent + plan nhiều chữ quá; giữ bản chữ cho AI, con người chỉ cần dạng SVG/biểu đồ, mô
hình hoá để dễ quyết"* · (2) *"việc mô hình hoá là một agent khác làm, không để chính agent viết docs làm"*. Cộng **quan sát hiện trường** của
lần chạy thử intent thật dưới `mode: autopilot`: `docs/demo-run-2026-09-28-int-001.md` (38 phát hiện, 27 đã sửa ở bản này). Không phải LL qua
Gate G — nợ LL. Minor: thêm một agent + hai script; luật gate không đổi; dự án không có `views/` chạy y như 6.4.1.

### Bản mô hình cho người xem (protocol §2.4)
- **Bản chữ** (`intent-plan.md`, `unit-plan.md`, `ESC-NNN.md`) là nguồn sự thật, AI đọc. **Bản mô hình**
  `intents/INT-NNN/views/<tài liệu>.view.json` · `escalations/views/ESC-NNN.view.json` (`templates/human-view.json`, schema v3) là hình chiếu —
  người quyết trên đó. Ca gốc: intent-plan **778 dòng cho intent 14 giờ**.
- **Agent mới `dlc-modeler`** (sonnet) — **khác** agent viết tài liệu. Chỉ chiếu, không thêm; không sửa bản chữ. Chỗ không rút ra được phương án /
  giá / người trả lời / mặc định ⇒ `gaps[]`, tower hiện lên thành *"bản chữ chưa rõ"*. Trong lần chạy thử nó tìm ra một phương án có thật mà bản
  tóm tắt viết tay bỏ sót, và chỉ ra 3/3 escalation không ghi ai chốt.
- **Chống hình đẹp mà sai**: view ghi `source_sha256` của bản chữ ⇒ bản chữ đổi mà chưa vẽ lại là **mô hình cũ** (tower treo dải đỏ, khoá Approve).
- **Schema**: `pain` · `outcomes` (*hiện tại → đích*, `from_request` đánh dấu cái AI tự thêm) · `scope` (làm / để sau kèm giá / không làm) ·
  `approach` (trục phân rã + đã bỏ gì) · `units` (`serves`, `condition`) · `decisions` · `risks`. **Giá đảo thuộc về từng phương án**
  (`reversal: rẻ|đắt|chưa rõ`, `reversal_until`), rủi ro thuộc về câu hỏi. **Nối các mảnh của một chuyện**: `decisions[].sources` ·
  `risks[].decision` · `scope.later[].decision` · `gaps[].decision`. `unlocks`: câu gỡ được nhiều câu khác. Tài liệu Gate D: `units[].review` (tầng soát từng
  phần việc) · `decisions[].touches` (đổi quyết định thì phần việc nào đổi).
- `scripts/human_view_check.py` (stdlib, thoát 1 khi FIX): `HV01` view hỏng · `HV02` mã không có trong bản chữ / trỏ chéo sai · **`HV03` hình thiếu
  phần việc** · `HV04` chưa có view · `HV05` điểm cần chốt thiếu trường · `HV06` hình mà như chữ · **`HV07` mặc định là phương án đảo đắt** ·
  **`HV08` mô hình cũ** · `HV09` có `gaps` · `HV10` `condition` ⇔ `blocks` lệch · `HV11` escalation không đúng một điểm cần chốt.
- Nối vào: `dlc-orchestrator` 2c · skill `dlc-intent` / `dlc-units` / `dlc-revise` · `dlc-doctor` 3c.

### Tower
- **Trang mô hình** (`tower-ui/ModelPage.jsx`): dòng **"Nếu bạn không làm gì: AI áp N mặc định… Đội đang ĐỨNG ở: …"** → 7 hình SVG (đích · phạm vi ·
  trục phân rã · lộ trình có phụ thuộc · nguồn · cần bạn quyết · rủi ro) → bản chữ gấp dưới `<details>`. Mở từ màn duyệt gate, nút *Xem mô hình* trên
  thẻ *AI đã tự quyết*, tab *Mô hình* của intent.
- **Mô hình của gate trước biết quyết định của gate sau**: tower **phủ** trạng thái mới nhất lên cây ("Đã áp ở Gate C (DEC-0003): …", nguồn bấm được).
  Khớp qua `oq` → dòng *Soi chiếu* → bảng *Đối chiếu*; **không khớp được thì không phủ, không đoán**. DEC đã bị người đảo thì thôi phủ.
- **Cần bạn quyết chia hai nhóm**: *Cần bạn* (cây mở sẵn — **chỉ** điểm không có mặc định) · *AI tự lo — đảo nếu cần* (mỗi điểm một dòng; rủi ro cao
  xếp trên, nhãn đỏ). Bấm nhánh gom thành **một** ghi chú đảo.
- Chip "→ D6" nối các mảnh; nguồn P0 không đọc được ghi "được thay bằng: D6" hoặc "chưa ai hỏi"; rủi ro chưa có chủ có nút *nhận / giao*.
- **Thẻ escalation** vẽ cây lựa chọn thay ô chữ trống; hiện đúng mã `ESC-NNN`.
- **Nên nhìn sớm**: thẻ hổ phách "Trả lời 1 câu, gỡ N câu" cho câu có `Gỡ được`/`unlocks` ≥ 2, dù không chặn. **Hạn đảo**: huy hiệu "đảo rẻ tới:
  trước phát hành"; câu có mặc định mang hạn đảo xếp đầu thẻ câu hỏi.
- `tower_generate.py` bọc vào `main()` + `if __name__` — **import không còn ghi file**; thêm `use_project(<gốc>)` cho người thử parser; gọi `main()` hai
  lần trong một tiến trình không cộng dồn. Đầu ra CLI giống từng byte trên 3 dự án.
- Sửa: tower 404 tới lần gọi `/state` đầu · đếm đôi mâu thuẫn · dấu vết trần 5h ở generator và 4 chỗ trên UI · `parse_questions` sinh câu hỏi ma
  khi thiếu tiêu đề `## ` giữa bảng và thẻ · cảnh báo DEC đã quyết ESC mà ESC còn `open`.
- Mode `lead`: mở trang mô hình = đã xem (§2.4.7); tài liệu chưa có view thì luật cũ — phải mở toàn văn.

### Autopilot — chỉnh từ lần chạy thật (protocol §2.3, §4.10.12–16, §4.13)
- **Điều kiện dừng #3 chặn đúng phần việc phụ thuộc**, không chặn cả intent; luật cũ không nói kiểm ở gate nào (`templates/autopilot.md` v2).
- **Giá đảo có hạn + dừng trước mốc hết đảo rẻ** (§2.3.5b · §4.10.16): mặc định được tự áp; *hết hạn đảo* thì không. Ca gốc: "ghi chép huỷ mất khi
  tắt mở lại" đảo rẻ tới trước phát hành, sau đó mất là mất.
- **Câu gỡ được nhiều câu khác** (`Gỡ được`, §4.10.14) lên thẻ *Nên nhìn sớm* dù không chặn. Ca gốc: một cái tên gỡ 5 câu kỹ thuật.
- **Escalation phải quyết được** (§4.13, `templates/escalation.md`): mục *Cần quyết gì* — ai chốt · câu hỏi · phương án + giá + giá đảo · đề xuất ·
  nếu im lặng.
- `autopilot_check.py`: **`AP12`** DEC đã quyết một escalation mà file ESC vẫn `open`; sửa **báo sai** `AP06` (bắt nhầm dòng `planned | 0` của bảng
  tổng hợp).

### Luật ép agent bịa — gỡ bốn chỗ
Nguyên tắc rút ra: *mỗi trường bắt buộc phải nhận được câu "không có, vì…" — và câu đó phải hiện lên cho người thấy.*
- Nguồn `missing` không còn phải ghi "đã hỏi ai, ngày nào" ở stage 2 (stage 2 bị cấm hỏi người) — `checklists/source-plan.md` **v2**,
  `templates/source-ledger.md`, `dlc-context-archaeologist`.
- Người trả lời `CHƯA RÕ tên — <vai> (chờ OQB-NN)` hợp lệ khi có câu hỏi đúng cái tên đó (§4.10.13, doctor 1b).
- `recommended` được để trống khi `gaps` nói rõ bản chữ không có khuyến nghị (`HV05`).
- Câu rủi ro cao mà giá đảo của mặc định `chưa rõ` ⇒ `default: null` + `needs`, không đoán (`HV07`).

### Khác
- `protocol.md` §5: mẫu HOF **mỗi khoá một dòng** (mẫu cũ gộp ba khoá một dòng làm tower hiện rác).
- File câu hỏi nghiệp vụ trích nguồn đã soát bằng **mã sổ cái + lời** (§4.10.12) — hết đá nhau giữa "phải trích nguồn" và "cấm đường dẫn".
- Bỏ trần "≤150 từ" cho thẻ bản chữ (§4.10.15) — trần độ dài áp trên cây của tower, đo được.
- Stage 2 được **chạy thử** hệ thống để kiểm AS-IS với ba điều kiện (`dlc-context-archaeologist`).
- **§4.17 làm rõ chữ** (không nới): trigger `qa` chỉ bắn với NFR có ngưỡng **cần dụng cụ đo**, không phải mọi ngưỡng số; `peer` của bolt một dev = agent
  dev khác phiên, context tươi.
- `dlc-intent-analyst` · `dlc-context-validator` · `dlc-unit-planner` · `dlc-retro-keeper` khai thêm `Bash` — không có thì không lấy được giờ thật cho
  heartbeat §9.4.
- `templates/intent-plan.md`: gỡ "Tổng ≤5.0".

### Test
`python3 -m unittest discover -s tests` — **107 ca** (6.4.1: 42). Mới: `test_human_view_check` (32) · tower `HumanView` / `TowerDetails` / `TowerServe`
(16) · `AP12` + ca báo sai `AP06`. Đột biến cố ý vào checker mới: 10/10 bị bắt.

### Chưa làm / giới hạn đã biết
- Chưa có template cho `static-model` · `dynamic-model` · `decisions-inventory` (#8). `unit-plan.md` còn chép lại nội dung của `spec.md` (#31). Chưa có
  chỗ chuẩn cho việc nền (#34). Hai DEC autopilot mâu thuẫn nhau không có máy bắt (#36). 
- **Mô hình của gate trước không biết quyết định ở gate sau** (#25): trang mô hình Gate A vẫn ghi "đội đang đứng" ở câu đã được áp mặc định
  tại Gate C. Định nghĩa `risk` còn hai cách hiểu (#26).
- **Autopilot tự áp được cả việc miễn một mục DoD** (#38) — hiện chỉ được giữ lại bằng hạn đảo. Tower chưa có nhóm *Xác nhận trước mốc*, chưa cảnh
  báo hai DEC mâu thuẫn (#36), parser bảng Unit còn lấy bảng đầu tiên chứa mã (#30) — đang làm, ra ở bản vá kế.
- Lần chạy thử dừng ở stage 5; **chưa dòng code nào được viết bởi flow autopilot**. Agent trong lần chạy là `general-purpose` đóng vai.
- `tower_aws_v2.py` (engine aws-v2) chưa có trang mô hình.

## 6.4.1 (2026-09-28) — luật autopilot máy kiểm được + bộ test đầu tiên của gói

**Nguồn**: `docs/plugin-7-policy-layer-plan.md` §7 câu 6 (đã chốt: `tests/` là điều kiện của 7.0.0-a) + nguyên tắc
§4.15 áp cho chính gói. Patch: không đổi luật, không đổi format — chỉ làm cho luật 6.4.0 **kiểm được bằng máy**.

- `scripts/autopilot_check.py` (stdlib, chỉ đọc, thoát 1 khi có FIX): `AP01` DEC thiếu dòng · `AP02` *Hiện ở* trỏ file
  không có · `AP03` block check thiếu/`hit` mà vẫn quyết · `AP04` `gates_auto` không có DEC · **`AP05` BỎ BƯỚC** (artefact
  của gate đã tự đóng thiếu hoặc chỉ là vỏ; Unit thiếu một trong bốn file) · **`AP06` TỰ QUYẾT QUA BLOCK** (câu `CHẶN`
  còn mở không có mặc định; nguồn còn `planned`) · `AP07` `steer-*` chưa xử lý · `AP08` block > 24h · `AP09` tỷ lệ đảo
  ngoài 10–30% · `AP10` dừng không lý do · `AP11` DEC autopilot dưới `mode: lead`. `dlc-doctor` 3b và `dlc-orchestrator`
  2b gọi nó. **Chưa kiểm** (vẫn soát tay): hạ tầng review so với trigger §4.17 · diff chạm migration/auth/PII/deploy.
- `tests/` — 42 ca, `unittest` stdlib, không thêm phụ thuộc: `python3 -m unittest discover -s tests`.
  `test_autopilot_check` (22: một ca sạch làm đối chứng, mỗi ca đột biến một thứ và đòi đúng một mã; tài liệu **ngắn vì
  phạm vi nhỏ** phải qua, **vỏ rỗng** phải bị bắt) · `test_gate_guard` (6: Gate D do autopilot đóng mở guard như do người
  đóng; state tuỳ biến vẫn chặn) · `test_layout` (10: `layout.py` = `layout.ts` trên 10 kiểu thư mục — thay cho 14 ca
  chạy tay của 6.3.0) · `test_tower_generate` (4: `data.js` nạp được, SVG có mặt, **escape**, dự án `lead` không có thẻ
  autopilot, không đẻ `.ai-dlc/` rác).
- **Test của test** (§4.15): 12 đột biến cố ý vào `autopilot_check.py` · `gate_guard.py` · `layout.py` ·
  `tower_generate._x` (tắt escape) — **12/12 bị bộ test bắt**.
- Phát hiện khi viết test: fixture dựng cho tower ở 6.4.0 có `intent-plan.md`/`source-ledger.md` chỉ là vỏ — `AP05` bắt
  đúng. Fixture đó chỉ để vẽ hình, không phải ca mẫu của một intent chạy đủ.

## 6.4.0 (2026-09-28) — Autopilot: gate không chờ người, chạy đủ bước, dừng khi block · tower mô hình hoá bằng SVG

**Nguồn: quyết định chủ gói 2026-09-28** (`docs/plugin-7-policy-layer-plan.md` §9 — nguyên ý chỉ thị + bảng trade-off
§9.3) — không phải LL qua Gate G; nợ LL, trả bằng KPI `autopilot.*` ở retro kế. **Opt-in theo dự án**: không có
`governance/autopilot.md` hoặc `mode: lead` ⇒ hành vi 6.3.0 nguyên vẹn. Minor vì thêm núm + trường tuỳ chọn; luật
gate A–G, `gate_doc`, preview, request-changes **không đổi** cho `mode: lead`.

### Autopilot (protocol §2.3)
- **Không phải "fast mode bỏ bước".** Tám stage và mọi artefact vẫn sinh đủ, đúng template. Autopilot đổi **ai quyết
  ở gate**, không đổi **làm gì**. Bỏ/gộp stage, artefact thiếu mục ⇒ doctor **FIX**.
- **Cắt phạm vi vừa đủ** (§2.3.2): stage 1 tách intent khi Unit Map vượt `max_units_per_intent` hoặc có Unit không
  `releasable` một lượt — tài liệu ngắn vì phạm vi nhỏ, không vì rút mục.
- **Block check sáu điều kiện** tại mỗi gate: câu chặn không có mặc định khả thi / đảo đắt · thiếu thông tin để viết
  AC/test · nguồn P0 không tự đọc được · ranh đỏ (deploy khách/prod, migration phá huỷ, gửi ra ngoài, tiền, quyền) ·
  doctor FIX · tự sửa quá `max_self_fix`. Sạch ⇒ DEC autopilot, **chạy tiếp trong cùng lượt**. Block ⇒ `blocked_by`
  trong `status.md`, dừng; việc không phụ thuộc vẫn chạy.
- **DEC autopilot** (protocol §5): *Chọn · Bỏ · Đảo bằng · Hiện ở · Block check* (+ `reverses:` · `reason: silent-timeout`).
  Thiếu dòng nào là FIX — quyết định không đảo được là quyết định không được tự ra.
- **Gate F**: tự đóng phần nghiệm thu Unit; **deploy luôn dừng** (ranh đỏ #4). **Gate G**: LL tự ghi, patch gói vẫn
  cần người ký.
- **Đảo**: tower nút *Đảo* ⇒ `inbox/steer-*.json` ⇒ `REV-NN` from HUMAN ⇒ DEC mới `reverses: DEC-NNNN`.
  `dlc-resume` xử lý `steer-*` trước mọi thứ.
- `templates/autopilot.md` (núm `mode · wait_hours · max_units_per_intent · max_self_fix · notify`) · `templates/status.md`
  thêm `gates_auto` · `blocked_by` (tuỳ chọn; `plugin_version` template sửa từ `3.1.0` cũ).
- Nối vào: `dlc-orchestrator` (2b + điều cấm sửa lại) · `dlc-intent-analyst` (cắt phạm vi) · `dlc-context-validator`
  (phân loại `CHẶN` thật) · `dlc-bolt-coordinator` · skill `dlc-intent/validate/units/bolt/accept/retro/resume/init` ·
  `session_start.sh` (luật 5 đổi theo mode) · `dlc-doctor` **3b** (DEC thiếu dòng · bỏ bước · tự quyết qua block ·
  hạ tầng review · block quá 24h · steer chưa xử lý · tỷ lệ đảo ngoài 10–30%).
- `gate_guard.py` **không đổi**: nó đọc `gates_passed`, autopilot ghi Gate D vào đó bằng DEC thật.

### Tower — mô hình hoá bằng SVG, thẻ *AI đã tự quyết*, nút *Đảo*
Ca gốc (chủ gói 2026-09-28): "câu hỏi và quyết định đang quá nhiều chữ". SVG sinh **server-side** trong
`tower_generate.py` thành chuỗi trong `data.js` (khoá mới `svg`, `autopilot`) — không thêm thư viện/CDN; mọi chữ lấy
từ markdown đều escape. Chữ đầy đủ vẫn còn, gấp dưới `<details>`.
- **Flow intent**: băng ba pha · 8 hộp stage · hình thoi gate **đúng vị trí protocol §2** (A sau 1 · B sau 3 · C sau 4 ·
  D sau 5 · E trong stage 6 · F sau 7 · G sau 8) · hàng Unit dưới stage 6. Màu: xong (xanh) · **tự quyết (xanh viền
  nét đứt)** · chờ người (vàng, nhấp nháy, tắt khi reduced-motion) · **đang đứng vì block (đỏ + dải lý do)** · đang làm ·
  chưa tới. Bấm hộp/gate/Unit ⇒ mở đúng tài liệu/thẻ. Thay dải `StageStrip` ở Tra cứu › intent; có trong Bản tin.
- **Cây lựa chọn mỗi câu hỏi** (thẻ *Cần tôi trả lời*): gốc = câu hỏi, nhánh = phương án kèm **giá**; *AI đề xuất*
  viền dày; *nếu im lặng* viền nét đứt; góc có mã + `CHẶN UOW-NN`, hạn, người trả lời. Bấm nhánh ⇒ điền sẵn câu trả
  lời. Chỉ vẽ khi thẻ `### OQx-NN` có bảng ≥ 2 phương án — thiếu thì hiện chữ như cũ.
- **Thẻ *AI đã tự quyết — đảo nếu cần*** (tầng 0, **không** cộng vào số "việc đang chờ bạn"): hai cột **Chọn ≠ Bỏ**
  kèm giá/lý do · dải *Đảo bằng* · huy hiệu block check · *Hiện ở* bấm được. Nút **Đảo** hai nhịp, bắt buộc ghi chú
  ⇒ `POST /steer` ⇒ `inbox/steer-<ts>.json`. 3 thẻ mới nhất, còn lại gấp.
- `tower_serve.py`: route `/steer` (token · `note` · `previewed` · mã DEC hợp lệ — thiếu ⇒ 403/400); `/state` gửi
  thêm `inboxPending` (**sửa lỗi có từ 6.1.0**: UI đọc trường này mà server chưa từng gửi ⇒ thẻ vừa xử lý hiện lại
  sau F5).
- Regex tiêu đề DEC nới để nhận đoạn thứ 5 `· autopilot`; tiêu đề 4 đoạn cũ khớp như trước.
- KPI trong *Tra cứu ▾*: `autopilot.decisions` · `reversed` · `blocked`. **Giới hạn đã biết**: `blocked` đếm gate
  đang block lúc này, chưa có lịch sử và chưa tách theo #1–#6; bề rộng chữ trong SVG là ước lượng (dư ⇒ xuống dòng
  sớm, quá dài ⇒ cắt "…", bản đủ trong tooltip/`<details>`).
- Đã thử: `py_compile` · cú pháp 12 file JSX · `data.js` nạp được bằng `vm` · fixture autopilot (stage 5, gate D block,
  2 câu hỏi A/B/C, 2 DEC autopilot, 3 Unit) và fixture `lead` — generator bản cũ vs mới trên fixture `lead` cho
  29/30 khoá cũ giống hệt · tower thật dark + light 0 lỗi console · **ca đối chứng**: tiêm `<script>`/`<img onerror>`/
  `<foreignObject>` vào tiêu đề câu hỏi, phương án, dòng *Chọn*/*Đảo bằng* của DEC, `blocked_by` ⇒ 0 thẻ thô trong SVG.
- **Chưa làm**: `tower_aws_v2.py` (engine aws-v2) chưa có SVG/autopilot — kế hoạch §9.3.

## 6.3.0 (2026-09-23) — Phương án A: gói là lớp chính sách + tower TRÊN engine AWS `aidlc-workflows` v2

**Nguồn: quyết định chủ gói 2026-09-03** (`docs/multi-user-shared-space.md` mục 2.1b + spike
`docs/spikes/aws-v2-cross-clone-approval.md`) — không phải LL qua Gate G (xem nợ tổng ở đầu file).
**Không sửa template của đội** (`project-starter-template-ai`): mọi thứ gói cần nằm trong plugin.
**Không đổi luật gate của gói** — mọi thứ mới chỉ chạy khi cwd là workspace AWS v2, nơi khác fail-open;
dự án `.ai-dlc/` hiện có **không phải làm gì** (`MIGRATION.md`). Minor vì thêm hook + script, không đổi
format/layout. Phần layout resolver từng dán nhãn "7.0.0" trong code — nay là 6.3.0; 7.0.0 dành cho lát
kế theo `docs/plugin-7-policy-layer-plan.md` (đóng băng engine ai-dlc, doctor/status/resume trên aws-v2,
luật v2 mức WARN).

- `references/aws-v2-workspace.md` — bản đồ workspace AWS v2 gói đọc/ghi: layout control plane + sibling
  repo, `aidlc/spaces/<space>/intents/<id>/` (checkbox `[?]` = gate mở, shard audit per clone), event audit,
  6 guard trước gate, gói đặt gì ở đâu. Luật: đường dẫn gói ghi vào audit **luôn tương đối** với workspace.
- `hooks/aws_v2_write_receipt.ts` (PostToolUse `Write|Edit|MultiEdit|NotebookEdit`, cần `bun`, tự bỏ qua
  nếu không có) — ghi thêm một receipt `ARTIFACT_CREATED|UPDATED` với `File` **tương đối** (+ `Receipt:
  ai-dlc:relative`) qua đúng seam `appendAuditEntry` của workspace. Ca gốc: hook gốc ghi `File` tuyệt đối
  ⇒ guard "ghi lại sau xác nhận tóm tắt" không bao giờ khớp trên clone khác ⇒ PM không duyệt được từ máy
  mình (spike kết luận #2). Đã thử: sống chung với hook gốc, bỏ qua file ngoài record/codekb, không tự tạo
  ledger, fail-open ngoài workspace. Tắt: `AI_DLC_AWS_RECEIPT=off`.
- `scripts/tower_approve.ts` — một nút tower = một quyết định gate: `git pull --rebase` → kiểm `[?]` →
  `HUMAN_TURN` kèm `Actor`/`Source: tower` → `aidlc-orchestrate.ts report --user-input "<lời> — <tên>"` →
  kiểm `[x]` → commit tác giả = người bấm → push (retry 1 lần). Engine không kiểm *ai* (presence guard toàn
  workflow, spike kết luận #3) nên định danh là việc của script; **còn thiếu** đối chiếu RACI trước khi chạy.
- `scripts/tower_aws_v2.py` (stdlib) — tower cho workspace AWS v2: đọc `aidlc/spaces/*/intents/*/aidlc-state.md`
  + `audit/*.md`, đối chiếu RACI, sinh ba loại thẻ theo **vai của người đang xem** (git user của clone): *Cần tôi
  quyết* (stage `[?]`, nút Duyệt/Trả lại ⇒ `tower_approve.ts`, lời người bắt buộc) · *Cần tôi trả lời*
  (DECISION_RECORDED chưa có answer — hiện chưa ghi thay, chỉ báo + "nếu im lặng") · *Cần tôi kiểm* (cột "kiểm"
  RACI). Tầng 0 chỉ có thẻ; intent/sự kiện/KPI **trung vị giờ mở gate → quyết** trong *Tra cứu ▾*. `--serve`:
  GET /state · /doc (chỉ .md dưới workspace) · POST /pull · POST /decision; token như tower cũ. Đã thử: thẻ đúng
  vai, duyệt từ UI thành commit + push, KPI tính được từ audit.
- `templates/raci.md` + RACI trong `tower_approve.ts`: `.ai-dlc/governance/raci.md` (`| gate | quyết | kiểm |`,
  glob, `*` mặc định) — thiếu file ⇒ cho qua kèm `raci: missing` (bậc 1); có file mà không có tên ⇒ từ chối.
  Đã thử 4 ca. `.ai-dlc/` trong workspace AWS v2 = chỗ governance của gói (engine đã loại `.ai-dlc` khỏi sibling
  discovery); nên gitignore `.ai-dlc/tower/`.
- Chốt cùng ngày: im lặng quá hạn ⇒ AI quyết thay, ghi ASM "phương án tốt nhất theo AI · lý do im lặng
  quá hạn" (chỉ câu hỏi/test case, gate không có mặc định).
- **Layout cấu hình được (2026-09-09, quyết định chủ gói: "đủ linh động với bất kỳ cấu trúc folder nào; config
  từ file hoặc CLAUDE.md")** — `scripts/layout.py` + `scripts/layout.ts` (cùng luật, kiểm chéo `--json` trên 14
  ca) là resolver duy nhất: env `AI_DLC_*` → `ai-dlc.config.json` / `.ai-dlc/config.json` → fence ```` ```ai-dlc ````
  trong `CLAUDE.md`/`AGENTS.md` (JSON hoặc `key: value`) → tự dò (`.ai-dlc/context-memory` ⇒ ai-dlc; `aidlc/spaces`
  + `.claude/tools` ⇒ aws-v2). Key: `engine` (auto|ai-dlc|aws-v2|off) · `root` · `state` · `space` (auto = cursor
  → space duy nhất → default) · `governance` · `tower{out,port,mode}` · `search_up`. Đã nối: `session_start.sh`
  (banner riêng cho aws-v2, im lặng khi off) · `gate_guard.py` (chỉ chặn ở engine ai-dlc, state tuỳ biến vẫn
  chặn đúng) · `aws_v2_write_receipt.ts` · `tower_generate.py`/`tower_serve.py` (**tự chuyển sang
  `tower_aws_v2.py` khi engine aws-v2** — một lệnh `/ai-dlc:dlc-tower serve` cho cả hai; port/out theo config)
  · `tower_aws_v2.py` (raci từ `governance`, `mode: off`) · `tower_approve.ts` (space mặc định + raci từ config)
  · `session_brief.py`. Hành vi dự án hiện có **không đổi** (tự dò = luật cũ). Template `templates/ai-dlc.config.json`,
  tài liệu `references/layout-config.md`. Đã thử: 14 ca resolver py=ts; gate_guard chặn đúng với `state: docs/state`;
  tower 6.x sinh vào state tuỳ biến, không đẻ `.ai-dlc/` rác; tower_serve trên template đội → tower AWS v2 trả
  `/state` 200, template 0 thay đổi; tower_approve dry-run qua fence (raci ok / từ chối người ngoài / missing khi
  không config / env từ thư mục con / `--space` tường minh thắng); receipt hook từ thư mục con qua fence.

## 6.2.0 (2026-08-27) — Workspace map v2 (repos · areas) + codekb dùng lại giữa các intent

**Nguồn: quyết định chủ gói** trên `docs/workspace-knowledge-model-from-team-atlas.md` (đưa phần team tự
nghĩ trong `docs/explore-aidlc-phases-v2.html` vào gói) — không phải LL qua Gate G; nợ LL như 5.0.0/6.0.0.
**Không đổi luật gate**, additive: map v1 vẫn đọc được, intent đang chạy không phải làm gì.

### Một `.ai-dlc/` = một space (protocol §3)
- Space = một đội ổn định, một bộ luật, một tower. Space **không** là frontend/backend — đó là *code area*.
  Một đội nhiều repo ⇒ `.ai-dlc/` ở thư mục cha; hai đội có người duyệt riêng ⇒ hai `.ai-dlc/`. Không có
  `spaces/`. `dlc-init` hỏi **đúng một câu** ("đội nào duyệt vùng code này?") thay vì hỏi FE/BE hay mấy repo.
- `gate_guard.py` + `session_start.sh` tìm `.ai-dlc/context-memory/` từ cwd đi lên tối đa 2 cấp (đa repo
  mức "cho phép", chưa test kỹ — quyết định #5). Path trong map tương đối với thư mục chứa `.ai-dlc/`.

### `workspace-map.md` v2
- Thêm `repos:` (id + path) và `areas:` (tên tự do, mỗi area `repo` · `path` · `tests`); giữ `code:`/`tests:`
  để 6.x đọc. `gate_guard.py` lấy code roots từ `areas.*.path` **lẫn** `code.*`; bỏ `.` (cả workspace).
  `tower_generate.scan_activity` bắt cả hai dạng, bỏ `.`.
- `spec.md` thêm `areas: []`; `unit-plan.md` thêm cột *Areas* và luật **cắt dọc là mặc định** — cắt theo
  area (`u1-domain → u2-api → u3-web`) chỉ khi `contract.md` đã chốt và mọi mảnh khai `released_with:`.
  Lý do: Unit theo area không `releasable` ⇒ Lead không có gì để nhìn tới Unit thứ 3 (white paper v2 §IV).
- Doctor 6a: `areas.*.path` không tồn tại → FIX · Unit khai area không có trong map → FIX · Bolt ghi file ngoài
  `areas` → WARN · map còn v1 → WARN.

### `codekb/<repo>/` — bản đồ code bền vững (protocol §3, §4.8)
- Ca gốc: PILOT INT-002 và INT-003 dựng lại AS-IS trên cùng một backend. Nay khi intent **đóng** (stage 8),
  acceptance-recorder promote **nguyên văn** `as-is/{static,dynamic,decisions-inventory}.md` vào
  `codekb/<repo>/` + `freshness.md` (`git_head` lúc AS-IS được đọc · `areas_scanned` · `ledger`). Không viết
  lại, không dựng bù.
- Intent kế: `dlc-discover` 1b so `git_head` với HEAD trên path các area intent chạm → `CURRENT` reuse ·
  `STALE` quét delta (`as-is/delta.md`) · `UNKNOWN_SCOPE` quét như chưa có. **Vẫn qua No-unread-source**:
  reuse = dòng `read` trong ledger với evidence `freshness.md CURRENT @<sha7>`; quyết định ghi ở **mục 0**
  của `source-ledger.md` để người duyệt Gate B thấy. Dùng codekb không ledger = đọc thầm ⇒ doctor FIX.
- Source-planner đặt `codekb/<repo>/` làm dòng đầu bảng 2.1; `session_start.sh` in trạng thái freshness;
  `INDEX.md` thêm hai dòng tra cứu. Template mới `templates/codekb-freshness.md`.

### Quyết định chủ gói ghi kèm (cho 7.0.0, chưa làm ở bản này)
- `intent.kind` 6 tuyến (bugfix bỏ stage 3–5) — đổi luật, để 7.0.0. `governance/raci.md` — dự án nhỏ cho
  người làm ký thay; doctor WARN khi Gate R mục bảo mật do Lead ký mà Unit chạm auth/PII. Plugin org cho
  governance projection — chưa có ý định, protocol chỉ ghi cơ chế.

## 6.1.1 (2026-08-24) — tower khai đúng version gói

- `tower_generate.py` đọc version từ `.claude-plugin/plugin.json` thay vì chuỗi hardcode —
  lộ ra khi update PILOT lên 6.1.0 mà `data.js` vẫn khai `"plugin": "5.0.0"` (nằm chết từ 5.0.0,
  qua hai bản major không ai thấy vì không có chỗ đối chiếu). Đúng luật §4.11: số trên tower
  phải truy được về nguồn thật.

## 6.1.0 (2026-08-22) — Tower decision-first: mở lên chỉ thấy "Cần tôi quyết", hoạt động AI vào Tra cứu

**Nguồn: phản hồi trực tiếp của chủ gói trên tower 6.0.0** ("thông tin rất loạn, chưa đủ rõ để làm;
sidebar loạn, chưa gần gũi với người dùng") — không phải LL qua Gate G. Spec:
`docs/control-tower-lead-view.md`; nguyên tắc: white paper v2 §VII.4. **Không đổi luật gate** — đây là
bước đi được trước khi chốt phương án 7.0.0 (`docs/plugin-transition-plan.md`). Chỉ đổi UI (`tower-ui/`),
generator không đổi.

### Màn mặc định mới: Cần tôi quyết (`LeadInbox.jsx`)
- Chỉ thẻ cần NGƯỜI hành động, thứ tự: ký phát hành (Gate F) → đang đứng (escalation mức
  high/medium hoặc chạm phạm vi) → gate A/B/C/D/G → xem thử (Gate E) → **câu hỏi đang chặn** (từng thẻ)
  → phát hiện mức low chưa ai nhận → câu hỏi không chặn (**gom một thẻ mỗi yêu cầu**). Tối đa 7 thẻ,
  còn lại "và N việc khác ▸".
- Mỗi thẻ: câu hỏi một dòng bằng lời (Gate A–G đọc lại: "Đích của yêu cầu này đúng chưa?"…) · **"Nếu
  bạn im lặng"** (6.x: "đội đang đứng"; câu hỏi: cột *nếu im lặng* của §4.10) · phương án + "đội đề xuất"
  từ decision brief · nút quyết ngay trên thẻ · *Xem thêm ▸* mở đúng một tài liệu.
- Trống ⇒ một dòng "Không có gì cần bạn. Đội đang làm việc." — không hiện gì khác.
- Ca đối chứng lúc viết: PILOT có 0 gate mở · 12 escalation mở · 38 câu hỏi mở (5 chặn) ⇒ 19 thẻ thay vì
  50; thẻ đầu tiên là việc đứng, không phải panel agent.

### Bản tin hôm nay (`Brief.jsx`) — tầng 1
- Một trang bằng lời: đã làm · sẵn để bạn xem · cần bạn · đang đứng · sức khoẻ đội (một dòng, link
  sang Đội AI). Không bảng, không mã.

### Sidebar viết lại (`Shell.jsx`)
- Ba khối: *Cần tôi quyết* (badge) · *Bản tin hôm nay* · **Việc đang làm** = tên yêu cầu + một dòng
  trạng thái bằng lời ("đang xây 1/30 · 1 chờ bạn"), tối đa 5, đã xong gấp lại.
- **Gỡ**: header `AI-DLC · 18 agents · gates A–G`, cây `Intent → Unit → Bolt`, chấm màu, đuôi `gate E`/`△`,
  `+N unit ngoài phạm vi`, `_trash`, chân `supervisor · Human`. Rộng 268 → 220.
- **Tra cứu ▾** (gấp) chứa mọi màn cũ, tên Việt trước, tên cũ trong ngoặc: Phần việc & vòng xây (Bolt /
  Task Board) · Trao đổi & soát (Comms & Reviews) · **Đội AI (Mission Control)** · Dòng chảy 3 pha · Danh
  sách yêu cầu (Intents) · Luật & bài học (Governance & Learning). Không màn nào bị bỏ.
- Vì sidebar không còn cây Unit, `BoltBoard` có hàng chọn phần việc ở đầu màn.
- Tên yêu cầu cắt dấu `"` bao quanh (`plainName`) — intent.md của PILOT để nguyên ngoặc kép cả câu.
- Thanh trên bỏ chip `N MỤC CHỜ BẠN` (badge sidebar đã là nguồn duy nhất). Màn mở mặc định là `inbox`;
  pref cũ `mission` được đổi sang `inbox` một lần.

### Trả lời ngay trên tower — không phải quay về terminal
- Thẻ câu hỏi có **ô nhập + "Gửi câu trả lời"** (và "Dùng mặc định" khi cột *nếu im lặng* có nội dung);
  thẻ gom câu không chặn mở từng câu để trả lời; thẻ escalation có ô **"Chỉ đạo"**.
- `tower_serve.py` thêm `POST /answer` (token như `/decision`) → `inbox/answer-<INT>-<OQ>-<ts>.json` ·
  `inbox/direction-<INT>-<ESC>-<ts>.json`. Server chỉ xếp hàng, **không sửa hồ sơ** — áp nguyên văn là việc
  của orchestrator khi drain (protocol §5 có format + luật: Trạng thái `đã chốt` · bảng *Đã trả lời* ·
  changelog · `blocking` ⇒ gỡ chặn · direction ⇒ mục *Chỉ đạo* + owner/status trong ESC).
- Generator thêm `inboxPending` (file còn trong `inbox/`): thẻ đã gửi biến khỏi "Cần tôi quyết" và một dòng
  "N việc bạn đã gửi đang chờ phiên Claude Code áp" thay thế — không hỏi lại, không hiện lại sau F5.
- Hook SessionStart, `dlc-resume`, `dlc-orchestrator`, `dlc-tower` cập nhật luật drain cho ba loại file.

### Sửa hướng dẫn gọi lệnh
- Skill của plugin được Claude Code đặt tên `/<plugin>:<skill>` ⇒ lệnh thật là **`/ai-dlc:dlc-tower`**,
  `/ai-dlc:dlc-resume`, … Dạng `/dlc-…` trong README, CLAUDE.md, MIGRATION, protocol, SKILL.md, template,
  chuỗi in ra từ hook/script/tower UI (34 file) đã đổi sang dạng có prefix. Tên thư mục skill, tên agent
  và path không đổi. Các entry CHANGELOG cũ giữ nguyên dạng cũ (lịch sử).

### Nợ
- Thẻ Gate E mới chỉ là "xem thử rồi ký" trên gate_doc — Showcase Pack thật (bấm gì, nhìn gì, giả định
  nào đang hiện) là việc của 7.0.0 (§IV white paper v2). Mốc chờ (`wait_until`) chưa có ở 6.x.
- Trả lời câu hỏi vẫn là mở file / trả lời trong phiên — tower chưa ghi `FB` (7.0.0).

## 6.0.0 (2026-08-19) — Gỡ Review Board mặc định: review theo tầng rủi ro, self-verify có bằng chứng, peer trong bolt

**Nguồn: quyết định của chủ gói, KHÔNG phải LL qua Gate G** — cùng vị thế với 5.0.0, và cùng kỷ luật:
ghi rõ để không tự lừa mình, **nợ một LL** (retro đầu tiên có dữ liệu tầng phải trả). Ba căn cứ kiểm được:

1. **White paper (SSOT) không có Review Board agent.** Grep toàn văn: mọi chỗ "rà soát" đều là **con
   người** (mob rà soát artefact ở Inception; "Developer rà soát mã và kịch bản kiểm thử do AI tạo" ở
   Construction). Bảy reviewer agent là phát minh của gói — như trần 5h đã gỡ ở 5.0.0.
2. **Thực địa: review bắt buộc mọi nơi không chạy được.** LL-002: 13 review-request, **0 verdict**, 17
   unit vẫn đóng. §4.12 (4.0.0) làm nó *kiểm được* nhưng không làm nó *chạy được*: INT-003 đang mang
   RV-019/RV-020 `unfulfilled` ngay lúc luật này viết. Với 30 unit, kết cục là hàng đợi nghẽn hoặc một
   đống DEC waiver hình thức.
3. **Chi phí đo được**: mỗi Bolt tới ~6 lượt spawn reviewer (DoR + tech-lead & security design + BE/FE/
   security/qa code), hai trong số đó chạy opus; mỗi lượt là một phiên lạnh nạp lại bối cảnh — đắt và
   thường nông hơn peer đã đọc sẵn design/contract.

### Đổi luật điểm dừng + format (major)
- **protocol §4.17 mới**: mỗi Unit khai `review: none|peer|specialist(<vai>)` theo **bảng trigger kiểm
  được** (auth/PII → security · migration/public API/ADR trái pattern → tech-lead · NFR ngưỡng đo → qa ·
  contract FE↔BE / vùng lạ / unit đầu chạm bounded context → peer · còn lại → none). Người duyệt **cả
  bảng tầng một lần tại Gate D** — `review: none` được duyệt ở đó chính là waiver có địa chỉ, hết DEC lẻ.
  Nâng tầng giữa chừng: tự do + MSG note; hạ tầng: phải DEC. Doctor đối chiếu trigger với dấu vết thật.
- **§4.12 mở rộng**: đường bằng chứng thứ ba `self_verify:` (chỉ tier `none`) — `evidence/self-verify.md`
  (template mới) từng mục checklist kèm **con trỏ bằng chứng**, §4.15 bắt buộc (ca đối chứng + mutation
  test) vì không có mắt thứ hai. Dấu ✓ suông = doctor FIX.
- **Checklist shift-left (§4.17.4)**: BE/FE checklist thành pre-flight trong `read_first` của HOF dev —
  đọc TRƯỚC khi code, điền SAU khi code; reviewer (khi có) *verify* chứ không *discover*.
- **Peer review**: reviewer của tier `peer` là dev còn lại trong cùng bolt — đã đọc design/contract cho
  task của mình nên HOF review chỉ cần diff + checklist. Format RV giữ nguyên; 2× request-changes vẫn
  escalate lên người.
- **Gates A–G của NGƯỜI không đổi** — Gate E(a)/E(b) dừng cho mọi tầng. Gỡ reviewer agent không phải gỡ
  giám sát; giám sát nằm ở người, đúng white paper.

### Agents & flow
- **Gỡ** `dlc-backend-reviewer`, `dlc-frontend-reviewer` (16 agents còn lại). ba/pm-po/qa/security/
  tech-lead-reviewer thành **on-demand** (trigger specialist, escalation, hoặc người yêu cầu tại gate).
- Inception hết spawn review mặc định: intent-analyst/context-validator/unit-planner **tự pre-flight**
  theo đúng checklist cũ, điền từng mục kèm con trỏ vào gate_doc (mục Pre-flight mới trong unit-plan).
- bolt-coordinator tự DoR-check (checklist máy đối chiếu được, không spawn qa); acceptance-recorder tự
  chạy lại test + ca đối chứng, security-reviewer chỉ khi có unit `specialist(security)` hoặc MUST mở.

### Nghiệm kết quả — §9.6 mới (mắt thứ hai không tốn phiên mới)
Agent đóng HOF `done` mới là **lời khai xong**. Kết quả chỉ được dùng tiếp (task done, đóng Unit, mở gate,
spawn lượt phụ thuộc) sau khi **người giao** (mainlead: coordinator/orchestrator — đang sống, có sẵn bối
cảnh) nghiệm ba bước: đối chiếu *Đã làm* với DoD của lượt · mở ít nhất MỘT bằng chứng thật (với tier
`none`: mở 1–2 con trỏ trong `self-verify.md` kiểm chúng có thật) · ghi `result_check: pass|returned` lên
frontmatter HOF. Trường mới trong template HOF (v2.2); KPI `handoffHealth.checked/closed`; doctor FIX HOF
`done` thiếu nghiệm (legacy chỉ ghi chú), WARN HOF tự giao tự nghiệm. §9.6 không thay §4.17 — nó bịt đúng
cái khe "dev tự đóng, không ai nhìn lại" mà tier `none` mở ra.

### Giới hạn nói thật
Dev và peer chạy cùng model, cùng điểm mù — cái mất thật là tính độc lập ở tier `none`/`peer`. Lưới đỡ:
trigger specialist + mutation test bắt buộc + **nghiệm của người giao (§9.6)** + KPI lỗi lọt theo tầng để
retro nâng trigger bằng số, không bằng cảm giác. `units.reviewed` mở rộng đếm cả ba đường bằng chứng, kèm
cột tầng.

### Không dựng bù hồ sơ
Unit lập trước v6 không bị bắt khai `review:` (luật §4.12 cũ vẫn áp); **nợ review cũ không được xoá** —
RV-019/RV-020 của PILOT vẫn `unfulfilled` cho tới khi có RV thật hoặc DEC miễn công khai.

### Kèm theo
`MIGRATION.md` mục 5.x→6.0.0 · protocol §1.0c (điểm dừng theo tầng) + §4.12 + §4.17 + **§9.6** + §6
(on-demand) · template `handoff.md` v2.2 (`result_check:` + mục Nghiệm kết quả) ·
template `self-verify.md` mới, `unit-spec.md` (+`review:`/`self_verify:`), `unit-plan.md` (cột Review +
mục Pre-flight), `dod.md` v4, `tasks.md` (approver theo tầng) · checklists: backend v3 · frontend v3 ·
tech-lead v2 · security v2 · qa v5 · pm-po v4 · ba v4 · skills `dlc-bolt`/`dlc-units`/`dlc-accept`/
`dlc-intent`/`dlc-validate`/`dlc-revise`/`dlc-doctor` · `tower_generate` (`units.reviewed` ba đường +
cột tầng) · dọn nốt câu "≤5h" sót lại của 5.0.0 trong template `unit-spec`/`unit-plan` và skill
`dlc-units`/`dlc-intent`.

## 5.0.0 (2026-08-13) — Bỏ trần 5h/Unit: cắt theo đường ra sản phẩm, không theo đồng hồ

**Nguồn: quyết định của chủ gói, KHÔNG phải LL qua Gate G.** Ghi rõ để không tự lừa mình — đây là lần thứ
hai trong ngày một luật đổi mà chưa có retro chống lưng. Bù lại, ba căn cứ đều kiểm được:

1. **White paper (SSOT) không có trần 5h.** Nó nói chu kỳ tính bằng "**giờ hoặc ngày**" và bounded context
   "độc lập, **đúng kích thước**". Trần 5h là phát minh của gói ở v2 — **hẹp hơn** tài liệu gốc, tức là
   chính nó đang lệch SSOT.
2. **`MIGRATION.md` v2 đã tự đặt câu hỏi này**: *"trần 5h có làm vỡ vụn Unit không"* — treo từ đó tới nay.
3. **Ca thật**: `DEC-0052` của PILOT tách một Unit thành 3.5h + 2.75h **chỉ để lọt trần**; hai mảnh phải ra
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
  phạt — là dữ liệu để intent sau cắt sát hơn. PILOT/INT-001 khi đo lần đầu: **13/17**.

### Không dựng bù hồ sơ
Intent đã qua Gate D được lập dưới luật cũ → tower · `/dlc-doctor` · `session_brief` **không** đòi khai lại
`releasable`/`session_fit`, chỉ ghi một dòng WARN "kế hoạch cũ, áp §4.9 v5 từ intent kế". Kiểm trên PILOT:
68 Unit của INT-001/002/003 **không** bị biến thành 68 lỗi giả.

### Kèm theo
`MIGRATION.md` mục 4.x→5.0.0 · template `sizing.md` + `unit-spec.md` (3 trường mới) · `/dlc-init` seed
`governance/sizing.md` · checklists `pm-po` v3 · `qa` v4 · `ba` v3 · agents `dlc-intent-analyst`,
`dlc-unit-planner`, `dlc-pm-po-reviewer`, `dlc-qa-reviewer`, `dlc-ba-reviewer`, `dlc-orchestrator` ·
`/dlc-doctor` mục 2 viết lại · KPI mới trên Mission Control + Dòng chảy.

## 4.1.0 (2026-08-13) — Nhịp sống phải kiểm chéo được · teammate vào giao thức

**Nguồn: quan sát hiện trường, KHÔNG phải LL đã qua Gate G.** Ca gốc là PILOT · INT-003 · `HOF-0039` ngày
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
  chiếu: tỉ lệ này). PILOT lúc phát hiện: **0/1**.
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

**Nguồn (hết `LL-PENDING`):** retro thật đầu tiên — `LL-001` + `LL-002` của INT-001 dự án PILOT, **đã qua
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
- **KPI `units.reviewed`** — "unit đã xong CÓ người thứ hai ký". Trên PILOT: **0/17**, kèm cảnh báo *"con số
  unit đã xong ở trên là TỰ KHAI"*. Đây là LL-002 §1 tự hiện ra trên dashboard thay vì phải đọc retro.
- **KPI `units.artifacts`** — unit đã đóng có đủ `bolts/` · `tasks.md` · `evidence/`. Trên PILOT: **0/17**
  (14 unit không có thư mục bolt nào, 0 unit có `evidence/`) — đúng con số LL-003 đo tay.
- **Panel "Phát hiện ngoài phạm vi — chờ người nhận"** đọc `escalations/`; mục `open` không có `owner` được
  tô hổ phách: đó chính là mục sẽ chìm nếu chỉ nằm trong HOF.
- **`units/_trash/` không còn bị đếm là Unit** (trước 4.0.0 nó hiện thành một unit tên `_trash`, làm sai mọi
  thống kê của intent); sidebar hiện "+N unit lỗi thời" riêng.
- **Bolt đọc từ chính Unit, và hiện đủ bốn chặng** (`unit.boltDetails`): mỗi bolt hiện chuỗi
  `Domain Design → Logical Design + ADR → Contract → Task board → Evidence` với trạng thái **có/không đọc
  thẳng từ đĩa**, bấm vào chặng có thật là mở tài liệu. Unit không có bolt thì nói thẳng "các chặng đó
  không xảy ra", không mượn số của unit khác. Trên PILOT: UOW-06/11/13 **4/6 chặng**, UOW-16 **1/6**,
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
  Trên PILOT: mỗi unit **4 điểm dừng bị đi qua** — đây là LL-002 §1 hiện thành hình, không phải thành chữ.
- **Brownfield có chặng riêng ở đầu Inception**: `as-is/static-model.md` + `as-is/dynamic-model.md` hiện
  trong Dòng chảy **chỉ khi** intent khai `brownfield_type` — greenfield không hiện (bịa việc cũng là nói dối).
- Dòng chảy nói rõ *"N bolt / M unit · X unit CHƯA có bolt nào"* thay vì chỉ đếm bolt.
- Bỏ nốt hai panel mock còn sót trong Bolt board (*API contract "GET/POST/PATCH /api/releases"*,
  *checkpoint "Demo SCR-REL-10/11"*) — thay bằng dữ liệu thật của unit + nguồn file.
- `lessons` đọc được LL viết tay (tiêu đề H1 khi không có dòng `Lesson:`, frontmatter tiếng Việt).

### Sửa (ba lỗi người dùng bắt được khi soi dự án thật)
- **Không còn đẻ ra `.ai-dlc/` rác.** `tower_generate` / `tower_serve` trước đây nhận **bừa `cwd`** làm gốc
  dự án và tạo `.ai-dlc/tower/` ở bất cứ đâu — chạy nhầm từ `app-fe/` hay từ trong `.ai-dlc/context-memory/`
  là sinh ra một thư mục `.ai-dlc` rỗng trông y như dự án thật (PILOT có đúng hai cái như vậy). Nay:
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

**Vì sao (nguồn):** người dùng đọc dashboard PILOT và không thể xác nhận số nào cả — *"Xem trong dòng chảy thì
có 13 mâu thuẫn nhưng tôi không tìm được ở đâu"*. Điều tra: generator đọc sổ cái **theo số thứ tự mục**
(§2 = bảng nguồn, §3 = mâu thuẫn). Sổ cái của PILOT dùng §3 cho *"Nguồn code — hiện trạng FE/BE"*, nên 13 dòng
nguồn code bị đếm thành **13 mâu thuẫn**. Cùng nguyên nhân: cột `Trạng thái` bị lấy sai vị trí nên
27 nguồn đã đọc hiện thành **0/11**. `LL-PENDING` (chung với 2.0.0).

### Sửa (số liệu sai trên dashboard)
- **Sổ cái đọc theo tên, không theo vị trí**: nhận bảng bằng tên cột (`#` · `Nguồn` · `Trạng thái`), gộp
  MỌI bảng nguồn trong file (trước chỉ lấy một mục). Trên PILOT: `0/11` → **27/28**.
- **Mâu thuẫn nhận bằng tên mục** ("Mâu thuẫn…"/"conflict") + dấu `[CONFLICT]` rải trong file, bỏ mục
  Changelog và câu phủ định ("không có `[CONFLICT]`"). Trên PILOT: `13` → **0** (đúng: sổ cái không có mâu thuẫn nào).
- **Trạng thái viết tay được chuẩn hoá**: `✅ đã đọc` · `⬜ chưa` · `read` · `missing` · `deferred` ·
  `superseded`. Ô không hiểu được → `unknown` + cảnh báo, **không** âm thầm tính là 0. Có cả đường lùi khi
  hàng bị lệch cột do dấu `|` nằm trong inline code.
- **Descoped chỉ do `DESCOPED.md` quyết định.** Trước đây suy "không có trong `unit-plan.md` ⇒ ngoài phạm vi",
  khiến 5 unit sinh sau Gate D (UOW-15/19/20/21/22 của PILOT, đã giao xong) bị loại khỏi mọi thống kê.
  18 unit / 67h thay cho "22 unit · 55h" — trước đó **đếm một tập, cộng giờ một tập khác**.
- **Bolt board**: bỏ nhãn cứng "UOW-01 · Bolt 1 — Release Planning" (di sản bản mock). Hiện đúng unit/bolt của
  file đang đọc, và cảnh báo khi task đang hiện thuộc unit đã ra ngoài phạm vi.
- **Trạng thái Unit chuẩn hoá từ vựng.** Trước đây chỉ đúng chữ `done` mới tính là xong, nên 21/22 unit của
  PILOT ghi `status: approved` (đã duyệt = đã xong) hiện thành "chưa xong" trong khi intent đã ở Operations —
  người xem thấy mâu thuẫn mà không có cách nào tra. Nay `done` · `approved` · `accepted` · `completed` ·
  `closed` · `xong` · `đã nghiệm thu` đều là xong. Trên PILOT: `1` → **18 unit đã xong**, khớp DEC-0014.
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

**Vì sao (nguồn):** vận hành thật trên PILOT — `open-questions.md` gộp mọi câu vào một file có phân nhóm phạm vi
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

**Vì sao (nguồn):** vận hành thật trên PILOT — 4 `dlc-fe-dev` chạy song song mà tower không thể hiện gì.
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
  agent quên cập nhật HOF thì file nó vừa ghi vẫn tố cáo là nó đang chạy. Đo trên PILOT: 87ms/lần sinh.
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
- Nguồn phương pháp: white paper AI-DLC (đã biên tập). Chưa có LL nào — thay đổi sau này bắt buộc link LL.
