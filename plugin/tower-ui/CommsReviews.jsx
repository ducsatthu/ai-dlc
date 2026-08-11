(function(){
const NSc = window.ControlTowerDesignSystem_68131c;
const { Panel, DataTable, Chip, IdCode, VerdictBadge, FeedItem, AgentAvatar, TraceChain } = NSc;

const THREAD = [
  { id: 'MSG-0058', from: 'fe-dev', to: 'be-dev', type: 'clarification', body: 'status enum trả code hay label? i18n phía nào?' },
  { id: 'MSG-0059', from: 'be-dev', to: 'fe-dev', type: 'question', body: 'FE có bảng i18n sẵn cho status không, hay cần BE trả label theo locale?' },
  { id: 'MSG-0060', from: 'fe-dev', to: 'be-dev', type: 'answer', body: 'FE có next-intl sẵn — chốt: BE trả code, FE map i18n.' },
  { id: 'MSG-0061', from: 'be-dev', to: 'fe-dev', type: 'handoff', body: 'contract.md v2 cập nhật, FREEZE. TSK-03 chạy được với mock đúng shape.' }
];

function CommsReviews({ data, onOpenFeed }) {
  const [tab, setTab] = React.useState('Comms');
  const [type, setType] = React.useState('all');
  const rows = data.feed.filter(m => type === 'all' || m.type === type);
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', gap: 2 }}>
        {['Comms', 'Reviews'].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            fontFamily: 'var(--mono)', fontSize: 11.5, letterSpacing: '0.08em', textTransform: 'uppercase',
            padding: '8px 14px', cursor: 'pointer', background: 'transparent', border: 'none',
            borderBottom: '2px solid ' + (tab === t ? 'var(--accent)' : 'var(--line)'),
            color: tab === t ? 'var(--ink)' : 'var(--muted)', flex: 'none'
          }}>{t}</button>
        ))}
        <div style={{ flex: 1, borderBottom: '2px solid var(--line)' }} />
      </div>
      {tab === 'Comms' ? (
        <React.Fragment>
        <Panel title="Truy vết — MSG-0058 nằm ở đâu trong chuỗi quyết định" meta="click một mắt xích để mở">
          <TraceChain activeId="MSG-0058" onSelect={() => {}} steps={[
            { kind: 'intent', id: 'INT-001', note: 'Phase 2 PCT' },
            { kind: 'dec', id: 'DEC-0015', note: 'Gate A · scope' },
            { kind: 'spec', id: 'UOW-01/spec.md', note: 'AC-03 unique name' },
            { kind: 'task', id: 'TSK-01', note: 'contract draft + freeze' },
            { kind: 'msg', id: 'MSG-0058', note: 'fe-dev hỏi status enum' },
            { kind: 'design', id: 'contract.md v2', note: 'FROZEN' },
            { kind: 'rv', id: 'RV-010', note: 'pm-po · notes' },
            { kind: 'code', id: 'releases/service.py', note: '409 unique name' }
          ]} />
        </Panel>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.2fr) minmax(320px,1fr)', gap: 16, alignItems: 'start', marginTop: 16 }}>
          <Panel title="Messages" meta={rows.length + ' MSG'} pad={false}>
            <div style={{ display: 'flex', gap: 6, padding: '8px 12px', borderBottom: '1px solid var(--line)', flexWrap: 'wrap' }}>
              {['all', 'clarification', 'answer', 'handoff', 'finding', 'review-request', 'decision'].map(t => (
                <span key={t} onClick={() => setType(t)} style={{ cursor: 'pointer' }}><Chip tone={type === t ? 'agent' : 'pending'}>{t}</Chip></span>
              ))}
            </div>
            {rows.map(m => <FeedItem key={m.id} {...m} onClick={() => onOpenFeed(m)} />)}
          </Panel>
          <Panel title="Thread · re: contract /api/releases" meta="4 MSG">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {THREAD.map(m => (
                <div key={m.id} style={{ borderLeft: '2px solid var(--line)', paddingLeft: 12 }}>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                    <AgentAvatar name={m.from} size={18} />
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--blue)' }}>{m.from} → {m.to}</span>
                    <IdCode style={{ fontSize: 10.5 }}>{m.id}</IdCode>
                    <Chip tone="agent">{m.type}</Chip>
                  </div>
                  <div style={{ fontSize: 13.5, marginTop: 4 }}>{m.body}</div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
        </React.Fragment>
      ) : (
        <Panel title="Review verdicts" meta={data.reviews.length + ' RV'}>
          <DataTable columns={['RV', 'Reviewer', 'Target', 'Verdict', 'Checklist version', 'Findings']}
            rows={data.reviews.map(r => [
              r.id, r.reviewer, r.target,
              <VerdictBadge verdict={r.verdict} />,
              <IdCode variant="inline">{r.checklist}</IdCode>,
              r.findings
            ])} />
        </Panel>
      )}
    </div>
  );
}
window.CommsReviews = CommsReviews;
})();
