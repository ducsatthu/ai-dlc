import React from 'react';

const KINDS = {
  pipeline: { color: 'var(--ink)', background: 'var(--surface-2)', borderColor: 'var(--line)' },
  review: { color: 'var(--blue)', background: 'var(--blue-bg)', borderColor: 'var(--blue)' },
  human: { color: 'var(--accent)', background: 'var(--accent-bg)', borderColor: 'var(--accent)' },
  learning: { color: 'var(--ok)', background: 'var(--ok-bg)', borderColor: 'var(--ok)' }
};

export function Tag({ kind = 'pipeline', children, style, ...rest }) {
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: '0.04em',
      padding: '2px 8px', borderRadius: 'var(--radius-chip)',
      borderWidth: 1, borderStyle: 'solid', display: 'inline-block',
      ...KINDS[kind], ...style
    }} {...rest}>{children}</span>
  );
}
