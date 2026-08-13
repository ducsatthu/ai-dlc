// Sample data — taken verbatim from docs/control-tower-design-prompt.md and docs/simulation-phase2-pct.html
window.CT_DATA = {
  // Ba pha của AI-DLC — Intent nằm ở đâu trên trục Inception → Construction → Operations
  phase: {
    now: 'construction',
    lanes: [
      { key: 'inception', name: 'Inception', ritual: 'Mob Elaboration', intents: ['INT-002', 'INT-005'],
        note: 'AI làm rõ Intent → User Story · NFR · rủi ro → đề xuất Unit' },
      { key: 'construction', name: 'Construction', ritual: 'Mob Construction', intents: ['INT-001', 'INT-003'],
        note: 'Domain Design → Logical Design + ADR → Code + Unit Test' },
      { key: 'operations', name: 'Operations', ritual: '—', intents: ['INT-004', 'INT-006'],
        note: 'Telemetry · bất thường · runbook chờ Developer phê duyệt' }
    ]
  },
  // Bolt đang chạy — vòng lặp tính bằng giờ, không phải tuần
  bolt: {
    id: 'Bolt 1', unit: 'UOW-01 Release Planning', intent: 'INT-001', ritual: 'Mob Construction',
    elapsed: '4h 12m', budget: '1 ngày', pct: 52, agents: 3,
    step: 'Bước 4 · Mô hình hóa miền, sinh mã và kiểm thử'
  },
  // Pha Operations — AI phân tích telemetry, đề xuất hành động runbook, chờ người phê duyệt
  ops: {
    deployed: [
      { id: 'DU-014', unit: 'UOW-01 Lifecycle rules', intent: 'INT-006', env: 'production', since: '2 ngày' },
      { id: 'DU-013', unit: 'UOW-02 Data migration', intent: 'INT-006', env: 'production', since: '2 ngày' }
    ],
    signals: [
      { id: 'OPS-021', sev: 'warn', what: 'p95 /api/reports/export 2.8s → 6.1s trong giờ cao điểm',
        forecast: 'dự báo chạm ngưỡng SLA 8s sau ~3 giờ', runbook: 'RB-07 · scale-worker',
        action: 'Tăng job queue từ 2 lên 4 worker', status: 'chờ bạn duyệt' },
      { id: 'OPS-022', sev: 'info', what: 'Lỗi 409 tăng nhẹ sau khi bật ràng buộc unique release name',
        forecast: 'trong ngưỡng — khớp AC-03, không phải sự cố', runbook: null,
        action: null, status: 'theo dõi' }
    ]
  },
  intents: [
    { id: 'INT-001', name: 'Triển khai Phase 2 PCT (Release + Milestone + Backlog)', stage: 5, gate: 'D', holder: 'unit-planner', brownfield: 'Add feature', doc: 'wiki/docs/phase2-screens.md', owner: 'PMO Túy', updated: '14:22 hôm nay', units: [4, 0], risk: 'high' },
    { id: 'INT-002', name: 'Slack reminder FB-012', stage: 2, holder: 'context-archaeologist', brownfield: 'Add feature', doc: 'FEEDBACK_TRACKER.md', owner: 'APM Hà', updated: '13:05 hôm nay', units: [0, 0], risk: null },
    { id: 'INT-003', name: 'Quality Gate P1.2 — đóng nốt BATCH-020', stage: 6, holder: 'be-dev', brownfield: 'Add feature', doc: 'plans/phase-1/batch-020.md', owner: 'CTO', updated: '11:40 hôm nay', units: [3, 2], risk: null },
    { id: 'INT-004', name: 'Weekly report export PDF chậm > 30s', stage: 6, gate: 'E', holder: 'tech-lead-reviewer', brownfield: 'Optimize NFR', doc: 'FEEDBACK_TRACKER.md#FB-031', owner: 'APM Hà', updated: 'hôm qua', units: [2, 1], risk: 'med' },
    { id: 'INT-005', name: 'Gỡ mock layer SCR-REL-10 sau khi nối API thật', stage: 3, holder: 'context-validator', brownfield: 'Technical debt', doc: 'DEBT-03', owner: 'tech-lead', updated: 'hôm qua', units: [0, 0], risk: null },
    { id: 'INT-006', name: 'Sai trạng thái RFE/NOID khi close case cũ', stage: 8, holder: 'acceptance-recorder', brownfield: 'Fix defect', doc: 'wiki/docs/use-cases.md', owner: 'Client SME', updated: '09/08', units: [2, 2], risk: null }
  ],
  unitsByIntent: {
    'INT-003': [
      { id: 'UOW-01', name: 'Checklist gate cho batch', status: 'in-bolt', bolt: 'Bolt 1', done: 80, risks: [] },
      { id: 'UOW-02', name: 'Badge trạng thái gate trên milestone', status: 'in-bolt', bolt: 'Bolt 2', done: 40, risks: [] },
      { id: 'UOW-03', name: 'Export báo cáo gate', status: 'pending-gate', bolt: 'Bolt 3', done: 0, risks: [] }
    ],
    'INT-004': [
      { id: 'UOW-01', name: 'Cache query weekly report', status: 'in-bolt', bolt: 'Bolt 1', done: 65, risks: ['DEBT-02'] },
      { id: 'UOW-02', name: 'Render PDF nền (job queue)', status: 'blocked', bolt: 'Bolt 2', done: 10, risks: [] }
    ],
    'INT-006': [
      { id: 'UOW-01', name: 'Lifecycle rules cho terminal status', status: 'done', bolt: 'Bolt 1', done: 100, risks: [] },
      { id: 'UOW-02', name: 'Data migration case cũ', status: 'done', bolt: 'Bolt 2', done: 100, risks: [] }
    ]
  },
  gates: [
    { key: 'g1', kind: 'gate', gate: 'D', target: 'INT-001', title: 'Duyệt scope 4 Units + DoD v1',
      brief: 'unit-planner đề xuất 4 Units; pm-po verdict approve-with-notes (RV-010).',
      options: ['Approve cả 4 Units — UOW-04 Backlog phụ thuộc dữ liệu LakeHouse chưa nối (RISK-01)', 'Defer UOW-04 Backlog nếu chờ LakeHouse; 01–03 chạy ngay'],
      recommendation: 'approve 01–03, quyết riêng 04', evidence: ['RV-010', 'units/UOW-01..04/spec.md', 'risks.md'] },
    { key: 'g2', kind: 'escalation', target: 'UOW-03', title: 'tech-lead vs be-dev bất đồng: sync call legacy API sẽ timeout batch >500',
      brief: 'Đề xuất chuyển sang queue. 2× request-changes cùng một điểm (RV-012) → tự động escalate.',
      options: ['Giữ sync call, giới hạn batch 500 ở FE', 'Chuyển sang queue — thêm ~1 ngày, bỏ giới hạn batch'],
      recommendation: 'tech-lead: chuyển queue', evidence: ['RV-012', 'MSG-0074'] }
  ],
  units: [
    { id: 'UOW-01', name: 'Release Planning', status: 'in-bolt', bolt: 'Bolt 1', done: 60, risks: [] },
    { id: 'UOW-02', name: 'Milestone Timeline', status: 'in-bolt', bolt: 'Bolt 2', done: 25, risks: [] },
    { id: 'UOW-03', name: 'Release ↔ Milestone liên kết + badge', status: 'blocked', bolt: 'Bolt 3', done: 0, risks: ['escalation'] },
    { id: 'UOW-04', name: 'Backlog Integration View', status: 'pending-gate', bolt: 'Bolt 4', done: 0, risks: ['RISK-01 LakeHouse'] }
  ],
  tasks: [
    { id: 'TSK-01', title: 'API contract draft + freeze', status: 'done', claimedBy: 'be-dev', approver: 'fe-dev + tech-lead', msgCount: 4 },
    { id: 'TSK-02', title: 'BE: migration + model + service + router + tests', status: 'in-progress', claimedBy: 'be-dev', approver: 'backend-reviewer', dependsOn: 'TSK-01', msgCount: 2 },
    { id: 'TSK-03', title: 'FE: SCR-REL-10 list + filter (bỏ cột QG theo Q52)', status: 'in-progress', claimedBy: 'fe-dev', approver: 'frontend-reviewer', dependsOn: 'TSK-01', msgCount: 1 },
    { id: 'TSK-04', title: 'FE: SCR-REL-11 popup tạo/sửa nối API thật', status: 'blocked', approver: 'frontend-reviewer', dependsOn: 'TSK-02' },
    { id: 'TSK-05', title: 'Integration + E2E theo AC', status: 'todo', approver: 'qa-reviewer', dependsOn: 'TSK-03, TSK-04' }
  ],
  work: [
    {
      taskId: 'TSK-02', title: 'BE: migration + model + service + router + tests', agent: 'be-dev', status: 'in-progress', elapsed: '18 phút',
      doing: 'Viết migration cho bảng release — ràng buộc unique (project_id, name) để trả 409 đúng AC-03',
      target: 'app-be/migrations/003_release.py',
      steps: [
        { label: 'Đọc pattern router→service→model của app-be', state: 'done' },
        { label: 'Migration + rollback script', state: 'doing' },
        { label: 'Model Release + status enum 4 giá trị', state: 'todo' },
        { label: 'Service + router theo contract v2', state: 'todo' },
        { label: 'Unit tests theo AC-01..05', state: 'todo' }
      ],
      messages: [
        { id: 'MSG-0060', from: 'be-dev', to: 'fe-dev', type: 'answer', body: 'Chốt: BE trả status code, FE map i18n.' },
        { id: 'MSG-0062', from: 'be-dev', to: 'tech-lead-reviewer', type: 'question', body: 'Migration cần rollback script riêng hay dùng downgrade() của alembic là đủ?' }
      ],
      assumption: 'Rollback dùng downgrade() của alembic, không viết script riêng — chưa có xác nhận của tech-lead-reviewer.',
      context: ['UOW-01/spec.md#AC-03', 'UOW-01/design.md', 'DEC-0015'],
      waitingOn: 'backend-reviewer ký sau khi tests xanh'
    },
    {
      taskId: 'TSK-03', title: 'FE: SCR-REL-10 list + filter', agent: 'fe-dev', status: 'in-progress', elapsed: '26 phút',
      doing: 'Dựng bảng release với mock theo contract v2 — bỏ cột Quality Gate theo Q52',
      target: 'app-fe/features/release/ReleaseList.tsx',
      steps: [
        { label: 'Mock data theo shape contract v2', state: 'done' },
        { label: 'Bảng + filter status/phase', state: 'doing' },
        { label: 'i18n key cho 4 status', state: 'todo' },
        { label: 'Component tests', state: 'todo' }
      ],
      messages: [
        { id: 'MSG-0058', from: 'fe-dev', to: 'be-dev', type: 'clarification', body: 'status enum trả code hay label? i18n phía nào?' },
        { id: 'MSG-0063', from: 'fe-dev', to: 'frontend-reviewer', type: 'review-request', body: 'Xin review sớm phần state của filter trước khi nối API thật.' }
      ],
      assumption: '4 status hiển thị bằng i18n phía FE, key đặt theo release.status.* — suy ra từ MSG-0060, chưa ghi vào spec.',
      context: ['UOW-01/contract.md v2', 'open-questions.md#Q52'],
      waitingOn: null
    },
    {
      taskId: 'TSK-04', title: 'FE: SCR-REL-11 popup tạo/sửa nối API thật', agent: 'fe-dev', status: 'blocked', elapsed: '—',
      doing: 'Chưa claim — luật claim chặn: task phụ thuộc chưa được approver duyệt',
      steps: [
        { label: 'TSK-02 done', state: 'todo' },
        { label: 'backend-reviewer duyệt TSK-02', state: 'todo' },
        { label: 'Nối form với POST/PATCH /api/releases', state: 'todo' }
      ],
      messages: [
        { id: 'MSG-0064', from: 'bolt-coordinator', to: 'fe-dev', type: 'note', body: 'TSK-04 mở khoá ngay khi RV của TSK-02 là approve.' }
      ],
      assumption: 'Form tạo và form sửa dùng chung một component, chỉ khác payload.',
      context: ['UOW-01/contract.md v2', 'RV-012'],
      waitingOn: 'TSK-02 done + backend-reviewer duyệt'
    },
    {
      taskId: 'TSK-01', title: 'API contract draft + freeze', agent: 'be-dev', status: 'done', elapsed: 'xong 13:40',
      doing: 'Đã freeze contract v2 sau 4 lượt trao đổi với fe-dev',
      target: 'UOW-01/contract.md',
      steps: [
        { label: 'Draft v1', state: 'done' },
        { label: 'fe-dev review + hỏi làm rõ', state: 'done' },
        { label: 'Chốt v2 + FREEZE', state: 'done' }
      ],
      messages: [
        { id: 'MSG-0061', from: 'be-dev', to: 'fe-dev', type: 'handoff', body: 'contract.md v2 FROZEN — TSK-03 chạy được với mock đúng shape.' }
      ],
      assumption: 'Đã chốt: 409 là mã lỗi cho trùng tên trong cùng project (AC-03).',
      context: ['UOW-01/spec.md', 'MSG-0058 → MSG-0061'],
      waitingOn: null
    }
  ],
  feed: [
    { time: '14:25', id: 'MSG-0060', from: 'be-dev', to: 'fe-dev', type: 'answer', summary: 'chốt: trả code, FE map i18n' },
    { time: '14:22', id: 'MSG-0058', from: 'fe-dev', to: 'be-dev', type: 'clarification', summary: 'status enum trả code hay label? i18n phía nào?' },
    { time: '14:11', id: 'RV-011', from: 'security-reviewer', to: 'UOW-01', type: 'review-request', summary: 'threat model OK — 0 MUST finding' },
    { time: '13:58', id: 'RV-012', from: 'tech-lead-reviewer', to: 'be-dev', type: 'finding', summary: 'sync call legacy API sẽ timeout batch >500 — request-changes lần 2' },
    { time: '13:40', id: 'MSG-0055', from: 'bolt-coordinator', to: 'fe-dev', type: 'handoff', summary: 'contract v2 FROZEN — TSK-03 có thể chạy với mock' },
    { time: '13:12', id: 'DEC-0017', from: 'orchestrator', to: 'INT-001', type: 'decision', summary: 'Gate C đóng — Backlog đi mock-first' },
    { time: '12:50', id: 'MSG-0049', from: 'qa-reviewer', to: 'unit-planner', type: 'question', summary: 'AC của UOW-02: Gantt cần zoom tuần không?' }
  ],
  // Nội dung đầy đủ của từng trao đổi — hỏi gì, trả lời gì, chốt ra sao
  threads: (function(){
    const t = {};
    t['MSG-0058'] = t['MSG-0060'] = {
      subject: 'status enum của Release: BE trả code hay label?',
      scope: 'TSK-01 · contract v2 · liên quan AC-02',
      turns: [
        { id: 'MSG-0058', time: '14:22', from: 'fe-dev', to: 'be-dev', type: 'clarification',
          body: 'Contract v2 ghi field status là enum 4 giá trị nhưng không nói API trả gì. FE cần biết: response trả code máy đọc (draft/active/frozen/released) hay trả label đã dịch sẵn? Nếu trả code thì i18n nằm phía FE và mình đặt key release.status.*; nếu trả label thì FE hiển thị thẳng nhưng không lọc được theo giá trị.' },
        { id: 'MSG-0059', time: '14:23', from: 'be-dev', to: 'fe-dev', type: 'note',
          body: 'Đang xem lại design.md. Enum lưu trong DB là code, nên trả label sẽ phải map thêm một lớp ở BE.' },
        { id: 'MSG-0060', time: '14:25', from: 'be-dev', to: 'fe-dev', type: 'answer',
          body: 'Chốt: API trả code, không trả label. Lý do: filter status theo query param cần đúng giá trị enum, và audit log cũng ghi code. FE map i18n với key release.status.draft / .active / .frozen / .released. Contract v2 không đổi shape nên không cần mở Gate.' },
        { id: 'MSG-0061', time: '14:27', from: 'fe-dev', to: 'be-dev', type: 'answer',
          body: 'OK, FE làm theo. Đã thêm 4 key i18n. Sẽ ghi lại vào spec.md phần NFR/UI để lần sau không phải hỏi lại.' }
      ],
      outcome: 'Không đổi contract. Nhãn trạng thái do FE dịch; be-dev giữ nguyên response.',
      refs: ['UOW-01/contract.md v2', 'UOW-01/spec.md#AC-02']
    };
    t['RV-011'] = {
      subject: 'security-reviewer: threat model cho UOW-01',
      scope: 'UOW-01 · review bắt buộc trước Gate E',
      turns: [
        { id: 'RV-011', time: '14:11', from: 'security-reviewer', to: 'UOW-01', type: 'review-request',
          body: 'Đã soát 3 điểm: (1) POST /api/releases yêu cầu quyền project-member — đã có; (2) lỗi 409 không rò tên release của project khác vì unique index nằm trong phạm vi project_id; (3) audit log ghi actor cho mọi lần chuyển trạng thái. Kết quả: 0 MUST finding, 1 NICE — nên rate-limit endpoint tạo release.' }
      ],
      outcome: 'Approve. Mục NICE ghi vào backlog kỹ thuật, không chặn Gate E.',
      refs: ['UOW-01/design.md']
    };
    t['RV-012'] = {
      subject: 'tech-lead-reviewer: sync call legacy API sẽ timeout với batch > 500',
      scope: 'TSK-02 · request-changes lần 2 → đủ điều kiện escalate',
      turns: [
        { id: 'RV-012', time: '13:58', from: 'tech-lead-reviewer', to: 'be-dev', type: 'finding',
          body: 'Service đang gọi legacy API đồng bộ trong request. Với batch trên 500 bản ghi, thời gian phản hồi vượt 30s và gateway sẽ cắt. Đây là lần thứ hai tôi request-changes cùng một điểm này. Đề xuất: đẩy sang job queue, endpoint trả 202 kèm job id.' },
        { id: 'MSG-0074', time: '14:02', from: 'be-dev', to: 'tech-lead-reviewer', type: 'question',
          body: 'Chuyển sang queue là thay đổi contract (201 → 202) nên phải mở Gate và sửa cả FE. Trong phạm vi Bolt này có kịp không, hay giữ sync và giới hạn batch 200 rồi làm queue ở Bolt sau?' }
      ],
      outcome: 'Chưa chốt — đã escalate lên bạn: hai lần request-changes cùng một điểm.',
      refs: ['UOW-01/contract.md v2', 'app-be/releases/service.py']
    };
    t['MSG-0055'] = {
      subject: 'contract v2 FROZEN — TSK-03 chạy được với mock',
      scope: 'bàn giao từ bolt-coordinator sang fe-dev',
      turns: [
        { id: 'MSG-0055', time: '13:40', from: 'bolt-coordinator', to: 'fe-dev', type: 'handoff',
          body: 'contract.md v2 đã đóng băng sau khi be-dev và tech-lead ký. FE dựng SCR-REL-10 với mock đúng shape trong contract, không chờ BE xong. Nếu cần đổi shape thì phải mở Gate — đừng sửa mock lệch contract rồi báo sau.' }
      ],
      outcome: 'TSK-03 bắt đầu với mock; contract là nguồn duy nhất.',
      refs: ['UOW-01/contract.md v2']
    };
    t['DEC-0017'] = {
      subject: 'Gate C đóng — Backlog Integration đi mock-first',
      scope: 'INT-001 · quyết định của bạn, orchestrator ghi lại',
      turns: [
        { id: 'MSG-0052', time: '13:05', from: 'unit-planner', to: 'orchestrator', type: 'question',
          body: 'UOW-04 phụ thuộc dữ liệu LakeHouse mà bên đó chưa mở API (RISK-01). Chờ hay làm mock-first?' },
        { id: 'DEC-0017', time: '13:12', from: 'orchestrator', to: 'INT-001', type: 'decision',
          body: 'Bạn chọn mock-first: UOW-04 dựng UI với dữ liệu mock theo shape thoả thuận, nối API thật khi LakeHouse mở. Đánh dấu nợ kỹ thuật DEBT-04 và không tính UOW-04 vào DoD của Bolt này.' }
      ],
      outcome: 'UOW-04 làm mock-first, ghi DEBT-04, ngoài DoD của Bolt 1.',
      refs: ['UOW-01/spec.md']
    };
    t['MSG-0049'] = {
      subject: 'AC của UOW-02: Gantt có cần zoom theo tuần?',
      scope: 'UOW-02 Milestone Timeline · câu hỏi mở Q54',
      turns: [
        { id: 'MSG-0049', time: '12:50', from: 'qa-reviewer', to: 'unit-planner', type: 'question',
          body: 'Spec UOW-02 nói timeline hiển thị theo tháng. QA cần biết có mức zoom tuần không, vì test case cho drag milestone phụ thuộc độ chi tiết của trục thời gian.' }
      ],
      outcome: 'Chưa có câu trả lời — đang nằm trong open-questions.md#Q54.',
      refs: ['open-questions.md#Q54']
    };
    return t;
  })(),
  // Nội dung markdown của artefact — preview ngay trong Control Tower
  docs: {
    'UOW-01/spec.md': {
      rev: 'v3', updated: '14:20 hôm nay', by: 'story-writer',
      md: `# UOW-01 · Release Planning\n\n## Bối cảnh\nMàn SCR-REL-10 hiện dùng mock layer. Unit này nối API thật và bổ sung ràng buộc tên release.\n\n## User story\n- Là **PM**, tôi tạo release trong một project để nhóm gắn milestone vào đó.\n- Là **PM**, tôi thấy lỗi rõ ràng khi trùng tên thay vì tạo bản ghi thứ hai.\n\n## Acceptance criteria\n- **AC-01** Tạo release cần \`name\`, \`start_date\`, \`end_date\`; \`end_date\` không nhỏ hơn \`start_date\`.\n- **AC-02** Bốn trạng thái: \`draft\` · \`active\` · \`frozen\` · \`released\`; chuyển trạng thái một chiều.\n- **AC-03** Trùng \`name\` trong cùng project trả \`409\` với body \`{code: "release_name_taken"}\`.\n- **AC-04** Sửa release đang \`released\` bị chặn ở tầng service, không chỉ ở UI.\n\n## NFR\n- p95 của \`GET /releases\` dưới 400ms với 500 bản ghi.\n- Mọi thay đổi trạng thái ghi audit log kèm actor.\n\n## Ngoài phạm vi\n- Quality Gate (theo DEC-0015, Gate A).\n- Backlog Integration View — thuộc UOW-04.`
    },
    'UOW-01/design.md': {
      rev: 'v2', updated: '13:05 hôm nay', by: 'domain-modeler',
      md: `# UOW-01 · Logical design\n\n## Entity\n| field | type | note |\n| --- | --- | --- |\n| id | uuid | pk |\n| project_id | uuid | fk, unique cùng name |\n| name | varchar(120) | unique (project_id, name) |\n| status | enum | draft/active/frozen/released |\n| start_date | date | AC-01 |\n| end_date | date | AC-01 |\n\n## Ràng buộc\n- Unique index \`uq_release_project_name\` sinh ra lỗi **AC-03**; service bắt \`IntegrityError\` và map sang \`409\`.\n- Chuyển trạng thái đi qua \`ReleaseService.transition()\`, không set trực tiếp.\n\n## Migration\n- \`alembic revision 0021_release_unique_name\`; rollback dùng \`downgrade()\` sẵn có.\n- Cần backfill: 3 bản ghi trùng tên trên staging phải đổi tên trước khi tạo index.\n\n## ADR liên quan\n- DEC-0015 — Phase 2 không gồm Quality Gate.`
    },
    'UOW-01/contract.md': {
      rev: 'v2 FROZEN', updated: '11:40 hôm nay', by: 'api-designer',
      md: `# UOW-01 · API contract (FROZEN)\n\n## POST /api/releases\nBody: \`{project_id, name, start_date, end_date}\`\n- \`201\` → \`{id, name, status: "draft"}\`\n- \`409\` → \`{code: "release_name_taken", field: "name"}\`\n- \`422\` → lỗi validate từng field\n\n## GET /api/releases?project_id=\n- \`200\` → \`{items: [...], total}\`, mặc định sort \`start_date desc\`\n- Filter \`status\` nhận nhiều giá trị, phân cách bằng dấu phẩy.\n\n## PATCH /api/releases/{id}\n- Chặn khi \`status = released\` → \`409\` \`{code: "release_locked"}\`\n\n## Ghi chú cho FE\n- Nhãn 4 trạng thái dùng i18n key \`release.status.*\` (theo MSG-0060).\n- Contract này đã đóng băng: đổi shape phải mở Gate và cập nhật \`open-questions.md\`.`
    },
    'app-be/releases/service.py': {
      rev: 'branch feat/uow-01', updated: '15:02 hôm nay', by: 'be-dev',
      md: `# service.py — trích đoạn\n\n## Đang sửa\n- \`create_release()\` bắt \`IntegrityError\` → raise \`ReleaseNameTaken\` (AC-03).\n- \`transition()\` chặn mọi thay đổi khi \`status = released\` (AC-04).\n\n## Test đi kèm\n- \`test_create_duplicate_name_returns_409\`\n- \`test_patch_released_is_blocked\`\n- Còn thiếu: test cho backfill migration.`
    }
  },
  trace: [
    { kind: 'code', id: 'app-be/releases/service.py', note: 'validate unique name → 409' },
    { kind: 'design', id: 'UOW-01/design.md', note: 'entity Release · status enum 4 giá trị' },
    { kind: 'spec', id: 'UOW-01/spec.md', note: 'AC-03' },
    { kind: 'dec', id: 'DEC-0015', note: 'Gate A — scope Phase 2 không gồm QG' },
    { kind: 'rv', id: 'RV-010', note: 'pm-po · approve-with-notes' },
    { kind: 'msg', id: 'MSG-0058', note: 'fe-dev hỏi status enum' },
    { kind: 'intent', id: 'INT-001', note: 'Triển khai Phase 2 PCT' }
  ],
  reviews: [
    { id: 'RV-010', reviewer: 'pm-po-reviewer', target: 'INT-001 · unit breakdown', verdict: 'approve-with-notes', checklist: 'plan-review v2', findings: 'SHOULD: ghi rõ thứ tự Bolt trong spec' },
    { id: 'RV-011', reviewer: 'security-reviewer', target: 'UOW-01 · design', verdict: 'approve', checklist: 'review-threat-model v4', findings: '—' },
    { id: 'RV-012', reviewer: 'tech-lead-reviewer', target: 'UOW-03 · approach', verdict: 'request-changes', checklist: 'review-approach v2', findings: 'MUST: batch >500 timeout — chuyển queue' },
    { id: 'RV-013', reviewer: 'qa-reviewer', target: 'UOW-01 · test strategy', verdict: 'approve', checklist: 'review-ac-coverage v3', findings: '—' }
  ],
  decisions: [
    { id: 'DEC-0015', when: '11/08 09:20', gate: 'A', by: 'Human supervisor', what: 'Scope Phase 2 = Release + Milestone + Backlog, không gồm Quality Gate', basis: 'RV-008' },
    { id: 'DEC-0016', when: '11/08 11:05', gate: 'B', by: 'Validation Mob', what: 'AS-IS đúng; tracker mới nhất do PMO giữ', basis: 'MSG-0031' },
    { id: 'DEC-0017', when: '11/08 13:12', gate: 'C', by: 'CTO', what: 'Backlog đi mock-first, không chờ LakeHouse', basis: 'open-questions.md#Q56' }
  ],
  questions: [
    { q: 'Backlog: làm UI trước với mock hay chờ LakeHouse nối xong?', who: 'CTO', due: '11/08', impact: 'UOW-04 không vào được Bolt', status: 'đã chốt' },
    { q: 'Release "Cancelled" có cho sửa milestone gắn kèm không?', who: 'PMO', due: '13/08', impact: 'AC của UOW-03', status: 'đang chờ' },
    { q: 'Gantt milestone: cần zoom tuần/tháng ngay đợt này?', who: 'APM đại diện', due: '13/08', impact: 'scope UOW-02', status: 'đang chờ' }
  ],
  risks: [
    { id: 'RISK-01', sev: 'high', text: 'LakeHouse chưa nối — dữ liệu backlog chưa có thật', owner: 'CTO' },
    { id: 'RISK-02', sev: 'med', text: 'FEEDBACK_TRACKER.md trên repo là bản cũ, bản mới PMO giữ', owner: 'PMO' },
    { id: 'RISK-04', sev: 'high', text: 'Migration case cũ chưa có câu trả lời từ client', owner: 'BA' }
  ],
  debt: [
    { id: 'DEBT-02', sev: 'med', text: 'app-be chưa có rollback script cho migration release', owner: 'tech-lead-reviewer' },
    { id: 'DEBT-03', sev: 'low', text: 'FE mock layer của SCR-REL-10 cần gỡ sau khi nối API thật', owner: 'fe-dev' }
  ],
  lessons: [
    { id: 'LL-001', trigger: 'Phase mapping đổi theo quyết định CTO ngoài repo', lesson: 'Luôn hỏi bản tracker/plan mới nhất nằm ở đâu — repo hay PMO giữ', patch: 'review-intent v1→v2', status: 'applied' },
    { id: 'LL-002', trigger: 'Legacy API có batch limit không tài liệu hóa', lesson: 'Hỏi batch limit/timeout của mọi external call ngay ở Domain Design', patch: 'review-approach v2→v3', status: 'proposed' }
  ],
  governance: {
    dor: { version: 'v3', items: ['AC đo được, có ví dụ số liệu', 'Open questions liên quan đã đóng hoặc có working-assumption gắn nhãn', 'Đã xác định approver cho từng task', 'Phụ thuộc Unit khác được ghi rõ'] },
    dod: { version: 'v1', items: ['Tests pass, coverage AC 100%', 'Security MUST findings = 0', 'Acceptance evidence đầy đủ (AC ✓, test output, screenshots, limitations)', 'Trace chain code → design → spec → DEC → RV → MSG → intent đủ'] },
    changelog: [
      { v: 'DoR v3', when: '02/08', by: 'Human supervisor', dec: 'DEC-0011', from: 'LL-001' },
      { v: 'DoD v1', when: '11/08', by: 'Human supervisor', dec: 'DEC-0018', from: '—' }
    ]
  }
};
