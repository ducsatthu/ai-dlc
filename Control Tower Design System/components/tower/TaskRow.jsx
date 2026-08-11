import React from 'react';
import { Chip } from '../core/Chip.jsx';
import { IdCode } from '../core/IdCode.jsx';

const STATUS_TONE = { done: 'done', 'in-progress': 'active', review: 'active', claimed: 'agent', blocked: 'blocked', todo: 'pending' };

export function TaskRow({ id, title, status = 'todo', claimedBy, approver, dependsOn, msgCount, onClick, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const meta = [
    claimedBy ? 'claim: ' + claimedBy : 'chưa claim',
    approver ? 'approver: ' + approver : null,
    dependsOn ? 'depends: ' + dependsOn : null,
    msgCount ? msgCount + ' MSG' : null
  ].filter(Boolean).join(' · ');
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        display: 'flex', gap: 'var(--sp-5)', padding: '10px 14px', borderBottom: '1px solid var(--line)',
        fontSize: 'var(--fs-sm)', alignItems: 'flex-start', flexWrap: 'wrap',
        background: hover && onClick ? 'var(--surface-2)' : 'transparent',
        cursor: onClick ? 'pointer' : 'default', ...style
      }} {...rest}>
      <IdCode style={{ width: 64, flex: 'none', fontSize: 'var(--fs-caption)' }}>{id}</IdCode>
      <Chip tone={STATUS_TONE[status] || 'pending'} style={{ width: 78, textAlign: 'center', flex: 'none' }}>{status}</Chip>
      <div style={{ flex: 1, minWidth: 240 }}>
        <div>{title}</div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--muted)', marginTop: 2 }}>{meta}</div>
      </div>
    </div>
  );
}
