import React from 'react';

const TYPES = {
  'review-request': 'agent', finding: 'gate', question: 'agent', answer: 'agent',
  clarification: 'agent', handoff: 'pipeline', note: 'muted', decision: 'done', escalation: 'gate'
};
const COLOR = { agent: 'var(--blue)', gate: 'var(--accent)', done: 'var(--ok)', pipeline: 'var(--ink)', muted: 'var(--muted)' };

export function FeedItem({ time, id, from, to, type = 'note', summary, onClick, isNew = false, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const c = COLOR[TYPES[type] || 'muted'];
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        fontFamily: 'var(--mono)', fontSize: 'var(--fs-caption)', lineHeight: 1.5,
        padding: '7px 12px', borderBottom: '1px solid var(--line)',
        background: hover && onClick ? 'var(--surface-2)' : 'transparent',
        cursor: onClick ? 'pointer' : 'default',
        borderLeft: isNew ? '2px solid var(--accent)' : '2px solid transparent',
        animation: isNew ? 'none' : undefined, ...style
      }} {...rest}>
      <div style={{ display: 'flex', gap: 'var(--sp-4)', alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ color: 'var(--muted)' }}>{time}</span>
        {id && <span style={{ color: 'var(--muted)' }}>{id}</span>}
        <span style={{ color: 'var(--blue)' }}>{from}{to ? ' → ' + to : ''}</span>
        <span style={{ color: c, border: '1px solid ' + c, borderRadius: 'var(--radius-chip)', padding: '0 5px', fontSize: 'var(--fs-micro)' }}>{type}</span>
      </div>
      {summary && <div style={{ color: 'var(--ink)', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{summary}</div>}
    </div>
  );
}
