(function(){
// Preview markdown của artefact ngay trong Control Tower (không rời màn hình)
const NSd = window.ControlTowerDesignSystem_68131c;
const { Chip: DChip, Button: DBtn } = NSd;

const MONO = { fontFamily: 'var(--mono)' };

// "UOW-01/contract.md v2" · "UOW-01/spec.md#AC-03" → "UOW-01/contract.md"
function docKey(s) {
  const m = (s || '').match(/^\s*([^\s#]+\.(?:md|py|ts|tsx|js|jsx|sql|yml|yaml|json))/i);
  return m ? m[1] : (s || '').split('#')[0].trim();
}
function docAnchor(s) {
  const h = (s || '').split('#')[1];
  return h ? h.trim() : null;
}

function inline(s, key) {
  // `code` và **bold**
  const out = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*)/g;
  let last = 0, m, i = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(s.slice(last, m.index));
    const t = m[0];
    if (t[0] === '`') out.push(<code key={key + 'c' + i++} style={{ ...MONO, fontSize: 11.5, background: 'var(--surface-2)', border: '1px solid var(--line)', borderRadius: 3, padding: '0 4px' }}>{t.slice(1, -1)}</code>);
    else out.push(<strong key={key + 'b' + i++} style={{ fontWeight: 'var(--fw-bold)' }}>{t.slice(2, -2)}</strong>);
    last = m.index + t.length;
  }
  if (last < s.length) out.push(s.slice(last));
  return out;
}

function Markdown({ src, highlight }) {
  const lines = src.split('\n');
  const blocks = [];
  let list = null;
  const flush = () => { if (list) { blocks.push({ t: 'ul', items: list }); list = null; } };
  lines.forEach(raw => {
    const l = raw.trimEnd();
    if (/^\s*[-*] /.test(l)) { (list = list || []).push(l.replace(/^\s*[-*] /, '')); return; }
    flush();
    if (!l.trim()) return;
    const h = l.match(/^(#{1,4}) (.*)$/);
    if (h) blocks.push({ t: 'h', lvl: h[1].length, text: h[2] });
    else if (/^\|/.test(l)) blocks.push({ t: 'tr', cells: l.split('|').slice(1, -1).map(c => c.trim()) });
    else if (/^---+$/.test(l)) blocks.push({ t: 'hr' });
    else blocks.push({ t: 'p', text: l });
  });
  flush();
  const rows = [];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      {blocks.map((b, i) => {
        const hit = highlight && b.text && b.text.indexOf(highlight) >= 0;
        if (b.t === 'h') return (
          <div key={i} style={{ ...MONO, fontSize: b.lvl <= 2 ? 12.5 : 11.5, letterSpacing: '0.06em', textTransform: b.lvl <= 2 ? 'uppercase' : 'none', color: hit ? 'var(--accent)' : b.lvl <= 2 ? 'var(--ink)' : 'var(--muted)', marginTop: i ? 6 : 0, fontWeight: 'var(--fw-bold)' }}>{b.text}</div>
        );
        if (b.t === 'hr') return <div key={i} style={{ height: 1, background: 'var(--line)', margin: '2px 0' }} />;
        if (b.t === 'ul') return (
          <ul key={i} style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 3 }}>
            {b.items.map((it, j) => (
              <li key={j} style={{ fontSize: 13, lineHeight: 1.55, textWrap: 'pretty', color: highlight && it.indexOf(highlight) >= 0 ? 'var(--accent)' : 'var(--ink)' }}>{inline(it, i + '-' + j)}</li>
            ))}
          </ul>
        );
        if (b.t === 'tr') {
          const head = !rows.length; rows.push(1);
          if (/^-+$/.test(b.cells.join(''))) return null;
          return (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: 'repeat(' + b.cells.length + ', minmax(0,1fr))', gap: 8, padding: '4px 0', borderBottom: '1px solid var(--line)' }}>
              {b.cells.map((c, j) => <span key={j} style={{ ...MONO, fontSize: 11.5, color: head ? 'var(--muted)' : 'var(--ink)', letterSpacing: head ? '0.08em' : 0, textTransform: head ? 'uppercase' : 'none', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c}</span>)}
            </div>
          );
        }
        return <div key={i} style={{ fontSize: 13, lineHeight: 1.6, textWrap: 'pretty', color: hit ? 'var(--accent)' : 'var(--ink)' }}>{inline(b.text, i)}</div>;
      })}
    </div>
  );
}

function DocPreview({ path, docs, onClose, highlight }) {
  const key = docKey(path);
  const anchor = highlight || docAnchor(path);
  const doc = docs[key];
  return (
    <div style={{ border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', background: 'var(--surface-2)', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderBottom: '1px solid var(--line)', background: 'var(--surface)' }}>
        <span style={{ ...MONO, fontSize: 11.5, color: 'var(--accent)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }}>{key}</span>
        {doc && <DChip tone="pending">{doc.rev}</DChip>}
        {onClose && <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)', ...MONO, fontSize: 12 }}>✕</button>}
      </div>
      {doc ? (
        <React.Fragment>
          <div style={{ ...MONO, fontSize: 10.5, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--muted)', padding: '7px 12px 0' }}>
            sửa lần cuối {doc.updated} · {doc.by}{anchor ? ' · nhảy tới ' + anchor : ''}
          </div>
          <div style={{ padding: '8px 12px 12px', maxHeight: 320, overflow: 'auto' }}>
            <Markdown src={doc.md} highlight={anchor} />
          </div>
        </React.Fragment>
      ) : (
        <div style={{ padding: '14px 12px', fontSize: 13, color: 'var(--muted)' }}>Artefact này chưa có bản markdown trong mô phỏng — chỉ có id truy vết.</div>
      )}
    </div>
  );
}
Object.assign(window, { DocPreview, Markdown, docKey });
})();
