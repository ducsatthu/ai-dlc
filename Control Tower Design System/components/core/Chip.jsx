import React from 'react';

const TONES = {
  pending: { color: 'var(--muted)', background: 'transparent', borderColor: 'var(--line)' },
  done: { color: 'var(--ok)', background: 'var(--ok-bg)', borderColor: 'var(--ok)' },
  active: { color: 'var(--accent)', background: 'var(--accent-bg)', borderColor: 'var(--accent)' },
  agent: { color: 'var(--blue)', background: 'var(--blue-bg)', borderColor: 'var(--blue)' },
  blocked: { color: 'var(--danger)', background: 'var(--danger-bg)', borderColor: 'var(--danger)' },
  here: { color: 'var(--text-invert)', background: 'var(--accent)', borderColor: 'var(--accent)', fontWeight: 'var(--fw-bold)' },
  neutral: { color: 'var(--ink)', background: 'var(--surface-2)', borderColor: 'var(--line)' }
};

export function Chip({ tone = 'pending', children, style, ...rest }) {
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: 'var(--fs-micro)',
      padding: '3px 7px', borderRadius: 'var(--radius-chip)',
      borderWidth: 1, borderStyle: 'solid', whiteSpace: 'nowrap',
      display: 'inline-block', ...TONES[tone], ...style
    }} {...rest}>{children}</span>
  );
}
