import React from 'react';
import { Chip } from '../core/Chip.jsx';
import { IdCode } from '../core/IdCode.jsx';
import { AgentAvatar } from './AgentAvatar.jsx';

const STEP_MARK = { done: '✓', doing: '●', todo: '·' };
const STEP_COLOR = { done: 'var(--ok)', doing: 'var(--accent)', todo: 'var(--muted)' };

export function AgentWorkCard({
  taskId, title, agent, lane = 'pipeline', status = 'in-progress', elapsed,
  doing, target, steps = [], messages = [], waitingOn, onOpenTask, style, ...rest
}) {
  return (
    <article style={{
      border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)',
      display: 'flex', flexDirection: 'column', ...style
    }} {...rest}>
      <header style={{
        display: 'flex', alignItems: 'center', gap: 'var(--sp-4)', padding: '10px 14px',
        borderBottom: '1px solid var(--line)', background: 'var(--surface-2)', flexWrap: 'wrap'
      }}>
        <AgentAvatar name={agent} lane={lane} size={20} />
        <IdCode style={{ fontSize: 'var(--fs-caption)' }}>{taskId}</IdCode>
        <span style={{ fontSize: 'var(--fs-sm)', flex: 1, minWidth: 120 }}>{title}</span>
        <Chip tone={status === 'done' ? 'done' : status === 'blocked' ? 'blocked' : 'active'}>{status}</Chip>
        {elapsed && <span style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--muted)' }}>{elapsed}</span>}
      </header>

      <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 'var(--sp-5)' }}>
        {doing && (
          <div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 4 }}>Đang làm</div>
            <div style={{ fontSize: 'var(--fs-body-sm)' }}>{doing}</div>
            {target && <IdCode variant="artifact" style={{ marginTop: 6 }}>{target}</IdCode>}
          </div>
        )}

        {steps.length > 0 && (
          <div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 4 }}>
              Các bước · {steps.filter(s => s.state === 'done').length}/{steps.length}
            </div>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 3 }}>
              {steps.map((s, i) => (
                <li key={i} style={{ display: 'flex', gap: 8, fontSize: 'var(--fs-sm)', color: s.state === 'todo' ? 'var(--muted)' : 'var(--ink)' }}>
                  <span style={{ fontFamily: 'var(--mono)', color: STEP_COLOR[s.state], width: 12, flex: 'none' }}>{STEP_MARK[s.state]}</span>
                  <span>{s.label}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {messages.length > 0 && (
          <div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 4 }}>Trao đổi gần nhất</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {messages.map(m => (
                <div key={m.id} style={{ borderLeft: '2px solid var(--blue)', paddingLeft: 10 }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--blue)' }}>
                    {m.id} · {m.from} → {m.to} · {m.type}
                  </div>
                  <div style={{ fontSize: 'var(--fs-sm)' }}>{m.body}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {waitingOn && (
          <div style={{
            border: '1px solid var(--accent)', background: 'var(--accent-bg)', color: 'var(--accent)',
            borderRadius: 'var(--radius-sm)', padding: '6px 10px', fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)'
          }}>chờ · {waitingOn}</div>
        )}

        {onOpenTask && (
          <span onClick={onOpenTask} style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--muted)', cursor: 'pointer' }}>mở toàn bộ task →</span>
        )}
      </div>
    </article>
  );
}
