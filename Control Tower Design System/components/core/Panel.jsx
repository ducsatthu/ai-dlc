import React from 'react';

export function Panel({ title, meta, pad = true, flush = false, children, style, ...rest }) {
  return (
    <section style={{
      background: 'var(--surface)', border: '1px solid var(--line)',
      borderRadius: flush ? 0 : 'var(--radius-xl)', overflow: 'hidden',
      display: 'flex', flexDirection: 'column', minHeight: 0, ...style
    }} {...rest}>
      {title && (
        <header style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--sp-6)',
          padding: '10px 16px', borderBottom: '1px solid var(--line)', background: 'var(--surface-2)'
        }}>
          <h5 style={{
            margin: 0, fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)',
            letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 'var(--fw-medium)'
          }}>{title}</h5>
          {meta && <span style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--muted)' }}>{meta}</span>}
        </header>
      )}
      <div style={{ padding: pad ? '16px 20px' : 0, minHeight: 0, overflow: 'auto', flex: 1 }}>{children}</div>
    </section>
  );
}
