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

/* Truy vết một con số: đếm cái gì, đọc từ file/mục nào, và ĐÚNG những dòng đã đếm.
   Mọi KPI trên dashboard đều mở được cái này — không có số nào không giải thích được. */
function MetricDrawerBody({ m, onDoc }) {
  if (!m) return null;
  const cols = m.rows && m.rows.length ? Object.keys(m.rows[0]) : [];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 30, fontWeight: 700, color: 'var(--blue)' }}>{m.value}</div>
        <div style={{ fontSize: 14.5 }}>{m.label}</div>
      </div>

      <div>
        <SectionLabel>Đếm cái gì</SectionLabel>
        <div style={{ fontSize: 13.5, lineHeight: 1.65, marginTop: 6 }}>{m.rule}</div>
      </div>

      <div>
        <SectionLabel>Đọc từ file nào</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 6 }}>
          {(m.files || []).map((f, i) => (
            <div key={i} onClick={() => f.file.endsWith('.md') && onDoc && onDoc(f.file)}
              style={{
                display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap',
                fontFamily: 'var(--mono)', fontSize: 11.5,
                cursor: f.file.endsWith('.md') ? 'pointer' : 'default',
                color: f.file.endsWith('.md') ? 'var(--blue)' : 'var(--muted)'
              }}>
              <span>{f.file}{f.file.endsWith('.md') ? ' ↗' : ''}</span>
              <span style={{ color: 'var(--muted)' }}>· {f.section}</span>
              {typeof f.rows === 'number' && <span style={{ color: 'var(--muted)' }}>· {f.rows} dòng</span>}
            </div>
          ))}
        </div>
      </div>

      {(m.warnings || []).length > 0 && (
        <div style={{
          border: '1px solid var(--accent)', borderRadius: 'var(--radius)', padding: '10px 12px',
          background: 'color-mix(in srgb, var(--accent) 8%, transparent)', fontSize: 13, lineHeight: 1.6
        }}>
          <strong style={{ color: 'var(--accent)' }}>Cảnh báo về chính con số này</strong>
          {m.warnings.map((w, i) => <div key={i} style={{ marginTop: 4 }}>{w}</div>)}
        </div>
      )}

      <div>
        <SectionLabel>Những dòng đã đếm ({m.rowCount})</SectionLabel>
        {m.rows && m.rows.length ? (
          <div style={{ overflowX: 'auto', marginTop: 6 }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 12 }}>
              <thead>
                <tr style={{ background: 'var(--surface-2)' }}>
                  {cols.map(h => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '6px 8px', fontFamily: 'var(--mono)', fontSize: 10,
                      letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--muted)',
                      borderBottom: '1px solid var(--line)', whiteSpace: 'nowrap'
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {m.rows.map((r, i) => (
                  <tr key={i}>
                    {cols.map(h => (
                      <td key={h} style={{
                        padding: '6px 8px', borderBottom: '1px solid var(--line)',
                        verticalAlign: 'top', maxWidth: 320
                      }}>{String(r[h] === undefined || r[h] === '' ? '—' : r[h])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {m.rowCount > m.rows.length && (
              <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 6 }}>
                … còn {m.rowCount - m.rows.length} dòng nữa, mở file gốc ở trên để xem hết.
              </div>
            )}
          </div>
        ) : (
          <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 6 }}>
            Không có dòng nào — con số này bằng 0 vì <em>không tìm thấy gì để đếm</em>, không phải vì
            tower giấu bớt. Kiểm lại file nguồn ở trên nếu bạn cho rằng phải có.
          </div>
        )}
      </div>
    </div>
  );
}

/* Chi tiết một Unit — mạch của nó: US/NFR/risk · nguồn · bolt · evidence */
function UnitDrawerBody({ unit, data, intentId, onDoc }) {
  if (!unit) return null;
  const src = (data.sourcesByIntent || {})[intentId];
  const rows = (src && src.rows) || [];
  const used = rows.filter(r => (unit.sources || []).includes(r.id));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ fontSize: 15, fontWeight: 650 }}>{unit.name}</div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        <AChip tone={unit.estimate > 5 ? 'blocked' : 'done'}>{unit.estimate ? unit.estimate.toFixed(1) + 'h' : 'chưa ước lượng'}</AChip>
        <AChip tone={unit.stories ? 'done' : 'blocked'}>{unit.stories} user story</AChip>
        <AChip tone={unit.nfrs ? 'done' : 'blocked'}>{unit.nfrs} NFR</AChip>
        <AChip tone={unit.riskCount ? 'done' : 'blocked'}>{unit.riskCount} rủi ro</AChip>
      </div>
      {unit.problems && unit.problems.length > 0 && (
        <Note tone="danger" title="Chưa đạt DoR">{unit.problems.join(' · ')}</Note>
      )}
      <SectionLabel>Nguồn Unit này dựa vào</SectionLabel>
      {used.length ? used.map(r => (
        <div key={r.id} style={{ borderLeft: '2px solid ' + (r.status === 'read' ? 'var(--ok)' : 'var(--accent)'), paddingLeft: 10 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--blue)' }}>{r.id} · {r.status} · {r.source}</div>
          <div style={{ fontSize: 12.5, color: 'var(--muted)' }}>{r.evidence || r.need || '—'}</div>
        </div>
      )) : <div style={{ fontSize: 13, color: 'var(--muted)' }}>Unit chưa khai <code>sources:</code> — không truy được kết luận về nguồn nào.</div>}
      <SectionLabel>Bolt & task</SectionLabel>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.9 }}>
        <div>bolts · {unit.bolts && unit.bolts.length ? unit.bolts.join(', ') : '— chưa vào construction'}</div>
        <div>tasks · {unit.tasks[0]}/{unit.tasks[1]} done</div>
        <div>evidence · {unit.evidence} file</div>
      </div>
      {unit.specPath && (
        <ABtn variant="secondary" onClick={() => onDoc(unit.specPath)}>Đọc spec.md</ABtn>
      )}
    </div>
  );
}

function App() {
  const base = window.CT_DATA;
  const [live, setLive] = React.useState(null);
  const [liveOn, setLiveOn] = React.useState(false);
  const [needReload, setNeedReload] = React.useState(false);

  /* Tower là ảnh chụp: data.js nạp một lần lúc mở trang. Agent chạy trong lúc bạn đang
     nhìn thì màn hình đứng yên. Poll /state (server tự sinh lại khi .ai-dlc/ đổi) và trộn
     phần hay đổi vào — mở dạng file:// thì fetch fail, UI lặng lẽ về chế độ tĩnh. */
  React.useEffect(() => {
    const token = new URLSearchParams(location.search).get('token') || '';
    let stopped = false;
    const tick = () => fetch('/state?token=' + encodeURIComponent(token), { cache: 'no-store' })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(j => {
        if (stopped) return;
        setLive(j); setLiveOn(true);
        const now = (j.gateKeys || []).join(',');
        const had = (base.gates || []).map(g => g.key).join(',');
        if (now !== had) setNeedReload(true);
      })
      .catch(() => { if (!stopped) setLiveOn(false); });
    tick();
    const h = setInterval(tick, 5000);
    return () => { stopped = true; clearInterval(h); };
  }, []);

  const data = React.useMemo(() => (live ? {
    ...base,
    stations: live.stations || base.stations,
    handoffs: live.handoffs || base.handoffs,
    activity: live.activity || base.activity,
    tasks: live.tasks && live.tasks.length ? live.tasks : base.tasks,
    feed: live.feed && live.feed.length ? live.feed : base.feed,
    project: { ...base.project, generated: live.generated || base.project.generated }
  } : base), [live]);

  /* Chỗ đang đứng phải sống qua reload. Tower tự sinh lại mỗi lần .ai-dlc/ đổi và
     người dùng F5 liên tục — về màn mặc định mỗi lần là mất chỗ đang đọc dở.
     Khoá theo tên project để hai dự án mở cùng máy không giẫm lên nhau. */
  const SCREENS = ['mission', 'flow', 'intents', 'intent', 'bolt', 'comms', 'gov'];
  const PREF_KEY = 'ai-dlc.tower.' + ((base.project && base.project.name) || 'default');
  const saved = React.useMemo(() => {
    try { return JSON.parse(localStorage.getItem(PREF_KEY) || '{}') || {}; } catch (e) { return {}; }
  }, []);

  const firstIntent = (data.intents[0] && data.intents[0].id) || null;
  const savedIntent = data.intents.some(i => i.id === saved.intentId) ? saved.intentId : firstIntent;
  const unitsOfSaved = (data.unitsByIntent || {})[savedIntent] || [];
  const [screen, setScreen] = React.useState(
    SCREENS.includes(saved.screen) ? saved.screen : (data.gates.length ? 'mission' : 'flow'));
  const [intentId, setIntentId] = React.useState(savedIntent);
  const [unitId, setUnitId] = React.useState(
    unitsOfSaved.some(u => u.id === saved.unitId) ? saved.unitId
      : (unitsOfSaved.find(u => !u.descoped) || unitsOfSaved[0] || {}).id || null);
  const [navOpen, setNavOpen] = React.useState(
    Array.isArray(saved.navOpen) ? saved.navOpen.filter(id => data.intents.some(i => i.id === id))
      : (savedIntent ? [savedIntent] : []));
  const [theme, setTheme] = React.useState(saved.theme === 'light' ? 'light' : 'dark');
  const [gates, setGates] = React.useState(data.gates);

  React.useEffect(() => {
    try {
      localStorage.setItem(PREF_KEY, JSON.stringify({ theme, screen, intentId, unitId, navOpen }));
    } catch (e) { /* private mode / quota — mất trí nhớ chứ không gãy màn hình */ }
  }, [theme, screen, intentId, unitId, navOpen]);
  const [drawer, setDrawer] = React.useState(null);
  const [toast, setToast] = React.useState(null);
  const [review, setReview] = React.useState(null);   // gate đang được đọc để quyết
  const [viewDoc, setViewDoc] = React.useState(null); // tài liệu đang đọc (không quyết)

  React.useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);

  /* Đổi intent ở màn khác thì unit đang chọn có thể không còn thuộc intent đó nữa. */
  React.useEffect(() => {
    const us = (data.unitsByIntent || {})[intentId] || [];
    if (!us.some(u => u.id === unitId)) {
      setUnitId((us.find(u => !u.descoped) || us[0] || {}).id || null);
    }
  }, [intentId]);

  const say = (m, ms) => { setToast(m); setTimeout(() => setToast(null), ms || 4500); };
  const openDoc = path => {
    const d = (data.docs || {})[path];
    if (d) { setViewDoc(d); return; }
    const token = new URLSearchParams(location.search).get('token') || '';
    fetch('/doc?path=' + encodeURIComponent(path) + '&token=' + encodeURIComponent(token))
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(j => setViewDoc({ path: j.path, name: path.split('/').pop(), markdown: j.markdown }))
      .catch(() => say('Không đọc được ' + path + ' — tower đang mở dạng file tĩnh? Chạy /dlc-tower serve.'));
  };

  /* Quyết định thật — POST về tower_serve → .ai-dlc/inbox/ (durable).
     approve BẮT BUỘC kèm previewed (protocol §2.1); server cũng chặn lần nữa. */
  const decide = (gate, verdict, comment, previewed) => {
    const token = new URLSearchParams(location.search).get('token') || '';
    fetch('/decision?token=' + encodeURIComponent(token), {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gate: gate.gate || 'ESC', intent: gate.target || gate.intent || '', verdict,
        comment: comment || '', doc: gate.doc || '', doc_version: gate.docVersion || '',
        previewed: !!previewed, decided_at: new Date().toISOString()
      })
    }).then(r => {
      if (r.ok) {
        setReview(null);
        if (verdict === 'request-changes') {
          setGates(gs => gs.map(x => x.key === gate.key ? { ...x, pendingRevision: true } : x));
          say('Đã gửi yêu cầu chỉnh sửa — gate vẫn mở, agent sẽ sửa rồi trình lại bản mới');
        } else {
          setGates(gs => gs.filter(x => x.key !== gate.key));
          say(verdict === 'approve'
            ? 'Đã approve — ghi vào inbox, session Claude Code sẽ xử lý và chạy stage kế tiếp'
            : 'Đã reject — lý do đã gửi về orchestrator');
        }
      } else if (r.status === 403) {
        say('Thiếu/sai token — mở lại tower bằng đúng URL có ?token=… (in ở terminal khi chạy /dlc-tower serve); mở 1 lần là nhớ cookie');
      } else {
        r.json().then(j => say('Server từ chối (' + r.status + '): ' + (j.error || ''), 6000))
          .catch(() => say('Server từ chối (' + r.status + ') — xem log tower_serve', 6000));
      }
    }).catch(() => {
      say('Không nối được server — tower đang mở dạng file tĩnh hoặc server đã tắt; chạy /dlc-tower serve');
    });
  };

  const openGate = (gateOrLetter) => {
    const g = typeof gateOrLetter === 'string'
      ? gates.find(x => x.gate === gateOrLetter && x.target === intentId)
      : gateOrLetter;
    if (!g) { say('Gate này chưa mở — không có gì để quyết'); return; }
    setReview(g);
  };

  const intentName = (data.intents.find(x => x.id === intentId) || data.intents[0] || {}).name || '';
  const unitSel = ((data.unitsByIntent || {})[intentId] || []).find(u => u.id === unitId) || null;
  const titles = {
    mission: ['Mission Control', 'cái gì đang chờ tôi · mọi thứ đang ở đâu'],
    flow: ['Dòng chảy — Inception · Construction · Operations', intentId ? intentId + ' · mỗi Unit là một mạch chạy xuyên ba pha' : ''],
    intents: ['Intents', data.intents.length + ' intent đang mở · lọc theo trạng thái, loại brownfield, người yêu cầu'],
    intent: [(intentId || '') + ' · ' + intentName, 'Units · Nguồn · Handoff · Open questions · Decisions · Chỉnh sửa · Tài liệu'],
    bolt: [unitSel ? unitSel.id + ' · ' + unitSel.name : 'Bolt / Task Board',
      unitSel
        ? (unitSel.boltDetails && unitSel.boltDetails.length
            ? unitSel.boltDetails.length + ' bolt · mỗi bolt: Domain Design → Logical Design + ADR → Code + Unit Test'
            : 'unit này chưa có bolt nào — chặng thiết kế chưa để lại gì trên đĩa')
        : 'chọn một Unit ở cây bên trái'],
    comms: ['Comms & Reviews', 'mọi trao đổi là văn bản truy vết được'],
    gov: ['Governance & Learning', 'DoR/DoD · risk · tech-debt · lessons']
  };
  const crumbs = {
    flow: [{ label: 'Dự án · ' + (data.project ? data.project.name : '') }, { label: 'Dòng chảy' }],
    intents: [{ label: 'Dự án · ' + (data.project ? data.project.name : '') }, { label: 'Intents' }],
    intent: [{ label: 'Intents', to: 'intents' }, { label: intentId || '' }],
    bolt: [{ label: 'Intents', to: 'intents' }, { label: intentId || '', to: 'intent' }]
      .concat(unitSel ? [{ label: unitSel.id }] : [{ label: 'chưa chọn Unit' }]),
    comms: [{ label: 'Dự án' }, { label: 'Comms & Reviews' }],
    gov: [{ label: 'Dự án' }, { label: 'Governance & Learning' }]
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)', color: 'var(--ink)' }}>
      <Sidebar screen={screen} setScreen={setScreen} gateCount={gates.length} project={data.project}
        data={data} intentId={intentId} setIntentId={setIntentId} unitId={unitId} setUnitId={setUnitId}
        expanded={navOpen} setExpanded={setNavOpen} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopBar title={titles[screen][0]} subtitle={titles[screen][1]} theme={theme} setTheme={setTheme}
          crumbs={crumbs[screen]} onCrumb={setScreen}
          right={
            <span style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
              <span title={liveOn ? 'Tự cập nhật mỗi 5 giây từ .ai-dlc/' : 'Không nối được server — số liệu đứng yên tại lúc mở trang'}>
                <StatusChip tone={liveOn ? 'agent' : 'muted'}>
                  {liveOn ? 'LIVE · ' + (data.project ? data.project.generated : '') : 'TĨNH — không tự cập nhật'}
                </StatusChip>
              </span>
              <StatusChip tone={gates.length ? 'gate' : 'done'}>{gates.length ? gates.length + ' MỤC CHỜ BẠN' : 'KHÔNG CÓ GÌ CHỜ BẠN'}</StatusChip>
            </span>
          } />
        {needReload && (
          <div style={{
            display: 'flex', gap: 10, alignItems: 'center', padding: '8px 24px',
            background: 'var(--accent-bg)', borderBottom: '1px solid var(--accent)',
            color: 'var(--ink)', fontSize: 13.5
          }}>
            <span style={{ fontFamily: 'var(--mono)', color: 'var(--accent)' }}>◇</span>
            <span>Hàng đợi gate vừa đổi (gate mới mở hoặc vừa đóng) — tải lại trang để lấy tài liệu gate mới nhất.</span>
            <ABtn variant="primary" onClick={() => location.reload()} style={{ marginLeft: 'auto' }}>Tải lại</ABtn>
          </div>
        )}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {screen === 'mission' && <MissionControl data={data} gates={gates} onOpenGate={openGate}
            onOpenIntent={id => { setIntentId(id); setScreen('flow'); }} onOpenFeed={m => setDrawer({ kind: 'msg', m })}
            onOpenDoc={openDoc} onMetric={m => setDrawer({ kind: 'metric', metric: m })} />}
          {screen === 'flow' && <PhaseFlow data={data} intentId={intentId} gates={gates}
            onDoc={openDoc} onGate={openGate} onSelectIntent={setIntentId}
            onMetric={m => setDrawer({ kind: 'metric', metric: m })}
            onOpenUnit={uid => {
              const u = (data.unitsByIntent[intentId] || []).find(x => x.id === uid);
              if (u) { setUnitId(u.id); setDrawer({ kind: 'unit', u }); }
            }} />}
          {screen === 'intents' && <IntentList data={data} onOpenIntent={id => { setIntentId(id); setScreen('intent'); }} />}
          {screen === 'intent' && <IntentDetail data={data} intentId={intentId}
            onOpenBolt={() => setScreen('bolt')} onOpenList={() => setScreen('intents')} onSelectIntent={setIntentId}
            onDoc={openDoc} onOpenFlow={() => setScreen('flow')}
            onOpenUnit={u => { setUnitId(u.id); setDrawer({ kind: 'unit', u }); }} />}
          {screen === 'bolt' && <BoltBoard data={data} intentId={intentId} unitId={unitId}
            onOpenTask={t => setDrawer({ kind: 'task', t })} onOpenUnit={u => setDrawer({ kind: 'unit', u })}
            onDoc={openDoc} />}
          {screen === 'comms' && <CommsReviews data={data} onOpenFeed={m => setDrawer({ kind: 'msg', m })} />}
          {screen === 'gov' && <Governance data={data} />}
        </div>
      </main>

      {review && <GateReview gate={review} doc={(data.docs || {})[review.doc]}
        revisions={(data.revisionsByIntent || {})[review.target] || []}
        onClose={() => setReview(null)} onDecide={decide} />}
      {viewDoc && <DocViewer doc={viewDoc} onClose={() => setViewDoc(null)} />}

      <Drawer open={!!drawer} onClose={() => setDrawer(null)}
        title={drawer ? (drawer.kind === 'task' ? drawer.t.id + ' · task detail'
          : drawer.kind === 'unit' ? drawer.u.id + ' · unit detail'
          : drawer.kind === 'metric' ? 'Số này ở đâu ra?'
          : drawer.m.id + ' · message') : ''}>
        {drawer && drawer.kind === 'metric' && <MetricDrawerBody m={drawer.metric} onDoc={openDoc} />}
        {drawer && drawer.kind === 'task' && <TaskDrawerBody task={drawer.t} data={data} />}
        {drawer && drawer.kind === 'unit' && <UnitDrawerBody unit={drawer.u} data={data} intentId={intentId} onDoc={openDoc} />}
        {drawer && drawer.kind === 'msg' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)' }}>{drawer.m.time} · {drawer.m.from} → {drawer.m.to} · {drawer.m.type}</div>
            <div style={{ fontSize: 14.5 }}>{drawer.m.summary}</div>
            <SectionLabel style={{ marginTop: 8 }}>Truy ngược từ message này</SectionLabel>
            <ATrace direction="vertical" steps={data.trace} />
          </div>
        )}
      </Drawer>

      {toast && (
        <div style={{
          position: 'fixed', bottom: 20, left: '50%', transform: 'translateX(-50%)', zIndex: 50,
          background: 'var(--surface)', border: '1px solid var(--ok)', color: 'var(--ok)',
          borderRadius: 'var(--radius-md)', padding: '10px 16px', fontFamily: 'var(--mono)', fontSize: 12,
          boxShadow: 'var(--shadow-overlay)', maxWidth: '80vw'
        }}>{toast}</div>
      )}
    </div>
  );
}
const rootEl = document.getElementById('root');
if (rootEl) ReactDOM.createRoot(rootEl).render(<App />);
})();
