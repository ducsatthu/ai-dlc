import React from 'react';

export function TimelineItem({ actor, lane = 'agent', heading, children, last = false, style, ...rest }) {
  const color = lane === 'human' ? 'var(--accent)' : 'var(--blue)';
  return (
    <div style={{ position: 'relative', marginBottom: last ? 0 : 30, ...style }} {...rest}>
      <span style={{
        position: 'absolute', left: -33, top: 6, width: 12, height: 12, borderRadius: '50%',
        background: lane === 'human' ? 'var(--accent)' : 'var(--surface)',
        border: '2.5px solid ' + color, boxSizing: 'border-box'
      }} />
      <div style={{ fontWeight: 'var(--fw-semibold)', fontSize: '15.5px', display: 'flex', gap: 'var(--sp-5)', alignItems: 'baseline', flexWrap: 'wrap' }}>
        {actor && <span style={{
          fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', padding: '2px 8px', borderRadius: 'var(--radius-chip)',
          color, background: lane === 'human' ? 'var(--accent-bg)' : 'var(--blue-bg)', border: '1px solid ' + color
        }}>{actor}</span>}
        <span>{heading}</span>
      </div>
      <div style={{ fontSize: 'var(--fs-body-sm)', color: 'var(--muted)', maxWidth: '74ch', marginTop: 4 }}>{children}</div>
    </div>
  );
}

export function Timeline({ children, style, ...rest }) {
  return (
    <div style={{ borderLeft: '2px solid var(--line)', marginLeft: 10, paddingLeft: 26, marginTop: 'var(--sp-9)', ...style }} {...rest}>{children}</div>
  );
}
