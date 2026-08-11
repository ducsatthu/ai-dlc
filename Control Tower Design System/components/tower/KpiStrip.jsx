import React from 'react';

export function KpiStrip({ items = [], style, ...rest }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'stretch', gap: 0, border: '1px solid var(--line)',
      background: 'var(--surface)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', ...style
    }} {...rest}>
      {items.map((it, i) => (
        <div key={i} style={{
          padding: '10px 18px', flex: 1, minWidth: 0,
          borderLeft: i ? '1px solid var(--line)' : 'none',
          display: 'flex', alignItems: 'baseline', gap: 'var(--sp-4)'
        }}>
          <span style={{
            fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 'var(--fw-bold)', lineHeight: 1,
            color: it.tone === 'gate' ? 'var(--accent)' : it.tone === 'done' ? 'var(--ok)' : it.tone === 'agent' ? 'var(--blue)' : 'var(--ink)'
          }}>{it.value}</span>
          <span style={{
            fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)',
            textTransform: 'uppercase', color: 'var(--muted)'
          }}>{it.label}</span>
        </div>
      ))}
    </div>
  );
}
