(function(){
const NSb = window.ControlTowerDesignSystem_68131c;
const { Panel, TaskRow, Chip, IdCode, Button, MermaidDiagram, AgentAvatar, AgentWorkCard } = NSb;

function unitsOfB(data, id) { return data.unitsByIntent[id] || (id === 'INT-001' ? data.units : []); }

function BoltBoard({ data, onOpenTask, intentId = 'INT-001', unitId = 'UOW-01' }) {
  const [view, setView] = React.useState('hoạt động');
  const units = unitsOfB(data, intentId);
  const unit = units.find(u => u.id === unitId) || units[0];
  const hasWork = intentId === 'INT-001' && unit && unit.id === 'UOW-01';
  const intent = data.intents.find(i => i.id === intentId) || {};

  if (!hasWork) {
    return (
      <div style={{ padding: 24 }}>
        <Panel title={(unit ? unit.id + ' · ' + unit.bolt : intentId) + ' — ' + (unit ? unit.name : intent.name || '')}
          meta={unit ? unit.status : 'chưa có unit'}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: '18px 4px', color: 'var(--muted)' }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--accent)' }}>◇ chưa có task cho unit này</div>
            <div style={{ fontSize: 13.5, maxWidth: 560, textWrap: 'pretty' }}>
              {unit
                ? 'Bản mô phỏng này mới dựng task board cho INT-001 · UOW-01. Unit đang chọn (' + unit.id + ' · ' + unit.name + ') thuộc ' + intentId + ', tiến độ ' + unit.done + '%.'
                : intentId + ' chưa được phân rã thành Unit — còn ở pha Inception.'}
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <Chip tone="pending">{intentId}</Chip>
              {unit && <Chip tone="pending">{unit.bolt}</Chip>}
            </div>
          </div>
        </Panel>
      </div>
    );
  }

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Panel title={unit.id + ' · ' + unit.bolt + ' — ' + unit.name} meta="1/5 done" pad={false}>
          <div style={{ display: 'flex', gap: 6, padding: '8px 14px', borderBottom: '1px solid var(--line)' }}>
            {['hoạt động', 'flow', 'lifecycle', 'list'].map(v => (
              <span key={v} onClick={() => setView(v)} style={{ cursor: 'pointer' }}><Chip tone={view === v ? 'agent' : 'pending'}>{v}</Chip></span>
            ))}
          </div>
          {view === 'hoạt động' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(340px,1fr))', gap: 12, padding: 14 }}>
              {data.work.map(w => {
                const { assumption, context, ...cw } = w;
                return (
                <AgentWorkCard key={w.taskId} {...cw}
                  lane={w.agent.includes('reviewer') ? 'review' : 'pipeline'}
                  onOpenTask={() => onOpenTask(data.tasks.find(t => t.id === w.taskId) || { id: w.taskId, title: w.title, status: w.status, approver: '—' })} />
                );
              })}
            </div>
          )}
          {view === 'list' && data.tasks.map(t => <TaskRow key={t.id} {...t} onClick={() => onOpenTask(t)} />)}
          {view === 'flow' && (
            <div style={{ padding: '0 14px 8px' }}>
              <MermaidDiagram chart={window.CT_DIAGRAMS.boltFlow} style={{ marginTop: 14 }}
                caption="Ai bàn giao cho ai trong Bolt 1. Ô xanh dương là điểm một reviewer phải ký; TSK-04 không chờ BE code xong mà chờ backend-reviewer duyệt." />
            </div>
          )}
          {view === 'lifecycle' && (
            <div style={{ padding: '0 14px 8px' }}>
              <MermaidDiagram chart={window.CT_DIAGRAMS.taskLifecycle} style={{ marginTop: 14 }}
                caption="Vòng đời của một task: claim → code → review → verdict. Hai lần request-changes cùng một điểm thì việc chuyển thành escalation của người." />
            </div>
          )}
        </Panel>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 16, alignItems: 'start' }}>
          <Panel title="API contract">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <Chip tone="done">FROZEN v2</Chip>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>be-dev ✓ · fe-dev ✓ · tech-lead ✓</span>
            </div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink)', lineHeight: 1.9 }}>
              GET/POST/PATCH /api/releases
            </div>
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 8 }}>
              {['MSG-0058', 'MSG-0059', 'MSG-0060', 'MSG-0061'].map(m => <IdCode key={m} variant="artifact">{m}</IdCode>)}
            </div>
          </Panel>
          <Panel title="Checkpoint · Gate E">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Chip tone="done">✓</Chip><span style={{ fontSize: 13 }}>Design + contract OK</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Chip tone="pending">◇</Chip><span style={{ fontSize: 13, color: 'var(--muted)' }}>Demo SCR-REL-10/11 sau review</span>
                <Button variant="secondary" size="sm" style={{ marginLeft: 'auto' }}>Mở demo</Button>
              </div>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
window.BoltBoard = BoltBoard;
})();
