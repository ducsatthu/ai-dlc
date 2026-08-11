import React from 'react';
import { IdCode } from '../core/IdCode.jsx';
import { Button } from '../core/Button.jsx';

export function GateCard({
  gate, target, title, brief, options = [], recommendation, evidence = [],
  kind = 'gate', expanded: expandedProp, defaultExpanded = false,
  onApprove, onReject, onDiscuss, style, ...rest
}) {
  const [open, setOpen] = React.useState(defaultExpanded);
  const [rejecting, setRejecting] = React.useState(false);
  const [reason, setReason] = React.useState('');
  const expanded = expandedProp === undefined ? open : expandedProp;
  const isEsc = kind === 'escalation';
  return (
    <article style={{
      border: '1px solid var(--accent)', background: 'var(--accent-bg)',
      borderRadius: 'var(--radius-md)', marginBottom: 'var(--sp-4)',
      fontSize: 'var(--fs-row)', ...style
    }} {...rest}>
      <header
        onClick={() => setOpen(v => !v)}
        style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--sp-5)', padding: '10px 12px', cursor: 'pointer' }}>
        <span style={{
          color: 'var(--accent)', fontFamily: 'var(--mono)', fontSize: 13, lineHeight: '20px', flex: 'none', width: 12, textAlign: 'center'
        }}>{isEsc ? '△' : '◇'}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 'var(--fw-semibold)' }}>
            <IdCode style={{ color: 'var(--accent)', fontSize: 'var(--fs-caption)', marginRight: 6 }}>
              {isEsc ? 'ESCALATION' : 'Gate ' + gate}{target ? ' · ' + target : ''}
            </IdCode>
            {title}
          </div>
          {!expanded && brief && (
            <div style={{ color: 'var(--muted)', fontSize: 'var(--fs-sm)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{brief}</div>
          )}
        </div>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', color: 'var(--accent)', flex: 'none' }}>{expanded ? '−' : '+'}</span>
      </header>
      {expanded && (
        <div style={{ padding: '0 12px 12px 34px', display: 'flex', flexDirection: 'column', gap: 'var(--sp-5)' }}>
          {brief && <p style={{ margin: 0, color: 'var(--ink)', maxWidth: 'var(--measure-note)' }}>{brief}</p>}
          {options.length > 0 && (
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 4 }}>Phương án · trade-off</div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 'var(--fs-body-sm)' }}>
                {options.map((o, i) => <li key={i} style={{ marginBottom: 4 }}>{o}</li>)}
              </ul>
            </div>
          )}
          {recommendation && (
            <div style={{ fontSize: 'var(--fs-body-sm)' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-label)', textTransform: 'uppercase', color: 'var(--muted)', marginRight: 8 }}>Khuyến nghị</span>
              {recommendation}
            </div>
          )}
          {evidence.length > 0 && (
            <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap' }}>
              {evidence.map((e, i) => <IdCode key={i} variant="artifact">{e}</IdCode>)}
            </div>
          )}
          {rejecting ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
              <textarea
                value={reason} onChange={e => setReason(e.target.value)} rows={2}
                placeholder="Lý do reject (bắt buộc)"
                style={{
                  width: '100%', fontFamily: 'var(--sans)', fontSize: 'var(--fs-sm)', color: 'var(--ink)',
                  background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 'var(--radius-sm)', padding: '8px 10px', resize: 'vertical'
                }} />
              <div style={{ display: 'flex', gap: 'var(--sp-4)' }}>
                <Button variant="danger" size="sm" disabled={!reason.trim()} onClick={() => { onReject && onReject(reason); setRejecting(false); setReason(''); }}>Gửi reject</Button>
                <Button variant="ghost" size="sm" onClick={() => setRejecting(false)}>Huỷ</Button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 'var(--sp-4)', flexWrap: 'wrap' }}>
              <Button variant="ok" size="sm" onClick={onApprove}>Approve</Button>
              <Button variant="danger" size="sm" onClick={() => setRejecting(true)}>Reject</Button>
              <Button variant="ghost" size="sm" onClick={onDiscuss}>Cần thảo luận</Button>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
