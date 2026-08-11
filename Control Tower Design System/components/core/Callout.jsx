import React from 'react';

const TONES = { agent: 'var(--blue)', gate: 'var(--accent)', done: 'var(--ok)' };
const BGS = { agent: 'var(--blue-bg)', gate: 'var(--accent-bg)', done: 'var(--ok-bg)' };

export function Callout({ tone = 'agent', children, style, ...rest }) {
  return (
    <div style={{
      borderLeft: '3px solid ' + TONES[tone], background: BGS[tone],
      borderRadius: '0 var(--radius-lg) var(--radius-lg) 0',
      padding: '12px 18px', margin: '16px 0', fontSize: 'var(--fs-body-sm)',
      maxWidth: 'var(--measure-note)', ...style
    }} {...rest}>{children}</div>
  );
}
