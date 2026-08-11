import React from 'react';

const LANES = {
  pipeline: { color: 'var(--ink)', border: 'var(--line)', bg: 'var(--surface-2)' },
  review: { color: 'var(--blue)', border: 'var(--blue)', bg: 'var(--blue-bg)' },
  human: { color: 'var(--accent)', border: 'var(--accent)', bg: 'var(--accent-bg)' },
  learning: { color: 'var(--ok)', border: 'var(--ok)', bg: 'var(--ok-bg)' }
};

function initials(name = '') {
  const parts = String(name).split('-').filter(Boolean);
  return (parts.length > 1 ? parts[0][0] + parts[1][0] : String(name).slice(0, 2)).toUpperCase();
}

export function AgentAvatar({ name = '', lane = 'pipeline', size = 22, withName = false, style, ...rest }) {
  const l = LANES[lane] || LANES.pipeline;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--sp-3)', ...style }} title={name} {...rest}>
      <span style={{
        width: size, height: size, borderRadius: '50%', flex: 'none',
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'var(--mono)', fontSize: Math.round(size * 0.42), fontWeight: 'var(--fw-medium)',
        color: l.color, background: l.bg, border: '1px solid ' + l.border
      }}>{initials(name)}</span>
      {withName && <span style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--muted)' }}>{name}</span>}
    </span>
  );
}
