import React from 'react';

export function GateStop({ label, children, style, ...rest }) {
  return (
    <div style={{
      border: '1.5px solid var(--accent)', background: 'var(--accent-bg)',
      borderRadius: 'var(--radius-lg)', padding: '14px 18px', marginTop: 'var(--sp-4)',
      fontSize: 'var(--fs-body-sm)', maxWidth: 'var(--measure-note)', ...style
    }} {...rest}>
      <span style={{
        fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)',
        color: 'var(--accent)', fontWeight: 'var(--fw-bold)', display: 'block', marginBottom: 'var(--sp-3)'
      }}>{label}</span>
      {children}
    </div>
  );
}
