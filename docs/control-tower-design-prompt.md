# Design Prompt — AI-DLC Control Tower UI

> Cách dùng: dán toàn bộ phần dưới dấu `---` vào Claude design (hoặc bất kỳ AI design tool nào).
> Nên chạy 2 vòng: vòng 1 để nó dựng **Screen 1 (Mission Control)** và **Screen 2 (Bản đồ AI-DLC)** trước — hai màn quan trọng nhất;
> ưng rồi mới bảo nó làm tiếp Screen 3–6 cùng design system. Mỗi lần feedback, chỉ sửa 1 màn.

---

Thiết kế giao diện web app tên **Control Tower** — màn hình quan sát cho một người (Human Supervisor) đang giám sát một đội **17 AI agents** làm phần mềm theo quy trình AI-DLC (AI-Driven Development Lifecycle). Người này KHÔNG code — vai trò của họ là **quan sát tiến độ, ra quyết định tại các điểm dừng (gate), và truy vết mọi việc AI đã làm**.

## Bối cảnh hệ thống (để hiểu data)

Công việc chảy qua 8 stage: `1 Request → 2 Discovery → 3 Validation → 4 Clarify → 5 Units → 6 Construction → 7 Acceptance → 8 Release`. Flow **dừng bắt buộc** tại 7 loại gate (A–G) chờ người duyệt — không có cơ chế cho AI tự vượt gate.

Khái niệm chính:
- **Intent** (`INT-001`) — một yêu cầu lớn, ví dụ "Triển khai Phase 2 cho PCT"
- **Unit of Work** (`UOW-01`) — một business capability bàn giao được, ví dụ "Release Planning"
- **Bolt** — vòng lặp nhỏ nhất (thay cho Sprint), chu kỳ build–xác nhận tính bằng giờ hoặc ngày. **Một Unit chạy qua một hoặc nhiều Bolt, song song hoặc tuần tự** (theo white paper AI-DLC); mỗi Bolt gói một phạm vi rõ trong Unit và đi qua: Domain Design → Logical Design + ADR → Code + Unit Test
- **Phân cấp chuẩn**: Project → Intent → Unit → Bolt → Task
- **3 pha** (theo white paper): **Inception** (Mob Elaboration: Intent → Units + PR-FAQ, User Stories, NFR, Rủi ro, Bolt đề xuất) → **Construction** (Mob Construction: các Bolt chạy) → **Operations** (Deployment Unit production, telemetry, runbook chờ Developer phê duyệt)
- **Artefact bổ sung**: PR-FAQ (tùy chọn), NFR, ADR (biên bản quyết định kiến trúc), Deployment Unit (mã + config + IaC đã kiểm thử, đóng gói)
- **Task** (`TSK-02`) — việc kỹ thuật trong task board của Bolt, có `claimed_by` (agent nhận), `approver` (người/agent duyệt — assign sẵn), `depends_on`, `status: todo/claimed/in-progress/blocked/review/done`
- **MSG** (`MSG-0058`) — message giữa 2 agents (type: review-request, finding, question, answer, clarification, handoff, note)
- **RV** (`RV-012`) — review verdict: `approve / approve-with-notes / request-changes`
- **DEC** (`DEC-0018`) — quyết định đã chốt (thường do người duyệt tại gate)
- **LL** (`LL-002`) — lesson learned sau retro, kèm patch nâng version checklist của agent
- **Escalation** — khi 2 agents bất đồng 2 lần, hoặc phát hiện logic sai từ gốc / tài liệu thiếu → đẩy lên người

Agents chia 3 nhóm: **Pipeline** (orchestrator, intent-analyst, context-archaeologist, context-validator, unit-planner, bolt-coordinator, be-dev, fe-dev, acceptance-recorder), **Review Board** (ba, pm-po, tech-lead, security, backend, frontend, qa reviewer), **Learning** (retro-keeper).

## Jobs-to-be-done (xếp theo độ ưu tiên)

1. **"Cái gì đang chờ TÔI?"** — gate queue phải là thứ đập vào mắt đầu tiên. Mỗi gate card có **decision brief**: bối cảnh 2–3 dòng, các phương án, trade-off, khuyến nghị của ba-reviewer, và nút **Approve / Reject / Cần thảo luận**.
2. **"Mọi thứ đang ở đâu?"** — pipeline board: mỗi intent một hàng, 8 stage chips, đang đứng stage nào, gate nào đang mở.
3. **"Agents đang làm gì với nhau?"** — activity + comms feed realtime, lọc theo agent/type/task.
4. **"Truy vết một quyết định"** — từ 1 dòng code hoặc 1 task, mở drawer xem chuỗi: `code → design → UOW spec → DEC → RV → MSG → intent`.
5. **"Rủi ro và bài học"** — risk register, tech-debt, lessons + version các checklist.

## Screens (6 màn)

### Screen 1 — Mission Control (màn chính, quan trọng nhất)
- **Hàng đầu**: KPI strip nhỏ (Gates chờ tôi: 2 · Escalations: 1 · Bolts đang chạy: 2 · Units done tuần này: 3)
- **Khối lớn nhất, trên cùng bên trái: GATE QUEUE** — danh sách gate card màu cam. Card mở rộng được để đọc decision brief ngay tại chỗ, có nút Approve/Reject (Reject bắt buộc nhập lý do). Escalation card cũng nằm đây, phân biệt bằng icon.
- **Pipeline Board**: mỗi intent 1 hàng — mã + tên + 8 stage chips (done=xanh lá, active=cam có ký hiệu gate nếu đang chờ, pending=xám) + avatar agent đang giữ ball.
- **Cột phải: Live feed** — trộn activity + comms, mỗi dòng: thời gian, from → to, type badge, 1 dòng tóm tắt, click mở chi tiết.
- Empty state khi chưa có gate chờ: "Không có gì chờ bạn — agents đang làm việc" + nhịp thở nhẹ.

### Screen 2 — Bản đồ AI-DLC (Map view — QUAN TRỌNG, theo đúng Hình 1 của white paper AI-DLC)

Tái hiện "Bản đồ AI-DLC" của white paper thành bản đồ **sống** — cùng bố cục, nhưng mỗi node hiển thị trạng thái realtime của intent đang chọn:

- **Bố cục 3 cột**: trái = "Vai trò / Nghi thức", giữa = "Dòng chảy công việc", phải = "Artefact". Ba band ngang theo pha: **Inception → Construction → Operations**.
- **Band Inception**: cột trái ghi "Product Owner, Developers, QA, AI · Mob Elaboration". Giữa: node Intent → các Unit card, mỗi Unit có badge "Mob xác nhận ✓ / đang chờ" (amber khi chờ). Phải: chip artefact PR-FAQ · User Stories · NFR · Rủi ro · Bolt đề xuất — chip sáng khi artefact đã tồn tại, click mở nội dung.
- **Band Construction**: cột trái "Developers, AI · Product Owner khi cần · Mob Construction (Mob Programming + Mob Testing)". Giữa: mỗi Unit một swimlane, trong lane là các **Bolt pill** (Bolt 1, Bolt 2…) chạy song song hoặc tuần tự; trong mỗi Bolt pill hiện mini-progress 3 nấc **Domain Design → Logical Design + ADR → Code + Unit Test**, với chấm amber tại điểm đang chờ con người xác nhận. Với intent brown-field, đầu band có node "Nâng mã lên mô hình tĩnh + động" (reverse engineering). Phải: chip Domain Design · Logical Design + ADR · Code + Unit Test · **Deployment Unit** (đã kiểm thử, bảo mật, đóng gói).
- **Band Operations**: cột trái "Product Owner, Developers, AI". Giữa: các Deployment Unit đang production + dòng telemetry/anomaly/dự báo SLA; hành động runbook hiển thị dạng card amber "chờ Developer phê duyệt". Phải: chip Telemetry · Runbook actions.
- **Nguyên tắc hiển thị xuyên suốt** (in làm caption của màn): *"Ở mọi điểm phân rã, AI đề xuất trước và con người xác nhận trước khi đi tiếp"* — mọi điểm xác nhận là diamond amber, đồng bộ ngôn ngữ màu với Gate Queue.
- Click bất kỳ node/chip → drawer truy vết (spec, MSG/RV/DEC liên quan). Chọn intent khác bằng dropdown ở header màn.

### Screen 3 — Intent Detail (`INT-001`)
- Header: tên intent, stage hiện tại trên progress bar 8 bước, brownfield type, link tài liệu gốc
- Tab **Units**: card mỗi UOW — status, Bolt nào, % task done, risk chips
- Tab **Open Questions**: câu hỏi, ai trả lời, deadline, ảnh hưởng nếu chưa trả lời
- Tab **Decisions (DEC)**: bảng timeline các quyết định, ai quyết, căn cứ (link RV/MSG)
- Tab **Changelog**: mọi thay đổi trong intent

### Screen 4 — Bolt / Task Board (`UOW-01 · Bolt 1`)
- Kanban 6 cột theo status HOẶC list view — mỗi task card: ID, tên, `claimed_by` (avatar agent), `approver`, depends_on (vẽ liên kết hoặc badge "chờ TSK-02"), số MSG gắn kèm
- Panel **Contract**: trạng thái API contract (draft / negotiating / **FROZEN v2**), ai đã đồng ý, link các MSG clarification
- **Checkpoint strip**: 2 điểm Gate E (design OK? · demo OK?) — trạng thái từng điểm
- Click task → drawer: full metadata + toàn bộ comms của task đó theo thread

### Screen 5 — Comms & Reviews
- **Comms**: bảng lọc được (from/to/type/re/status), click mở thread. Thread view giống chat nhưng mỗi message có ID + type badge — nhấn mạnh đây là văn bản truy vết được, không phải chat phù du
- **Reviews**: bảng RV — reviewer, target, verdict chip (xanh lá/vàng cam), checklist version đã dùng, findings MUST/SHOULD

### Screen 6 — Governance & Learning
- **DoR / DoD**: nội dung hiện hành + version + changelog từng version (ai đổi, DEC nào, từ lesson nào)
- **Risk register + Tech-debt register**: bảng, severity chip
- **Lessons**: card LL — trigger, lesson, patch đã apply vào checklist nào (v2→v3), trạng thái proposed/approved/applied

## Data mẫu để fill UI (dùng đúng, đừng lorem)

- Intent: `INT-001 — Triển khai Phase 2 PCT (Release + Milestone + Backlog)` — đang ở stage 5, Gate D mở
- Gate card 1: `Gate D · INT-001 — Duyệt scope 4 Units + DoD v1`. Brief: "unit-planner đề xuất 4 Units; pm-po verdict approve-with-notes (RV-010); trade-off: defer UOW-04 Backlog nếu chờ LakeHouse; khuyến nghị: approve 01–03, quyết riêng 04"
- Gate card 2 (escalation): `UOW-03 — tech-lead vs be-dev bất đồng: sync call legacy API sẽ timeout batch >500 → đề xuất chuyển queue (RV-012, 2× request-changes)`
- Intent 2: `INT-002 — Slack reminder FB-012` — đang ở stage 2
- Tasks Bolt 1: `TSK-01 API contract (done, be-dev, duyệt bởi fe-dev + tech-lead)` · `TSK-02 BE migration+service (in-progress, be-dev, approver backend-reviewer)` · `TSK-03 FE SCR-REL-10 list (in-progress, fe-dev, mock theo contract frozen)` · `TSK-04 FE popup nối API thật (blocked — chờ TSK-02 done + duyệt)` · `TSK-05 Integration E2E (todo, approver qa-reviewer)`
- MSG mẫu: `MSG-0058 · fe-dev → be-dev · clarification · "status enum trả code hay label? i18n phía nào?"` → `MSG-0060 · chốt: trả code, FE map i18n`
- Review: `RV-011 security-reviewer · approve` · `RV-012 tech-lead · request-changes`
- Lesson: `LL-002 — legacy API có batch limit không tài liệu hóa → patch review-approach v2→v3: "hỏi batch limit/timeout của mọi external call ngay ở Domain Design"`
- Risk: `RISK-04 · high · migration case cũ chưa có câu trả lời từ client`

## Design direction

- **Ops console / air-traffic control**, nghiêm túc, mật độ thông tin cao nhưng thoáng — KHÔNG phải marketing site, không hero, không gradient tím
- Ngôn ngữ semantics màu (nhất quán toàn app): **cam/amber = cần con người quyết** (gate, escalation) · **xanh dương = hoạt động của review/agents** · **xanh lá = done/approved** · xám = pending. Nền neutral lạnh
- Monospace cho mọi ID (INT/UOW/TSK/MSG/RV/DEC/LL) và số liệu; sans-serif cho phần đọc
- Hỗ trợ light + dark mode; dark là mode chính (ops console)
- Realtime: dòng mới trong feed trượt vào nhẹ nhàng; gate mới xuất hiện có hiệu ứng nổi bật 1 lần rồi tĩnh — người dùng cần yên tâm là màn hình "sống" nhưng không gây mệt
- Desktop-first (màn 13–27"), responsive xuống tablet là đủ
- Stack ưa thích: Next.js + Tailwind + shadcn/ui, tiếng Việt là ngôn ngữ chính của UI (giữ term tiếng Anh: Intent, Unit, Bolt, Gate…)

Bắt đầu với **Screen 1 — Mission Control** trước, đầy đủ trạng thái với data mẫu ở trên. Các screen sau chỉ làm khi Screen 1 đã chốt.
