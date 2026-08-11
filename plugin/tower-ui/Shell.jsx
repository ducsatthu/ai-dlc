(function(){
const NS = window.ControlTowerDesignSystem_68131c;
const { StatusChip, IdCode } = NS;

const NAV = [
  { key: 'mission', label: 'Mission Control', mark: '◇' },
  { key: 'intents', label: 'Intents', mark: '▤' },
  { key: 'intent', label: 'Intent Detail', mark: '·' },
  { key: 'bolt', label: 'Bolt / Task Board', mark: '▦' },
  { key: 'comms', label: 'Comms & Reviews', mark: '→' },
  { key: 'gov', label: 'Governance & Learning', mark: '△' }
];

function Sidebar({ screen, setScreen, gateCount, intentCount }) {
  return (
    <nav style={{
      width: 232, flex: 'none', borderRight: '1px solid var(--line)', background: 'var(--surface)',
      display: 'flex', flexDirection: 'column', padding: '16px 0'
    }}>
      <div style={{ padding: '0 18px 16px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
          <span style={{ color: 'var(--accent)', fontFamily: 'var(--mono)' }}>◇</span>
          <span style={{ fontSize: 17, fontWeight: 750, letterSpacing: '-0.02em' }}>Control Tower</span>
        </div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--muted)', marginTop: 4 }}>AI-DLC · 17 agents</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', padding: '10px 8px', gap: 2 }}>
        {NAV.map(n => {
          const on = screen === n.key;
          return (
            <button key={n.key} onClick={() => setScreen(n.key)} style={{
              display: 'flex', alignItems: 'center', gap: 10, textAlign: 'left',
              padding: '8px 10px', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
              border: '1px solid ' + (on ? 'var(--line)' : 'transparent'),
              background: on ? 'var(--surface-2)' : 'transparent',
              color: on ? 'var(--ink)' : 'var(--muted)', fontFamily: 'var(--sans)', fontSize: 13.5,
              paddingLeft: n.key === 'intent' ? 30 : 10
            }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: on ? 'var(--accent)' : 'var(--muted)', width: 12 }}>{n.mark}</span>
              <span style={{ flex: 1 }}>{n.label}</span>
              {n.key === 'intents' && intentCount ? (
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{intentCount}</span>
              ) : null}
              {n.key === 'mission' && gateCount > 0 && (
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--accent)', border: '1px solid var(--accent)', background: 'var(--accent-bg)', borderRadius: 999, padding: '0 6px' }}>{gateCount}</span>
              )}
            </button>
          );
        })}
      </div>
      <div style={{ marginTop: 'auto', padding: '12px 18px 0', borderTop: '1px solid var(--line)' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', lineHeight: 1.8 }}>
          <div>supervisor · Human</div>
          <div>spoke-project-control-tower</div>
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
