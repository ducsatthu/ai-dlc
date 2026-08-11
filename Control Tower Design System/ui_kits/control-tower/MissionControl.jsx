(function(){
const NSm = window.ControlTowerDesignSystem_68131c;
const { KpiStrip, GateCard, Panel, PipelineRow, FeedItem, VerdictBadge, Chip, IdCode: Id } = NSm;

function MissionControl({ data, gates, onDecision, onOpenIntent, onOpenFeed }) {
  const filters = ['all', 'comms', 'review', 'decision'];
  const [filter, setFilter] = React.useState('all');
  const feed = data.feed.filter(x =>
    filter === 'all' ? true :
    filter === 'comms' ? ['clarification', 'question', 'answer', 'handoff', 'note'].includes(x.type) :
    filter === 'review' ? ['review-request', 'finding'].includes(x.type) : x.type === 'decision');

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16, minHeight: 0 }}>
      <KpiStrip items={[
        { value: gates.filter(g => g.kind === 'gate').length, label: 'Gates chờ tôi', tone: 'gate' },
        { value: gates.filter(g => g.kind === 'escalation').length, label: 'Escalations', tone: 'gate' },
        { value: 2, label: 'Bolts đang chạy', tone: 'agent' },
        { value: 3, label: 'Units done tuần này', tone: 'done' }
      ]} />
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.55fr) minmax(320px,1fr)', gap: 16, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Panel title="Gate queue — chờ quyết định của bạn" meta={gates.length + ' mục'}>
            {gates.length === 0 ? (
              <div style={{ padding: '28px 8px', textAlign: 'center', color: 'var(--muted)' }}>
                <style>{'@keyframes ct-breathe{0%,100%{opacity:.45}50%{opacity:1}}'}</style>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 22, color: 'var(--ok)', animation: 'ct-breathe 1600ms ease-in-out infinite' }}>●</div>
                <div style={{ marginTop: 8, fontSize: 14.5 }}>Không có gì chờ bạn — agents đang làm việc</div>
              </div>
            ) : gates.map(g => (
              <GateCard key={g.key} {...g} defaultExpanded={g.key === 'g1'}
                onApprove={() => onDecision(g.key, 'approve')}
                onReject={r => onDecision(g.key, 'reject', r)}
                onDiscuss={() => onDecision(g.key, 'discuss')} />
            ))}
          </Panel>
          <Panel title="Pipeline board" meta="2 intents" pad={false}>
            {data.intents.map(i => (
              <PipelineRow key={i.id} id={i.id} name={i.name} current={i.stage} gate={i.gate} holder={i.holder}
                onClick={() => onOpenIntent(i.id)} />
            ))}
            <div style={{ display: 'flex', gap: 6, padding: '10px 16px', flexWrap: 'wrap' }}>
              {data.reviews.slice(0, 3).map(r => <VerdictBadge key={r.id} id={r.id} reviewer={r.reviewer.replace('-reviewer', '')} verdict={r.verdict} />)}
            </div>
          </Panel>
        </div>
        <Panel title="Live feed" meta="activity + comms" pad={false}
          style={{ position: 'sticky', top: 0, maxHeight: 'calc(100vh - 190px)' }}>
          <div style={{ display: 'flex', gap: 6, padding: '8px 12px', borderBottom: '1px solid var(--line)', flexWrap: 'wrap' }}>
            {filters.map(x => (
              <span key={x} onClick={() => setFilter(x)} style={{ cursor: 'pointer' }}>
                <Chip tone={filter === x ? 'agent' : 'pending'}>{x}</Chip>
              </span>
            ))}
          </div>
          {feed.map((x, i) => <FeedItem key={x.id} {...x} isNew={i === 0} onClick={() => onOpenFeed(x)} />)}
        </Panel>
      </div>
    </div>
  );
}
window.MissionControl = MissionControl;
})();
