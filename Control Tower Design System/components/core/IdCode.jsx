import React from 'react';

export function IdCode({ variant = 'plain', children, style, ...rest }) {
  const base = { fontFamily: 'var(--mono)', whiteSpace: 'nowrap' };
  const variants = {
    plain: { fontSize: 'var(--fs-sm)', color: 'var(--muted)' },
    inline: { fontSize: '0.92em', color: 'var(--ink)', background: 'var(--surface-2)', padding: '1px 5px', borderRadius: 'var(--radius-chip)' },
    artifact: {
      fontSize: 'var(--fs-caption)', color: 'var(--ink)', background: 'var(--surface-2)',
      border: '1px solid var(--line)', borderRadius: 'var(--radius-sm)', padding: '2px 8px',
      display: 'inline-block', margin: '2px 4px 2px 0'
    }
  };
  return <span style={{ ...base, ...variants[variant], ...style }} {...rest}>{children}</span>;
}
