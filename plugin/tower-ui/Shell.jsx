(function(){
const NS = window.ControlTowerDesignSystem_68131c;
const { StatusChip, IdCode } = NS;

const NAV = [
  { key: 'mission', label: 'Mission Control', mark: '◇' },
  { key: 'flow', label: 'Dòng chảy 3 pha', mark: '≡' },
  { key: 'intents', label: 'Intents', mark: '▤' },
  { key: 'intent', label: 'Intent Detail', mark: '·' },
  { key: 'bolt', label: 'Bolt / Task Board', mark: '▦' },
  { key: 'comms', label: 'Comms & Reviews', mark: '→' },
  { key: 'gov', label: 'Governance & Learning', mark: '△' }
];

/* Sidebar = cây Intent → Unit → Bolt (Control Tower Design System, variant C).
   Cây phản ánh đúng phân cấp của phương pháp, nên vị trí trong cây trả lời được
   "tôi đang ở đâu" mà không cần đọc breadcrumb. Màu chấm theo semantic DS:
   xanh lá = xong · hổ phách = đang trong bolt · đỏ = chặn · xám = chưa qua gate. */
const MICRO = { fontFamily: 'var(--mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--muted)' };
const UNIT_DOT = {
  done: 'var(--ok)', 'in-bolt': 'var(--accent)', blocked: 'var(--danger)',
  'pending-gate': 'var(--line)', descoped: 'var(--line)'
};
const unitsOf = (data, id) => (data.unitsByIntent || {})[id] || [];

function Leaf({ depth, caret, dot, id, name, on, dim, onClick, onCaret, tail, title }) {
  return (
    <div title={title} style={{
      display: 'flex', alignItems: 'center', gap: 4, padding: '0 6px 0 ' + (6 + depth * 13) + 'px',
      height: 24, borderRadius: 'var(--radius-sm)',
      background: on ? 'var(--accent-bg)' : 'transparent',
      boxShadow: on ? 'inset 2px 0 0 var(--accent)' : 'none'
    }}>
      {caret ? (
        <button onClick={onCaret} style={{ width: 12, flex: 'none', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 9, padding: 0 }}>{caret}</button>
      ) : <span style={{ width: 12, flex: 'none' }} />}
      {dot && <span style={{ width: 6, height: 6, borderRadius: 999, background: dot, flex: 'none' }} />}
      <button onClick={onClick} style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'baseline', gap: 6, background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, textAlign: 'left' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, flex: 'none', color: on ? 'var(--accent)' : dim ? 'var(--muted)' : 'var(--ink)' }}>{id}</span>
        <span style={{ fontSize: 11.5, color: 'var(--muted)', opacity: on ? 1 : 0.85, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{name}</span>
      </button>
      {tail}
    </div>
  );
}

function Sidebar({ screen, setScreen, gateCount, project, data, intentId, setIntentId, unitId, setUnitId, expanded, setExpanded }) {
  const intents = data.intents || [];
  const isOpen = id => (expanded || []).includes(id);
  const toggle = id => setExpanded(e => (e.includes(id) ? e.filter(x => x !== id) : e.concat(id)));
  const openIntent = id => {
    setIntentId(id);
    const u = unitsOf(data, id);
    if (!u.some(x => x.id === unitId)) setUnitId(u.length ? u[0].id : null);
    setExpanded(e => (e.includes(id) ? e : e.concat(id)));
    setScreen('intent');
  };
  const flat = (key, mark, label, badge) => {
    const on = screen === key;
    return (
      <button key={key} onClick={() => setScreen(key)} style={{
        display: 'flex', alignItems: 'center', gap: 10, width: '100%', textAlign: 'left',
        padding: '7px 10px', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
        border: '1px solid ' + (on ? 'var(--line)' : 'transparent'),
        background: on ? 'var(--surface-2)' : 'transparent',
        color: on ? 'var(--ink)' : 'var(--muted)', fontSize: 13.5
      }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, width: 12, color: on ? 'var(--accent)' : 'var(--muted)' }}>{mark}</span>
        <span style={{ flex: 1 }}>{label}</span>{badge}
      </button>
    );
  };
  return (
    <nav style={{
      width: 268, flex: 'none', borderRight: '1px solid var(--line)', background: 'var(--surface)',
      display: 'flex', flexDirection: 'column', padding: '16px 0',
      /* cuộn DỌC thôi: một chuỗi dài trong dữ liệu không được phép đẩy cây điều hướng ra ngoài */
      overflowY: 'auto', overflowX: 'hidden'
    }}>
      <div style={{ padding: '0 18px 14px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
          <span style={{ color: 'var(--accent)', fontFamily: 'var(--mono)' }}>◇</span>
          <span style={{ fontSize: 17, fontWeight: 750, letterSpacing: '-0.02em' }}>Control Tower</span>
        </div>
        <div style={{ ...MICRO, fontSize: 10.5, marginTop: 4 }}>AI-DLC · 18 agents · gates A–G</div>
      </div>

      <div style={{ padding: '10px 8px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {flat('mission', '◇', 'Mission Control', gateCount > 0 ? (
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--accent)', border: '1px solid var(--accent)', background: 'var(--accent-bg)', borderRadius: 999, padding: '0 6px' }}>{gateCount}</span>
        ) : null)}
        {flat('flow', '≡', 'Dòng chảy 3 pha')}
      </div>

      <div style={{ padding: '8px 6px 10px', borderTop: '1px solid var(--line)', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0 10px 8px' }}>
          <span style={MICRO}>Intent → Unit → Bolt</span>
          <button onClick={() => setScreen('intents')} style={{ marginLeft: 'auto', background: 'transparent', border: 'none', cursor: 'pointer', ...MICRO, fontSize: 9, color: screen === 'intents' ? 'var(--accent)' : 'var(--muted)' }}>bảng {intents.length}</button>
        </div>
        {intents.length === 0 && (
          <div style={{ padding: '2px 12px 4px', fontSize: 11.5, color: 'var(--muted)' }}>
            Chưa có intent nào — chạy <code style={{ fontFamily: 'var(--mono)' }}>/dlc-intent</code>.
          </div>
        )}
        {intents.map(i => {
          const units = unitsOf(data, i.id);
          const live = units.filter(u => !u.descoped);
          const out = units.length - live.length;
          const open = isOpen(i.id);
          const sel = i.id === intentId;
          return (
            <div key={i.id}>
              <Leaf depth={0} caret={units.length ? (open ? '▾' : '▸') : '·'} onCaret={() => toggle(i.id)}
                dot={i.gate ? 'var(--accent)' : 'var(--line)'} id={i.id} name={i.name}
                title={i.gate ? 'Gate ' + i.gate + ' đang chờ bạn' : 'stage ' + i.stage + ' · ' + i.phase}
                on={sel && (screen === 'intent' || screen === 'flow')} dim={!sel}
                onClick={() => openIntent(i.id)}
                tail={i.gate ? (
                  /* Cắt cứng: dữ liệu bẩn (gate_open ghi lạc cả một câu) từng làm nhãn này dài 336px
                     và đẩy vỡ cả sidebar. Nhãn điều hướng không bao giờ được co giãn theo nội dung. */
                  <span style={{ ...MICRO, fontSize: 9, color: 'var(--accent)', flex: 'none', maxWidth: 54, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    gate {String(i.gate).slice(0, 12)}
                  </span>
                ) : null} />
              {open && (live.length ? live.map(u => {
                const uSel = sel && unitId === u.id;
                const go = () => { setIntentId(i.id); setUnitId(u.id); setScreen('bolt'); };
                return (
                  <div key={u.id}>
                    <Leaf depth={1} dot={UNIT_DOT[u.status] || 'var(--line)'} id={u.id} name={u.name}
                      title={u.id + ' · ' + u.status + (u.rawStatus ? ' (spec.md ghi: ' + u.rawStatus + ')' : '')}
                      on={uSel && screen === 'bolt'} dim={!uSel} onClick={go}
                      tail={u.problems && u.problems.length
                        ? <span title={u.problems.join(' · ')} style={{ color: 'var(--danger)', fontFamily: 'var(--mono)', fontSize: 10, flex: 'none' }}>△</span>
                        : null} />
                    {uSel && ((u.boltDetails || []).length
                      ? u.boltDetails.map(b => (
                        <Leaf key={b.path} depth={2} id={b.id}
                          name={b.stepsDone + '/' + b.stepsTotal + ' chặng · ' + b.tasks.length + ' task'}
                          title={b.path + ' — thiếu: ' + (b.steps.filter(s => !s.exists).map(s => s.label).join(', ') || 'không thiếu chặng nào')}
                          on={false} dim onClick={go} />
                      ))
                      : <Leaf depth={2} id="—" name="chưa có bolt nào" on={false} dim onClick={go} />)}
                  </div>
                );
              }) : (
                <div style={{ padding: '2px 6px 2px 32px', fontSize: 11, color: 'var(--muted)', opacity: 0.8 }}>chưa phân rã thành Unit</div>
              ))}
              {open && out > 0 && (
                <div style={{ padding: '2px 6px 2px 32px', ...MICRO, fontSize: 9 }}>+{out} unit ngoài phạm vi</div>
              )}
              {open && (i.obsolete || []).length > 0 && (
                <div title={'units/_trash/: ' + i.obsolete.join(', ') + ' — giữ làm bằng chứng cho retro, không tính vào thống kê'}
                  style={{ padding: '2px 6px 2px 32px', ...MICRO, fontSize: 9 }}>+{i.obsolete.length} unit lỗi thời (_trash)</div>
              )}
            </div>
          );
        })}
      </div>

      <div style={{ padding: '10px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        <div style={{ ...MICRO, padding: '0 10px 6px' }}>Xuyên suốt</div>
        {flat('comms', '→', 'Comms & Reviews')}
        {flat('gov', '△', 'Governance & Learning')}
      </div>

      <div style={{ marginTop: 'auto', padding: '12px 18px 0', borderTop: '1px solid var(--line)' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', lineHeight: 1.8 }}>
          <div>supervisor · Human</div>
          <div style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{(project && project.name) || '—'}</div>
          {project && project.generated && <div style={{ opacity: 0.75 }}>cập nhật {project.generated}</div>}
        </div>
      </div>
    </nav>
  );
}

function TopBar({ title, subtitle, crumbs, onCrumb, right, theme, setTheme }) {
  return (
    <header style={{
      display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
      padding: '12px 24px', borderBottom: '1px solid var(--line)', background: 'var(--surface)'
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        {crumbs && crumbs.length > 0 && (
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', marginBottom: 3, flexWrap: 'wrap' }}>
            {crumbs.map((c, i) => (
              <React.Fragment key={c.label + i}>
                {i > 0 && <span style={{ opacity: 0.6 }}>›</span>}
                <span onClick={() => c.to && onCrumb && onCrumb(c.to)} style={{ cursor: c.to ? 'pointer' : 'default', color: i === crumbs.length - 1 ? 'var(--ink)' : 'var(--muted)' }}>{c.label}</span>
              </React.Fragment>
            ))}
          </div>
        )}
        <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.01em' }}>{title}</div>
        {subtitle && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>{subtitle}</div>}
      </div>
      {right}
      <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} style={{
        fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.1em', textTransform: 'uppercase',
        color: 'var(--muted)', background: 'transparent', border: '1px solid var(--line)',
        borderRadius: 'var(--radius-sm)', padding: '5px 10px', cursor: 'pointer'
      }}>{theme === 'dark' ? 'dark' : 'light'}</button>
    </header>
  );
}

function Drawer({ open, title, onClose, children }) {
  if (!open) return null;
  return (
    <aside style={{
      position: 'fixed', top: 0, right: 0, bottom: 0, width: 460, maxWidth: '92vw', zIndex: 20,
      background: 'var(--surface)', borderLeft: '1px solid var(--line)', boxShadow: 'var(--shadow-overlay)',
      display: 'flex', flexDirection: 'column'
    }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 18px', borderBottom: '1px solid var(--line)', background: 'var(--surface-2)' }}>
        <span style={{ flex: 1, fontFamily: 'var(--mono)', fontSize: 12, letterSpacing: '0.08em' }}>{title}</span>
        <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 14 }}>✕</button>
      </header>
      <div style={{ padding: '16px 18px', overflow: 'auto' }}>{children}</div>
    </aside>
  );
}

function SectionLabel({ children, style }) {
  return <div style={{ fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 8, ...style }}>{children}</div>;
}

Object.assign(window, { Sidebar, TopBar, Drawer, SectionLabel, NAV });
})();
