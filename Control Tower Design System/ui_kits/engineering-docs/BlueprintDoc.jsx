(function(){
const NSd = window.ControlTowerDesignSystem_68131c;
const { Eyebrow, StatusChip, Tag, DataTable, Callout, Panel, Timeline, TimelineItem, GateStop, IdCode, Chip, PipelineRow, FeedItem, GateCard, VerdictBadge } = NSd;

const ROSTER_PIPELINE = [
  ['orchestrator', 'xuyên suốt', 'Điều phối flow, giữ state, enforce gate — không cho stage sau chạy khi gate trước chưa có quyết định.', 'status.md · decisions-log.md'],
  ['intent-analyst', '1 · Request', 'Capture problem · outcome · priority; nhận diện brownfield type và vùng ảnh hưởng.', 'intent.md'],
  ['context-archaeologist', '2 · Discovery', 'Đọc code · docs · tickets · tests · DB → AS-IS model.', 'as-is/'],
  ['context-validator', '3–4 · Validation + Clarify', 'Trình bày AS-IS cho Validation Mob; generate open questions.', 'open-questions.md'],
  ['unit-planner', '5 · Unit Definition', 'Chia Intent thành Units theo business capability; reject pseudo-unit.', 'units/UOW-xx/spec.md'],
  ['bolt-coordinator', '6 · Construction', 'Điều phối một Bolt cho một Unit: chia task board, enforce luật claim.', 'tasks.md + design.md'],
  ['be-dev', '6 · Construction', 'API contract draft, service, DB migration, tests.', 'code BE + contract.md'],
  ['fe-dev', '6 · Construction', 'Review contract trước khi code, component, state, tests.', 'code FE'],
  ['acceptance-recorder', '7–8 · Acceptance + Release', 'Gom Acceptance Evidence; trace decision → requirement → design → code.', 'evidence/ · changelog.md']
];

const ROSTER_REVIEW = [
  ['ba-reviewer', 'Business Analyst', 'Góc nhìn business stage 1–4; soạn decision brief cho gate A–D.', 'review-intent · business-validation · decision-brief'],
  ['pm-po-reviewer', 'PM / PO', 'Plan & task breakdown, risk register mỗi bolt, DoD/DoR compliance ở gate D.', 'plan-review · risk-register · quality-gate'],
  ['tech-lead-reviewer', 'Technical Leader', 'Technical approach & design trước khi viết code; giữ tech-debt-register.', 'review-approach · review-infra · review-techstack'],
  ['security-reviewer', 'Security / DevSecOps', 'Threat model, code security, dependency, CI/CD. Có quyền block release.', 'review-threat-model · review-code-security · review-pipeline'],
  ['backend-reviewer', 'Dev góc nhìn BE', 'Code BE trong bolt: API contract, DB migration, performance.', 'review-api · review-db · review-perf'],
  ['frontend-reviewer', 'Dev góc nhìn FE', 'Code FE: kiến trúc component, state, accessibility, nhất quán UX.', 'review-component · review-state · review-a11y'],
  ['qa-reviewer', 'QA / QC', 'DoR check trước Bolt, test strategy trong bolt, verify Acceptance Evidence stage 7.', 'review-test-strategy · review-ac-coverage · qc-evidence']
];

function BlueprintDoc() {
  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '48px 24px 96px' }}>
      <header style={{ borderBottom: '2px solid var(--ink)', paddingBottom: 24, marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 12, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--muted)' }}>AI-DLC · Engineering process · TechTus</div>
          <StatusChip tone="gate">BẢN THIẾT KẾ v3 — CHỜ DUYỆT</StatusChip>
        </div>
        <h1 style={{ fontSize: 'clamp(28px,4.5vw,44px)', fontWeight: 750, letterSpacing: '-0.02em', lineHeight: 1.12, margin: '10px 0 12px' }}>Agent Team &amp; Control Tower</h1>
        <p style={{ maxWidth: '68ch', color: 'var(--muted)', fontSize: 17, margin: 0 }}>
          Bản thiết kế đầy đủ trước khi triển khai: 9 pipeline agents chạy flow 8 stage, 7 review agents độc lập theo vai trò, task board trong từng Unit với dependency — claim — approver, vòng retro — lesson learned, và Control Tower theo dõi toàn bộ. Mọi quyết định và thay đổi của AI đều thành tài liệu truy vết được.
        </p>
      </header>

      <section style={{ marginTop: 64 }}>
        <Eyebrow>01 · Đội hình</Eyebrow>
        <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.01em', marginBottom: 12 }}>Bốn nhóm, một nguyên tắc: AI thực thi — người quyết định</h2>
        <p style={{ maxWidth: '68ch', marginBottom: 12 }}>Đội hình chia bốn nhóm. <strong>Pipeline agents</strong> đẩy công việc qua 8 stage của AI-DLC. <strong>Review Board</strong> — các agent độc lập theo vai trò, không tham gia thực thi, chỉ review đúng đoạn thuộc chuyên môn và ra verdict. <strong>Learning</strong> — retro-keeper biến lesson learned thành nâng cấp skill cho agent.</p>
        <h3 style={{ fontSize: 18, fontWeight: 650, margin: '28px 0 8px', display: 'flex', gap: 10, alignItems: 'baseline' }}><Tag kind="pipeline">PIPELINE</Tag> — 9 agents thực thi theo stage</h3>
        <DataTable columns={['Agent', 'Stage', 'Trách nhiệm', 'Output']} rows={ROSTER_PIPELINE} />
        <h3 style={{ fontSize: 18, fontWeight: 650, margin: '28px 0 8px', display: 'flex', gap: 10, alignItems: 'baseline' }}><Tag kind="review">REVIEW BOARD</Tag> — 7 agents review độc lập</h3>
        <DataTable columns={['Agent', 'Vai trò', 'Review cái gì · khi nào', 'Bộ skill chuyên biệt']} rows={ROSTER_REVIEW} />
        <h3 style={{ fontSize: 18, fontWeight: 650, margin: '28px 0 8px', display: 'flex', gap: 10, alignItems: 'baseline' }}><Tag kind="learning">LEARNING</Tag> — 1 agent giữ vòng học</h3>
        <DataTable columns={['Agent', 'Khi nào chạy', 'Trách nhiệm', 'Output']} rows={[[
          'retro-keeper', 'Sau mỗi Release (stage 8)',
          'Phân tích comms + verdicts + escalations → rút lesson learned → đề xuất patch vào checklist. Patch chỉ apply sau Gate G.',
          'lessons-learned/LL-xx.md · skill patch + version'
        ]]} />
        <p style={{ maxWidth: '68ch', color: 'var(--muted)', fontSize: 14.5, marginTop: 16 }}>Mỗi bộ skill là một checklist file có version trong <IdCode variant="inline">.claude/skills/</IdCode> — tiêu chí đánh giá được chuẩn hóa và tiến hóa có kiểm soát qua retro.</p>
      </section>

      <section style={{ marginTop: 64 }}>
        <Eyebrow>02 · Hành trình</Eyebrow>
        <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.01em', marginBottom: 12 }}>Từ câu lệnh của anh/chị tới danh sách Unit được duyệt</h2>
        <Callout tone="agent"><strong>Phát hiện quan trọng ngay ở bước đọc</strong>: tài liệu cũ nói Phase 2 gồm Quality Gate, nhưng mapping CTO 2026-08-11 đã kéo nhóm QG lên Phase 1.2. "Phase 2 thật" = Release Planning + Milestone + Backlog Integration.</Callout>
        <Timeline>
          <TimelineItem actor="intent-analyst + ba-reviewer" heading="Stage 1 · Request → Intent">
            Capture problem, outcome, brownfield type và vùng ảnh hưởng. ba-reviewer soạn decision brief cho Gate A.
            <div style={{ marginTop: 6 }}><IdCode variant="artifact">INT-001/intent.md</IdCode><IdCode variant="artifact">decision-brief-A.md</IdCode></div>
            <GateStop label="◇ GATE A — DỪNG, CHỜ ANH/CHỊ (lần confirm #1)">
              Scope Phase 2 = Release + Milestone + Backlog, không gồm Quality Gate — đúng không? Outcome đo bằng gì? Backlog Integration thuộc đợt này hay defer?
            </GateStop>
          </TimelineItem>
          <TimelineItem actor="context-archaeologist" heading="Stage 2 · Context Discovery (AS-IS)">
            Đọc code + docs → dựng AS-IS model: schema hiện tại, pattern router→service→model của app-be, pattern component + i18n của app-fe. Không hỏi ai ở stage này — chỉ đọc.
          </TimelineItem>
          <TimelineItem actor="Validation Mob" lane="human" heading="Stage 3 · Context Validation">
            AI trình bày understanding; ba-reviewer đối chiếu từng khẳng định với wiki + Q&amp;A, gắn nhãn phần nào là suy luận chưa có căn cứ.
            <GateStop label="◇ GATE B — DỪNG, CHỜ ANH/CHỊ (lần confirm #2)">QG P1.2 đã ship tới đâu? Bản tracker trên repo là bản cũ — AS-IS có thiếu batch nào không?</GateStop>
          </TimelineItem>
          <TimelineItem actor="unit-planner → pm-po-reviewer" heading="Stage 5 · Unit Definition" last>
            Chia Intent thành 4 Units theo business capability; pm-po lập risk register; qa check DoR.
            <GateStop label="◇ GATE D — DỪNG, CHỜ ANH/CHỊ (lần confirm #4 — quan trọng nhất)">
              Approve scope + DoD → các Unit unlocked, ghi <IdCode variant="inline">DEC</IdCode>. Từ đây mới được viết dòng code đầu tiên.
            </GateStop>
          </TimelineItem>
        </Timeline>
      </section>

      <section style={{ marginTop: 64 }}>
        <Eyebrow>03 · Control Tower</Eyebrow>
        <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.01em', marginBottom: 12 }}>Một màn hình trả lời: đang ở đâu, ai đang làm gì, cái gì chờ tôi</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.1fr) minmax(280px,1fr)', gap: 16, marginTop: 20 }}>
          <Panel title="Gate queue">
            <GateCard gate="D" target="INT-001" title="Duyệt scope 4 Units + DoD v1" brief="pm-po-reviewer verdict: approve-with-notes (RV-010)." />
            <GateCard kind="escalation" target="UOW-03" title="tech-lead vs be-dev: queue vs sync call" brief="2× request-changes (RV-012)." />
          </Panel>
          <Panel title="Pipeline board" pad={false}>
            <PipelineRow id="INT-001" name="Phase 2 PCT" current={5} gate="D" holder="unit-planner" />
            <PipelineRow id="INT-002" name="Slack reminder FB-012" current={2} holder="context-archaeologist" />
            <div style={{ display: 'flex', gap: 6, padding: '10px 16px', flexWrap: 'wrap' }}>
              <VerdictBadge id="RV-011" reviewer="security" verdict="approve" />
              <VerdictBadge id="RV-012" reviewer="tech-lead" verdict="request-changes" />
            </div>
          </Panel>
        </div>
        <p style={{ maxWidth: '68ch', color: 'var(--muted)', fontSize: 14.5, marginTop: 14 }}>Ngoài 7 loại điểm dừng này, agents không hỏi vặt — mọi thứ khác tự chạy và tự ghi lại.</p>
      </section>

      <div style={{ marginTop: 56, border: '2px solid var(--accent)', borderRadius: 12, background: 'var(--accent-bg)', padding: '24px 28px' }}>
        <h2 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8 }}>Chờ anh/chị duyệt</h2>
        <p style={{ marginBottom: 6, maxWidth: '68ch' }}>Nếu bản thiết kế này đúng ý, bước tiếp theo là scaffold bộ agent rồi chạy thật <IdCode variant="inline">/intent</IdCode> cho PCT Phase 2 — dừng ở Gate A chờ anh/chị.</p>
      </div>
    </div>
  );
}
const rootEl = document.getElementById('root');
if (rootEl) ReactDOM.createRoot(rootEl).render(<BlueprintDoc />);
})();
