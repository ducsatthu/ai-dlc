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
  });
  return s;
}

/* Dựng danh sách thẻ từ state 6.x. Thứ tự theo spec: ký phát hành → đang đứng (escalation)
   → gate khác → xem thử (E) → câu hỏi chặn → phát hiện low → câu hỏi không chặn (gom). */
function buildInbox(data, gates) {
  const cards = [];
  const pend = pendingKeys(data);
  (gates || []).forEach(g => {
    const w = GATE_WORDS[g.gate] || { q: g.title, kind: 'Chờ bạn ký', mark: '■' };
    cards.push({
      id: g.key, type: 'gate', rank: GATE_RANK[g.gate] !== undefined ? GATE_RANK[g.gate] : 2,
      mark: w.mark, kind: w.kind, intent: g.target, intentName: intentName(data, g.target),
      q: w.q, brief: g.brief, silent: 'Đội đang đứng chờ — gate này chưa có mặc định (luật 6.x)',
      options: g.options || [], recommendation: g.recommendation, blockers: g.blockers || [],
      pendingRevision: g.pendingRevision, more: g.doc, moreLabel: g.docTitle || g.doc, gate: g
    });
  });
  /* Escalation mức high/medium hoặc chạm phạm vi đứng trên câu hỏi chặn; mức low xuống dưới —
     12 phát hiện `low` chưa ai nhận không được che mất 5 câu đang chặn việc. */
  (data.escalations || []).filter(e => e.status === 'open' && !pend.has('esc:' + e.id)).forEach(e => {
    const hot = /high|critical|medium/i.test(e.severity || '') || (e.scopeImpact && e.scopeImpact !== 'none');
    cards.push({
      id: e.id, type: 'esc', rank: hot ? 1 : 4.5, mark: '■', kind: hot ? 'Đang đứng — cần bạn' : 'Phát hiện chưa ai nhận',
      intent: e.foundIn, intentName: intentName(data, e.foundIn) || [e.foundIn, e.foundBy].filter(Boolean).join(' · '),
      q: plainTxt(e.title || 'Phát hiện ngoài phạm vi, chưa ai nhận'),
      brief: [e.where && ('Ở: ' + e.where), e.severity && ('Mức: ' + e.severity),
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
        more: file(q.audience), moreLabel: q.code || 'danh sách câu hỏi'
      });
    });
    const rest = open.filter(q => !q.blocking);
    if (rest.length) {
      const auds = Array.from(new Set(rest.map(q => q.audience)));
      cards.push({
        id: iid + ':rest', type: 'qgroup', rank: 5, mark: '?', kind: 'Câu hỏi chưa chốt — không chặn ai',
        intent: iid, intentName: intentName(data, iid),
        q: rest.length + ' câu hỏi còn mở' + (rest.length > 1 ? ', đội đang đi tiếp bằng phương án chọn sẵn' : ''),
        brief: '', silent: 'Đội giữ phương án chọn sẵn; bạn chốt lúc nào cũng được, không gấp',
        options: [], questions: rest, fileOf: file,
        more: file(auds[0]), moreLabel: 'danh sách câu hỏi'
      });
    }
  });
  return cards.sort((a, b) => a.rank - b.rank);
}

const KIND_COLOR = { gate: 'var(--accent)', esc: 'var(--danger)', q: 'var(--blue)', qgroup: 'var(--blue)' };
const KIND_BG = { gate: 'var(--accent-bg)', esc: 'var(--danger-bg)', q: 'var(--blue-bg)', qgroup: 'var(--blue-bg)' };
const LABEL = { fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' };

/* Ô trả lời — gửi là xong, không chuyển màn. `defaultText` có thì thêm nút "Dùng mặc định". */
function AnswerBox({ placeholder, defaultText, sendLabel, onSend }) {
  const [v, setV] = React.useState('');
  const [busy, setBusy] = React.useState(false);
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

function Card({ c, onOpenGate, onDoc, onAnswer, onSent }) {
  const color = c.mark === '◉' ? 'var(--ok)' : KIND_COLOR[c.type];
  const bg = c.mark === '◉' ? 'var(--ok-bg)' : KIND_BG[c.type];
  const [openQ, setOpenQ] = React.useState(null);      // thẻ gom: câu nào đang mở ô trả lời
  const [doneQ, setDoneQ] = React.useState([]);        // câu đã gửi trong thẻ gom (ẩn ngay, chờ state mới)

  /* Khoá gửi trùng với khoá của inboxPending (pendingKeys) — để khi /state về, cùng một việc không bị
     đếm hai lần (một lần local, một lần từ inbox/). */
  const sendAnswer = (q, file) => (text, usedDefault) => onAnswer({
    kind: 'answer', intent: c.intent, code: q.code || '', audience: q.audience || '', file: file.split('/').pop(),
    question: q.q, answer: text, used_default: usedDefault, blocking: !!q.blocking
  }).then(ok => { if (ok) { setDoneQ(d => d.concat(q.code || q.q)); onSent('q:' + c.intent + ':' + (q.code || '')); } return ok; });
  const sendDirection = (text) => onAnswer({
    kind: 'direction', intent: c.intent || '', esc: c.esc.id, title: c.q, answer: text
  }).then(ok => { if (ok) onSent('esc:' + c.esc.id); return ok; });

  const restQ = c.type === 'qgroup' ? c.questions.filter(q => !doneQ.includes(q.code || q.q)) : [];
  if (c.type === 'qgroup' && restQ.length === 0) return null;

  return (
    <article style={{
      border: '1px solid ' + color, background: bg, borderRadius: 'var(--radius-md)',
      padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10, maxWidth: 760
    }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', color, fontSize: 13 }}>{c.mark}</span>
        <span style={{ ...LABEL, color }}>{c.kind}</span>
        <span style={{ fontSize: 12.5, color: 'var(--muted)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
          title={c.intent}>{c.intentName}</span>
        {c.pendingRevision && <Chip tone="active">đang chờ bản sửa</Chip>}
      </div>

      <div style={{ fontSize: 16, fontWeight: 650, letterSpacing: '-0.01em', lineHeight: 1.35 }}>
        {c.type === 'qgroup' ? restQ.length + ' câu hỏi còn mở' + (restQ.length > 1 ? ', đội đang đi tiếp bằng phương án chọn sẵn' : '') : c.q}
      </div>
      {c.brief && <div style={{ fontSize: 13.5, color: 'var(--ink)', lineHeight: 1.55, maxWidth: '68ch' }}>{c.brief}</div>}

      <div style={{ fontSize: 13, lineHeight: 1.5 }}>
        <span style={LABEL}>Nếu bạn im lặng · </span>
        <span style={{ color: 'var(--muted)' }}>{c.silent}</span>
      </div>

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
          sendLabel="Gửi câu trả lời →" onSend={sendAnswer(c.question, c.file)} />
      )}
      {c.type === 'esc' && (
        <AnswerBox placeholder="Chỉ đạo: ai nhận · làm gì · hay bỏ qua vì sao"
          sendLabel="Gửi chỉ đạo →" onSend={sendDirection} />
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
                  <button onClick={() => setOpenQ(on ? null : k)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--blue)', fontSize: 12.5, flex: 'none' }}>
                    {on ? 'đóng ▴' : 'trả lời ▸'}
                  </button>
                </div>
                {hasDefault((q.fallback || '').trim()) && !on && (
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>mặc định: {q.fallback.trim()}</div>
                )}
                {on && (
                  <div style={{ marginTop: 6 }}>
                    <AnswerBox placeholder="Câu trả lời của bạn" sendLabel="Gửi câu trả lời →"
                      defaultText={hasDefault((q.fallback || '').trim()) ? q.fallback.trim() : null}
                      onSend={sendAnswer(q, c.fileOf(q.audience))} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginTop: 2 }}>
        {c.type === 'gate' && <Button variant="primary" onClick={() => onOpenGate(c.gate)}>Đọc hồ sơ &amp; quyết →</Button>}
        {c.more && (
          <button onClick={() => onDoc(c.more)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, fontSize: 12.5, color: 'var(--muted)' }}>
            Xem thêm ▸ <span style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>{(c.moreLabel || '').toString().split('/').pop()}</span>
          </button>
        )}
      </div>
    </article>
  );
}

function LeadInbox({ data, gates, onOpenGate, onDoc, onAnswer, onBrief }) {
  const [sent, setSent] = React.useState([]);     // khoá việc vừa gửi — ẩn ngay, không đợi /state 5 giây
  const keyOf = c => c.type === 'esc' ? 'esc:' + c.esc.id : c.type === 'q' ? 'q:' + c.intent + ':' + (c.code || '') : null;
  const cards = React.useMemo(() => buildInbox(data, gates).filter(c => !sent.includes(keyOf(c))), [data, gates, sent]);
  const [all, setAll] = React.useState(false);
  const LIMIT = 7;
  const shown = all ? cards : cards.slice(0, LIMIT);
  const rest = cards.length - shown.length;
  const pending = new Set([...pendingKeys(data), ...sent]).size
    + (data.inboxPending || []).filter(p => p.kind !== 'answer' && p.kind !== 'direction').length;
  const pendingLine = pending > 0 && (
    <div style={{ fontSize: 12.5, color: 'var(--muted)', padding: '4px 0' }}>
      {pending} việc bạn đã gửi đang chờ phiên Claude Code áp vào hồ sơ — phiên đang chạy bắt ngay;
      phiên đã đóng thì mở lại bằng <code style={{ fontFamily: 'var(--mono)' }}>/ai-dlc:dlc-resume</code>.
    </div>
  );

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
        onSent={id => setSent(s => s.concat(id))} />)}
      {rest > 0 && (
        <button onClick={() => setAll(true)} style={{
          alignSelf: 'flex-start', background: 'transparent', border: '1px solid var(--line)',
          borderRadius: 'var(--radius-sm)', padding: '7px 12px', cursor: 'pointer', color: 'var(--muted)', fontSize: 13
        }}>và {rest} việc khác ▸</button>
      )}
      {all && cards.length > LIMIT && (
        <button onClick={() => setAll(false)} style={{ alignSelf: 'flex-start', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: 12.5 }}>thu gọn ▴</button>
      )}
    </div>
  );
}

Object.assign(window, { LeadInbox, buildInbox });
})();
