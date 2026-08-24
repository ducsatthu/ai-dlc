(function(){
/* Bản tin hôm nay — tầng 1 (docs/control-tower-lead-view.md §1). Một trang, bằng lời, không bảng.
   Trả lời: đội đã làm tới đâu · cái gì sẵn để tôi xem · cái gì cần tôi · đội có ổn không.
   Mọi chi tiết (agent nào, HOF nào, task nào) nằm ở Tra cứu — ở đây chỉ một dòng mỗi ý. */

const PHASE_WORDS = {
  inception: 'đang làm rõ yêu cầu',
  construction: 'đang xây',
  operations: 'đang nghiệm thu'
};

function intentLine(i) {
  const [live, done] = i.units || [0, 0];
  if (i.stage >= 8 && live > 0 && done >= live) return 'đã xong · ' + done + '/' + live + ' phần việc';
  if (i.phase === 'construction' || i.phase === 'operations') {
    return PHASE_WORDS[i.phase] + ' · ' + done + '/' + live + ' phần việc xong';
  }
  return PHASE_WORDS.inception + (live ? ' · dự kiến ' + live + ' phần việc' : '');
}

function Row({ label, children }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: 14, padding: '12px 0', borderBottom: '1px solid var(--line)' }}>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', paddingTop: 3 }}>{label}</div>
      <div style={{ fontSize: 14.5, lineHeight: 1.6, display: 'flex', flexDirection: 'column', gap: 4 }}>{children}</div>
    </div>
  );
}

function Brief({ data, gates, onInbox, onLookup, onOpenIntent }) {
  const intents = data.intents || [];
  const inbox = window.buildInbox ? window.buildInbox(data, gates) : [];
  const showcases = (gates || []).filter(g => g.gate === 'E');
  const escOpen = (data.escalations || []).filter(e => e.status === 'open');
  /* DEC không theo mẫu "Quyết định: …" thì `what` rỗng — không in dòng trống. */
  const decisions = (data.decisions || []).filter(d => d.what).slice(-3).reverse();
  const plain = s => String(s || '').replace(/`/g, '');
  const hh = data.handoffHealth || {};
  const zombies = ((data.team || {}).zombies || []).length;
  const health = [];
  if (hh.accepted) health.push(hh.accepted + ' việc đang có người làm');
  if ((hh.suspect || []).length) health.push((hh.suspect || []).length + ' việc báo nhịp không đáng tin');
  if ((hh.noHeartbeat || []).length) health.push((hh.noHeartbeat || []).length + ' việc chưa báo nhịp');
  if (zombies) health.push(zombies + ' phiên nên tắt');
  const link = (txt, fn) => <span onClick={fn} style={{ color: 'var(--blue)', cursor: 'pointer' }}>{txt}</span>;

  return (
    <div style={{ padding: '24px 24px 48px', maxWidth: 820 }}>
      <div style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 8 }}>
        Một trang, bằng lời. Chi tiết nằm ở {link('Tra cứu ▸', onLookup)}.
      </div>

      <Row label="Đã làm">
        {intents.length === 0 && <span style={{ color: 'var(--muted)' }}>Chưa có yêu cầu nào.</span>}
        {intents.map(i => (
          <div key={i.id}>
            {link(window.plainName ? window.plainName(i.name) : i.name, () => onOpenIntent(i.id))}
            <span style={{ color: 'var(--muted)' }}> — {intentLine(i)}</span>
          </div>
        ))}
        {decisions.length > 0 && (
          <div style={{ marginTop: 4, color: 'var(--muted)', fontSize: 13.5 }}>
            Vừa chốt: {decisions.map(d => (d.what || '').slice(0, 80)).join(' · ')}
          </div>
        )}
      </Row>

      <Row label="Sẵn để bạn xem">
        {showcases.length === 0
          ? <span style={{ color: 'var(--muted)' }}>Chưa có gì mới để xem thử.</span>
          : showcases.map(g => <div key={g.key}>{link((data.intents.find(x => x.id === g.target) || {}).name || g.target, onInbox)} — vòng xây đang chờ bạn xem rồi ký</div>)}
      </Row>

      <Row label="Cần bạn">
        {inbox.length === 0
          ? <span style={{ color: 'var(--muted)' }}>Không có gì. Đội đang làm việc.</span>
          : <div>{link(inbox.length + ' việc đang chờ bạn ▸', onInbox)}
              <span style={{ color: 'var(--muted)' }}> — {inbox.slice(0, 3).map(c => plain(c.q)).join(' · ')}{inbox.length > 3 ? ' · …' : ''}</span>
            </div>}
      </Row>

      <Row label="Đang đứng">
        {escOpen.length === 0
          ? <span style={{ color: 'var(--muted)' }}>Không có gì đứng chờ người.</span>
          : escOpen.map(e => <div key={e.id}>{plain(e.title) || e.id}<span style={{ color: 'var(--muted)' }}> — {e.owner && !/^[\s\-—–]*$/.test(e.owner) && !/^unassigned/i.test(e.owner) ? 'đang ở ' + e.owner : 'chưa ai nhận'}</span></div>)}
      </Row>

      <Row label="Sức khoẻ đội">
        <div style={{ color: health.length ? 'var(--ink)' : 'var(--muted)' }}>
          {health.length ? health.join(' · ') : 'Không có gì bất thường.'} {link('Đội AI ▸', () => onLookup('mission'))}
        </div>
      </Row>

      <div style={{ marginTop: 14, fontSize: 12, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
        cập nhật {data.project && data.project.generated}
      </div>
    </div>
  );
}

Object.assign(window, { Brief });
})();
