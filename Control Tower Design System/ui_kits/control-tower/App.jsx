(function(){
const NSa = window.ControlTowerDesignSystem_68131c;
const { Panel, IdCode: AId, Chip: AChip, VerdictBadge: AVerdict, Button: ABtn, StatusChip, TraceChain: ATrace } = NSa;

function TaskDrawerBody({ task, data }) {
  const [doc, setDoc] = React.useState(null);
  if (!task) return null;
  const previewable = s => !!data.docs[docKey(s.id)];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ fontSize: 15, fontWeight: 650 }}>{task.title}</div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.9 }}>
        <div>status · {task.status}</div>
        <div>claimed_by · {task.claimedBy || '—'}</div>
        <div>approver · {task.approver}</div>
        <div>depends_on · {task.dependsOn || '—'}</div>
      </div>
      <SectionLabel>Comms của task</SectionLabel>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {data.feed.slice(0, 3).map(m => (
          <div key={m.id} style={{ borderLeft: '2px solid var(--line)', paddingLeft: 10 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--blue)' }}>{m.id} · {m.from} → {m.to} · {m.type}</div>
            <div style={{ fontSize: 13 }}>{m.summary}</div>
          </div>
        ))}
      </div>
      <SectionLabel>Chuỗi truy vết</SectionLabel>
      <ATrace direction="vertical" steps={data.trace} activeId={doc} onSelect={s => setDoc(previewable(s) ? (doc === s.id ? null : s.id) : null)} />
      {doc && <DocPreview path={doc} docs={data.docs} onClose={() => setDoc(null)} />}
    </div>
  );
}

function MsgDrawerBody({ m, data, doc, setDoc }) {
  const th = data.threads[m.id];
  const turns = th ? th.turns : [{ id: m.id, time: m.time, from: m.from, to: m.to, type: m.type, body: m.summary }];
  const TONE = { question: 'var(--blue)', clarification: 'var(--blue)', answer: 'var(--ok)', decision: 'var(--accent)', finding: 'var(--danger)', 'review-request': 'var(--blue)', handoff: 'var(--muted)', note: 'var(--muted)' };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <div style={{ fontSize: 15, fontWeight: 650, textWrap: 'pretty' }}>{th ? th.subject : m.summary}</div>
        {th && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', marginTop: 3 }}>{th.scope}</div>}
      </div>

      <SectionLabel>Hội thoại · {turns.length} lượt</SectionLabel>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {turns.map(t => (
          <div key={t.id} style={{ border: '1px solid ' + (t.id === m.id ? 'var(--accent)' : 'var(--line)'), borderRadius: 'var(--radius-md)', background: t.id === m.id ? 'var(--accent-bg)' : 'var(--surface-2)', padding: '9px 12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.06em' }}>
              <span style={{ color: 'var(--muted)' }}>{t.time}</span>
              <span style={{ color: 'var(--ink)' }}>{t.from}</span>
              <span style={{ color: 'var(--muted)' }}>→</span>
              <span style={{ color: 'var(--ink)' }}>{t.to}</span>
              <span style={{ marginLeft: 'auto', color: TONE[t.type] || 'var(--muted)', textTransform: 'uppercase' }}>{t.type}</span>
              <span style={{ color: 'var(--muted)' }}>{t.id}</span>
            </div>
            <div style={{ fontSize: 13.5, lineHeight: 1.6, marginTop: 5, textWrap: 'pretty' }}>{t.body}</div>
          </div>
        ))}
      </div>

      {th && (
        <div style={{ borderLeft: '2px solid var(--ok)', paddingLeft: 10 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>Kết quả</div>
          <div style={{ fontSize: 13.5, lineHeight: 1.6, marginTop: 3, textWrap: 'pretty' }}>{th.outcome}</div>
        </div>
      )}

      {th && th.refs && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>Artefact liên quan</span>
          {th.refs.map(r => {
            const has = !!data.docs[docKey(r)];
            return (
              <span key={r} title={has ? 'mở preview markdown' : 'chưa có bản preview'} onClick={() => has && setDoc(doc === r ? null : r)} style={{ cursor: has ? 'pointer' : 'default', opacity: has ? 1 : 0.7, borderBottom: has ? '1px dotted var(--muted)' : 'none' }}>
                <AId variant="artifact">{r}</AId>
              </span>
            );
          })}
        </div>
      )}
      {doc && <DocPreview path={doc} docs={data.docs} onClose={() => setDoc(null)} />}
    </div>
  );
}

function App() {
  const data = window.CT_DATA;
  const [screen, setScreen] = React.useState('mission');
  const [intentId, setIntentId] = React.useState('INT-001');
  const [unitId, setUnitId] = React.useState('UOW-01');
  const [theme, setTheme] = React.useState('dark');
  const [gates, setGates] = React.useState(data.gates);
  const [drawer, setDrawer] = React.useState(null);
  const [msgDoc, setMsgDoc] = React.useState(null);
  const [toast, setToast] = React.useState(null);

  React.useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);

  const decide = (key, action, reason) => {
    setGates(g => g.filter(x => x.key !== key));
    setToast(action === 'approve' ? 'Đã approve — ghi DEC-0019, stage 6 mở khoá'
      : action === 'reject' ? 'Đã reject — lý do gửi về orchestrator: "' + reason + '"'
      : 'Đã chuyển sang thảo luận — MSG gửi tới ba-reviewer');
    setTimeout(() => setToast(null), 3200);
  };

  const unitsSel = data.unitsByIntent[intentId] || (intentId === 'INT-001' ? data.units : []);
  const unitSel = unitsSel.find(u => u.id === unitId) || unitsSel[0];

  const titles = {
    mission: ['Mission Control', 'agents đang làm gì ngay lúc này · dừng sớm trước khi đi sai'],
    intents: ['Intents', data.intents.length + ' intent đang mở · lọc theo trạng thái, loại brownfield, người yêu cầu'],
    intent: [intentId + ' · ' + (data.intents.find(x => x.id === intentId) || data.intents[0]).name, 'Units · Open questions · Decisions · Changelog'],
    bolt: [unitSel ? unitSel.id + ' · ' + unitSel.bolt + ' — ' + unitSel.name : intentId + ' — chưa có Unit',
      unitSel ? 'task board · contract · checkpoint' : 'intent còn ở pha Inception'],
    comms: ['Comms & Reviews', 'mọi trao đổi là văn bản truy vết được'],
    gov: ['Governance & Learning', 'DoR/DoD · risk · tech-debt · lessons']
  };

  const crumbs = {
    intents: [{ label: 'Dự án · spoke-project-control-tower' }, { label: 'Intents' }],
    intent: [{ label: 'Intents', to: 'intents' }, { label: intentId }],
    bolt: [{ label: 'Intents', to: 'intents' }, { label: intentId, to: 'intent' }].concat(unitSel ? [{ label: unitSel.id }, { label: unitSel.bolt }] : [{ label: 'chưa có Unit' }]),
    comms: [{ label: 'Dự án' }, { label: 'Comms & Reviews' }],
    gov: [{ label: 'Dự án' }, { label: 'Governance & Learning' }]
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)', color: 'var(--ink)' }}>
      <Sidebar screen={screen} setScreen={setScreen} gateCount={gates.length} data={data}
        intentId={intentId} setIntentId={setIntentId} unitId={unitId} setUnitId={setUnitId} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopBar title={titles[screen][0]} subtitle={titles[screen][1]} theme={theme} setTheme={setTheme}
          crumbs={crumbs[screen]} onCrumb={setScreen}
          right={<StatusChip tone={gates.length ? 'gate' : 'done'}>{gates.length ? gates.length + ' MỤC CHỜ BẠN' : 'KHÔNG CÓ GÌ CHỜ BẠN'}</StatusChip>} />
        <div style={{ flex: 1, overflow: 'auto' }}>
          {screen === 'mission' && <MissionControl data={data} gates={gates} onDecision={decide}
            onOpenIntent={id => { setIntentId(id); setScreen('intent'); }} onOpenIntents={() => setScreen('intents')}
            onOpenTask={w => setDrawer({ kind: 'task', t: data.tasks.find(t => t.id === w.taskId) || { id: w.taskId, title: w.title, status: w.status, approver: '—' } })}
            onOpenFeed={m => setDrawer({ kind: 'msg', m })} />}
          {screen === 'intents' && <IntentList data={data} onOpenIntent={id => { setIntentId(id); setScreen('intent'); }} />}
          {screen === 'intent' && <IntentDetail data={data} intentId={intentId}
            onOpenBolt={() => setScreen('bolt')} onOpenList={() => setScreen('intents')} onSelectIntent={setIntentId} />}
          {screen === 'bolt' && <BoltBoard data={data} intentId={intentId} unitId={unitId} onOpenTask={t => setDrawer({ kind: 'task', t })} />}
          {screen === 'comms' && <CommsReviews data={data} onOpenFeed={m => setDrawer({ kind: 'msg', m })} />}
          {screen === 'gov' && <Governance data={data} />}
        </div>
      </main>
      <Drawer open={!!drawer} onClose={() => { setDrawer(null); setMsgDoc(null); }}
        title={drawer ? (drawer.kind === 'task' ? drawer.t.id + ' · task detail' : drawer.m.id + ' · message') : ''}>
        {drawer && drawer.kind === 'task' && <TaskDrawerBody task={drawer.t} data={data} />}
        {drawer && drawer.kind === 'msg' && <MsgDrawerBody m={drawer.m} data={data} doc={msgDoc} setDoc={setMsgDoc} />}
      </Drawer>
      {toast && (
        <div style={{
          position: 'fixed', bottom: 20, left: '50%', transform: 'translateX(-50%)', zIndex: 30,
          background: 'var(--surface)', border: '1px solid var(--ok)', color: 'var(--ok)',
          borderRadius: 'var(--radius-md)', padding: '10px 16px', fontFamily: 'var(--mono)', fontSize: 12,
          boxShadow: 'var(--shadow-overlay)'
        }}>{toast}</div>
      )}
    </div>
  );
}
const rootEl = document.getElementById('root');
if (rootEl) ReactDOM.createRoot(rootEl).render(<App />);
})();
