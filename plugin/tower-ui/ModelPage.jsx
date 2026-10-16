(function(){
const NSmp = window.ControlTowerDesignSystem_68131c;
const { Button: MButton } = NSmp;

/* Trang mô hình — bản cho NGƯỜI của một tài liệu gate (protocol §2.4).
   Bản chữ (intent-plan.md 778 dòng) là nguồn sự thật cho AI; người quyết trên trang này: sáu hình do
   generator vẽ sẵn từ `views/<tài liệu>.view.json` (data.humanView). Dùng chung ở ba chỗ: màn duyệt gate,
   nút "Xem mô hình" trên thẻ AI đã tự quyết, và tab Mô hình của một yêu cầu.

   Mục "Cần bạn quyết" chia hai nhóm để người mở trang thấy 1–3 cây chứ không phải 7:
     · CẦN BẠN   — CHƯA CÓ mặc định (thông tin chưa đủ rõ, đội đang đứng): cây mở sẵn
     · XÁC NHẬN TRƯỚC MỐC — mặc định đã áp nhưng chỉ đảo rẻ tới một mốc, chưa người nào xác nhận: cây mở sẵn.
                   Đây là thứ duy nhất người còn nợ sau khi gate sau đã áp mặc định — không được gấp
     · AI TỰ LO  — đã có mặc định: mỗi điểm MỘT dòng, bấm dòng mới mở cây. Rủi ro cao mà đã có mặc định
                   vẫn thuộc nhóm này (AI đi tiếp, người đảo nếu cần) — đứng đầu nhóm, dòng có huy hiệu đỏ

   Bấm một nhánh trên cây lựa chọn = nói "tôi muốn phương án này". Lời đó đi đâu tuỳ chỗ đang đứng:
     · câu đó có trong open-questions đang mở  → ô trả lời (POST /answer), như thẻ câu hỏi
     · gate đã được AI tự quyết, DEC còn sống   → gom vào MỘT ghi chú Đảo (POST /steer)
     · gate đang mở chờ người (mode lead)       → gom vào lời gửi kèm quyết định của gate */

const LBL = { fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' };
const txt = s => String(s || '').replace(/`/g, '');

function modelOf(data, intent, docPath) {
  const hv = ((data && data.humanView) || {})[intent];
  if (!hv) return null;
  return (docPath && hv.docs[docPath]) || hv.docs[hv.primary] || null;
}
function modelOfDoc(data, docPath) {
  const all = (data && data.humanView) || {};
  for (const k of Object.keys(all)) if (all[k].docs[docPath]) return all[k].docs[docPath];
  return null;
}

/* Ghi chú gom các lựa chọn: mỗi điểm một dòng "D3: đổi sang B. Mọi ca". Chọn lại đúng phương án đang áp
   thì dòng của điểm đó biến mất — không có gì để đổi. Chữ người tự viết thêm được giữ nguyên.
   `code` là mã đứng đầu dòng: mã điểm của view (D3), hoặc mã CÂU HỎI của gate sau (OQB-06) khi điểm đó đã
   được gate sau quyết — vì DEC bị đảo đã chọn trong bộ phương án của câu hỏi ấy. */
function applyPick(note, code, optLabel, isCurrent) {
  const head = code + ':';
  const lines = String(note || '').split('\n').filter(l => l.trim() && l.trim().indexOf(head) !== 0);
  if (!isCurrent) lines.push(head + ' đổi sang ' + optLabel);
  return lines.join('\n');
}

function Banner({ tone, title, children }) {
  const c = tone === 'danger' ? 'var(--danger)' : 'var(--accent)';
  const bg = tone === 'danger' ? 'var(--danger-bg)' : 'var(--accent-bg)';
  return (
    <div style={{ border: '1px solid ' + c, borderLeft: '4px solid ' + c, background: bg, borderRadius: 'var(--radius-md)', padding: '10px 14px' }}>
      <div style={{ ...LBL, color: c, fontWeight: 700 }}>{title}</div>
      {children && <div style={{ fontSize: 13.5, lineHeight: 1.55, marginTop: 4 }}>{children}</div>}
    </div>
  );
}

function Fold({ tone, summary, items }) {
  if (!items || !items.length) return null;
  const c = tone === 'danger' ? 'var(--danger)' : 'var(--accent)';
  return (
    <details style={{ fontSize: 13, lineHeight: 1.55 }}>
      <summary style={{ cursor: 'pointer', color: c, fontSize: 13 }}>{summary}</summary>
      <ul style={{ margin: '6px 0 0', paddingLeft: 18, maxWidth: '88ch' }}>
        {items.map((g, i) => <li key={i} style={{ marginBottom: 3 }}>{txt(g)}</li>)}
      </ul>
    </details>
  );
}

function ModelPage({ model, data, onNav, actions, focusId }) {
  const act = actions || {};
  /* Ghi chú đảo gom THEO DEC: điểm đã được gate sau quyết thì đảo DEC của gate sau (nơi nó thật sự được
     quyết), điểm còn lại đảo DEC của tài liệu đang xem. Khoá GATE = lời gửi kèm quyết định (mode lead). */
  const [notes, setNotes] = React.useState({});
  const [busy, setBusy] = React.useState(false);
  const [sentDecs, setSentDecs] = React.useState([]);
  const [answering, setAnswering] = React.useState(null);   // {id, preset} — điểm đang mở ô trả lời
  const [answered, setAnswered] = React.useState([]);
  const [hint, setHint] = React.useState('');
  const [opened, setOpened] = React.useState([]);            // điểm "AI tự lo" đang mở cây
  const [escBox, setEscBox] = React.useState(null);           // ESC đang mở ô "nhận / giao"
  const [escSent, setEscSent] = React.useState([]);
  const rootRef = React.useRef(null);
  /* Mở trang từ một thẻ "Nên nhìn sớm": tới thẳng cây của điểm đó. */
  React.useEffect(() => {
    if (!focusId) return;
    setOpened(o => o.includes(focusId) ? o : o.concat(focusId));
    const h = setTimeout(() => {
      const el = rootRef.current && rootRef.current.querySelector('#tree-' + focusId);
      if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center' });
    }, 120);
    return () => clearTimeout(h);
  }, [focusId]);
  if (!model) return null;

  if (model.error) {
    return (
      <Banner tone="danger" title="Không vẽ được trang mô hình">
        {model.error}. Tower rơi về bản chữ đầy đủ bên dưới — phải đọc toàn văn như trước.
      </Banner>
    );
  }

  const live = window.autoDecisions ? window.autoDecisions(data) : [];
  const GATE = '__gate';
  const canSteer = id => !!(id && act.onSteer && !sentDecs.includes(id) && live.some(d => d.id === id));
  const steerable = canSteer(model.dec);
  const commenting = !!act.onComment;
  const gateOf = id => ((live.find(d => d.id === id) || {}).gate || '').slice(0, 1);
  const lineOf = code => Object.values(notes).join('\n').split('\n').find(l => l.indexOf(code + ':') === 0);
  const qTree = code => ((data.svg || {}).questions || {})[model.intent + ':' + code];
  const questions = ((data.questionsByIntent || {})[model.intent]) || [];
  const openQ = code => questions.find(q => q.code === code && !/closed|đã chốt|da chot|đóng|descoped/i.test(q.status || ''));

  const setNoteOf = (k, text) => {
    setNotes(n => Object.assign({}, n, { [k]: text }));
    if (k === GATE && commenting) act.onComment(text);
  };
  /* Một lựa chọn đi đâu: mode lead ⇒ lời gửi kèm quyết định; autopilot ⇒ ghi chú đảo của đúng DEC. */
  const route = decId => commenting ? GATE : (canSteer(decId) ? decId : null);
  /* Cuộn trong chính trang mô hình này (trang có thể đang nằm trong lớp phủ hoặc màn duyệt gate). */
  const scrollTo = sel => setTimeout(() => {
    const el = rootRef.current && rootRef.current.querySelector(sel);
    if (el && el.scrollIntoView) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 60);
  /* Bấm một phần tử trên hình: "→ D6" cuộn tới cây D6 (mở nó ra nếu đang gấp) · "nhận / giao" mở ô chỉ đạo. */
  const go = target => {
    const t = String(target || '');
    if (t.indexOf('goto:') === 0) {
      const id = t.slice(5);
      setOpened(o => o.includes(id) ? o : o.concat(id));
      scrollTo('#tree-' + id);
    } else if (t.indexOf('esc:') === 0) {
      setEscBox(t.slice(4));
      scrollTo('#model-esc-box');
    } else if (onNav) onNav(t);
  };
  const sendDirection = esc => text => act.onAnswer({
    kind: 'direction', intent: model.intent, esc, title: 'Giao người chịu rủi ro (' + esc + ')', answer: text
  }).then(ok => { if (ok) { setEscSent(x => x.concat(esc)); setEscBox(null); } return ok; });
  const pick = d => target => {
    if (String(target).indexOf('pick:') !== 0) { go(target); return; }
    const o = (d.options || []).find(x => x.key === target.slice(5));
    if (!o) return;
    setHint('');
    if (d.oq && openQ(d.oq) && act.onAnswer && !answered.includes(d.id)) {
      setAnswering({ id: d.id, preset: { text: o.label, n: Date.now() } });
      return;
    }
    if (model.stale) { setHint('Mô hình này vẽ từ bản chữ cũ — chờ đội vẽ lại rồi hãy chọn.'); return; }
    /* Điểm đã được gate sau quyết mà câu hỏi đó không có cây để chọn: vẫn nhắm đúng DEC của gate sau, nhưng
       không ghép phương án của cây cũ với phương án của câu hỏi — để người tự viết. */
    /* DEC áp thẳng lên mã điểm của view (`Áp: D4 = B`): CÙNG bộ phương án với cây này — chọn được ngay trên cây,
       ghi chú nhắm DEC đang áp điểm đó. */
    if (d.resolved && d.resolved.parts[0].direct) {
      const p = d.resolved.parts[0];
      const k = route(p.dec);
      if (k) { setNoteOf(k, applyPick(notes[k], d.id, o.label, o.key === p.key)); return; }
      setHint(p.dec + ' đã được gửi đảo hoặc đã đổi — chờ đội áp rồi chọn tiếp.');
      return;
    }
    if (d.resolved && !d.resolved.closed) {
      const p = d.resolved.parts[0];
      const k = route(p.dec);
      if (k) { setNoteOf(k, applyPick(notes[k], p.oq, '… (viết phương án của ' + p.oq + ' bạn muốn)', false)); return; }
    }
    if (d.resolved && d.resolved.closed) { setHint(d.id + ' đã do người chốt — muốn đổi thì trả lời lại câu hỏi ' + d.resolved.oq + '.'); return; }
    const k = route(model.dec);
    if (k) { setNoteOf(k, applyPick(notes[k], d.id, o.label, o.key === d.default)); return; }
    setHint(sentDecs.length || model.dec
      ? 'Quyết định của bước này đã được gửi đảo hoặc đã đổi — chờ đội áp rồi chọn tiếp.'
      : 'Bước này chưa tới lúc quyết trên tower — lựa chọn của bạn chưa gửi đi đâu.');
  };
  /* Bấm nhánh trên cây của CÂU HỎI gate sau (OQB-06): đảo DEC đã áp câu đó, ghi bằng mã và phương án của nó. */
  const pickQ = (d, p, qt) => target => {
    if (String(target).indexOf('pick:') !== 0) { go(target); return; }
    const o = (qt.options || []).find(x => x.key === target.slice(5));
    if (!o) return;
    setHint('');
    const k = route(p.dec);
    /* "đang áp" là phương án DEC đã ghi ở dòng Áp (p.key), không nhất thiết là mặc định in trong file câu hỏi */
    if (k) { setNoteOf(k, applyPick(notes[k], p.oq, o.label, o.key === (p.key || qt.silent))); return; }
    setHint(p.dec + ' đã được gửi đảo hoặc đã đổi — chờ đội áp rồi chọn tiếp.');
  };

  const sendSteer = decId => {
    const text = (notes[decId] || '').trim();
    if (!text || busy) return;
    setBusy(true);
    Promise.resolve(act.onSteer({ dec: decId, intent: model.intent, note: text }))
      .then(ok => { if (ok) { setSentDecs(x => x.concat(decId)); setNotes(n => Object.assign({}, n, { [decId]: '' })); } })
      .finally(() => setBusy(false));
  };
  const sendAnswer = d => (text, usedDefault) => {
    const q = openQ(d.oq);
    const file = { business: 'open-questions-business.md', tech: 'open-questions-tech.md' }[q.audience] || 'open-questions.md';
    return act.onAnswer({
      kind: 'answer', intent: model.intent, code: q.code, audience: q.audience || '', file,
      question: q.q, answer: text, used_default: !!usedDefault, blocking: !!q.blocking
    }).then(ok => { if (ok) { setAnswered(a => a.concat(d.id)); setAnswering(null); } return ok; });
  };

  let n = 0;
  return (
    <div ref={rootRef} style={{ display: 'flex', flexDirection: 'column', gap: 18, maxWidth: 1040 }}>
      {model.stale && (
        <Banner tone="danger" title={'Mô hình cũ — bản chữ đã đổi sau khi vẽ (v' + model.staleFrom + ' → v' + model.staleTo + '). Đừng quyết trên hình này.'}>
          Hình dưới đây có thể không còn đúng với thứ đội sẽ làm. Đội phải vẽ lại mô hình trước;
          trong lúc chờ, bản chữ đầy đủ ở cuối trang là bản đúng.
        </Banner>
      )}

      <header>
        <div style={{ fontSize: 21, fontWeight: 700, letterSpacing: '-0.015em', lineHeight: 1.3 }}>{model.headline || model.docName}</div>
        {model.summary && <div style={{ fontFamily: 'var(--mono)', fontSize: 12.5, color: 'var(--muted)', marginTop: 6 }}>{model.summary}</div>}
      </header>

      {/* Dòng quan trọng nhất của trang: không làm gì thì chuyện gì xảy ra. Tự tính từ `default` của từng điểm. */}
      {model.idle && (model.idle.defaults.length > 0 || model.idle.standing.length > 0 || (model.idle.applied || []).length > 0) && (() => {
        const auto = ((data.autopilot || {}).mode === 'autopilot');
        const jump = id => <span key={id} onClick={() => go('goto:' + id)} style={{ cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 12.5, color: 'var(--blue)' }}>{id}</span>;
        const standing = model.idle.standing;
        const applied = model.idle.applied || [];
        const confirm = model.idle.confirm || [];
        const edge = standing.length ? 'var(--danger)' : confirm.length ? 'var(--accent)' : 'var(--ok)';
        return (
          <div style={{
            border: '1px solid ' + (standing.length || confirm.length ? edge : 'var(--line)'), borderLeft: '4px solid ' + edge,
            background: 'var(--surface)', borderRadius: 'var(--radius-md)', padding: '11px 14px', fontSize: 14, lineHeight: 1.6
          }}>
            <div>
              <b>{auto ? 'Nếu bạn không làm gì:' : 'Nếu bạn duyệt nguyên trạng:'}</b>{' '}
              {model.idle.defaults.length > 0
                ? <>{auto ? 'AI áp ' : 'đội áp '}{model.idle.defaults.length} mặc định ({model.idle.defaults.map((x, i) => (
                    <React.Fragment key={x.id}>{i ? ' · ' : ''}{jump(x.id)}<span style={{ fontFamily: 'var(--mono)', fontSize: 12.5 }}>→{x.key}</span></React.Fragment>
                  ))}){model.idle.minor ? ' và ' + model.idle.minor + ' điểm nhỏ' : ''}.</>
                : 'chưa điểm nào có mặc định.'}
            </div>
            {/* Gate sau đã áp mặc định cho điểm mà mô hình này vẽ lúc chưa có — đội KHÔNG còn đứng ở đó. */}
            {applied.length > 0 && (
              <div style={{ color: 'var(--ok)' }}>
                <b>Đã áp ở gate sau:</b>{' '}
                {applied.map((x, i) => (
                  <React.Fragment key={x.id}>{i ? ' · ' : ''}{jump(x.id)}
                    <span style={{ color: 'var(--ink)' }}> {x.gate ? '(Gate ' + x.gate + (x.dec ? ' · ' + x.dec : '') + ')' : '(đã chốt)'}</span>
                  </React.Fragment>
                ))}
              </div>
            )}
            {confirm.length > 0 && (
              <div style={{ color: 'var(--accent)' }}>
                <b>Cần bạn xác nhận {txt(confirm[0].until)}:</b>{' '}
                {confirm.map((x, i) => (
                  <React.Fragment key={x.id}>{i ? ' · ' : ''}{jump(x.id)}
                    {x.until !== confirm[0].until && <span style={{ color: 'var(--ink)' }}> ({txt(x.until)})</span>}
                  </React.Fragment>
                ))}
                <span style={{ color: 'var(--ink)' }}> — qua mốc đó là hết đảo rẻ.</span>
              </div>
            )}
            {standing.length > 0 && (
              <div style={{ color: 'var(--danger)' }}>
                <b>Đội đang ĐỨNG ở:</b>{' '}
                {standing.map((x, i) => (
                  <React.Fragment key={x.id}>{i ? ' · ' : ''}{jump(x.id)} <span style={{ color: 'var(--ink)' }}>— {txt(x.needs || x.question)}</span></React.Fragment>
                ))}
              </div>
            )}
          </div>
        );
      })()}

      <Fold tone="danger" items={model.warnings}
        summary={(model.warnings || []).length + ' chỗ mô hình lệch bản chữ (đánh dấu “?” trên hình) ▸'} />

      {(model.figures || []).map(f => {
        n += 1;
        return (
          <section key={f.key} id={'model-' + f.key} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>{n}</span>
              <span style={{ ...LBL, fontSize: 11.5, color: 'var(--ink)', fontWeight: 700 }}>{f.title}</span>
              {f.note && <span style={{ fontSize: 12.5, color: 'var(--muted)' }}>{f.note}</span>}
            </div>

            {f.key !== 'decisions' && <window.SvgFigure svg={f.svg} onNav={go} />}

            {f.key === 'risks' && escSent.length > 0 && (
              <div style={{ fontSize: 12.5, color: 'var(--ok)' }}>Đã gửi chỉ đạo cho {escSent.join(', ')} — đội ghi người chịu vào hồ sơ.</div>
            )}
            {f.key === 'risks' && escBox && act.onAnswer && window.AnswerBox && (
              <div id="model-esc-box" style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ ...LBL, color: 'var(--danger)', fontWeight: 700 }}>Nhận / giao người chịu · {escBox}</div>
                <window.AnswerBox placeholder="Ai chịu rủi ro này · làm gì · hay chấp nhận vì sao"
                  sendLabel="Gửi chỉ đạo →" onSend={sendDirection(escBox)} />
              </div>
            )}

            {f.key === 'decisions' && (() => {
              const all = model.decisions || [];
              const need = all.filter(d => d.group === 'need');
              const confirm = all.filter(d => d.group === 'confirm');
              const auto = all.filter(d => d.group !== 'need' && d.group !== 'confirm');
              const untils = Array.from(new Set(confirm.map(d => d.defaultUntil)));
              const autopilot = ((data.autopilot || {}).mode === 'autopilot');
              const figLabel = { scope: 'model-scope', sources: 'model-sources', risks: 'model-risks' };
              const tree = d => (
                <div key={d.id} id={'tree-' + d.id} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {(d.gaps || []).length > 0 && (
                    <div style={{ border: '1px solid var(--accent)', background: 'var(--accent-bg)', borderRadius: 'var(--radius-sm)', padding: '7px 11px', fontSize: 12.5, lineHeight: 1.5 }}>
                      <span style={{ ...LBL, color: 'var(--accent)', fontWeight: 700 }}>Bản chữ chưa rõ ở điểm này · </span>
                      {d.gaps.map((g, i) => <span key={i}>{i ? ' · ' : ''}{txt(g.text)}</span>)}
                    </div>
                  )}
                  {d.resolved && (
                    <div style={{ border: '1px solid var(--ok)', borderLeft: '4px solid var(--ok)', background: 'var(--ok-bg)', borderRadius: 'var(--radius-sm)', padding: '7px 11px', fontSize: 13, lineHeight: 1.5 }}>
                      {d.resolved.parts.map((p, i) => (
                        <div key={p.oq}>
                          <b style={{ color: 'var(--ok)' }}>{p.closed ? 'Đã chốt' : 'Đã áp' + (p.gate ? ' ở Gate ' + p.gate : '') + ' (' + p.dec + ((p.replaces || []).length ? ', thay ' + p.replaces.join(', ') : '') + ')'}:</b>{' '}
                          {txt(p.option)}
                          {p.until && <span style={{ color: 'var(--accent)', fontWeight: 650 }}> · đảo rẻ tới: {txt(p.until)}</span>}
                        </div>
                      ))}
                      {d.resolved.confirmed && (
                        <div style={{ fontSize: 12, color: 'var(--ok)', marginTop: 2 }}>
                          Đã có người xác nhận{d.resolved.confirmedBy ? ' (' + d.resolved.confirmedBy + ')' : ''}.
                        </div>
                      )}
                    </div>
                  )}
                  {/* Điểm đã được gate sau quyết: CHỌN trên cây của câu hỏi gate sau — đó là bộ phương án mà DEC
                      ấy đã chọn. Cây lúc gate trước gấp lại làm bối cảnh, không ghép phương án của hai cây. */}
                  {d.resolved && d.resolved.parts.filter(p => !p.closed && qTree(p.oq)).map(p => (
                    <div key={p.oq} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {/* cây câu hỏi vẽ rộng 760 — giữ đúng cỡ, không kéo giãn theo trang 1000 */}
                      <window.SvgFigure svg={qTree(p.oq).svg} onNav={pickQ(d, p, qTree(p.oq))} style={{ maxWidth: 760 }} />
                      {lineOf(p.oq) && (
                        <div style={{ fontSize: 12.5, color: 'var(--accent)' }}>
                          ↳ {lineOf(p.oq)} — {commenting ? 'đã vào lời gửi kèm quyết định' : 'đã vào ghi chú đảo ' + p.dec + ' ở cuối mục này'}
                        </div>
                      )}
                    </div>
                  ))}
                  {d.resolved && d.resolved.parts.some(p => !p.closed && qTree(p.oq))
                    ? (d.svg && (
                        <details style={{ fontSize: 12.5 }}>
                          <summary style={{ cursor: 'pointer', color: 'var(--muted)' }}>Cây lúc Gate {model.gate || 'trước'} — vẽ khi chưa có quyết định này ▸</summary>
                          <div style={{ marginTop: 6, opacity: 0.85 }}><window.SvgFigure svg={d.svg} onNav={t => { if (String(t).indexOf('pick:') !== 0) go(t); }} /></div>
                        </details>
                      ))
                    : (d.svg
                        ? <window.SvgFigure svg={d.svg} onNav={pick(d)} />
                        : <div style={{ fontSize: 13.5 }}><b>{d.id}</b> · {txt(d.question)} <span style={{ color: 'var(--danger)' }}>— chưa đủ phương án để vẽ</span></div>)}
                  {lineOf(d.id) && (
                    <div style={{ fontSize: 12.5, color: 'var(--accent)' }}>
                      ↳ {lineOf(d.id)} — {commenting ? 'đã vào lời gửi kèm quyết định' : 'đã vào ghi chú đảo ở cuối mục này'}
                    </div>
                  )}
                  {d.resolved && (
                    <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                      trạng thái lấy từ{' '}
                      {d.resolved.parts.map((p, i) => (
                        <React.Fragment key={p.oq}>{i ? ' · ' : ''}
                          {p.file && <span onClick={() => onNav && onNav('doc:context-memory/intents/' + model.intent + '/' + p.file)}
                            style={{ color: onNav ? 'var(--blue)' : 'inherit', cursor: onNav ? 'pointer' : 'default', fontFamily: 'var(--mono)', fontSize: 11.5 }}>
                            {p.file} {[p.oq].concat(p.also || []).join(' ↔ ')}
                          </span>}
                          {p.dec && <>{p.file ? ' · ' : ''}<span onClick={() => onNav && onNav('dec:' + p.dec)}
                            style={{ color: onNav ? 'var(--blue)' : 'inherit', cursor: onNav ? 'pointer' : 'default', fontFamily: 'var(--mono)', fontSize: 11.5 }}>{p.dec}</span></>}
                        </React.Fragment>
                      ))}
                      <span> (khớp qua {d.resolved.how})</span>
                    </div>
                  )}
                  {(d.also || []).length > 0 && (
                    <div style={{ fontSize: 12.5, color: 'var(--muted)' }}>
                      chuyện này còn hiện ở:{' '}
                      {d.also.map((a, i) => (
                        <React.Fragment key={a.fig}>{i ? ' · ' : ''}
                          <span onClick={() => scrollTo('#' + figLabel[a.fig])} style={{ color: 'var(--blue)', cursor: 'pointer' }}>{a.label}</span>
                        </React.Fragment>
                      ))}
                    </div>
                  )}
                  {answered.includes(d.id) && <div style={{ fontSize: 12.5, color: 'var(--ok)' }}>Đã gửi câu trả lời cho {d.id} — đội áp nguyên văn vào hồ sơ.</div>}
                  {answering && answering.id === d.id && window.AnswerBox && (
                    <window.AnswerBox placeholder={'Câu trả lời cho ' + d.id + ' — đội áp nguyên văn vào hồ sơ'}
                      preset={answering.preset} sendLabel="Gửi câu trả lời →" onSend={sendAnswer(d)} />
                  )}
                </div>
              );
              return (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {(model.gaps || []).length > 0 && (
                  <Banner tone="gate" title={'Bản chữ chưa rõ — AI không vẽ được (' + model.gaps.length + ')'}>
                    <ul style={{ margin: 0, paddingLeft: 18, maxWidth: '92ch' }}>
                      {model.gaps.map((g, i) => (
                        <li key={i} style={{ marginBottom: 2 }}>
                          {txt(g.text)}
                          {g.ref && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}> · mục {g.ref}</span>}
                          {g.decision && <span onClick={() => go('goto:' + g.decision)} style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--blue)', cursor: 'pointer' }}> → {g.decision}</span>}
                        </li>
                      ))}
                    </ul>
                  </Banner>
                )}

                {need.length > 0 && <div style={{ ...LBL, color: 'var(--danger)', fontWeight: 700 }}>Cần bạn · {need.length}</div>}
                {need.map(tree)}
                {all.length > 0 && need.length === 0 && (
                  <div style={{ fontSize: 13.5, color: 'var(--ok)' }}>Không điểm nào buộc phải chờ bạn — mọi điểm đã có mặc định.</div>
                )}

                {confirm.length > 0 && (
                  <div style={{ ...LBL, color: 'var(--accent)', fontWeight: 700, marginTop: 4 }}>
                    Xác nhận {untils.length === 1 ? txt(untils[0]) : 'trước mốc'} · {confirm.length}
                    <span style={{ textTransform: 'none', letterSpacing: 0, fontFamily: 'var(--sans)', fontSize: 12.5, fontWeight: 400, color: 'var(--muted)' }}>
                      {' '}— mặc định đã áp, nhưng qua mốc này là hết đảo rẻ
                    </span>
                  </div>
                )}
                {confirm.map(tree)}

                {auto.length > 0 && (
                  <div style={{ ...LBL, color: 'var(--muted)', fontWeight: 700, marginTop: 4 }}>
                    {autopilot ? 'AI tự lo — đảo nếu cần' : 'Đã có mặc định — đổi nếu cần'} · {auto.length}
                  </div>
                )}
                {auto.map(d => {
                  const on = opened.includes(d.id);
                  const changed = !!lineOf(d.id) || !!(d.resolved && d.resolved.parts.some(p => lineOf(p.oq)));
                  return (
                    <div key={d.id} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <button onClick={() => setOpened(o => on ? o.filter(x => x !== d.id) : o.concat(d.id))}
                        aria-expanded={on} title={d.ref ? 'bản chữ: mục ' + d.ref : undefined}
                        style={{
                          display: 'flex', gap: 10, alignItems: 'baseline', width: '100%', textAlign: 'left', cursor: 'pointer',
                          background: 'var(--surface)', border: '1px solid ' + (changed ? 'var(--accent)' : 'var(--line)'),
                          borderRadius: 'var(--radius-md)', padding: '9px 12px', color: 'var(--ink)', fontFamily: 'var(--sans)'
                        }}>
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 11.5, fontWeight: 700, flex: 'none' }}>{d.id}</span>
                        <span style={{ fontSize: 13.5, fontWeight: 600, flex: '0 1 auto', minWidth: 0 }}>{txt(d.question)}</span>
                        <span style={{ fontSize: 13, color: d.defaultUntil ? 'var(--accent)' : 'var(--muted)', flex: '1 1 0', minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>→ {txt(d.line)}</span>
                        {d.risk === 'cao' && <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--danger)', border: '1px solid var(--danger)', background: 'var(--danger-bg)', borderRadius: 999, padding: '0 7px', flex: 'none' }}>rủi ro cao</span>}
                        {(d.unlocks || []).length > 0 && <span style={{ fontSize: 11, color: 'var(--blue)', flex: 'none' }}>gỡ {d.unlocks.length} điểm</span>}
                        {d.costly && d.costly.length > 0 && <span style={{ fontSize: 11, color: 'var(--danger)', flex: 'none' }}>có phương án đảo đắt</span>}
                        <span style={{ fontSize: 12, color: 'var(--blue)', flex: 'none' }}>{on ? 'thu ▴' : 'mở cây ▸'}</span>
                      </button>
                      {on && tree(d)}
                    </div>
                  );
                })}

                {hint && <div style={{ fontSize: 12.5, color: 'var(--accent)' }}>{hint}</div>}

                {Object.keys(notes).filter(k => k !== GATE && (notes[k] || '').trim() !== '' && canSteer(k)).map(k => (
                  <div key={k} style={{ border: '1px dashed var(--accent)', background: 'var(--accent-bg)', borderRadius: 'var(--radius-md)', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ ...LBL, color: 'var(--accent)', fontWeight: 700 }}>Đảo quyết định AI đã tự chốt · {k}</div>
                    {k !== model.dec && (
                      <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                        đảo {k}{gateOf(k) ? ' (Gate ' + gateOf(k) + ')' : ''} — nơi điểm này thật sự được quyết
                      </div>
                    )}
                    <textarea value={notes[k]} onChange={e => setNoteOf(k, e.target.value)} rows={Math.max(2, notes[k].split('\n').length)}
                      style={{
                        width: '100%', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'var(--sans)', fontSize: 13.5,
                        padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--line)',
                        background: 'var(--surface)', color: 'var(--ink)', lineHeight: 1.5
                      }} />
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                      <MButton variant="primary" onClick={() => sendSteer(k)} disabled={busy}>{busy ? 'Đang gửi…' : 'Gửi yêu cầu đảo ' + k + ' →'}</MButton>
                      <MButton variant="secondary" onClick={() => setNoteOf(k, '')} disabled={busy}>Thôi, giữ nguyên</MButton>
                      <span style={{ fontSize: 12, color: 'var(--muted)' }}>Bấm thêm nhánh khác để gom nhiều điểm vào một lần đảo.</span>
                    </div>
                  </div>
                ))}
                {sentDecs.map(k => (
                  <div key={k} style={{ fontSize: 13, color: 'var(--ok)' }}>Đã gửi yêu cầu đảo {k} — đội làm lại đúng phần đó rồi ghi quyết định mới.</div>
                ))}
                {commenting && (notes[GATE] || '').trim() !== '' && (
                  <div style={{ fontSize: 12.5, color: 'var(--muted)' }}>
                    Lựa chọn của bạn đã vào ô “gửi kèm quyết định” ở cột bên phải.
                  </div>
                )}

                {(model.minor || []).length > 0 && (
                  <details style={{ fontSize: 13, lineHeight: 1.55 }}>
                    <summary style={{ cursor: 'pointer', color: 'var(--muted)', fontSize: 12.5 }}>
                      {model.minor.length} điểm nhỏ — không đổi khối lượng việc, AI giữ mặc định ▸
                    </summary>
                    <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>
                      {model.minor.map((m, i) => <li key={i}>{txt(m)}</li>)}
                    </ul>
                  </details>
                )}
              </div>
              );
            })()}
          </section>
        );
      })}
    </div>
  );
}

/* Bản chữ đầy đủ, gấp. Tài liệu của gate đang mở đã nằm sẵn trong data.docs; tài liệu khác nạp khi mở. */
function FullText({ path, lines, data, open, innerRef }) {
  const have = ((data && data.docs) || {})[path];
  const [md, setMd] = React.useState(have ? have.markdown : null);
  const [err, setErr] = React.useState('');
  const load = () => {
    if (md !== null || err) return;
    const token = new URLSearchParams(location.search).get('token') || '';
    fetch('/doc?path=' + encodeURIComponent(path) + '&token=' + encodeURIComponent(token))
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(j => setMd(j.markdown))
      .catch(() => setErr('Không đọc được bản chữ — tower đang mở dạng file tĩnh? Chạy /ai-dlc:dlc-tower serve.'));
  };
  React.useEffect(() => { if (open) load(); }, [open]);
  return (
    <details ref={innerRef} open={open || undefined} onToggle={e => { if (e.target.open) load(); }}
      style={{ borderTop: '1px solid var(--line)', paddingTop: 12 }}>
      <summary style={{ cursor: 'pointer', fontSize: 13.5, color: 'var(--muted)' }}>
        Bản chữ đầy đủ — bản cho AI và để tra cứu ({lines} dòng)
      </summary>
      <div style={{ marginTop: 14 }}>
        {err && <div style={{ color: 'var(--danger)', fontSize: 13 }}>{err}</div>}
        {md !== null && window.Markdown && <window.Markdown text={md} />}
        {md === null && !err && <div style={{ color: 'var(--muted)', fontSize: 13 }}>Đang nạp…</div>}
      </div>
    </details>
  );
}

/* Mở trang mô hình như một lớp phủ — từ nút "Xem mô hình" trên thẻ AI đã tự quyết. */
function ModelViewer({ model, data, onClose, onNav, actions, focusId }) {
  if (!model) return null;
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 40, background: 'rgba(8,12,16,0.72)',
      display: 'flex', justifyContent: 'center', padding: '3vh 3vw'
    }} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        width: 'min(1120px,100%)', display: 'flex', flexDirection: 'column', background: 'var(--bg)',
        border: '1px solid var(--line)', borderRadius: 'var(--radius-xl)', overflow: 'hidden', boxShadow: 'var(--shadow-overlay)'
      }}>
        <header style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', background: 'var(--surface)', borderBottom: '1px solid var(--line)' }}>
          <span style={{ ...LBL, color: 'var(--ink)' }}>Mô hình · {model.docName}</span>
          <span style={{ marginLeft: 'auto' }} />
          <button onClick={onClose} style={{
            background: 'transparent', border: '1px solid var(--line)', borderRadius: 'var(--radius-sm)',
            color: 'var(--muted)', cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 12, padding: '4px 9px'
          }}>✕ đóng</button>
        </header>
        <div style={{ overflow: 'auto', padding: '20px 28px 48px', display: 'flex', flexDirection: 'column', gap: 22 }}>
          <ModelPage model={model} data={data} actions={actions} focusId={focusId}
            onNav={t => { onClose(); if (onNav) onNav(t); }} />
          <FullText path={model.doc} lines={model.lines} data={data} open={!!model.error} />
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ModelPage, ModelViewer, FullText, modelOf, modelOfDoc });
})();
