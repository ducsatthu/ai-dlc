(function(){
const NSm = window.ControlTowerDesignSystem_68131c;
const { GateCard, Panel, FeedItem, Chip, Button, IdCode: Id, AgentWorkCard, AgentAvatar } = NSm;

const L = { fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)' };
const MORE = { fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, whiteSpace: 'nowrap' };

// Một dải duy nhất: pha nào đang chạy · nghi thức · đồng hồ Bolt
function PhaseBar({ phase, bolt, onOpenIntents }) {
  return (
    <div style={{ display: 'flex', alignItems: 'stretch', flexWrap: 'wrap', gap: 0, border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)', overflow: 'hidden' }}>
      {phase.lanes.map((l, i) => {
        const here = l.key === phase.now;
        return (
          <button key={l.key} onClick={onOpenIntents} style={{
            flex: '1 1 120px', minWidth: 0, textAlign: 'left', cursor: 'pointer', border: 'none',
            borderLeft: i ? '1px solid var(--line)' : 'none',
            background: here ? 'var(--surface-2)' : 'transparent', padding: '10px 12px',
            display: 'flex', alignItems: 'baseline', gap: 6, overflow: 'hidden'
          }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: here ? 'var(--accent)' : 'var(--line)', flex: 'none' }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 'var(--fw-bold)', color: here ? 'var(--accent)' : 'var(--muted)', minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{l.name}</span>
            <span style={{ ...L, fontSize: 'var(--fs-micro)', flex: 'none' }}>{l.intents.length}</span>
          </button>
        );
      })}
      <div style={{ flex: '1 1 200px', minWidth: 0, borderLeft: '1px solid var(--line)', background: 'var(--accent-bg)', padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 17, fontWeight: 'var(--fw-bold)', color: 'var(--accent)', lineHeight: 1.1 }}>{bolt.elapsed}</div>
          <div style={{ ...L, fontSize: 'var(--fs-micro)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{bolt.id} / {bolt.budget}</div>
        </div>
        <div style={{ flex: 'none', width: 48, height: 4, background: 'var(--line)', borderRadius: 999, overflow: 'hidden', marginLeft: 'auto' }}>
          <div style={{ width: bolt.pct + '%', height: '100%', background: 'var(--accent)' }} />
        </div>
      </div>
    </div>
  );
}

// Một agent = một dòng; chi tiết mở khi cần
function AgentRow({ w, state, onCmd, docs, onOpenTask, open, onToggle }) {
  const paused = state === 'paused', asked = state === 'asked';
  const live = w.status === 'in-progress';
  const [doc, setDoc] = React.useState(null);
  const done = (w.steps || []).filter(s => s.state === 'done').length;
  const tone = paused ? 'var(--danger)' : asked ? 'var(--blue)' : w.status === 'blocked' ? 'var(--danger)' : w.status === 'done' ? 'var(--ok)' : 'var(--accent)';
  return (
    <div style={{ borderBottom: '1px solid var(--line)' }}>
      <div style={{ padding: '9px 14px', display: 'flex', flexDirection: 'column', gap: 3 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: 999, background: tone, flex: 'none' }} />
          <AgentAvatar name={w.agent} lane={w.agent.includes('reviewer') ? 'review' : 'pipeline'} size={18} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', flex: 'none' }}>{w.taskId}</span>
          <span style={{ flex: 1 }} />
          {w.steps && <span style={{ ...L, fontSize: 'var(--fs-micro)', flex: 'none' }}>{done}/{w.steps.length}</span>}
          {w.elapsed && w.elapsed !== '—' && <span style={{ ...L, fontSize: 'var(--fs-micro)', flex: 'none' }}>{w.elapsed}</span>}
          {live && !paused && <button onClick={() => onCmd('paused')} title="dừng agent này" style={{ ...MORE, color: 'var(--danger)', fontSize: 11 }}>dừng</button>}
          {paused && <button onClick={() => onCmd('running')} title="cho chạy tiếp" style={{ ...MORE, color: 'var(--ok)', fontSize: 11 }}>chạy tiếp</button>}
          <button onClick={onToggle} style={MORE}>{open ? '−' : 'chi tiết'}</button>
        </div>
        <button onClick={onToggle} style={{ display: 'block', width: '100%', textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer', padding: '0 0 0 32px' }}>
          <span style={{ display: 'block', fontSize: 13, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{w.doing || w.title}</span>
        </button>
      </div>
      {(paused || asked) && (
        <div style={{ padding: '0 14px 8px 40px', fontFamily: 'var(--mono)', fontSize: 10.5, color: paused ? 'var(--danger)' : 'var(--blue)' }}>
          {paused ? 'đã dừng — agent giữ nguyên trạng thái, chờ chỉ dẫn' : 'đã gửi câu hỏi — agent hoãn bước kế tiếp'}
        </div>
      )}
      {open && (
        <div style={{ padding: '0 14px 14px 40px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {w.assumption && (
            <div>
              <div style={L}>Giả định đang dùng</div>
              <div style={{ fontSize: 13, textWrap: 'pretty' }}>{w.assumption}</div>
            </div>
          )}
          {w.steps && (
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 2 }}>
              {w.steps.map((s, i) => (
                <li key={i} style={{ display: 'flex', gap: 8, fontSize: 12.5, color: s.state === 'todo' ? 'var(--muted)' : 'var(--ink)' }}>
                  <span style={{ fontFamily: 'var(--mono)', width: 10, flex: 'none', color: s.state === 'done' ? 'var(--ok)' : s.state === 'doing' ? 'var(--accent)' : 'var(--muted)' }}>{s.state === 'done' ? '✓' : s.state === 'doing' ? '●' : '·'}</span>
                  <span>{s.label}</span>
                </li>
              ))}
            </ul>
          )}
          {w.context && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                <span style={{ ...L, fontSize: 'var(--fs-micro)' }}>Đang đọc</span>
                {w.context.map(c => {
                  const has = docs && docs[docKey(c)];
                  return (
                    <span key={c} title={has ? 'mở preview markdown' : 'chưa có bản preview'} onClick={() => has && setDoc(doc === c ? null : c)} style={{ cursor: has ? 'pointer' : 'default', opacity: has ? 1 : 0.7, borderBottom: has ? '1px dotted var(--muted)' : 'none' }}>
                      <Id variant="artifact" style={{ fontSize: 'var(--fs-micro)' }}>{c}</Id>
                    </span>
                  );
                })}
              </div>
              {doc && <DocPreview path={doc} docs={docs} onClose={() => setDoc(null)} />}
            </div>
          )}
          {w.waitingOn && <div style={{ ...L, fontSize: 'var(--fs-micro)', color: 'var(--accent)' }}>chờ · {w.waitingOn}</div>}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            {live && !paused && <Button size="sm" onClick={() => onCmd('asked')}>Hỏi lại giả định</Button>}
            {paused && <Button size="sm" onClick={() => onCmd('running')}>Đổi hướng</Button>}
            {onOpenTask && <button onClick={onOpenTask} style={MORE}>mở toàn bộ task →</button>}
          </div>
        </div>
      )}
    </div>
  );
}

function OpsRow({ s }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={{ borderBottom: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px' }}>
        <span style={{ width: 6, height: 6, borderRadius: 999, background: s.sev === 'warn' ? 'var(--accent)' : 'var(--line)', flex: 'none' }} />
        <button onClick={() => setOpen(v => !v)} style={{ flex: 1, minWidth: 0, textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, fontSize: 12.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.what}</button>
        {s.action ? <Button size="sm" variant="primary">Duyệt</Button> : <span style={{ ...L, fontSize: 'var(--fs-micro)' }}>{s.status}</span>}
        <button onClick={() => setOpen(v => !v)} style={MORE}>{open ? '−' : 'chi tiết'}</button>
      </div>
      {open && (
        <div style={{ padding: '0 12px 10px 26px', display: 'flex', flexDirection: 'column', gap: 4, fontSize: 12.5, color: 'var(--muted)' }}>
          <div>{s.forecast}</div>
          {s.action && <div style={{ color: 'var(--ink)' }}>Đề xuất: {s.action} <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>({s.runbook})</span></div>}
          <div style={{ ...L, fontSize: 'var(--fs-micro)' }}>{s.id} · {s.status}</div>
        </div>
      )}
    </div>
  );
}

function MissionControl({ data, gates, onDecision, onOpenIntent, onOpenFeed, onOpenTask, onOpenIntents }) {
  const [ctrl, setCtrl] = React.useState({});
  const [openRow, setOpenRow] = React.useState(null);
  const [openGate, setOpenGate] = React.useState(null);
  const [feedOpen, setFeedOpen] = React.useState(false);
  const live = data.work.filter(w => w.status === 'in-progress');
  const rest = data.work.filter(w => w.status !== 'in-progress');
  const rows = live.concat(rest);

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 14, minHeight: 0 }}>
      <PhaseBar phase={data.phase} bolt={data.bolt} onOpenIntents={onOpenIntents} />

      {gates.length > 0 && (
        <section style={{ border: '1px solid var(--accent)', borderRadius: 'var(--radius-lg)', background: 'var(--accent-bg)', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderBottom: '1px solid var(--accent)' }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 'var(--fw-bold)', color: 'var(--accent)' }}>◇ {gates.length} mục chờ bạn chốt</span>
          </div>
          <div style={{ padding: '4px 8px 8px' }}>
            {gates.map(g => (
              <GateCard key={g.key} {...g} defaultExpanded={false}
                style={{ marginBottom: 4, border: '1px solid var(--line)', background: 'var(--surface)' }}
                onApprove={() => onDecision(g.key, 'approve')}
                onReject={r => onDecision(g.key, 'reject', r)}
                onDiscuss={() => onDecision(g.key, 'discuss')} />
            ))}
          </div>
        </section>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.6fr) minmax(280px,1fr)', gap: 14, alignItems: 'start' }}>
        <Panel title="Agents đang chạy" meta={live.length + ' / ' + rows.length + ' · ' + data.bolt.ritual} pad={false}>
          {rows.map(w => (
            <AgentRow key={w.taskId} w={w} docs={data.docs}
              state={ctrl[w.taskId] || 'running'}
              onCmd={v => setCtrl(c => ({ ...c, [w.taskId]: v }))}
              open={openRow === w.taskId} onToggle={() => setOpenRow(k => (k === w.taskId ? null : w.taskId))}
              onOpenTask={onOpenTask ? () => onOpenTask(w) : undefined} />
          ))}
        </Panel>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Panel title="Operations" meta={data.ops.deployed.length + ' unit ở production'} pad={false}>
            {data.ops.signals.map(s => <OpsRow key={s.id} s={s} />)}
          </Panel>
          <Panel title="Live feed" meta={data.feed.length + ' mục'} pad={false}>
            {(feedOpen ? data.feed : data.feed.slice(0, 4)).map((x, i) => (
              <div key={x.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 12px', borderBottom: '1px solid var(--line)', cursor: 'pointer' }} onClick={() => onOpenFeed(x)}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: i === 0 && !feedOpen ? 'var(--accent)' : 'var(--muted)', flex: 'none' }}>{x.id}</span>
                <span style={{ fontSize: 12.5, flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{x.summary}</span>
                <span style={{ ...L, fontSize: 'var(--fs-micro)', flex: 'none' }}>{x.type}</span>
              </div>
            ))}
            <div style={{ padding: '8px 12px' }}>
              <button onClick={() => setFeedOpen(v => !v)} style={MORE}>{feedOpen ? 'thu gọn' : 'xem tất cả ' + data.feed.length + ' →'}</button>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
window.MissionControl = MissionControl;
})();
