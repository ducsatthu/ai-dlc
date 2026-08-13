(function(){
const NSm = window.ControlTowerDesignSystem_68131c;
const { KpiStrip, Panel, PipelineRow, FeedItem, VerdictBadge, Chip, IdCode: Id, Button } = NSm;

/* Gate trong hàng đợi: KHÔNG có nút approve tại chỗ.
   Muốn quyết thì phải mở tài liệu ra đọc — protocol §2.1 (cấm approve mù). */
function GateQueueItem({ g, onOpen }) {
  const isEsc = g.kind === 'escalation';
  return (
    <article style={{
      border: '1px solid ' + (isEsc ? 'var(--danger)' : 'var(--accent)'),
      background: isEsc ? 'var(--danger-bg)' : 'var(--accent-bg)',
      borderRadius: 'var(--radius-md)', marginBottom: 8, padding: '12px 14px',
      display: 'flex', flexDirection: 'column', gap: 9
    }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ color: isEsc ? 'var(--danger)' : 'var(--accent)', fontFamily: 'var(--mono)' }}>{isEsc ? '△' : '◇'}</span>
        <Id style={{ color: 'var(--accent)', fontSize: 12 }}>{isEsc ? 'ESCALATION' : 'Gate ' + g.gate} · {g.target}</Id>
        <span style={{ fontSize: 14.5, fontWeight: 650 }}>{g.title}</span>
        {g.pendingRevision && <Chip tone="active">đang chờ bản sửa</Chip>}
      </div>
      {g.brief && <div style={{ fontSize: 13.5, color: 'var(--ink)', maxWidth: 'var(--measure-note)' }}>{g.brief}</div>}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
        {g.docTitle
          ? <Chip tone="neutral">tài liệu · {(g.doc || '').split('/').pop()}{g.docVersion ? ' v' + g.docVersion : ''}</Chip>
          : <Chip tone="blocked">chưa có tài liệu gate</Chip>}
        {(g.blockers || []).length > 0 && <Chip tone="blocked">{g.blockers.length} điều kiện chưa đạt</Chip>}
        {(g.evidence || []).map(e => <Id key={e} variant="inline">{e}</Id>)}
      </div>
      <div>
        <Button variant="primary" onClick={() => onOpen(g)}>Đọc tài liệu &amp; quyết định →</Button>
      </div>
    </article>
  );
}

/* Vị trí đang làm việc — sinh từ handoffs/. Màu theo semantic của DS:
   xanh = agent đang chạy · hổ phách = chờ được nhận · đỏ = trả lại, cần người. */
const ST = {
  accepted: { tone: 'agent', color: 'var(--blue)', label: 'đang làm', mark: '◐' },
  open: { tone: 'active', color: 'var(--accent)', label: 'chờ nhận', mark: '◇' },
  returned: { tone: 'blocked', color: 'var(--danger)', label: 'trả lại', mark: '△' }
};

function StationRow({ s, onOpenDoc }) {
  const v = ST[s.status] || ST.open;
  return (
    <div onClick={() => onOpenDoc && onOpenDoc(s.doc)} style={{
      display: 'flex', gap: 10, padding: '10px 14px', borderBottom: '1px solid var(--line)',
      cursor: onOpenDoc ? 'pointer' : 'default', alignItems: 'flex-start'
    }}>
      <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: v.color, width: 12, flex: 'none', lineHeight: '18px' }}>{v.mark}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', gap: 7, alignItems: 'baseline', flexWrap: 'wrap' }}>
          <Id style={{ fontSize: 11.5, color: v.color }}>{s.id}</Id>
          <span style={{ fontSize: 13.5, fontWeight: 600 }}>{s.agent}</span>
          <Chip tone={v.tone}>{v.label}</Chip>
          {/* teammate = phiên Claude riêng (agent team), không phải sub-agent — protocol §9.5 */}
          {s.teammate && <Chip tone="agent">⧉ {s.teammate}</Chip>}
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{s.re}</span>
        </div>
        {s.task && <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 2 }}>{s.task}</div>}
        {s.status === 'accepted' && (
          <div style={{ fontSize: 12.5, marginTop: 3, color: s.stale ? 'var(--accent)' : 'var(--blue)' }}>
            {s.progress && s.progress !== '-' ? s.progress : 'chưa báo tiến độ'}
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: s.stale ? 'var(--accent)' : 'var(--muted)', marginLeft: 6 }}>
              {s.hbKind ? '· nhịp khai KHÔNG tin được'
                : s.silentMin === null || s.silentMin === undefined ? ''
                  : s.stale ? '· im lặng ' + s.silentMin + ' phút' : '· nhịp ' + s.silentMin + ' phút trước'}
            </span>
          </div>
        )}
        {/* Lời khai vs dấu vết (§9.4). Đừng để người giám sát đọc "im lặng 1099 phút" của một agent
            vừa ghi file 0 phút trước — số sai còn nguy hơn không có số. */}
        {s.status === 'accepted' && s.hbKind && (
          <div style={{ fontSize: 12, color: 'var(--danger)', marginTop: 3 }}>
            {s.hbWhy}
            {typeof s.fileMin === 'number' && (
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, marginLeft: 6, color: 'var(--muted)' }}>
                · file vừa đổi {s.fileMin} phút trước
              </span>
            )}
          </div>
        )}
        {s.status === 'open' && s.unclaimedActivity && (
          <div style={{ fontSize: 12.5, color: 'var(--accent)', marginTop: 3 }}>
            có file trong phạm vi này vừa đổi — nhiều khả năng agent đang chạy nhưng chưa đặt
            <code style={{ fontFamily: 'var(--mono)' }}> status: accepted</code> (protocol §9.4)
          </div>
        )}
        {s.pending && s.pending.length > 0 && (
          <div style={{ fontSize: 12, color: 'var(--accent)', marginTop: 3 }}>còn treo: {s.pending.join(' · ')}</div>
        )}
        {s.blocked && s.blocked.length > 0 && (
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--danger)', marginTop: 3 }}>chặn bởi {s.blocked.join(', ')}</div>
        )}
      </div>
      <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', flex: 'none' }}>
        {(s.accepted && s.accepted !== '-' ? s.accepted : s.created || '').slice(5, 16).replace('T', ' ')}
      </span>
    </div>
  );
}

/* Dải pha (Control Tower Design System) — một dòng trả lời "dự án đang ở đâu".
   Số intent mỗi pha đọc thẳng từ `phase` của intent, mà `phase` sinh từ `stage:` trong status.md;
   bấm vào pha nào thì mở intent đầu tiên của pha đó ở màn Dòng chảy. */
const PHASES = [
  { key: 'inception', name: 'Inception', hint: 'stage 1–5 · intent → nguồn → unit plan' },
  { key: 'construction', name: 'Construction', hint: 'stage 6 · bolt chạy, code + test' },
  { key: 'operations', name: 'Operations', hint: 'stage 7–8 · UAT, deploy, retro' }
];

function PhaseBar({ intents, onOpenIntent }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'stretch', flexWrap: 'wrap',
      border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)',
      background: 'var(--surface)', overflow: 'hidden'
    }}>
      {PHASES.map((p, i) => {
        const inPhase = intents.filter(x => x.phase === p.key);
        const here = inPhase.length > 0;
        return (
          <button key={p.key} title={p.hint + (inPhase.length ? ' · ' + inPhase.map(x => x.id).join(', ') : ' · chưa intent nào')}
            onClick={() => inPhase.length && onOpenIntent(inPhase[0].id)}
            style={{
              flex: '1 1 160px', minWidth: 0, textAlign: 'left',
              cursor: inPhase.length ? 'pointer' : 'default', border: 'none',
              borderLeft: i ? '1px solid var(--line)' : 'none',
              background: here ? 'var(--surface-2)' : 'transparent', padding: '10px 14px',
              display: 'flex', alignItems: 'baseline', gap: 8, overflow: 'hidden'
            }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: here ? 'var(--accent)' : 'var(--line)', flex: 'none' }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 700, color: here ? 'var(--accent)' : 'var(--muted)' }}>{p.name}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)', marginLeft: 'auto', flex: 'none' }}>
              {inPhase.length} intent
            </span>
          </button>
        );
      })}
    </div>
  );
}

function MissionControl({ data, gates, onOpenGate, onOpenIntent, onOpenFeed, onOpenDoc, onMetric }) {
  const filters = ['all', 'comms', 'review', 'decision'];
  const [filter, setFilter] = React.useState('all');
  const feed = data.feed.filter(x =>
    filter === 'all' ? true :
    filter === 'comms' ? ['clarification', 'question', 'answer', 'handoff', 'note'].includes(x.type) :
    filter === 'review' ? ['review-request', 'finding'].includes(x.type) : x.type === 'decision');

  /* KPI ở đây GỘP MỌI INTENT. Mỗi ô mở được bảng "số này ở đâu ra" — dòng thật đã đếm,
     kèm cột Intent để thấy số nào của intent nào (protocol: không có số nào không giải thích được). */
  const metricsByIntent = data.metricsByIntent || {};
  const merge = (key, label, tone) => {
    const parts = Object.entries(metricsByIntent)
      .map(([id, ms]) => [id, ms[key]]).filter(([, m]) => m);
    if (!parts.length) return null;
    const nums = parts.map(([, m]) => String(m.value));
    const isFrac = nums.some(v => v.indexOf('/') >= 0);
    const sum = a => a.reduce((x, y) => x + y, 0);
    const value = isFrac
      ? sum(nums.map(v => parseFloat(v.split('/')[0]) || 0)) + '/' + sum(nums.map(v => parseFloat(v.split('/')[1]) || 0))
      : sum(nums.map(v => parseFloat(v) || 0));
    const first = parts[0][1];
    return {
      key, value, label: label || first.label, tone: tone || first.tone,
      rule: first.rule + (parts.length > 1 ? ' Ở màn này số của ' + parts.length + ' intent được CỘNG LẠI.' : ''),
      files: parts.flatMap(([, m]) => m.files),
      warnings: parts.flatMap(([id, m]) => m.warnings.map(w => parts.length > 1 ? id + ': ' + w : w)),
      rows: parts.flatMap(([id, m]) => m.rows.map(r => (parts.length > 1 ? Object.assign({ Intent: id }, r) : r))),
      rowCount: sum(parts.map(([, m]) => m.rowCount))
    };
  };
  const units = Object.values(data.unitsByIntent || {}).flat();
  const kpis = [
    {
      key: 'gates.queue', value: gates.filter(g => g.kind === 'gate').length, label: 'Gates chờ tôi', tone: 'gate',
      rule: 'Đếm intent có `gate_open` trong `status.md` mà chưa có quyết định trong `inbox/processed/`.',
      files: [{ file: '.ai-dlc/context-memory/intents/*/status.md', section: 'frontmatter `gate_open`' }],
      warnings: [], rowCount: gates.length,
      rows: gates.map(g => ({ Mục: g.title || g.key, Intent: g.target || '—', Loại: g.kind }))
    },
    merge('sources.read'), merge('sources.planned'), merge('sources.conflicts'),
    merge('units.problems'), merge('units.done'), merge('units.reviewed'), merge('units.artifacts')
  ].filter(Boolean);

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16, minHeight: 0 }}>
      <PhaseBar intents={data.intents} onOpenIntent={onOpenIntent} />
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))',
        border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)', overflow: 'hidden'
      }}>
        {kpis.map((k, i) => (
          <div key={k.key} onClick={() => onMetric && onMetric(k)} title="Bấm để xem số này ở đâu ra"
            style={{ padding: '11px 16px', borderLeft: i ? '1px solid var(--line)' : 'none', cursor: onMetric ? 'pointer' : 'default' }}>
            <div style={{
              fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, lineHeight: 1.1,
              color: k.tone === 'gate' ? 'var(--accent)' : k.tone === 'done' ? 'var(--ok)' : 'var(--blue)'
            }}>{k.value}{(k.warnings || []).length ? <span style={{ color: 'var(--accent)', fontSize: 13 }}> ⚠</span> : null}</div>
            <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 3 }}>
              {k.label} <span style={{ opacity: 0.55 }}>ⓘ</span>
            </div>
          </div>
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.55fr) minmax(320px,1fr)', gap: 16, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Panel title="Gate queue — chờ quyết định của bạn" meta={gates.length + ' mục'}>
            {gates.length === 0 ? (
              <div style={{ padding: '28px 8px', textAlign: 'center', color: 'var(--muted)' }}>
                <style>{'@keyframes ct-breathe{0%,100%{opacity:.45}50%{opacity:1}}'}</style>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 22, color: 'var(--ok)', animation: 'ct-breathe 1600ms ease-in-out infinite' }}>●</div>
                <div style={{ marginTop: 8, fontSize: 14.5 }}>Không có gì chờ bạn — agents đang làm việc</div>
              </div>
            ) : gates.map(g => <GateQueueItem key={g.key} g={g} onOpen={onOpenGate} />)}
          </Panel>
          <Panel title="Vị trí đang làm việc" pad={false}
            meta={(data.stations || []).length ? (data.stations || []).length + ' handoff mở' : 'không có vị trí nào mở'}>
            {(data.stations || []).length === 0 ? (
              <div style={{ padding: '18px 16px', color: 'var(--muted)', fontSize: 13.5 }}>
                Chưa có handoff nào đang mở. Mỗi lần giao việc cho agent là một file
                <code style={{ fontFamily: 'var(--mono)' }}> handoffs/HOF-NNNN.md</code> — đó là thứ giữ bối cảnh
                khi phiên kết thúc, và là dấu vết để retro.
              </div>
            ) : (data.stations || []).map(s => <StationRow key={s.id} s={s} onOpenDoc={onOpenDoc} />)}
          </Panel>
          {/* Phiên teammate đang sống. Vòng đời teammate = vòng đời HOF của nó (§9.5.6): sống lâu hơn
              không tốn token (phiên rảnh không gọi API) nhưng mang theo bối cảnh cũ — nó vẫn nhớ bản v3
              trong khi đĩa đã v4. Kill rẻ vì spawn lại chỉ là một dòng trỏ HOF. */}
          {((data.team || {}).members || []).length > 1 && (
            <Panel title="Agent team — phiên đang sống" pad={false}
              meta={(data.team.zombies || []).length > 0
                ? (data.team.zombies.length + ' phiên nên tắt')
                : (data.team.members.length - 1) + ' teammate · đều còn việc'}>
              {data.team.members.filter(m => m.state !== 'lead').map(m => {
                const tone = m.state === 'working' ? 'agent' : m.state === 'zombie' ? 'blocked' : 'active';
                const color = m.state === 'working' ? 'var(--blue)' : m.state === 'zombie' ? 'var(--danger)' : 'var(--accent)';
                const word = m.state === 'working' ? 'đang giữ việc' : m.state === 'zombie' ? 'nên tắt' : 'không rõ';
                return (
                  <div key={m.name} style={{ display: 'flex', gap: 10, padding: '9px 14px', borderBottom: '1px solid var(--line)', alignItems: 'flex-start' }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 13, width: 12, flex: 'none', color: color }}>⧉</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', gap: 7, alignItems: 'baseline', flexWrap: 'wrap' }}>
                        <Id style={{ fontSize: 11.5, color: color }}>{m.name}</Id>
                        <Chip tone={tone}>{word}</Chip>
                        {m.hof && <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{m.hof}</span>}
                        {m.pane && <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>pane {m.pane}</span>}
                      </div>
                      <div style={{ fontSize: 12.5, color: m.state === 'working' ? 'var(--muted)' : color, marginTop: 2 }}>{m.why}</div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', marginTop: 2 }}>{m.type || 'không khai agent type'}</div>
                    </div>
                  </div>
                );
              })}
            </Panel>
          )}
          {/* Tin chết: gửi cho teammate chưa bao giờ spawn. SendMessage chỉ ghi file JSON nên nó báo
              "đã gửi" — người gửi tin là đã giao việc, còn thực tế không có ai ở đầu bên kia. §9.5 */}
          {((data.team || {}).deadLetters || []).length > 0 && (
            <Panel title="Tin chết — gửi cho teammate không tồn tại" pad={false}
              meta={data.team.deadLetters.length + ' hộp thư · team ' + (data.team.name || '—')}>
              <div style={{ padding: '9px 14px', fontSize: 12.5, color: 'var(--danger)', borderBottom: '1px solid var(--line)' }}>
                Spawn teammate hỏng nhưng tin vẫn được ghi vào hộp thư của nó. Không ai đọc, và người gửi
                tưởng đã giao xong — đúng dạng “xin review, không có verdict” của LL-002, lần này ở tầng team.
              </div>
              {data.team.deadLetters.map(d => (
                <div key={d.to} style={{ display: 'flex', gap: 10, padding: '9px 14px', borderBottom: '1px solid var(--line)', alignItems: 'flex-start' }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 13, width: 12, flex: 'none', color: 'var(--danger)' }}>✉</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', gap: 7, alignItems: 'baseline', flexWrap: 'wrap' }}>
                      <Id style={{ fontSize: 11.5, color: 'var(--danger)' }}>{d.to}</Id>
                      <Chip tone="blocked">{d.count} tin chưa ai đọc</Chip>
                      <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>từ {d.from} · {d.at}</span>
                    </div>
                    <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 2 }}>{d.text}</div>
                  </div>
                </div>
              ))}
            </Panel>
          )}
          {(data.escalations || []).length > 0 && (
            <Panel title="Phát hiện ngoài phạm vi — chờ người nhận" pad={false}
              meta={(data.escalations || []).filter(e => e.status === 'open').length + ' mở / ' + data.escalations.length}>
              {data.escalations.map(e => {
                const orphan = e.status === 'open' && !e.owner;
                return (
                  <div key={e.id} onClick={() => onOpenDoc && onOpenDoc(e.path)} style={{
                    display: 'flex', gap: 10, padding: '9px 14px', borderBottom: '1px solid var(--line)',
                    alignItems: 'flex-start', cursor: onOpenDoc ? 'pointer' : 'default'
                  }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 13, width: 12, flex: 'none', color: orphan ? 'var(--accent)' : 'var(--muted)' }}>△</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', gap: 7, alignItems: 'baseline', flexWrap: 'wrap' }}>
                        <Id style={{ fontSize: 11.5, color: orphan ? 'var(--accent)' : 'var(--muted)' }}>{e.id}</Id>
                        <span style={{ fontSize: 13.5, fontWeight: 600 }}>{e.title}</span>
                        {e.severity && <Chip tone={e.severity === 'high' ? 'blocked' : 'pending'}>{e.severity}</Chip>}
                        {e.scopeImpact && e.scopeImpact !== 'none' && <Chip tone="active">chạm {e.scopeImpact}</Chip>}
                      </div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', marginTop: 2 }}>
                        {e.where || '—'} · thấy bởi {e.foundBy || '—'}{e.foundIn ? ' (' + e.foundIn + ')' : ''}
                      </div>
                      {orphan && (
                        <div style={{ fontSize: 12.5, color: 'var(--accent)', marginTop: 3 }}>
                          chưa ai nhận — đây là mục sẽ chìm nếu chỉ nằm trong HOF (protocol §4.13)
                        </div>
                      )}
                    </div>
                    <Chip tone={e.status === 'open' ? 'active' : e.status === 'claimed' ? 'agent' : 'done'}>{e.status}</Chip>
                  </div>
                );
              })}
            </Panel>
          )}
          <Panel title="Hoạt động gần đây — file thật vừa đổi" pad={false}
            meta={(data.activity || []).length ? (data.activity || []).length + ' file · 2 giờ qua' : 'không có gì đổi'}>
            {(data.activity || []).length === 0 ? (
              <div style={{ padding: '16px', color: 'var(--muted)', fontSize: 13.5 }}>
                Không file nào trong <code style={{ fontFamily: 'var(--mono)' }}>.ai-dlc/</code> hoặc code root đổi
                trong 2 giờ qua. Nếu bạn biết có agent đang chạy thì nó chưa ghi gì xuống đĩa.
              </div>
            ) : (data.activity || []).slice(0, 12).map(a => (
              <div key={a.path} style={{
                display: 'flex', gap: 10, padding: '7px 14px', borderBottom: '1px solid var(--line)',
                alignItems: 'baseline'
              }}>
                <Chip tone={a.kind === 'code' ? 'agent' : 'pending'}>{a.kind === 'code' ? 'code' : 'state'}</Chip>
                <span style={{
                  fontFamily: 'var(--mono)', fontSize: 11.5, flex: 1, minWidth: 0,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', direction: 'rtl', textAlign: 'left'
                }} title={a.path}>{a.path}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', flex: 'none' }}>
                  {a.mins === 0 ? 'vừa xong' : a.mins + ' phút trước'}
                </span>
              </div>
            ))}
          </Panel>
          <Panel title="Pipeline board" meta={data.intents.length + ' intents'} pad={false}>
            {data.intents.map(i => (
              <PipelineRow key={i.id} id={i.id} name={i.name} current={i.stage} gate={i.gate} holder={i.holder}
                onClick={() => onOpenIntent(i.id)} />
            ))}
            <div style={{ display: 'flex', gap: 6, padding: '10px 16px', flexWrap: 'wrap' }}>
              {data.reviews.slice(0, 3).map(r => <VerdictBadge key={r.id} id={r.id} reviewer={r.reviewer.replace('-reviewer', '')} verdict={r.verdict} />)}
            </div>
          </Panel>
        </div>
        <Panel title="Live feed" meta="activity + comms" pad={false}
          style={{ position: 'sticky', top: 0, maxHeight: 'calc(100vh - 190px)' }}>
          <div style={{ display: 'flex', gap: 6, padding: '8px 12px', borderBottom: '1px solid var(--line)', flexWrap: 'wrap' }}>
            {filters.map(x => (
              <span key={x} onClick={() => setFilter(x)} style={{ cursor: 'pointer' }}>
                <Chip tone={filter === x ? 'agent' : 'pending'}>{x}</Chip>
              </span>
            ))}
          </div>
          {feed.map((x, i) => <FeedItem key={x.id} {...x} isNew={i === 0} onClick={() => onOpenFeed(x)} />)}
        </Panel>
      </div>
    </div>
  );
}
window.MissionControl = MissionControl;
})();
