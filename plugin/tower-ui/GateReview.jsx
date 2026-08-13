(function () {
const NSgr = window.ControlTowerDesignSystem_68131c;
const { Panel, IdCode, Chip, Button, StatusChip } = NSgr;

/* Khối cảnh báo — DS Callout không có tone danger nên dựng tại chỗ theo đúng token */
function Note({ tone = 'gate', title, children }) {
  const c = tone === 'danger' ? 'var(--danger)' : tone === 'done' ? 'var(--ok)' : tone === 'agent' ? 'var(--blue)' : 'var(--accent)';
  const bg = tone === 'danger' ? 'var(--danger-bg)' : tone === 'done' ? 'var(--ok-bg)' : tone === 'agent' ? 'var(--blue-bg)' : 'var(--accent-bg)';
  return (
    <div style={{ borderLeft: '3px solid ' + c, background: bg, borderRadius: '0 var(--radius-lg) var(--radius-lg) 0', padding: '11px 14px' }}>
      {title && <div style={{
        fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase',
        color: c, marginBottom: 5
      }}>{title}</div>}
      <div style={{ fontSize: 13.5, color: 'var(--ink)' }}>{children}</div>
    </div>
  );
}

/* Khối markdown đã render — dùng chung cho gate doc và doc thường */
function Markdown({ text }) {
  const html = React.useMemo(() => (window.MD ? window.MD.render(text || '').html : ''), [text]);
  return <div className="md" dangerouslySetInnerHTML={{ __html: html }} />;
}

function Outline({ text, onJump }) {
  const items = React.useMemo(() => (window.MD ? window.MD.outline(text || '') : []), [text]);
  if (items.length < 3) return null;
  return (
    <nav style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {items.map((it, i) => (
        <span key={i} onClick={() => onJump(it.text)} title={it.text} style={{
          cursor: 'pointer', fontSize: it.level === 1 ? 12.5 : 12,
          fontWeight: it.level === 1 ? 650 : 400,
          color: it.level === 1 ? 'var(--ink)' : 'var(--muted)',
          padding: '3px 8px', paddingLeft: 8 + (it.level - 1) * 10,
          borderLeft: '2px solid ' + (it.level === 1 ? 'var(--accent)' : 'transparent'),
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
        }}>{it.text}</span>
      ))}
    </nav>
  );
}

/* Người duyệt đọc TOÀN VĂN tài liệu gate rồi mới quyết được — protocol §2.1 */
function GateReview({ gate, doc, revisions, onClose, onDecide }) {
  const [confirmed, setConfirmed] = React.useState(false);
  const [reachedEnd, setReachedEnd] = React.useState(false);
  const [mode, setMode] = React.useState(null);      // 'request-changes' | 'reject'
  const [comment, setComment] = React.useState('');
  const [sending, setSending] = React.useState(false);
  const bodyRef = React.useRef(null);

  const blockers = gate.blockers || [];
  const hardBlocked = blockers.length > 0;
  const md = doc ? doc.markdown : '';

  React.useEffect(() => {
    const el = bodyRef.current;
    if (!el) return;
    const onScroll = () => {
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 40) setReachedEnd(true);
    };
    onScroll();
    el.addEventListener('scroll', onScroll);
    return () => el.removeEventListener('scroll', onScroll);
  }, [doc]);

  const jump = (text) => {
    const el = bodyRef.current;
    if (!el) return;
    const hs = el.querySelectorAll('.md-h');
    for (const h of hs) {
      if (h.textContent.trim().startsWith(text.slice(0, 40))) { h.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
    }
  };

  const send = (verdict) => {
    if (sending) return;
    setSending(true);
    onDecide(gate, verdict, comment, confirmed);
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 40, background: 'rgba(8,12,16,0.72)',
      display: 'flex', alignItems: 'stretch', justifyContent: 'center', padding: '2vh 2vw'
    }} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        display: 'flex', flexDirection: 'column', width: 'min(1240px,100%)',
        background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-overlay)', overflow: 'hidden'
      }}>
        {/* header */}
        <header style={{
          display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap',
          padding: '12px 18px', background: 'var(--surface)', borderBottom: '1px solid var(--line)'
        }}>
          <IdCode style={{ color: 'var(--accent)', fontSize: 12.5 }}>Gate {gate.gate} · {gate.target}</IdCode>
          <span style={{ fontSize: 15.5, fontWeight: 700 }}>{gate.title}</span>
          {doc && <Chip tone="neutral">{doc.name}{doc.version ? ' · v' + doc.version : ''}</Chip>}
          {doc && doc.truncated && <Chip tone="blocked">tài liệu bị cắt bớt — mở file gốc để đọc đủ</Chip>}
          <span style={{ marginLeft: 'auto' }} />
          <StatusChip tone={confirmed ? 'done' : 'gate'}>{confirmed ? 'ĐÃ ĐỌC' : 'CHƯA XÁC NHẬN ĐỌC'}</StatusChip>
          <button onClick={onClose} style={{
            background: 'transparent', border: '1px solid var(--line)', borderRadius: 'var(--radius-sm)',
            color: 'var(--muted)', cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 12, padding: '4px 9px'
          }}>✕ đóng</button>
        </header>

        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 340px', minHeight: 0 }}>
          {/* tài liệu */}
          <div style={{ display: 'grid', gridTemplateColumns: '210px minmax(0,1fr)', minHeight: 0 }}>
            <aside style={{
              borderRight: '1px solid var(--line)', background: 'var(--surface)', overflow: 'auto', padding: '12px 4px'
            }}>
              <div style={{
                fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase',
                color: 'var(--muted)', padding: '0 8px 8px'
              }}>Mục lục</div>
              <Outline text={md} onJump={jump} />
            </aside>
            <div ref={bodyRef} style={{ overflow: 'auto', padding: '20px 28px 60px', background: 'var(--bg)' }}>
              {!doc ? (
                <Note tone="danger" title="Không tìm thấy tài liệu gate">
                  Gate này khai <code>gate_doc</code> nhưng file không tồn tại (hoặc intent tạo bằng plugin 1.x
                  chưa có tài liệu này). Không duyệt được khi chưa có bản để đọc — yêu cầu orchestrator sinh
                  tài liệu rồi regenerate tower.
                </Note>
              ) : (
                <>
                  {doc.changelog && doc.changelog.length > 0 && (
                    <div style={{
                      border: '1px solid var(--blue)', background: 'var(--blue-bg)', borderRadius: 'var(--radius-md)',
                      padding: '10px 14px', marginBottom: 18
                    }}>
                      <div style={{
                        fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em',
                        textTransform: 'uppercase', color: 'var(--blue)', marginBottom: 4
                      }}>Đã đổi gì ở bản này</div>
                      {doc.changelog.map((c, i) => (
                        <div key={i} style={{ fontSize: 13, color: 'var(--ink)' }}>· {c}</div>
                      ))}
                    </div>
                  )}
                  <Markdown text={md} />
                  <div style={{
                    marginTop: 28, padding: '14px 16px', border: '1px dashed var(--line)',
                    borderRadius: 'var(--radius-md)', color: 'var(--muted)', fontSize: 13
                  }}>
                    — hết tài liệu — {reachedEnd ? 'bạn đã cuộn tới cuối.' : ''}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* bảng quyết định */}
          <aside style={{
            borderLeft: '1px solid var(--line)', background: 'var(--surface)', overflow: 'auto',
            padding: 16, display: 'flex', flexDirection: 'column', gap: 14
          }}>
            {hardBlocked && (
              <Note tone="danger" title="Nút Approve đang bị khóa">
                <div style={{ marginBottom: 6 }}>Tick “đã đọc” là chưa đủ — gate này còn điều kiện chưa đạt:</div>
                <ul style={{ margin: '4px 0 0', paddingLeft: 16, fontSize: 13 }}>
                  {blockers.map((b, i) => <li key={i}>{b}</li>)}
                </ul>
                <div style={{ marginTop: 8, fontSize: 12.5, color: 'var(--muted)' }}>
                  Sửa trong phiên Claude Code rồi chạy lại <code>/dlc-tower</code>; hoặc dùng
                  <b> Yêu cầu chỉnh sửa</b> ở dưới để gửi đúng yêu cầu này về cho agent.
                </div>
              </Note>
            )}

            {gate.checks && gate.checks.length > 0 && (
              <div>
                <SectionLabel>Bạn cần quyết những gì</SectionLabel>
                <ol style={{ margin: 0, paddingLeft: 18, fontSize: 13.5, lineHeight: 1.7 }}>
                  {gate.checks.map((c, i) => <li key={i}>{c}</li>)}
                </ol>
              </div>
            )}

            {gate.recommendation && (
              <div>
                <SectionLabel>Khuyến nghị của AI</SectionLabel>
                <div style={{ fontSize: 13.5, color: 'var(--ink)' }}>{gate.recommendation}</div>
              </div>
            )}

            {gate.options && gate.options.length > 0 && (
              <div>
                <SectionLabel>Phương án · trade-off</SectionLabel>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13, color: 'var(--muted)' }}>
                  {gate.options.map((o, i) => <li key={i} style={{ marginBottom: 4 }}>{o}</li>)}
                </ul>
              </div>
            )}

            {revisions && revisions.length > 0 && (
              <div>
                <SectionLabel>Vòng chỉnh sửa trước</SectionLabel>
                {revisions.map(r => (
                  <div key={r.id} style={{ borderLeft: '2px solid var(--accent)', paddingLeft: 10, marginBottom: 8 }}>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--accent)' }}>{r.id} · {r.status}</div>
                    <div style={{ fontSize: 12.5, color: 'var(--muted)' }}>{r.request}</div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 10 }}>
              <label style={{
                display: 'flex', gap: 9, alignItems: 'flex-start', cursor: doc ? 'pointer' : 'not-allowed',
                fontSize: 13, color: doc ? 'var(--ink)' : 'var(--muted)',
                border: '1px solid ' + (confirmed ? 'var(--ok)' : 'var(--line)'),
                background: confirmed ? 'var(--ok-bg)' : 'transparent',
                borderRadius: 'var(--radius-md)', padding: '10px 12px'
              }}>
                <input type="checkbox" disabled={!doc} checked={confirmed}
                  onChange={e => setConfirmed(e.target.checked)} style={{ marginTop: 2 }} />
                <span>Tôi đã đọc toàn văn tài liệu này và hiểu mình đang duyệt cái gì.
                  {!reachedEnd && doc && <span style={{ color: 'var(--muted)' }}> (bạn chưa cuộn hết trang)</span>}</span>
              </label>

              {mode && (
                <textarea autoFocus value={comment} onChange={e => setComment(e.target.value)}
                  placeholder={mode === 'request-changes'
                    ? 'Cần sửa phần nào? Ví dụ: "Phần 2 thiếu nguồn LakeHouse", "UOW-03 ước 8h — tách ra".'
                    : 'Lý do từ chối — sẽ được ghi thành DEC.'}
                  style={{
                    width: '100%', minHeight: 92, resize: 'vertical', boxSizing: 'border-box',
                    background: 'var(--bg)', color: 'var(--ink)', fontFamily: 'var(--sans)', fontSize: 13,
                    border: '1px solid ' + (mode === 'reject' ? 'var(--danger)' : 'var(--accent)'),
                    borderRadius: 'var(--radius-md)', padding: '9px 11px'
                  }} />
              )}

              {!mode && (
                <>
                  <Button variant="ok" full disabled={!doc || !confirmed || hardBlocked || sending}
                    onClick={() => send('approve')}>✓ Approve — mở stage kế tiếp</Button>
                  {/* Nút disabled phải tự nói vì sao — người dùng không nên phải đi tìm lý do ở đầu panel */}
                  {(hardBlocked || !doc) && (
                    <div style={{
                      fontSize: 12.5, color: 'var(--danger)', textAlign: 'center', lineHeight: 1.5,
                      border: '1px solid var(--danger)', background: 'var(--danger-bg)',
                      borderRadius: 'var(--radius-sm)', padding: '7px 10px'
                    }}>
                      {!doc ? 'Khóa vì không tìm thấy tài liệu gate.'
                        : 'Khóa vì ' + blockers.length + ' điều kiện chưa đạt (xem khung đỏ trên cùng) — không phải vì checkbox.'}
                    </div>
                  )}
                  <div style={{ display: 'flex', gap: 8 }}>
                    <Button variant="secondary" onClick={() => { setMode('request-changes'); setComment(''); }}
                      style={{ flex: 1 }}>Yêu cầu chỉnh sửa</Button>
                    <Button variant="danger" onClick={() => { setMode('reject'); setComment(''); }}>Reject</Button>
                  </div>
                  {!confirmed && doc && !hardBlocked && (
                    <div style={{ fontSize: 12, color: 'var(--muted)', textAlign: 'center' }}>
                      Approve mở khóa sau khi bạn xác nhận đã đọc.
                    </div>
                  )}
                </>
              )}

              {mode && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <Button variant="primary" disabled={!comment.trim() || sending}
                    onClick={() => send(mode)} style={{ flex: 1 }}>
                    Gửi {mode === 'reject' ? 'từ chối' : 'yêu cầu sửa'}
                  </Button>
                  <Button variant="secondary" onClick={() => { setMode(null); setComment(''); }}>Huỷ</Button>
                </div>
              )}
              <div style={{ fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.6 }}>
                Quyết định ghi vào <code style={{ fontFamily: 'var(--mono)' }}>.ai-dlc/inbox/</code> — phiên Claude Code
                sẽ drain và ghi DEC. “Yêu cầu chỉnh sửa” không đóng gate: agent sửa rồi trình lại bản mới.
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

/* Đọc một tài liệu bất kỳ (không kèm quyết định) */
function DocViewer({ doc, onClose }) {
  if (!doc) return null;
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 40, background: 'rgba(8,12,16,0.72)',
      display: 'flex', justifyContent: 'center', padding: '3vh 3vw'
    }} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        width: 'min(980px,100%)', display: 'flex', flexDirection: 'column', background: 'var(--bg)',
        border: '1px solid var(--line)', borderRadius: 'var(--radius-xl)', overflow: 'hidden',
        boxShadow: 'var(--shadow-overlay)'
      }}>
        <header style={{
          display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px',
          background: 'var(--surface)', borderBottom: '1px solid var(--line)'
        }}>
          <IdCode variant="artifact">{doc.path}</IdCode>
          {doc.version && <Chip tone="neutral">v{doc.version}</Chip>}
          <span style={{ marginLeft: 'auto' }} />
          <button onClick={onClose} style={{
            background: 'transparent', border: '1px solid var(--line)', borderRadius: 'var(--radius-sm)',
            color: 'var(--muted)', cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 12, padding: '4px 9px'
          }}>✕</button>
        </header>
        <div style={{ overflow: 'auto', padding: '20px 28px 48px' }}><Markdown text={doc.markdown} /></div>
      </div>
    </div>
  );
}

Object.assign(window, { GateReview, DocViewer, Markdown, Note });
})();
