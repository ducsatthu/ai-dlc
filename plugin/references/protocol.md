# AI-DLC Protocol — giao thức chung (v1)

> MỌI agent và skill của plugin PHẢI tuân thủ file này. Tài liệu phương pháp gốc: white paper AI-DLC
> (bản dịch nội bộ TechTus — `docs/whitepaper-ai-dlc-vi.md` trong repo plugin). Mâu thuẫn → white paper thắng.

## 1. Phân cấp & pha

**Project → Intent → Unit → Bolt → Task.** Một Unit chạy qua một hoặc nhiều Bolt, song song hoặc tuần tự.
Mỗi Bolt: `Domain Design → Logical Design + ADR → Code + Unit Test`.

Ba pha (white paper) ↔ 8 stage:
- **Inception** = stage 1 Request → 2 Discovery → 3 Validation → 4 Clarify → 5 Units (nghi thức Mob Elaboration).
  Artefact per Unit: user-stories, NFR, risks, (PR-FAQ tùy chọn), Bolt đề xuất.
- **Construction** = stage 6 (Mob Construction). Brown-field: stage 2–3 nâng mã lên mô hình tĩnh + động trước.
- **Operations** = stage 7 Acceptance → 8 Release → Deployment Unit, telemetry, runbook.

**Nguyên tắc xuyên suốt: ở mọi điểm phân rã, AI đề xuất trước — con người xác nhận trước khi đi tiếp.**

## 2. Gates (điểm dừng bắt buộc — không agent nào được vượt)

| Gate | Vị trí | Người quyết |
|---|---|---|
| A | sau stage 1 | Intent đúng outcome? scope? |
| B | sau stage 3 | AS-IS model đúng thực tế? |
| C | sau stage 4 | Chốt open questions business |
| D | sau stage 5 | Approve Units + Bolt plan + DoD/DoR version |
| E | trong mỗi Bolt | (a) OK design + ADR + contract; (b) OK demo sau review |
| F | sau stage 7 | UAT / approve deploy (cần: QC evidence đủ + security MUST = 0) |
| G | sau retro | Duyệt lesson + patch skill |
| động | bất kỳ | Escalation: 2× request-changes, logic sai từ gốc, tài liệu thiếu chạm scope |

Khi gate mở: orchestrator ghi gate vào `status.md`, tạo entry Gate Queue, cập nhật tower, gửi PushNotification
(nếu có), rồi **KẾT THÚC LƯỢT** với thông báo rõ cần người quyết gì. Quyết định đến qua terminal hoặc
`.ai-dlc/inbox/` (tower). Mỗi approval/reject = một DEC.

## 3. Layout state trong project

```
.ai-dlc/
├── workspace-map.md            # code/docs/wiki nằm đâu — NGUỒN DUY NHẤT để resolve path output
├── context-memory/
│   ├── governance/dor.md dod.md decisions-log.md changelog.md risks.md tech-debt-register.md
│   ├── comms/MSG-NNNN.md       # message bus
│   ├── reviews/RV-NNN.md
│   ├── lessons-learned/LL-NNN.md
│   └── intents/INT-NNN/
│       ├── intent.md  status.md  open-questions.md  as-is/  decision-briefs/
│       ├── pinned/              # snapshot checklists + governance lúc intent bắt đầu
│       └── units/UOW-NN/
│           ├── spec.md user-stories.md nfr.md risks.md (pr-faq.md)
│           └── bolts/BOLT-NN/  # domain-design.md logical-design.md adr/ contract.md tasks.md evidence/
├── inbox/                      # durable queue từ tower (processed/ sau khi xử lý)
├── overrides/                  # OVERRIDES.md + checklists/ agents/ governance/
└── tower/                      # HTML generated
```

## 4. Binding rules (bắt buộc, thứ tự kiểm tra)

1. **Override thắng**: trước khi dùng checklist/governance X, kiểm tra `.ai-dlc/overrides/**/X` — có thì dùng bản đó
   (kiểu `patch` = áp lên bản gốc; `replace` = thay hẳn). Override phải có frontmatter `reason`, `source`.
2. **Pinned thắng bản sống**: agent làm việc trong INT-NNN đọc checklist/governance từ `pinned/` của intent đó.
3. **Workspace map — không đoán path**: mọi output (code, docs) resolve đích qua `workspace-map.md`.
   Map thiếu mục cần dùng → HỎI, không đoán.
4. **No silent change**: đổi bất kỳ artifact đã qua duyệt → DEC mới + dòng changelog; chạm scope → mở lại gate.
5. **Ghi chú bắt buộc**: kết thúc lượt làm việc, agent ghi MSG type `note` tóm tắt đã làm gì + bàn giao gì.
6. **Escalation**: 2× request-changes cùng artifact, hoặc phát hiện logic sai từ gốc / tài liệu thiếu gây hiểu
   nhầm → KHÔNG tự vá; tạo MSG escalation → tech-lead-reviewer → gate động nếu chạm scope/business.
7. **Claim**: task chỉ được claim khi mọi `depends_on` đã `done` VÀ được approver ký. Một task một người claim.

## 5. Định dạng bản ghi

`comms/MSG-NNNN.md`:
```
---
from: <agent>  to: <agent|HUMAN>  re: INT-NNN[/UOW-NN[/BOLT-NN[/TSK-NN]]]
type: review-request|finding|question|answer|clarification|handoff|note|escalation
status: open|answered|closed
---
<nội dung>
```

`reviews/RV-NNN.md`:
```
---
reviewer: <agent>  target: <đường dẫn artifact>
verdict: approve|approve-with-notes|request-changes
checklist: <tên> v<N>
---
[MUST] ... / [SHOULD] ...
```

`governance/decisions-log.md` — append entry:
```
## DEC-NNNN · <ngày> · <Gate X | thay đổi> · INT-NNN
- Quyết định: ...   - Người quyết: HUMAN|<agent đề xuất>
- Căn cứ: RV-xxx · MSG-xxxx   - Ảnh hưởng: ...
```

`tasks.md` — mỗi task:
```
## TSK-NN · <tên>
perspective: BE|FE|shared   status: todo|claimed|in-progress|blocked|review|done
claimed_by: <agent|->   approver: <reviewer — assign lúc tạo board>
depends_on: [...]   comms: [MSG-...]   notes: ...
```

`status.md` (per intent):
```
---
intent: INT-NNN   stage: 1..8   phase: inception|construction|operations
gates_passed: [A, B, ...]   gate_open: <A..G|escalation|null>
plugin_version: 1.0.0
---
```

## 6. Phân tầng model (ai chạy bằng model nào)

| Tier | Model | Agents | Lý do |
|---|---|---|---|
| Sâu | opus | orchestrator, intent-analyst, context-archaeologist, unit-planner, ba-reviewer, tech-lead-reviewer, security-reviewer | phân rã, kiến trúc, rủi ro — sai ở đây lan xuống toàn hạ nguồn |
| Thực thi | sonnet | context-validator, bolt-coordinator, be-dev, fe-dev, pm-po-reviewer, backend-reviewer, frontend-reviewer, qa-reviewer, retro-keeper | code, review theo checklist, điều phối |
| Cơ học | haiku | acceptance-recorder | gom evidence, trace link, persist — theo khuôn |

Reviewer chỉ được gọi cho phần thuộc góc nhìn của mình; bolt thuần BE không gọi frontend-reviewer.

## 7. ID & đánh số

INT/UOW/BOLT: 2–3 chữ số, tăng dần trong phạm vi cha. MSG/RV/DEC/LL: đếm toàn cục trong project,
lấy số kế tiếp bằng cách liệt kê file/entry hiện có. Không tái sử dụng ID.
