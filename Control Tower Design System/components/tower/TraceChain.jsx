import React from 'react';

const KINDS = {
  code:     { label: 'code',     color: 'var(--ink)',   bg: 'var(--surface-2)', border: 'var(--line)' },
  design:   { label: 'design',   color: 'var(--ink)',   bg: 'var(--surface-2)', border: 'var(--line)' },
  spec:     { label: 'spec',     color: 'var(--ink)',   bg: 'var(--surface-2)', border: 'var(--line)' },
  task:     { label: 'task',     color: 'var(--ink)',   bg: 'var(--surface-2)', border: 'var(--line)' },
  dec:      { label: 'decision', color: 'var(--accent)', bg: 'var(--accent-bg)', border: 'var(--accent)' },
  gate:     { label: 'gate',     color: 'var(--accent)', bg: 'var(--accent-bg)', border: 'var(--accent)' },
  rv:       { label: 'review',   color: 'var(--blue)',  bg: 'var(--blue-bg)',   border: 'var(--blue)' },
  msg:      { label: 'message',  color: 'var(--blue)',  bg: 'var(--blue-bg)',   border: 'var(--blue)' },
  intent:   { label: 'intent',   color: 'var(--ok)',    bg: 'var(--ok-bg)',     border: 'var(--ok)' }
};

function Node({ step, active, onClick }) {
  const k = KINDS[step.kind] || KINDS.code;
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        border: '1px solid ' + k.border, background: k.bg, color: k.color,
        borderRadius: 'var(--radius-md)', padding: '7px 10px', minWidth: 116, flex: 'none',
        cursor: onClick ? 'pointer' : 'default',
        outline: active ? '1px solid ' + k.border : 'none', outlineOffset: 2,
        opacity: hover && onClick ? 0.86 : 1
      }}>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-micro)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', opacity: 0.75 }}>{k.label}</div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-sm)', fontWeight: 'var(--fw-medium)', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{step.id}</div>
      {step.note && <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 3, maxWidth: 190 }}>{step.note}</div>}
    </div>
  );
}

export function TraceChain({ steps = [], direction = 'horizontal', activeId, onSelect, style, ...rest }) {
  const vertical = direction === 'vertical';
  return (
    <div style={{
      display: 'flex', flexDirection: vertical ? 'column' : 'row',
      alignItems: vertical ? 'stretch' : 'flex-start',
      gap: 0, overflowX: vertical ? 'visible' : 'auto', paddingBottom: vertical ? 0 : 4, ...style
    }} {...rest}>
      {steps.map((s, i) => (
        <React.Fragment key={s.id + i}>
          {i > 0 && (
            <div style={{
              flex: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 12,
              width: vertical ? 'auto' : 26, height: vertical ? 18 : 44
            }}>
              <span style={{
                display: 'block',
                borderTop: vertical ? 'none' : '1px dashed var(--line)',
                borderLeft: vertical ? '1px dashed var(--line)' : 'none',
                width: vertical ? 0 : '100%', height: vertical ? '100%' : 0,
                marginLeft: vertical ? 22 : 0
              }} />
            </div>
          )}
          <Node step={s} active={activeId === s.id} onClick={onSelect ? () => onSelect(s) : undefined} />
        </React.Fragment>
      ))}
    </div>
  );
}
