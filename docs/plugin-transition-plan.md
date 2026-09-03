# Kế hoạch chuyển gói `ai-dlc` 6.0.0 → 7.0.0 theo white paper v2 (Human-Lead)

> Trạng thái: **ĐỀ XUẤT — chờ chủ gói chọn phương án** · Ngày: 2026-08-21
> Tài liệu chuẩn: `docs/whitepaper-ai-dlc-vi.md` (v2). Bản này chỉ trả lời: *gói phải đổi gì, theo lộ trình nào, và dự án đang chạy giữa chừng xử lý ra sao.*
> Bản kế hoạch gốc 2026-08-11 (7 gate, Review Board 17 agent) lưu tại `archive/plugin-plan-v1.md` — phần kiến trúc gói (override 3 lớp, workspace map, inbox bridge, vòng contribute, semver) **vẫn đúng** và không nhắc lại ở đây.
> **Bổ sung 2026-08-26:** `aws-aidlc-workflows-v2-vs-ai-dlc.md` đối chiếu với AWS `aidlc-workflows` nhánh `v2` — đề xuất mượn 8 cơ chế máy (mục 5 file đó) vào 7.0.0, trong đó #1–#3 (receipt review · state do tool ghi · HUMAN_TURN) làm được **trước** khi chọn A/B/C; và thêm 4 câu chốt (mục 7 file đó) vào danh sách §5 dưới.
> **Bổ sung 2026-08-27:** `anthropic-ai-native-sdlc-playbook-vs-ai-dlc.md` đối chiếu playbook Anthropic (2026-08-21) — **xác nhận** §1 (hook hỏi người chỉ ở prod; "an approval prompt during the build puts a person back on the critical path"), không phản bác điểm nào của v2. Mượn 10 cơ chế (mục 4 file đó): #1–#5 làm **ngay trên 6.x** không đổi luật gate (đề xuất 6.2.0: red-line guard song song `gate_guard` · evals cho gói từ LL · khoá file test khi fix + `dlc-verifier` · kiểm trôi plan + mục Proof · `repeat_of` → ứng viên LL); #6–#10 vào 7.0.0 cùng phương án B. Thêm 5 câu chốt (mục 6 file đó) vào §5 dưới.
> **Bổ sung 2026-08-27 (b):** `workspace-knowledge-model-from-team-atlas.md` đưa phần **team tự nghĩ** trong `explore-aidlc-phases-v2.html` vào gói — phần "workspace & tri thức" của 7.0.0, không thêm gate: một `.ai-dlc/` = một space · `workspace-map` v2 (`repos`/`areas`, Unit `areas:`) · `governance/` 4 tầng + `phases/` · `knowledge/` · `codekb/<repo>/` + freshness · `intents.json`/`active-intent` · `intent.kind` với bảng tuyến · `governance/raci.md` · plugin org cho governance projection. Hai việc additive làm được trên 6.x (`workspace-map` v2, `codekb/` promote). Mục 2.6 templates thêm: `raci.md` · `review.md` · `phases/*.md` · `workspace-map` v2. Thêm 6 câu chốt (mục 10 file đó) vào §5 dưới. **Đã chốt cùng ngày** (bảng mục 10 file đó): #1 chấp nhận · #2 **6.2.0 đã ra** (map v2 + codekb) · #3 `intent.kind` theo đề xuất → 7.0.0 · #4 dự án nhỏ Lead/người làm ký thay được · #5 đa repo cho phép, không test kỹ · #6 plugin org chưa có ý định.
> **Bổ sung 2026-08-27 (c):** `team-target-workflow-vs-ai-dlc.md` đối chiếu **workflow đích team vẽ** (`techtus-aidlc-workflow-viewer.html`: 3 gate người · Backlog Nulab · Preview→Confirm→Publish · tự sửa ≤3). Gần v2 nhất; gói chạy ~60%. Đề xuất **6.3.0** (không đổi gate): `dlc-backlog` + `governance/backlog.md` · `max_self_fix` · Work Unit `owner/verification/halting` · `dlc-bolt --units` · `dlc-verifier` · STALE-on-merge · tag sensor · `review.md` — gộp 5 việc playbook còn treo. Bốn chỗ workflow nên sửa trước khi đóng luật (mục 3 file đó). 7 câu chốt (mục 6), **câu 1 quyết tất cả: engine = gói `ai-dlc` / AWS v2 / plugin `/aidlc` mới**, kèm Codex.

> **Bổ sung 2026-09-03:** `multi-user-shared-space.md` — brainstorm với chủ gói về **nhiều người dùng chung** một `.ai-dlc/` (đội PM · APO · Team Lead · 2 Dev · Tester). Bốn quyết định đã chốt: mục tiêu bậc 2 (nhiều người chạy bolt) · thành công = release cho khách · **commit là quyết định** trên nhánh chính control plane · phải nhanh. Bậc 0–1 làm trên 6.3.0 (additive: `by:`, nút tower = commit, thẻ *trả lời*/*kiểm*); **bậc 2 chạm format bản ghi ⇒ là lý do bump 7.0.0** (ID theo intent + initials người tạo, file tổng hợp chỉ sinh, nhánh/worktree per Unit). File đó khuyến nghị **B** vì không nên đổi luật gate và đổi format cùng một lần khi pilot đang chạy. Thêm 2 câu chốt (mục 7 file đó) vào §5 dưới.

---

## 1 · Ba phương án lộ trình — cần chọn một

| | A · Big-bang 7.0.0 | **B · Núm `leadership.mode` (khuyến nghị)** | C · Pilot trên intent mới, giữ 6.x |
|---|---|---|---|
| Cách làm | Viết lại protocol + skills + tower một lượt; 7.0.0 chỉ còn luật v2 | 7.0.0 có `governance/leadership.md` với `mode: lead` (mặc định) hoặc `mode: gatekeeper` (luật v1). Orchestrator/hook/tower đọc núm | Không bump gói. Tạo `.ai-dlc/overrides/` trên PILOT cho INT-004 chạy v2 thủ công; đo KPI rồi mới upstream |
| INT-003 đang ở stage 6 (30 Unit, RV-019/020 `unfulfilled`) | bị ép sang v2 giữa chừng — cần migration script đổi gate E → showcase | giữ `mode: gatekeeper` cho INT-003 (pinned), INT-004 trở đi `lead` | không ảnh hưởng |
| Thời gian build | 3–4 ngày | 4–5 ngày (thêm nhánh núm) | 1 ngày override + chờ một intent |
| Rủi ro | đứt luồng pilot; không có ca đối chứng v1/v2 | code hai nhánh tồn tại tới khi `gatekeeper` bị gỡ (đặt hạn: 8.0.0) | v2 sống ngoài gói ⇒ không ai khác dùng được; dễ trôi |
| Dữ liệu trả nợ LL | không có đối chứng | **có**: cùng đội, cùng dự án, hai mode — KPI §IX của white paper so được | có nhưng chậm |

**Khuyến nghị B**: đúng kỷ luật "luật phải có ca đối chứng" (§4.15 cũ) áp cho chính thay đổi luật này. Nếu chọn A hoặc C, các mục dưới vẫn áp, chỉ khác chỗ đặt công tắc.

## 2 · Đổi gì trong gói (áp cho mọi phương án)

### 2.1 `references/protocol.md` → v7

| Mục | Hành động |
|---|---|
| §1.0c Điểm dừng trong Bolt | Viết lại: điểm dừng 1 (soát design) và 4 (soát code) giữ **trong đội** theo tầng §4.17; điểm dừng 3 (Gate E(a)) **gỡ**; điểm dừng 5 (Gate E(b)) thành **Showcase**; "năm trạng thái" giữ, thêm trạng thái `đang chờ Lead có hạn` |
| §2 Gates + §2.1 preview + §2.2 request-changes | Thay bằng bảng ba loại điểm dừng (white paper §II); luật preview chỉ cho Gate R và RED; vòng request-changes chỉ còn ở Gate R (`hold`) |
| §4.10 Open questions | Đổi thành **Sổ giả định** (§III): `OQB/OQT` → `ASM` có `default_if_silent`; giữ dòng "đã soát nguồn nào" (§4.10.9) làm `sources_checked`; câu `CHẶN UOW-NN` chỉ còn hợp lệ khi là Mốc chờ hoặc RED |
| §4.6 Escalation | Đổi tên thành **Ranh đỏ** với 9 dòng mặc định; `escalations/` giữ làm nơi sinh `RED` hoặc `ASM` |
| §4.12 Unit `done` | Thêm điều kiện: Showcase đã mở ≥ 1 lần (trừ Unit khai `no_showcase: <lý do>` — doctor WARN) |
| §9.6 Nghiệm kết quả | Giữ nguyên; trưởng ca là người nghiệm |
| Mới §4.18 Sổ giả định · §4.19 Showcase · §4.20 Gate R · §4.21 Bẻ lái · §4.22 Bản tin ca | Theo white paper §III–§VII |
| §5 Định dạng bản ghi | Thêm format `ASM` · `CP` · `SC`/`FB` · `STR` · `RED` · `GATE-R`; DEC chỉ còn sinh ở Gate R, RED, và patch gói |
| §8 Dòng chảy trên tower | Màn chính là Bản tin ca; Gate queue chỉ còn Gate R + RED |

### 2.2 Hooks

| Hook | 6.0.0 | 7.0.0 |
|---|---|---|
| PreToolUse `gate_guard.py` | chặn Edit/Write vào code roots khi intent chưa có DEC Gate D | **red-line guard**: chặn lệnh deploy / migration có `DROP|TRUNCATE|DELETE` không WHERE / ghi ra ngoài (gh pr, email, slack send) khi không có `DEC` trỏ `RED-NN` tương ứng. **Không chặn code.** Mode `gatekeeper` giữ hành vi cũ |
| SessionStart | nạp governance + drain inbox | thêm: in Bản tin ca mới nhất; drain `FB`/`STR` từ tower như drain inbox |

### 2.3 Skills

| Skill | Đổi |
|---|---|
| `dlc-intent` | Sau khi sinh intent-plan: ghi `CP-01` với `wait_until` (chỉ phần *đích*), **không** "DỪNG chờ duyệt"; tự chạy tiếp `dlc-discover` nếu không chạm RED |
| `dlc-discover` · `dlc-validate` | Ghi `CP`, đi tiếp. `dlc-validate` sinh `ASM` thay `open-questions-*.md`; câu đảo đắt → Mốc chờ |
| `dlc-units` | Ghi `CP` với Mốc chờ cho *thứ tự Unit + Unit nào Showcase trước*; bảng tầng review là nội bộ |
| `dlc-bolt` | Bỏ checkpoint Gate E(a) của người; kết thúc Bolt bằng gọi `dlc-showcase` |
| **`dlc-showcase`** (mới) | Kiểm "có thứ để dùng" (bảng §IV.1) → dựng Showcase Pack → đăng tower → mở Unit kế |
| **`dlc-ledger`** (mới) | Xem/lọc Sổ giả định theo Unit, mức, trạng thái; đóng ASM bằng FB/STR |
| **`dlc-steer`** (mới) | Lead ghi `STR-NNN`; orchestrator lập lại kế hoạch phần chạm |
| **`dlc-brief`** (mới, thay `session_brief`) | Bản tin ca một trang; `dlc-resume` in nó đầu tiên |
| `dlc-accept` → **`dlc-release`** | Dựng hồ sơ Gate R 9 mục; kết thúc lượt chờ ký; `hold` → Bolt sửa + mở lại với changelog |
| `dlc-retro` | Thêm bảng KPI §IX; LL là Mốc chờ; patch gói vẫn cần Lead ký |
| `dlc-doctor` | Thêm kiểm: ASM thiếu trường bắt buộc · `reversal_cost` thấp hơn dấu vết (grep migration/public API/auth/PII) · agent dừng không có `RED`/`wait_until` · Showcase không có thứ chạy · Unit đóng không Showcase · Gate R còn ASM ≥ `vừa` |
| `dlc-revise` | Chỉ còn dùng cho `hold` ở Gate R và DEC ở RED |

### 2.4 Agents

- `dlc-orchestrator` → đổi mô tả thành **trưởng ca**: giữ ledger, Team Agreement, quyết loại điểm dừng theo luật, viết Bản tin, dựng Gate R. Không "kết thúc lượt khi gate mở" nữa trừ Gate R/RED.
- `dlc-context-validator` → sinh ASM thay open questions.
- `dlc-acceptance-recorder` → thêm việc dựng Showcase Pack và hồ sơ Gate R (hoặc tách `dlc-showcase-builder` nếu HOF quá dài).
- Các dev/specialist: thêm vào `read_first` luật "không hỏi rồi chờ — ghi ASM".

### 2.5 Tower

Spec đầy đủ: `control-tower-lead-view.md` (decision-first, ba tầng). Tóm tắt:

| Màn | Đổi |
|---|---|
| **Cần tôi quyết** (mới, màn mặc định) | chỉ thẻ cần Lead hành động: ■ Gate R · ■ RED · ◇⏱ Mốc chờ sắp hết hạn · ◉ Showcase chờ FB · ? câu hỏi. Mỗi thẻ: câu hỏi bằng lời · nếu im lặng + hạn · phương án có giá · nút quyết trên thẻ · Xem thêm ▸. Tối đa 7 thẻ |
| **Bản tin ca** (mới) | một trang §VII.3, một nút |
| **Tra cứu ▾** (dropdown ẩn) | **mọi màn hiện có** của 6.0.0 chuyển vào đây không đổi: Mission Control (→ đổi tên *Agents & HOF*), Intents, Bolt/Task Board, Comms & Reviews, Dòng chảy 3 pha, Governance; thêm Sổ giả định, KPI |
| Gate Queue | thành thẻ ■ trong *Cần tôi quyết*; giữ luật preview/`previewed: true` |
| Showcase | thẻ ◉ với nút FB ba trạng thái cạnh từng ASM → ghi `feedback.md` qua inbox |
| Thông báo | push chỉ cho ■ và Mốc chờ < 1h; agent im lặng/tin chết/drift **không** push, chỉ một dòng cuối Bản tin |

**Làm được ngay trên 6.0.0** (mục 5 của spec, ~1 ngày, không đổi luật gate): `LeadInbox.jsx` làm màn mặc định, nav thu về 3 mục, open-questions (đã có "phương án kèm giá" + "mặc định nếu im lặng") đổ thẳng vào thẻ ?. Không phụ thuộc phương án A/B/C.

### 2.6 Templates & governance

- Thêm `templates/assumption.md` · `checkpoint.md` · `showcase/README.md` · `showcase/feedback.md` · `steer.md` · `gate-r.md` · `red-line.md` · `brief.md`.
- Thêm `templates/governance/leadership.md` (núm) và `red-lines.md` (9 dòng mặc định).
- `MIGRATION.md` v7: `open-questions-*.md` → `assumptions/ledger.md` (mỗi câu `OQB/OQT` thành ASM với `default_if_silent` = phương án chọn sẵn đã có); `status.md` `gate_open: E` đang treo → `SC` đang chờ; Gate F đang mở → Gate R với hồ sơ dựng lại **từ evidence thật** (thiếu thì ghi khoảng trống, không dựng bù).

## 3 · PILOT INT-003 (đang stage 6) xử lý thế nào

- Phương án B: pin `mode: gatekeeper` cho INT-003 qua `intents/INT-003/pinned/` — không đổi luật chơi giữa intent (đúng cơ chế pinned §7 của plan v1). RV-019/020 `unfulfilled` vẫn là nợ của INT-003, không xoá bằng migration.
- Intent kế (INT-004) chạy `mode: lead` từ đầu → retro INT-004 có dữ liệu v2, đối chứng với INT-003 → trả `LL` cho 7.0.0.
- Nợ KPI cũ của PILOT (`units.reviewed` 0/17 · `units.artifacts` 0/17) không đổi vì v2; Gate R của INT-004 có mục "Khoảng trống trung thực" để ghi nó.

## 4 · Kỷ luật sửa gói vẫn áp

7.0.0 là **quyết định chủ gói** như 5.0.0 và 6.0.0 — căn cứ ghi ở white paper §0 (Gate D 30 Unit/113h · LL-002 13/0 · 17 Unit không dừng · chờ người là đường găng). **Nợ một LL**; retro đầu tiên có dữ liệu hai mode phải trả bằng bảng KPI §IX. CHANGELOG 7.0.0 ghi rõ điều này, không ghi "theo LL".

## 5 · Việc cần chủ gói chốt trước khi làm

1. **Phương án A / B / C** (mục 1) — khuyến nghị B.
2. **Nhịp Gate R mặc định**: theo Unit (khuyến nghị, vì Unit đã `releasable`) hay theo Intent.
3. **`wait_until` mặc định** cho Mốc chờ: 4 giờ làm việc (khuyến nghị) · 1 ngày · tới ca sau.
4. **Ranh đỏ dòng 7** (auth/PII `cao`): giữ là chốt chặn, hay hạ thành Mốc chờ để nhanh hơn? — khuyến nghị giữ.
5. **Có gỡ `mode: gatekeeper` ở 8.0.0** không, hay giữ vĩnh viễn cho dự án chịu quy định?
6. **Số repo code của đội đầu tiên** (`multi-user-shared-space.md` mục 2.1) — `.ai-dlc/` trong monorepo hay repo control plane riêng; khuyến nghị **repo riêng** kể cả monorepo.
7. **"Im lặng quá hạn = mặc định"** cho câu hỏi và test case (không áp cho gate) — PM/APO có chấp nhận không; khuyến nghị có, hạn 1 ngày làm việc, tower hiện rõ "đã dùng mặc định".
