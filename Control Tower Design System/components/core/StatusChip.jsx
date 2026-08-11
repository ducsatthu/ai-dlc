import React from 'react';

const TONES = {
  gate: 'var(--accent)', agent: 'var(--blue)', done: 'var(--ok)', danger: 'var(--danger)', muted: 'var(--muted)'
};
const BGS = {
  gate: 'var(--accent-bg)', agent: 'var(--blue-bg)', done: 'var(--ok-bg)', danger: 'var(--danger-bg)', muted: 'transparent'
};

export function StatusChip({ tone = 'gate', dot = true, children, style, ...rest }) {
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: 'var(--fs-caption)', letterSpacing: 'var(--ls-chip)',
      color: TONES[tone], background: BGS[tone], border: '1px solid ' + TONES[tone],
      padding: '5px 12px', borderRadius: 'var(--radius-pill)', whiteSpace: 'nowrap',
      display: 'inline-flex', alignItems: 'center', gap: 'var(--sp-3)', ...style
    }} {...rest}>
      {dot && <span style={{ width: 7, height: 7, borderRadius: '50%', background: TONES[tone], flex: 'none' }} />}
      {children}
    </span>
  );
}
