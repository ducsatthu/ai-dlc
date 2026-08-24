(function(){
const NS = window.ControlTowerDesignSystem_68131c;
const { StatusChip, IdCode } = NS;

/* Điều hướng của LEAD, không phải của phương pháp (docs/control-tower-lead-view.md §3):
   tên thay mã · chỉ tới cấp yêu cầu (Intent) · trạng thái bằng lời · mọi màn kỹ thuật gấp
   trong "Tra cứu". Tên tiếng Việt trước, tên cũ (6.0.0) trong ngoặc để người quen không lạc. */
const NAV = [
  { key: 'inbox', label: 'Cần tôi quyết' },
  { key: 'brief', label: 'Bản tin hôm nay' },
  { key: 'bolt', label: 'Phần việc & vòng xây', old: 'Bolt / Task Board' },
  { key: 'comms', label: 'Trao đổi & soát', old: 'Comms & Reviews' },
  { key: 'mission', label: 'Đội AI', old: 'Mission Control' },
  { key: 'flow', label: 'Dòng chảy 3 pha' },
  { key: 'intents', label: 'Danh sách yêu cầu', old: 'Intents' },
  { key: 'gov', label: 'Luật & bài học', old: 'Governance & Learning' }
];
const LOOKUP = NAV.slice(2);

const MICRO = { fontFamily: 'var(--mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--muted)' };
/* Tên yêu cầu lấy từ title trong intent.md — có dự án để nguyên dấu ngoặc kép quanh cả câu. */
const plainName = s => String(s || '').trim().replace(/^["“”']+|["“”']+$/g, '').trim();

/* Một dòng trạng thái bằng lời cho mỗi yêu cầu — tối đa hai ý. Màu chỉ phụ hoạ chữ. */
function intentSummary(i) {
  const [live, done] = i.units || [0, 0];
  let s;
  if (i.stage >= 8 && live > 0 && done >= live) s = { text: 'đã xong · ' + done + '/' + live, done: true };
  else if (i.phase === 'inception') s = { text: 'đang làm rõ yêu cầu' };
  else if (i.phase === 'construction') s = { text: 'đang xây ' + done + '/' + live };
  else s = { text: 'đang nghiệm thu ' + done + '/' + live };
  return s;
}

function NavItem({ on, onClick, children, badge, indent, muted }) {
  return (
    <button onClick={onClick} style={{
      display: 'flex', alignItems: 'center', gap: 8, width: '100%', textAlign: 'left',
      padding: '7px 10px', paddingLeft: indent ? 22 : 10, borderRadius: 'var(--radius-sm)', cursor: 'pointer',
      border: '1px solid ' + (on ? 'var(--line)' : 'transparent'),
      background: on ? 'var(--surface-2)' : 'transparent',
      color: on ? 'var(--ink)' : muted ? 'var(--muted)' : 'var(--ink)', fontSize: indent ? 13 : 13.5
    }}>
      <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{children}</span>
      {badge}
    </button>
  );
}

function Sidebar({ screen, setScreen, inboxCount, project, data, intentId, onOpenIntent, lookupOpen, setLookupOpen }) {
  const intents = data.intents || [];
  const [showDone, setShowDone] = React.useState(false);
  const active = intents.filter(i => !intentSummary(i).done);
  const finished = intents.filter(i => intentSummary(i).done);
  const onLookup = LOOKUP.some(l => l.key === screen);
  const badge = inboxCount > 0 ? (
    <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--accent)', border: '1px solid var(--accent)', background: 'var(--accent-bg)', borderRadius: 999, padding: '0 6px' }}>{inboxCount}</span>
  ) : null;

  const IntentRow = ({ i }) => {
    const s = intentSummary(i);
    const on = (screen === 'intent' || screen === 'flow' || screen === 'bolt') && i.id === intentId;
    return (
      <button onClick={() => onOpenIntent(i.id)} title={i.id} style={{
        display: 'flex', flexDirection: 'column', gap: 2, width: '100%', textAlign: 'left',
        padding: '7px 10px', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
        border: '1px solid ' + (on ? 'var(--line)' : 'transparent'),
        background: on ? 'var(--surface-2)' : 'transparent'
      }}>
        <span style={{ fontSize: 13.5, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{plainName(i.name)}</span>
        <span style={{ fontSize: 11, color: s.done ? 'var(--ok)' : 'var(--muted)' }}>
          {s.text}{i.gate && !s.done ? <span style={{ color: 'var(--accent)' }}> · 1 chờ bạn</span> : null}
        </span>
      </button>
    );
  };

  return (
    <nav style={{
      width: 220, flex: 'none', borderRight: '1px solid var(--line)', background: 'var(--surface)',
      display: 'flex', flexDirection: 'column', padding: '16px 0', overflowY: 'auto', overflowX: 'hidden'
    }}>
      <div style={{ padding: '0 18px 12px' }}>
        <div style={{ fontSize: 16, fontWeight: 750, letterSpacing: '-0.02em', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
          title={project && project.root}>{(project && project.name) || 'Dự án'}</div>
      </div>

      <div style={{ padding: '0 8px 10px', display: 'flex', flexDirection: 'column', gap: 2, borderBottom: '1px solid var(--line)' }}>
        <NavItem on={screen === 'inbox'} onClick={() => setScreen('inbox')} badge={badge}>▸ Cần tôi quyết</NavItem>
        <NavItem on={screen === 'brief'} onClick={() => setScreen('brief')} muted>Bản tin hôm nay</NavItem>
      </div>

      <div style={{ padding: '10px 8px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ ...MICRO, padding: '0 10px 6px' }}>Việc đang làm</div>
        {active.length === 0 && finished.length === 0 && (
          <div style={{ padding: '2px 10px 4px', fontSize: 12, color: 'var(--muted)' }}>
            Chưa có yêu cầu nào — chạy <code style={{ fontFamily: 'var(--mono)' }}>/ai-dlc:dlc-intent</code>.
          </div>
        )}
        {active.slice(0, 5).map(i => <IntentRow key={i.id} i={i} />)}
        {active.length > 5 && <div style={{ padding: '2px 10px', fontSize: 11, color: 'var(--muted)' }}>và {active.length - 5} yêu cầu khác — xem Danh sách yêu cầu</div>}
        {finished.length > 0 && (
          <button onClick={() => setShowDone(v => !v)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '6px 10px 2px', ...MICRO, fontSize: 9.5, color: 'var(--muted)' }}>
            đã xong ({finished.length}) {showDone ? '▴' : '▸'}
          </button>
        )}
        {showDone && finished.map(i => <IntentRow key={i.id} i={i} />)}
      </div>

      <div style={{ padding: '10px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        <NavItem on={false} muted onClick={() => setLookupOpen(v => !v)}>
          {(lookupOpen || onLookup) ? 'Tra cứu ▾' : 'Tra cứu ▸'}
        </NavItem>
        {(lookupOpen || onLookup) && LOOKUP.map(l => (
          <NavItem key={l.key} indent muted on={screen === l.key} onClick={() => setScreen(l.key)}>
            {l.label}{l.old ? <span style={{ fontSize: 10.5, color: 'var(--muted)', opacity: 0.7 }}> ({l.old})</span> : null}
          </NavItem>
        ))}
      </div>

      <div style={{ marginTop: 'auto', padding: '12px 18px 0', borderTop: '1px solid var(--line)', fontSize: 11.5, color: 'var(--muted)' }}>
        {project && project.generated ? 'cập nhật ' + project.generated : ''}
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

Object.assign(window, { Sidebar, TopBar, Drawer, SectionLabel, NAV, plainName });
})();
