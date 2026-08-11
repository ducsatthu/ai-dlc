(function(){
const NSl = window.ControlTowerDesignSystem_68131c;
const { Panel, PipelineRow, Chip, IdCode, KpiStrip, AgentAvatar, StageStrip, MermaidDiagram } = NSl;

const FILTERS = [
  { key: 'all', label: 'tất cả' },
  { key: 'gate', label: 'chờ tôi' },
  { key: 'running', label: 'đang chạy' },
  { key: 'done', label: 'đã release' }
];

const BROWNFIELD = ['Add feature', 'Optimize NFR', 'Technical debt', 'Fix defect'];

function IntentList({ data, onOpenIntent }) {
  const [showMap, setShowMap] = React.useState(false);
  const [filter, setFilter] = React.useState('all');
  const [type, setType] = React.useState('all');
  const [q, setQ] = React.useState('');

  const rows = data.intents.filter(i => {
    const byState = filter === 'all' ? true
      : filter === 'gate' ? !!i.gate
      : filter === 'running' ? i.stage < 8 && !i.gate
      : i.stage === 8;
    const byType = type === 'all' || i.brownfield === type;
    const byQ = !q.trim() || (i.id + ' ' + i.name + ' ' + i.owner).toLowerCase().includes(q.toLowerCase());
    return byState && byType && byQ;
  });

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <KpiStrip items={[
        { value: data.intents.length, label: 'Intents đang mở', tone: 'neutral' },
        { value: data.intents.filter(i => i.gate).length, label: 'Có gate chờ tôi', tone: 'gate' },
        { value: data.intents.filter(i => i.stage === 6).length, label: 'Đang Construction', tone: 'agent' },
        { value: data.intents.filter(i => i.stage === 8).length, label: 'Đã release', tone: 'done' }
      ]} />
      <Panel title="Cấu trúc công việc — dự án › intent › unit › bolt › task"
        meta={<span onClick={() => setShowMap(v => !v)} style={{ cursor: 'pointer', color: 'var(--accent)' }}>{showMap ? 'thu gọn' : 'xem sơ đồ'}</span>}>
        {showMap
          ? <MermaidDiagram chart={window.CT_DIAGRAMS.hierarchy} style={{ margin: 0 }}
              caption="Một dự án có nhiều Intent (phát triển tiếp hoặc phần mới). Mỗi Intent chia thành nhiều Unit of Work; mỗi Unit chạy đúng một Bolt — một vòng build–validate vài giờ tới vài ngày; trong Bolt là các Task, mỗi task có agent claim và approver được assign sẵn." />
          : <div style={{ fontSize: 13.5, color: 'var(--muted)', maxWidth: '76ch' }}>Dự án → <strong style={{ color: 'var(--ok)' }}>Intent</strong> → <strong style={{ color: 'var(--blue)' }}>Unit of Work</strong> → <strong style={{ color: 'var(--accent)' }}>Bolt</strong> → Task. Một Intent có nhiều Unit; mỗi Unit chạy đúng một Bolt.</div>}
      </Panel>
      <Panel title="Intents" meta={rows.length + '/' + data.intents.length} pad={false}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '10px 14px', borderBottom: '1px solid var(--line)', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: 6 }}>
            {FILTERS.map(f => (
              <span key={f.key} onClick={() => setFilter(f.key)} style={{ cursor: 'pointer' }}>
                <Chip tone={filter === f.key ? 'agent' : 'pending'}>{f.label}</Chip>
              </span>
            ))}
          </div>
          <span style={{ width: 1, height: 18, background: 'var(--line)' }} />
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <span onClick={() => setType('all')} style={{ cursor: 'pointer' }}><Chip tone={type === 'all' ? 'neutral' : 'pending'}>mọi loại</Chip></span>
            {BROWNFIELD.map(b => (
              <span key={b} onClick={() => setType(b)} style={{ cursor: 'pointer' }}>
                <Chip tone={type === b ? 'neutral' : 'pending'}>{b}</Chip>
              </span>
            ))}
          </div>
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="tìm intent, người yêu cầu…" style={{
            marginLeft: 'auto', minWidth: 200, fontFamily: 'var(--mono)', fontSize: 11.5,
            color: 'var(--ink)', background: 'var(--surface-2)', border: '1px solid var(--line)',
            borderRadius: 'var(--radius-sm)', padding: '6px 10px'
          }} />
        </div>
        <div style={{
          display: 'grid', gridTemplateColumns: '84px minmax(220px,1fr) 132px 96px 110px',
          gap: 12, padding: '8px 16px', borderBottom: '2px solid var(--ink)',
          fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--muted)'
        }}>
          <span>Intent</span><span>Tên · vị trí</span><span>Loại</span><span>Units</span><span>Cập nhật</span>
        </div>
        {rows.map(i => (
          <div key={i.id} onClick={() => onOpenIntent(i.id)} style={{
            display: 'grid', gridTemplateColumns: '84px minmax(220px,1fr) 132px 96px 110px',
            gap: 12, padding: '12px 16px', borderBottom: '1px solid var(--line)',
            alignItems: 'center', cursor: 'pointer', fontSize: 13
          }}>
            <IdCode style={{ fontSize: 12, color: i.gate ? 'var(--accent)' : 'var(--muted)' }}>{i.id}</IdCode>
            <div style={{ minWidth: 0 }}>
              <div style={{ marginBottom: 6 }}>{i.name}</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                <StageStrip current={i.stage} gate={i.gate} />
                <AgentAvatar name={i.holder} size={18} />
              </div>
            </div>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>{i.brownfield}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)' }}>
              {i.units[0] ? i.units[1] + '/' + i.units[0] : '—'}
              {i.risk && <Chip tone={i.risk === 'high' ? 'blocked' : 'active'} style={{ marginLeft: 6 }}>risk</Chip>}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
              <div>{i.updated}</div>
              <div>{i.owner}</div>
            </span>
          </div>
        ))}
        {rows.length === 0 && (
          <div style={{ padding: '28px 16px', textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>Không có intent nào khớp bộ lọc.</div>
        )}
      </Panel>
    </div>
  );
}
window.IntentList = IntentList;
})();
