(function(){
const NSli = window.ControlTowerDesignSystem_68131c;
const { Button, Chip } = NSli;

/* Cần tôi quyết — màn mặc định của Lead (docs/control-tower-lead-view.md §2).
   Chỉ chứa thẻ cần NGƯỜI hành động. Không panel agent/HOF/feed/KPI nào được lên đây,
   kể cả dạng tóm tắt — mọi "tóm tắt nhỏ" đều lớn dần. Muốn xem đội AI → Tra cứu.

   Mỗi thẻ bắt buộc năm phần: câu hỏi một dòng bằng lời · "nếu bạn im lặng" + hạn ·
   phương án (khi có) · nút quyết ngay trên thẻ · Xem thêm ▸ mở đúng MỘT artefact.

   Trả lời ngay trên thẻ (6.1.0): câu hỏi → ô nhập → POST /answer → inbox/answer-*.json;
   escalation → ô "chỉ đạo" → inbox/direction-*.json. Phiên Claude Code áp nguyên văn vào hồ sơ
   (protocol §5) rồi làm tiếp — Lead không phải quay về terminal. */

/* Gate A–G của 6.x đọc lại bằng lời. 6.x vẫn chặn cứng ở mọi gate nên "nếu bạn im lặng"
   luôn là "đội đang đứng" — v2 (7.0.0) mới có mặc định theo Mốc chờ. */
const GATE_WORDS = {
  A: { q: 'Đích của yêu cầu này đúng chưa?', kind: 'Chờ bạn ký', mark: '■' },
  B: { q: 'Đội hiểu hệ thống hiện tại đúng chưa?', kind: 'Chờ bạn ký', mark: '■' },
  C: { q: 'Chốt các câu hỏi nghiệp vụ còn mở', kind: 'Chờ bạn ký', mark: '■' },
  D: { q: 'Cách chia phần việc và thứ tự làm — chốt chưa?', kind: 'Chờ bạn ký', mark: '■' },
  E: { q: 'Xem thử vòng xây này — ổn để đi tiếp chưa?', kind: 'Bạn xem thử được', mark: '◉' },
  F: { q: 'Ký phát hành?', kind: 'Chờ bạn ký phát hành', mark: '■' },
  G: { q: 'Bài học rút ra — duyệt để thành luật?', kind: 'Chờ bạn ký', mark: '■' }
};
const OQ_FILE = { business: 'open-questions-business.md', tech: 'open-questions-tech.md', legacy: 'open-questions.md' };
const GATE_RANK = { F: 0, E: 3 };            // F trước hết (chốt chặn thật), E sau các gate khác (xem thử)
const OPEN_Q = q => !/closed|đã chốt|da chot|đóng|descoped/i.test(q.status || '');
const plainTxt = s => String(s || '').replace(/`/g, '');

function intentName(data, id) {
  const i = (data.intents || []).find(x => x.id === id);
  return i ? (window.plainName ? window.plainName(i.name) : i.name) : id;
}
const noOwner = s => !s || /^[\s\-—–]*$/.test(s) || /^unassigned/i.test(s);
const hasDefault = fb => fb && !/^[-—?\s]*$/.test(fb);

/* Việc đã gửi từ tower mà phiên Claude Code chưa áp (file còn trong inbox/). Không hỏi lại. */
function pendingKeys(data) {
  const s = new Set();
  (data.inboxPending || []).forEach(p => {
    if (p.kind === 'answer') s.add('q:' + p.intent + ':' + p.code);
    if (p.kind === 'direction') s.add('esc:' + p.esc);
    if (p.kind === 'steer' && p.dec) s.add('steer:' + p.dec);
  });
  return s;
}
const svgOf = data => (data && data.svg) || {};
const treeOf = (data, iid, code) => (code && (svgOf(data).questions || {})[iid + ':' + code]) || null;

/* Quyết định AI đã tự ghi mà CHƯA bị đảo (6.4.0, protocol §2.3). Mới nhất lên trước.
   Không nằm trong buildInbox: đây là việc bạn ĐƯỢC làm, không phải việc đang chờ bạn — không cộng vào
   con số "N việc đang chờ bạn" ở sidebar. */
function autoDecisions(data) {
  const pend = pendingKeys(data);
  return ((data.autopilot || {}).decisions || [])
    .filter(d => !d.reversedBy && !d.steer && !pend.has('steer:' + d.id))
    .slice().reverse();
}

/* Dựng danh sách thẻ từ state 6.x. Thứ tự theo spec: ký phát hành → đang đứng (escalation)
   → gate khác → xem thử (E) → câu hỏi chặn → phát hiện low → câu hỏi không chặn (gom). */
function buildInbox(data, gates) {
  const cards = [];
  const pend = pendingKeys(data);
  (gates || []).forEach(g => {
    const w = GATE_WORDS[g.gate] || { q: g.title, kind: 'Chờ bạn ký', mark: '■' };
    /* Gate mở vì autopilot BLOCK (status.md `blocked_by`): thẻ đỏ, đứng trên cùng, lý do lên đầu. */
    const blocked = !!g.blockedBy;
    cards.push({
      id: g.key, type: 'gate', blocked, blockedBy: g.blockedBy,
      rank: blocked ? -1 : (GATE_RANK[g.gate] !== undefined ? GATE_RANK[g.gate] : 2),
      mark: blocked ? '■' : w.mark, kind: blocked ? 'Đang đứng — cần bạn' : w.kind,
      intent: g.target, intentName: intentName(data, g.target),
      flow: (svgOf(data).flowByIntent || {})[g.target],
      q: w.q, brief: g.brief,
      silent: blocked
        ? 'Không có mặc định — AI đã dừng vì không tự quyết được. Việc không phụ thuộc gate này vẫn chạy'
        : 'Đội đang đứng chờ — gate này chưa có mặc định (luật 6.x)',
      options: g.options || [], recommendation: g.recommendation, blockers: g.blockers || [],
      pendingRevision: g.pendingRevision, more: g.doc, moreLabel: g.docTitle || g.doc, gate: g
    });
  });
  /* Escalation mức high/medium hoặc chạm phạm vi đứng trên câu hỏi chặn; mức low xuống dưới —
     12 phát hiện `low` chưa ai nhận không được che mất 5 câu đang chặn việc. */
  (data.escalations || []).filter(e => e.status === 'open' && !pend.has('esc:' + e.id)).forEach(e => {
    const lvl = e.level || e.severity || '';
    const hot = /^(cao|vừa)$|high|critical|medium/i.test(lvl) || (e.scopeImpact && e.scopeImpact !== 'none');
    /* `found_in` thường là mã HOF, không phải yêu cầu — generator đã lần ra INT (`e.intent`). Thẻ mang mã
       của CHÍNH nó (ESC-NNN); trước đây chỗ này hiện "HOF-0001" như thể đó là tên yêu cầu. */
    const ev = (svgOf(data).escalations || {})[e.id];
    cards.push({
      id: e.id, type: 'esc', rank: hot ? 1 : 4.5, mark: '■', kind: hot ? 'Đang đứng — cần bạn' : 'Phát hiện chưa ai nhận',
      intent: e.intent || '', intentName: e.intent ? intentName(data, e.intent) : '', code: e.id,
      tree: ev && ev.svg ? ev : null, treeNote: ev && (ev.error || (ev.stale ? 'Mô hình của thẻ này vẽ từ bản chữ cũ — đọc bản chữ trước khi chỉ đạo.' : '')),
      q: plainTxt(e.title || 'Phát hiện ngoài phạm vi, chưa ai nhận'),
      brief: [e.where && ('Ở: ' + e.where), lvl && ('Mức: ' + lvl),
              e.scopeImpact && e.scopeImpact !== 'none' && ('Ảnh hưởng phạm vi: ' + e.scopeImpact)].filter(Boolean).join(' · '),
      silent: noOwner(e.owner) ? 'Chưa ai nhận — phát hiện này nằm im cho tới khi có chủ' : 'Đã có người nhận (' + e.owner + ') — vẫn mở, chưa chốt',
      options: [], more: e.path, moreLabel: e.id, esc: e
    });
  });
  /* Câu hỏi: chỉ câu ĐANG CHẶN việc mới đứng riêng một thẻ. Câu không chặn gom một thẻ mỗi yêu cầu —
     ca thật PILOT có 38 câu mở / 5 chặn; 33 thẻ "cần bạn" cho thứ không chặn ai là loạn theo kiểu mới. */
  Object.entries(data.questionsByIntent || {}).forEach(([iid, qs]) => {
    const open = (qs || []).filter(q => OPEN_Q(q) && !pend.has('q:' + iid + ':' + q.code));
    const file = aud => 'context-memory/intents/' + iid + '/' + (OQ_FILE[aud] || OQ_FILE.legacy);
    open.filter(q => q.blocking).forEach(q => {
      const fb = (q.fallback || '').trim();
      cards.push({
        id: iid + ':' + (q.code || q.q.slice(0, 30)), type: 'q', rank: 4,
        mark: '?', kind: 'Câu hỏi đang chặn việc',
        intent: iid, intentName: intentName(data, iid),
        q: plainTxt(q.q),
        brief: [q.who && ('Ai trả lời: ' + q.who), q.due && ('Hạn: ' + q.due), q.impact].filter(Boolean).join(' · '),
        silent: hasDefault(fb) ? fb : 'Chưa ghi mặc định — việc này đứng tới khi có câu trả lời',
        options: [], code: q.code, audience: q.audience, question: q, file: file(q.audience),
        tree: treeOf(data, iid, q.code),
        more: file(q.audience), moreLabel: q.code || 'danh sách câu hỏi'
      });
    });
    /* Nên nhìn sớm (protocol §4.10.14): câu KHÔNG chặn ai nhưng trả lời nó thì ≥ 2 câu khác tự hết mở.
       Áp mặc định cho nó là bỏ qua cách rẻ nhất để bớt giả định — nên nó đứng riêng, ngay dưới nhóm đỏ. */
    const unlocksOf = q => ((treeOf(data, iid, q.code) || {}).unlocks || []);
    const untilOf = q => (treeOf(data, iid, q.code) || {}).silentUntil || '';
    open.filter(q => !q.blocking && unlocksOf(q).length >= 2).forEach(q => {
      const fb = (q.fallback || '').trim();
      cards.push({
        id: iid + ':' + q.code, type: 'q', early: true, rank: 4.2, mark: '◇', kind: 'Nên nhìn sớm',
        intent: iid, intentName: intentName(data, iid),
        q: 'Trả lời 1 câu, gỡ ' + unlocksOf(q).length + ' câu: ' + plainTxt(q.q),
        brief: ['Gỡ được: ' + unlocksOf(q).join(', '), q.who && ('Ai trả lời: ' + q.who), q.due && ('Hạn: ' + q.due)].filter(Boolean).join(' · '),
        silent: hasDefault(fb) ? fb : 'Chưa ghi mặc định',
        options: [], code: q.code, audience: q.audience, question: q, file: file(q.audience),
        tree: treeOf(data, iid, q.code),
        more: file(q.audience), moreLabel: q.code
      });
    });
    /* Mặc định mang HẠN ĐẢO (§4.10.16) lên đầu danh sách: qua mốc đó thì đảo thành đắt. */
    const rest = open.filter(q => !q.blocking && unlocksOf(q).length < 2)
      .map((q, i) => ({ q, i, u: untilOf(q) }))
      .sort((a, b) => (a.u ? 0 : 1) - (b.u ? 0 : 1) || a.i - b.i)
      .map(x => x.u ? Object.assign({}, x.q, { until: x.u }) : x.q);
    if (rest.length) {
      const auds = Array.from(new Set(rest.map(q => q.audience)));
      cards.push({
        id: iid + ':rest', type: 'qgroup', rank: 5, mark: '?', kind: 'Câu hỏi chưa chốt — không chặn ai',
        intent: iid, intentName: intentName(data, iid),
        q: rest.length + ' câu hỏi còn mở' + (rest.length > 1 ? ', đội đang đi tiếp bằng phương án chọn sẵn' : ''),
        brief: '', silent: 'Đội giữ phương án chọn sẵn; bạn chốt lúc nào cũng được, không gấp',
        options: [], questions: rest, fileOf: file, treeOf: q => treeOf(data, iid, q.code),
        more: file(auds[0]), moreLabel: 'danh sách câu hỏi'
      });
    }
  });
  /* Cùng tầng "Nên nhìn sớm", nguồn thứ hai: điểm cần chốt trong trang mô hình có `unlocks` ≥ 2. */
  Object.entries(data.humanView || {}).forEach(([iid, hv]) => {
    const m = hv.docs[hv.primary];
    if (!m || m.error || m.stale) return;
    (m.early || []).forEach(id => {
      const d = (m.decisions || []).find(x => x.id === id);
      if (!d || !d.svg) return;
      cards.push({
        id: iid + ':hv:' + d.id, type: 'early', early: true, rank: 4.2, mark: '◇', kind: 'Nên nhìn sớm',
        intent: iid, intentName: intentName(data, iid),
        q: 'Trả lời 1 câu, gỡ ' + d.unlocks.length + ' câu: ' + plainTxt(d.question),
        brief: 'Gỡ được: ' + d.unlocks.join(', '), svg: d.svg, decision: d.id, modelDoc: m.doc,
        silent: d.default ? 'AI áp phương án ' + d.default + (d.defaultUntil ? ' — đảo rẻ tới: ' + d.defaultUntil : '') : 'Chưa có mặc định — đội đang đứng',
        options: [], more: m.doc, moreLabel: m.docName
      });
    });
  });
  return cards.sort((a, b) => a.rank - b.rank);
}

const KIND_COLOR = { gate: 'var(--accent)', esc: 'var(--danger)', q: 'var(--blue)', qgroup: 'var(--blue)', early: 'var(--accent)' };
const KIND_BG = { gate: 'var(--accent-bg)', esc: 'var(--danger-bg)', q: 'var(--blue-bg)', qgroup: 'var(--blue-bg)', early: 'var(--accent-bg)' };
const LABEL = { fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' };

/* Ô trả lời — gửi là xong, không chuyển màn. `defaultText` có thì thêm nút "Dùng mặc định". */
function AnswerBox({ placeholder, defaultText, sendLabel, onSend, preset }) {
  const [v, setV] = React.useState('');
  const [busy, setBusy] = React.useState(false);
  /* Bấm một nhánh trên cây lựa chọn ⇒ điền sẵn phương án đó; người vẫn sửa được trước khi gửi. */
  React.useEffect(() => { if (preset && preset.text) setV(preset.text); }, [preset]);
  const send = (text, usedDefault) => {
    if (!text || busy) return;
    setBusy(true);
    Promise.resolve(onSend(text, !!usedDefault)).finally(() => setBusy(false));
  };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <textarea value={v} onChange={e => setV(e.target.value)} rows={2} placeholder={placeholder}
        onKeyDown={e => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') send(v.trim()); }}
        style={{
          width: '100%', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'var(--sans)', fontSize: 13.5,
          padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--line)',
          background: 'var(--surface)', color: 'var(--ink)', lineHeight: 1.5
        }} />
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <Button variant="primary" onClick={() => send(v.trim())} disabled={!v.trim() || busy}>{busy ? 'Đang gửi…' : sendLabel}</Button>
        {defaultText && <Button variant="secondary" onClick={() => send(defaultText, true)} disabled={busy}>Dùng mặc định</Button>}
        <span style={{ fontSize: 11.5, color: 'var(--muted)' }}>⌘/Ctrl + Enter để gửi</span>
      </div>
    </div>
  );
}

/* Cây lựa chọn của một câu hỏi + chữ đầy đủ gấp bên dưới. Bấm nhánh ⇒ `onPick(nhãn phương án)`. */
function QuestionTree({ tree, q, silent, brief, onPick }) {
  const pick = target => {
    if (String(target).indexOf('pick:') !== 0) return;
    const o = (tree.options || []).find(x => x.key === target.slice(5));
    if (o) onPick(o.label);
  };
  const line = (label, text) => text ? (
    <div><span style={LABEL}>{label} · </span><span style={{ color: 'var(--muted)' }}>{plainTxt(text)}</span></div>
  ) : null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <window.SvgFigure svg={tree.svg} onNav={pick} />
      <details style={{ fontSize: 13, lineHeight: 1.55 }}>
        <summary style={{ cursor: 'pointer', color: 'var(--muted)', fontSize: 12.5 }}>Chữ đầy đủ</summary>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 6, maxWidth: '72ch' }}>
          {brief && <div>{brief}</div>}
          {line('Bối cảnh', tree.context)}
          {(tree.options || []).map(o => <React.Fragment key={o.key}>{line(o.label, o.cost ? 'giá: ' + o.cost : '')}</React.Fragment>)}
          {line('AI đề xuất', tree.recommendWhy)}
          {line('Nếu bạn im lặng', tree.silentText || silent)}
          {line('Đã soát mà không thấy đáp án', tree.checked)}
        </div>
      </details>
    </div>
  );
}

function Card({ c, onOpenGate, onDoc, onAnswer, onSent, onNav, onModel }) {
  const color = c.blocked ? 'var(--danger)' : c.mark === '◉' ? 'var(--ok)' : c.early ? KIND_COLOR.early : KIND_COLOR[c.type];
  const bg = c.blocked ? 'var(--danger-bg)' : c.mark === '◉' ? 'var(--ok-bg)' : c.early ? KIND_BG.early : KIND_BG[c.type];
  const [preset, setPreset] = React.useState(null);    // phương án vừa bấm trên cây lựa chọn
  const pickInto = text => setPreset({ text, n: Date.now() });
  const [openQ, setOpenQ] = React.useState(null);      // thẻ gom: câu nào đang mở ô trả lời
  const [doneQ, setDoneQ] = React.useState([]);        // câu đã gửi trong thẻ gom (ẩn ngay, chờ state mới)

  /* Khoá gửi trùng với khoá của inboxPending (pendingKeys) — để khi /state về, cùng một việc không bị
     đếm hai lần (một lần local, một lần từ inbox/). */
  const sendAnswer = (q, file) => (text, usedDefault) => onAnswer({
    kind: 'answer', intent: c.intent, code: q.code || '', audience: q.audience || '', file: file.split('/').pop(),
    question: q.q, answer: text, used_default: usedDefault, blocking: !!q.blocking
  }).then(ok => { if (ok) { setDoneQ(d => d.concat(q.code || q.q)); onSent('q:' + c.intent + ':' + (q.code || '')); } return ok; });
  const sendDirection = (text) => onAnswer({
    kind: 'direction', intent: c.intent || c.esc.foundIn || '', esc: c.esc.id, title: c.q, answer: text
  }).then(ok => { if (ok) onSent('esc:' + c.esc.id); return ok; });

  const restQ = c.type === 'qgroup' ? c.questions.filter(q => !doneQ.includes(q.code || q.q)) : [];
  if (c.type === 'qgroup' && restQ.length === 0) return null;

  return (
    <article id={'card-' + c.id} style={{
      border: (c.blocked ? '2px' : '1px') + ' solid ' + color, background: bg, borderRadius: 'var(--radius-md)',
      padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10, maxWidth: c.flow ? 1000 : 760
    }}>
      {c.blocked && (
        <div style={{ fontSize: 14.5, fontWeight: 650, color: 'var(--danger)', lineHeight: 1.45 }}>
          <span style={{ ...LABEL, color: 'var(--danger)' }}>Vì sao đứng · </span>{plainTxt(c.blockedBy)}
        </div>
      )}
      <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', color, fontSize: 13 }}>{c.mark}</span>
        <span style={{ ...LABEL, color }}>{c.kind}</span>
        <span style={{ fontSize: 12.5, color: 'var(--muted)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
          title={c.intent}>{c.intentName}</span>
        {c.type === 'esc' && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', flex: 'none' }}>{c.code}</span>}
        {c.pendingRevision && <Chip tone="active">đang chờ bản sửa</Chip>}
      </div>

      <div style={{ fontSize: 16, fontWeight: 650, letterSpacing: '-0.01em', lineHeight: 1.35 }}>
        {c.type === 'qgroup' ? restQ.length + ' câu hỏi còn mở' + (restQ.length > 1 ? ', đội đang đi tiếp bằng phương án chọn sẵn' : '') : c.q}
      </div>
      {c.flow && <window.SvgFigure svg={c.flow} onNav={onNav} />}
      {c.type === 'early' && (
        <window.SvgFigure svg={c.svg} onNav={() => onModel && onModel(c.intent, c.modelDoc, c.decision)} />
      )}
      {c.tree
        ? <QuestionTree tree={c.tree} q={c.question} brief={c.brief} silent={c.silent} onPick={pickInto} />
        : <>
            {c.brief && <div style={{ fontSize: 13.5, color: 'var(--ink)', lineHeight: 1.55, maxWidth: '68ch' }}>{c.brief}</div>}
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>
              <span style={LABEL}>Nếu bạn im lặng · </span>
              <span style={{ color: 'var(--muted)' }}>{c.silent}</span>
            </div>
          </>}

      {(c.options || []).length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <span style={LABEL}>Phương án</span>
          {c.options.map((o, i) => {
            const rec = c.recommendation && c.recommendation.indexOf(o.slice(0, 24)) >= 0;
            return (
              <div key={i} style={{ display: 'flex', gap: 8, fontSize: 13.5, lineHeight: 1.5 }}>
                <span style={{ fontFamily: 'var(--mono)', color: rec ? color : 'var(--muted)', flex: 'none' }}>{rec ? '●' : '○'}</span>
                <span>{o}{rec ? <span style={{ color: 'var(--muted)' }}> — đội đề xuất</span> : null}</span>
              </div>
            );
          })}
        </div>
      )}
      {(c.blockers || []).length > 0 && (
        <div style={{ fontSize: 12.5, color: 'var(--danger)' }}>
          {c.blockers.length} điều kiện chưa đạt — đội phải xử lý trước khi bạn ký (xem trong hồ sơ)
        </div>
      )}

      {/* Trả lời ngay trên thẻ */}
      {c.type === 'q' && (
        <AnswerBox placeholder="Câu trả lời của bạn — viết bằng lời, đội sẽ áp nguyên văn vào hồ sơ"
          defaultText={hasDefault((c.question.fallback || '').trim()) ? c.question.fallback.trim() : null}
          preset={preset} sendLabel="Gửi câu trả lời →" onSend={sendAnswer(c.question, c.file)} />
      )}
      {c.type === 'esc' && c.treeNote && <div style={{ fontSize: 12.5, color: 'var(--danger)' }}>{c.treeNote}</div>}
      {c.type === 'esc' && (
        <AnswerBox placeholder="Chỉ đạo: ai nhận · làm gì · hay bỏ qua vì sao"
          preset={preset} sendLabel="Gửi chỉ đạo →" onSend={sendDirection} />
      )}
      {c.type === 'qgroup' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {restQ.map(q => {
            const k = q.code || q.q;
            const on = openQ === k;
            return (
              <div key={k} style={{ borderTop: '1px solid var(--line)', paddingTop: 6 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', flex: 'none' }}>{q.code || '·'}</span>
                  <span style={{ fontSize: 13.5, flex: 1, lineHeight: 1.45 }}>{plainTxt(q.q)}</span>
                  <button onClick={() => { setPreset(null); setOpenQ(on ? null : k); }} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--blue)', fontSize: 12.5, flex: 'none' }}>
                    {on ? 'đóng ▴' : 'trả lời ▸'}
                  </button>
                </div>
                {hasDefault((q.fallback || '').trim()) && !on && (
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
                    mặc định: {q.fallback.trim()}
                    {q.until && <span style={{ color: 'var(--accent)', fontWeight: 650 }}> · đảo rẻ tới: {plainTxt(q.until)}</span>}
                  </div>
                )}
                {on && (
                  <div style={{ marginTop: 6, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {c.treeOf(q) && <QuestionTree tree={c.treeOf(q)} q={q} silent={q.fallback} onPick={pickInto} />}
                    <AnswerBox placeholder="Câu trả lời của bạn" sendLabel="Gửi câu trả lời →"
                      defaultText={hasDefault((q.fallback || '').trim()) ? q.fallback.trim() : null}
                      preset={preset} onSend={sendAnswer(q, c.fileOf(q.audience))} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginTop: 2 }}>
        {c.type === 'gate' && <Button variant="primary" onClick={() => onOpenGate(c.gate)}>Đọc hồ sơ &amp; quyết →</Button>}
        {c.type === 'early' && onModel && <Button variant="primary" onClick={() => onModel(c.intent, c.modelDoc, c.decision)}>Chọn trong trang mô hình →</Button>}
        {c.more && (
          <button onClick={() => onDoc(c.more)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, fontSize: 12.5, color: 'var(--muted)' }}>
            Xem thêm ▸ <span style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>{(c.moreLabel || '').toString().split('/').pop()}</span>
          </button>
        )}
      </div>
    </article>
  );
}

/* Thẻ "AI đã tự quyết" — một quyết định autopilot, hình hai cột Chọn/Bỏ, nút Đảo hai nhịp
   (bấm Đảo → viết đổi sang gì → gửi) để không ai đảo nhầm bằng một cú bấm. */
function AutoCard({ d, data, onDoc, onNav, onSteer, onSent, onModel }) {
  const [open, setOpen] = React.useState(false);
  const [note, setNote] = React.useState('');
  const [busy, setBusy] = React.useState(false);
  const first = (d.rejected || [])[0];
  const start = () => { setNote(first && first.option ? 'Đảo sang: ' + first.option : ''); setOpen(true); };
  const send = () => {
    if (!note.trim() || busy) return;
    setBusy(true);
    Promise.resolve(onSteer({ dec: d.id, intent: d.intent, note: note.trim() }))
      .then(ok => { if (ok) onSent('steer:' + d.id); })
      .finally(() => setBusy(false));
  };
  const line = (label, text) => text ? (
    <div><span style={LABEL}>{label} · </span><span style={{ color: 'var(--muted)' }}>{plainTxt(text)}</span></div>
  ) : null;
  return (
    <article id={'card-' + d.id} style={{
      border: '1px dashed var(--ok)', background: 'var(--ok-bg)', borderRadius: 'var(--radius-md)',
      padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10, maxWidth: 760
    }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', color: 'var(--ok)', fontSize: 13 }}>◇</span>
        <span style={{ ...LABEL, color: 'var(--ok)' }}>AI đã tự quyết</span>
        <span style={{ fontSize: 12.5, color: 'var(--muted)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
          title={d.intent}>{intentName(data, d.intent)}</span>
        {d.reason && <Chip tone="active">{/silent/i.test(d.reason) ? 'hết hạn chờ, không ai trả lời' : d.reason}</Chip>}
      </div>
      <div style={{ fontSize: 16, fontWeight: 650, letterSpacing: '-0.01em', lineHeight: 1.35 }}>{plainTxt(d.what) || d.id}</div>
      <window.SvgFigure svg={d.svg} onNav={onNav} />
      {(d.missing || []).length > 0 && (
        <div style={{ fontSize: 12.5, color: 'var(--danger)' }}>
          Quyết định này ghi thiếu {d.missing.length} dòng bắt buộc — đội phải bổ sung (xem trong hồ sơ)
        </div>
      )}
      <details style={{ fontSize: 13, lineHeight: 1.55 }}>
        <summary style={{ cursor: 'pointer', color: 'var(--muted)', fontSize: 12.5 }}>Chữ đầy đủ</summary>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 6, maxWidth: '72ch' }}>
          {line('Chọn', d.chosen + (d.chosenCost ? ' — giá: ' + d.chosenCost : ''))}
          {(d.rejected || []).map((r, i) => <React.Fragment key={i}>{line('Bỏ', r.option + (r.why ? ' — vì: ' + r.why : ''))}</React.Fragment>)}
          {line('Đảo bằng', d.undo)}
          {line('Ảnh hưởng', d.impact)}
          {line('Căn cứ', d.basis)}
          {line('Kiểm điều kiện dừng', d.blockCheck)}
        </div>
      </details>
      {open && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <textarea value={note} onChange={e => setNote(e.target.value)} rows={2} autoFocus
            placeholder="Đổi sang gì, vì sao — đội làm lại đúng theo lời này"
            onKeyDown={e => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') send(); }}
            style={{
              width: '100%', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'var(--sans)', fontSize: 13.5,
              padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--line)',
              background: 'var(--surface)', color: 'var(--ink)', lineHeight: 1.5
            }} />
          {d.undo && <div style={{ fontSize: 12, color: 'var(--muted)' }}>Cái giá của việc đảo: {plainTxt(d.undo)}</div>}
        </div>
      )}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginTop: 2 }}>
        {open
          ? <>
              <Button variant="primary" onClick={send} disabled={!note.trim() || busy}>{busy ? 'Đang gửi…' : 'Gửi yêu cầu đảo →'}</Button>
              <Button variant="secondary" onClick={() => setOpen(false)} disabled={busy}>Thôi, giữ nguyên</Button>
            </>
          : <Button variant="secondary" onClick={start}>Đảo</Button>}
        {!open && d.modelDoc && onModel && (
          <Button variant="secondary" onClick={() => onModel(d.intent, d.modelDoc)}>Xem mô hình</Button>
        )}
        <button onClick={() => onDoc('context-memory/governance/decisions-log.md')} style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, fontSize: 12.5, color: 'var(--muted)' }}>
          Xem thêm ▸ <span style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>{d.id}</span>
        </button>
      </div>
    </article>
  );
}

function LeadInbox({ data, gates, onOpenGate, onDoc, onAnswer, onBrief, onNav, onSteer, focus, onModel }) {
  const [sent, setSent] = React.useState([]);     // khoá việc vừa gửi — ẩn ngay, không đợi /state 5 giây
  const autos = React.useMemo(() => autoDecisions(data).filter(d => !sent.includes('steer:' + d.id)), [data, sent]);
  const [allAuto, setAllAuto] = React.useState(false);
  const AUTO_LIMIT = 3;
  /* Bấm một gate "tự quyết" trên sơ đồ ⇒ mở đủ nhóm rồi cuộn tới đúng thẻ của DEC đó. */
  React.useEffect(() => {
    if (!focus || !focus.id) return;
    setAllAuto(true);
    const h = setTimeout(() => {
      const el = document.getElementById('card-' + focus.id);
      if (el && el.scrollIntoView) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 60);
    return () => clearTimeout(h);
  }, [focus]);
  const autoGroup = autos.length > 0 && (
    <section style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
      <div>
        <div style={{ ...LABEL, color: 'var(--ok)' }}>AI đã tự quyết — đảo nếu cần</div>
        <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 3 }}>
          {autos.length} quyết định đội đã tự chốt và đi tiếp. Đồng ý thì không cần làm gì.
        </div>
      </div>
      {(allAuto ? autos : autos.slice(0, AUTO_LIMIT)).map(d => <AutoCard key={d.id} d={d} data={data} onDoc={onDoc}
        onNav={onNav} onSteer={onSteer} onModel={onModel} onSent={id => setSent(s => s.concat(id))} />)}
      {autos.length > AUTO_LIMIT && (
        <button onClick={() => setAllAuto(a => !a)} style={{
          alignSelf: 'flex-start', background: 'transparent', border: '1px solid var(--line)',
          borderRadius: 'var(--radius-sm)', padding: '7px 12px', cursor: 'pointer', color: 'var(--muted)', fontSize: 13
        }}>{allAuto ? 'thu gọn ▴' : 'và ' + (autos.length - AUTO_LIMIT) + ' quyết định khác ▸'}</button>
      )}
    </section>
  );
  const keyOf = c => c.type === 'esc' ? 'esc:' + c.esc.id : c.type === 'q' ? 'q:' + c.intent + ':' + (c.code || '') : null;
  const cards = React.useMemo(() => buildInbox(data, gates).filter(c => !sent.includes(keyOf(c))), [data, gates, sent]);
  const [all, setAll] = React.useState(false);
  const LIMIT = 7;
  const shown = all ? cards : cards.slice(0, LIMIT);
  const rest = cards.length - shown.length;
  const pending = new Set([...pendingKeys(data), ...sent]).size
    + (data.inboxPending || []).filter(p => p.kind !== 'answer' && p.kind !== 'direction' && p.kind !== 'steer').length;
  const pendingLine = pending > 0 && (
    <div style={{ fontSize: 12.5, color: 'var(--muted)', padding: '4px 0' }}>
      {pending} việc bạn đã gửi đang chờ phiên Claude Code áp vào hồ sơ — phiên đang chạy bắt ngay;
      phiên đã đóng thì mở lại bằng <code style={{ fontFamily: 'var(--mono)' }}>/ai-dlc:dlc-resume</code>.
    </div>
  );

  if (cards.length === 0 && autos.length > 0) {
    return (
      <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ fontSize: 14.5 }}>
          <span style={{ fontFamily: 'var(--mono)', color: 'var(--ok)' }}>● </span>
          <b>Không có gì cần bạn.</b>
          <span style={{ color: 'var(--muted)' }}> Đội đang làm việc. </span>
          <span onClick={onBrief} style={{ color: 'var(--blue)', cursor: 'pointer' }}>Bản tin hôm nay ▸</span>
        </div>
        {pendingLine}
        {autoGroup}
      </div>
    );
  }
  if (cards.length === 0) {
    return (
      <div style={{ padding: '72px 24px', textAlign: 'center' }}>
        <style>{'@keyframes ct-breathe{0%,100%{opacity:.45}50%{opacity:1}}'}</style>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 22, color: 'var(--ok)', animation: 'ct-breathe 1600ms ease-in-out infinite' }}>●</div>
        <div style={{ marginTop: 10, fontSize: 16, fontWeight: 600 }}>Không có gì cần bạn.</div>
        <div style={{ marginTop: 4, fontSize: 13.5, color: 'var(--muted)' }}>
          Đội đang làm việc. <span onClick={onBrief} style={{ color: 'var(--blue)', cursor: 'pointer' }}>Bản tin hôm nay ▸</span>
        </div>
        <div style={{ marginTop: 16, display: 'inline-block', textAlign: 'left' }}>{pendingLine}</div>
      </div>
    );
  }
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
      {pendingLine}
      {shown.map(c => <Card key={c.id} c={c} onOpenGate={onOpenGate} onDoc={onDoc} onAnswer={onAnswer}
        onNav={onNav} onModel={onModel} onSent={id => setSent(s => s.concat(id))} />)}
      {rest > 0 && (
        <button onClick={() => setAll(true)} style={{
          alignSelf: 'flex-start', background: 'transparent', border: '1px solid var(--line)',
          borderRadius: 'var(--radius-sm)', padding: '7px 12px', cursor: 'pointer', color: 'var(--muted)', fontSize: 13
        }}>và {rest} việc khác ▸</button>
      )}
      {all && cards.length > LIMIT && (
        <button onClick={() => setAll(false)} style={{ alignSelf: 'flex-start', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: 12.5 }}>thu gọn ▴</button>
      )}
      {autoGroup}
    </div>
  );
}

Object.assign(window, { LeadInbox, buildInbox, autoDecisions, AnswerBox });
})();
