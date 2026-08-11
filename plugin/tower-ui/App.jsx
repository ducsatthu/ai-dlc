(function(){
const NSa = window.ControlTowerDesignSystem_68131c;
const { Panel, IdCode: AId, Chip: AChip, VerdictBadge: AVerdict, Button: ABtn, StatusChip, TraceChain: ATrace } = NSa;

function TaskDrawerBody({ task, data }) {
  if (!task) return null;
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
      <ATrace direction="vertical" steps={data.trace} />
    </div>
  );
}

function App() {
  const data = window.CT_DATA;
  const [screen, setScreen] = React.useState('mission');
  const [intentId, setIntentId] = React.useState('INT-001');
  const [theme, setTheme] = React.useState('dark');
  const [gates, setGates] = React.useState(data.gates);
  const [drawer, setDrawer] = React.useState(null);
  const [toast, setToast] = React.useState(null);

  React.useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);

  // ai-dlc patch: quyết định thật — POST về tower_serve → .ai-dlc/inbox/ (durable)
  const decide = (key, action, reason) => {
    const g = gates.find(x => x.key === key) || {};
    if (action === 'approve' || action === 'reject') {
      const token = new URLSearchParams(location.search).get('token') || '';
      fetch('/decision?token=' + encodeURIComponent(token), {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gate: g.gate || 'ESC', intent: g.target || g.intent || '', verdict: action, comment: reason || '', decided_at: new Date().toISOString() })
      }).then(r => {
        if (r.ok) {
          setGates(gs => gs.filter(x => x.key !== key));
          setToast(action === 'approve' ? 'Đã approve — ghi vào inbox, session Claude Code sẽ xử lý'
            : 'Đã reject — lý do đã gửi về orchestrator');
        } else if (r.status === 403) {
          setToast('Thiếu/sai token — mở lại tower bằng đúng URL có ?token=… (in ở terminal khi chạy /dlc-tower serve); mở 1 lần là nhớ cookie');
        } else {
          setToast('Server từ chối (' + r.status + ') — xem log tower_serve');
        }
        setTimeout(() => setToast(null), 4500);
      }).catch(() => {
        setToast('Không nối được server — tower đang mở dạng file tĩnh hoặc server đã tắt; chạy /dlc-tower serve');
        setTimeout(() => setToast(null), 4500);
      });
      return;
    }
    setToast('Thảo luận: trả lời trực tiếp trong phiên Claude Code — nội dung sẽ thành MSG');
    setTimeout(() => setToast(null), 3600);
  };

  const titles = {
    mission: ['Mission Control', 'cái gì đang chờ tôi · mọi thứ đang ở đâu'],
    intents: ['Intents', data.intents.length + ' intent đang mở · lọc theo trạng thái, loại brownfield, người yêu cầu'],
    intent: [intentId + ' · ' + (data.intents.find(x => x.id === intentId) || data.intents[0]).name, 'Units · Open questions · Decisions · Changelog'],
    bolt: ['UOW-01 · Bolt 1 — Release Planning', 'task board · contract · checkpoint Gate E'],
    comms: ['Comms & Reviews', 'mọi trao đổi là văn bản truy vết được'],
    gov: ['Governance & Learning', 'DoR/DoD · risk · tech-debt · lessons']
  };

  const crumbs = {
    intents: [{ label: 'Dự án · spoke-project-control-tower' }, { label: 'Intents' }],
    intent: [{ label: 'Intents', to: 'intents' }, { label: intentId }],
    bolt: [{ label: 'Intents', to: 'intents' }, { label: intentId, to: 'intent' }, { label: 'UOW-01' }, { label: 'Bolt 1' }],
    comms: [{ label: 'Dự án' }, { label: 'Comms & Reviews' }],
    gov: [{ label: 'Dự án' }, { label: 'Governance & Learning' }]
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)', color: 'var(--ink)' }}>
      <Sidebar screen={screen} setScreen={setScreen} gateCount={gates.length} intentCount={data.intents.length} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopBar title={titles[screen][0]} subtitle={titles[screen][1]} theme={theme} setTheme={setTheme}
          crumbs={crumbs[screen]} onCrumb={setScreen}
          right={<StatusChip tone={gates.length ? 'gate' : 'done'}>{gates.length ? gates.length + ' MỤC CHỜ BẠN' : 'KHÔNG CÓ GÌ CHỜ BẠN'}</StatusChip>} />
        <div style={{ flex: 1, overflow: 'auto' }}>
          {screen === 'mission' && <MissionControl data={data} gates={gates} onDecision={decide}
            onOpenIntent={id => { setIntentId(id); setScreen('intent'); }} onOpenFeed={m => setDrawer({ kind: 'msg', m })} />}
          {screen === 'intents' && <IntentList data={data} onOpenIntent={id => { setIntentId(id); setScreen('intent'); }} />}
          {screen === 'intent' && <IntentDetail data={data} intentId={intentId}
            onOpenBolt={() => setScreen('bolt')} onOpenList={() => setScreen('intents')} onSelectIntent={setIntentId} />}
          {screen === 'bolt' && <BoltBoard data={data} onOpenTask={t => setDrawer({ kind: 'task', t })} />}
          {screen === 'comms' && <CommsReviews data={data} onOpenFeed={m => setDrawer({ kind: 'msg', m })} />}
          {screen === 'gov' && <Governance data={data} />}
        </div>
      </main>
      <Drawer open={!!drawer} onClose={() => setDrawer(null)}
        title={drawer ? (drawer.kind === 'task' ? drawer.t.id + ' · task detail' : drawer.m.id + ' · message') : ''}>
        {drawer && drawer.kind === 'task' && <TaskDrawerBody task={drawer.t} data={data} />}
        {drawer && drawer.kind === 'msg' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)' }}>{drawer.m.time} · {drawer.m.from} → {drawer.m.to} · {drawer.m.type}</div>
            <div style={{ fontSize: 14.5 }}>{drawer.m.summary}</div>
            <SectionLabel style={{ marginTop: 8 }}>Truy ngược từ message này</SectionLabel>
            <ATrace direction="vertical" steps={[
              { kind: 'msg', id: drawer.m.id, note: drawer.m.type },
              { kind: 'task', id: 'TSK-01', note: 'API contract draft + freeze' },
              { kind: 'design', id: 'UOW-01/contract.md', note: 'v2 FROZEN' },
              { kind: 'spec', id: 'UOW-01/spec.md' },
              { kind: 'intent', id: 'INT-001' }
            ]} />
          </div>
        )}
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
