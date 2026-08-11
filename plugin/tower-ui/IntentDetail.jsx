(function(){
const NSi = window.ControlTowerDesignSystem_68131c;
const { Panel, StageStrip, DataTable, Chip, IdCode, VerdictBadge, AgentAvatar } = NSi;

function Tabs({ tabs, active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 2, borderBottom: '1px solid var(--line)' }}>
      {tabs.map(t => (
        <button key={t} onClick={() => onChange(t)} style={{
          fontFamily: 'var(--mono)', fontSize: 11.5, letterSpacing: '0.08em', textTransform: 'uppercase',
          padding: '8px 14px', cursor: 'pointer', background: 'transparent',
          border: 'none', borderBottom: '2px solid ' + (active === t ? 'var(--accent)' : 'transparent'),
          color: active === t ? 'var(--ink)' : 'var(--muted)'
        }}>{t}</button>
      ))}
    </div>
  );
}

function UnitCard({ u, onOpenBolt }) {
  const tone = u.status === 'in-bolt' ? 'active' : u.status === 'blocked' ? 'blocked' : 'pending';
  return (
    <div onClick={() => u.bolt === 'Bolt 1' && onOpenBolt()} style={{
      border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)',
      padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8,
      cursor: u.bolt === 'Bolt 1' ? 'pointer' : 'default'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <IdCode style={{ fontSize: 12 }}>{u.id}</IdCode>
        <Chip tone={tone}>{u.status}</Chip>
        <span style={{ marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>{u.bolt}</span>
      </div>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{u.name}</div>
      <div style={{ height: 4, background: 'var(--surface-2)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: u.done + '%', height: '100%', background: u.done ? 'var(--ok)' : 'transparent' }} />
      </div>
      <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{u.done}% task done</span>
        {u.risks.map(r => <Chip key={r} tone="blocked">{r}</Chip>)}
      </div>
    </div>
  );
}

function IntentDetail({ data, intentId, onOpenBolt, onOpenList, onSelectIntent }) {
  const intent = data.intents.find(x => x.id === intentId) || data.intents[0];
  const units = intent.id === 'INT-001' ? data.units : (data.unitsByIntent[intent.id] || []);
  const [tab, setTab] = React.useState('Units');
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <span onClick={onOpenList} style={{ cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)' }}>← tất cả intents</span>
        <span style={{ width: 1, height: 14, background: 'var(--line)' }} />
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {data.intents.map(x => (
            <span key={x.id} onClick={() => onSelectIntent && onSelectIntent(x.id)} style={{ cursor: 'pointer' }}>
              <Chip tone={x.id === intent.id ? 'agent' : x.gate ? 'active' : 'pending'}>{x.id}</Chip>
            </span>
          ))}
        </div>
      </div>
      <Panel>
        <div style={{ display: 'flex', gap: 12, alignItems: 'baseline', flexWrap: 'wrap' }}>
          <IdCode style={{ fontSize: 13, color: 'var(--accent)' }}>{intent.id}</IdCode>
          <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.01em' }}>{intent.name}</span>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
            <Chip tone="neutral">brownfield · {intent.brownfield}</Chip>
            <IdCode variant="artifact">{intent.doc}</IdCode>
          </span>
        </div>
        <div style={{ marginTop: 14 }}><StageStrip current={intent.stage} gate={intent.gate} labels /></div>
      </Panel>
      <Panel pad={false}>
        <div style={{ padding: '0 8px' }}><Tabs tabs={['Units', 'Open Questions', 'Decisions', 'Changelog']} active={tab} onChange={setTab} /></div>
        <div style={{ padding: 16 }}>
          {tab === 'Units' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 12 }}>
              {units.length ? units.map(u => <UnitCard key={u.id} u={u} onOpenBolt={onOpenBolt} />) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>Chưa tới stage 5 — chưa có Unit nào được chia.</div>}
            </div>
          )}
          {tab === 'Open Questions' && (
            <DataTable columns={['Câu hỏi', 'Ai trả lời', 'Deadline', 'Ảnh hưởng nếu chưa trả lời', 'Trạng thái']}
              monoFirst={false}
              rows={data.questions.map(q => [q.q, q.who, q.due, q.impact, <Chip tone={q.status === 'đã chốt' ? 'done' : 'active'}>{q.status}</Chip>])} />
          )}
          {tab === 'Decisions' && (
            <DataTable columns={['DEC', 'Thời điểm', 'Gate', 'Ai quyết', 'Nội dung', 'Căn cứ']}
              rows={data.decisions.map(d => [d.id, d.when, <Chip tone="done">{d.gate}</Chip>, d.by, d.what, <IdCode variant="inline">{d.basis}</IdCode>])} />
          )}
          {tab === 'Changelog' && (
            <DataTable columns={['Khi nào', 'Thay đổi', 'Nguồn']}
              monoFirst={false}
              rows={[
                ['11/08 13:12', 'Gate C đóng — Backlog đi mock-first', <IdCode variant="inline">DEC-0017</IdCode>],
                ['11/08 11:05', 'AS-IS được Validation Mob xác nhận', <IdCode variant="inline">DEC-0016</IdCode>],
                ['11/08 09:20', 'Scope Phase 2 chốt (không gồm Quality Gate)', <IdCode variant="inline">DEC-0015</IdCode>]
              ]} />
          )}
        </div>
      </Panel>
    </div>
  );
}
window.IntentDetail = IntentDetail;
})();
