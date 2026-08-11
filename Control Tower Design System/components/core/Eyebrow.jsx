import React from 'react';

export function Eyebrow({ children, rule = true, style, ...rest }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'baseline', gap: 'var(--sp-6)',
      fontFamily: 'var(--mono)', fontSize: 'var(--fs-caption)', letterSpacing: 'var(--ls-eyebrow)',
      textTransform: 'uppercase', color: 'var(--accent)', marginBottom: 'var(--sp-4)', ...style
    }} {...rest}>
      <span>{children}</span>
      {rule && <span style={{ flex: 1, borderTop: '1px solid var(--line)', transform: 'translateY(-3px)' }} />}
    </div>
  );
}
