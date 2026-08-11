(function(){
const NSg = window.ControlTowerDesignSystem_68131c;
const { Panel, DataTable, Chip, IdCode, Button, Callout } = NSg;

function DefList({ title, version, items }) {
  return (
    <Panel title={title} meta={version}>
      <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13.5, lineHeight: 1.7 }}>
        {items.map((i, k) => <li key={k}>{i}</li>)}
      </ul>
    </Panel>
  );
}

function Governance({ data }) {
  const g = data.governance;
  const sev = s => <Chip tone={s === 'high' ? 'blocked' : s === 'med' ? 'active' : 'pending'}>{s}</Chip>;
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 16 }}>
        <DefList title="Definition of Ready" version={g.dor.version} items={g.dor.items} />
        <DefList title="Definition of Done" version={g.dod.version} items={g.dod.items} />
      </div>
      <Panel title="Changelog — governance" pad={false}>
        <div style={{ padding: 16 }}>
          <DataTable columns={['Version', 'Khi nào', 'Ai đổi', 'DEC', 'Từ lesson']}
            rows={g.changelog.map(c => [c.v, c.when, c.by, <IdCode variant="inline">{c.dec}</IdCode>, c.from])} />
        </div>
      </Panel>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(340px,1fr))', gap: 16 }}>
        <Panel title="Risk register" meta={data.risks.length + ' risks'}>
          <DataTable columns={['ID', 'Severity', 'Nội dung', 'Owner']}
            rows={data.risks.map(r => [r.id, sev(r.sev), r.text, r.owner])} />
        </Panel>
        <Panel title="Tech-debt register" meta={data.debt.length + ' items'}>
          <DataTable columns={['ID', 'Severity', 'Nội dung', 'Owner']}
            rows={data.debt.map(r => [r.id, sev(r.sev), r.text, r.owner])} />
        </Panel>
      </div>
      <Panel title="Lessons learned" meta="retro-keeper">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 12 }}>
          {data.lessons.map(l => (
            <div key={l.id} style={{ border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', padding: '12px 14px', background: 'var(--surface)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <IdCode style={{ fontSize: 12 }}>{l.id}</IdCode>
                <Chip tone={l.status === 'applied' ? 'done' : 'active'}>{l.status}</Chip>
                <span style={{ marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{l.patch}</span>
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 8 }}>Trigger: {l.trigger}</div>
              <div style={{ fontSize: 13.5, marginTop: 4 }}>{l.lesson}</div>
              {l.status === 'proposed' && (
                <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                  <Button variant="ok" size="sm">Duyệt patch</Button>
                  <Button variant="ghost" size="sm">Xem diff checklist</Button>
                </div>
              )}
            </div>
          ))}
        </div>
        <Callout tone="gate" style={{ maxWidth: 'none' }}>Patch chỉ được apply sau <strong>Gate G</strong> — mỗi lần apply ghi version mới vào changelog của skill đó.</Callout>
      </Panel>
    </div>
  );
}
window.Governance = Governance;
})();
