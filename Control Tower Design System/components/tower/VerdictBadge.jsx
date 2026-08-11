import React from 'react';

const V = {
  approve: { label: 'approve', color: 'var(--ok)', bg: 'var(--ok-bg)' },
  'approve-with-notes': { label: 'approve-with-notes', color: 'var(--ok)', bg: 'var(--ok-bg)' },
  'request-changes': { label: 'request-changes', color: 'var(--accent)', bg: 'var(--accent-bg)' }
};

export function VerdictBadge({ id, reviewer, verdict = 'approve', style, ...rest }) {
  const v = V[verdict] || V.approve;
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', padding: '2px 8px',
      borderRadius: 'var(--radius-chip)', color: v.color, background: v.bg, border: '1px solid ' + v.color,
      display: 'inline-block', whiteSpace: 'nowrap', ...style
    }} {...rest}>
      {[id, reviewer, v.label].filter(Boolean).join(' · ')}
    </span>
  );
}
