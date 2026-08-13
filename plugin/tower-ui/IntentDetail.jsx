(function(){
const NSi = window.ControlTowerDesignSystem_68131c;
const { Panel, StageStrip, DataTable, Chip, IdCode, VerdictBadge, AgentAvatar, Button } = NSi;

function Tabs({ tabs, active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 2, borderBottom: '1px solid var(--line)', flexWrap: 'wrap' }}>
      {tabs.map(t => (
        <button key={t} onClick={() => onChange(t)} style={{
          fontFamily: 'var(--mono)', fontSize: 11.5, letterSpacing: '0.08em', textTransform: 'uppercase',
          padding: '8px 14px', cursor: 'pointer', background: 'transparent',
          border: 'none', borderBottom: '2px solid ' + (active === t ? 'var(--accent)' : 'transparent'),
          color: active === t ? 'var(--ink)' : 'var(--muted)'
        }}>{t}</button>
      ))}
    </div>
  );
}

function UnitCard({ u, onOpenUnit, onDoc }) {
  const tone = u.status === 'in-bolt' ? 'active' : u.status === 'done' ? 'done' : 'pending';
  const bad = u.problems && u.problems.length > 0;
  return (
    <div onClick={() => onOpenUnit && onOpenUnit(u)} style={{
      border: '1px solid ' + (bad ? 'var(--danger)' : 'var(--line)'), borderRadius: 'var(--radius-lg)',
      background: 'var(--surface)', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8,
      cursor: 'pointer'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <IdCode style={{ fontSize: 12 }}>{u.id}</IdCode>
        <Chip tone={u.descoped ? 'pending' : u.provisional ? 'agent' : tone}>
          {u.descoped ? 'ngoài phạm vi đợt này' : u.provisional ? 'dự kiến' : u.status}
        </Chip>
        <span style={{
          marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 11,
          color: u.estimate > 5 ? 'var(--danger)' : 'var(--muted)'
        }}>{u.estimate ? u.estimate.toFixed(1) + 'h' : 'chưa ước lượng'}</span>
      </div>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{u.name}</div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        <Chip tone={u.stories ? 'done' : 'blocked'}>{u.stories} US</Chip>
        <Chip tone={u.nfrs ? 'done' : 'blocked'}>{u.nfrs} NFR</Chip>
        <Chip tone={u.riskCount ? 'done' : 'blocked'}>{u.riskCount} risk</Chip>
        {(u.sources || []).length > 0 && <Chip tone="agent">{u.sources.length} nguồn</Chip>}
      </div>
      <div style={{ height: 4, background: 'var(--surface-2)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: u.done + '%', height: '100%', background: u.done ? 'var(--ok)' : 'transparent' }} />
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>
          {u.bolt} · {u.tasks[0]}/{u.tasks[1]} task done
        </span>
        {u.specPath && (
          <span onClick={e => { e.stopPropagation(); onDoc(u.specPath); }} style={{
            fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--blue)', cursor: 'pointer'
          }}>spec.md ↗</span>
        )}
      </div>
      {bad && (
        <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--danger)' }}>△ {u.problems.join(' · ')}</div>
      )}
    </div>
  );
}

function IntentDetail({ data, intentId, onOpenBolt, onOpenList, onSelectIntent, onDoc, onOpenUnit, onOpenFlow }) {
  const intent = data.intents.find(x => x.id === intentId) || data.intents[0];
  if (!intent) return <div style={{ padding: 24, color: 'var(--muted)' }}>Chưa có intent nào.</div>;
  const units = data.unitsByIntent[intent.id] || [];
  const src = (data.sourcesByIntent || {})[intent.id] || { counts: {}, rows: [], conflicts: [] };
  const revs = (data.revisionsByIntent || {})[intent.id] || [];
  const questions = ((data.questionsByIntent || {})[intent.id]) || data.questions || [];
  const hofs = (data.handoffs || []).filter(h => (h.re || '').startsWith(intent.id));
  const c = src.counts || {};
  const [tab, setTab] = React.useState('Units');
  const docList = Object.values(data.docs || {}).filter(d => d.path.indexOf(intent.id) >= 0);

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <span onClick={onOpenList} style={{ cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)' }}>← tất cả intents</span>
        <span style={{ width: 1, height: 14, background: 'var(--line)' }} />
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {data.intents.map(x => (
            <span key={x.id} onClick={() => onSelectIntent && onSelectIntent(x.id)} style={{ cursor: 'pointer' }}>
              <Chip tone={x.id === intent.id ? 'agent' : x.gate ? 'active' : 'pending'}>{x.id}</Chip>
            </span>
          ))}
        </div>
        <span style={{ marginLeft: 'auto' }} />
        <Button variant="secondary" onClick={onOpenFlow}>Xem dòng chảy 3 pha →</Button>
      </div>

      <Panel>
        <div style={{ display: 'flex', gap: 12, alignItems: 'baseline', flexWrap: 'wrap' }}>
          <IdCode style={{ fontSize: 13, color: 'var(--accent)' }}>{intent.id}</IdCode>
          <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.01em' }}>{intent.name}</span>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <Chip tone="neutral">brownfield · {intent.brownfield || '—'}</Chip>
            <Chip tone={c.planned ? 'active' : 'done'}>nguồn {c.read || 0}/{c.total || 0}</Chip>
            {/* đếm và cộng giờ CÙNG một tập unit (trong phạm vi) — trước 3.1.0 chip này
                đếm cả unit ngoài phạm vi nhưng chỉ cộng giờ của unit trong phạm vi */}
            <Chip tone="neutral">
              {units.filter(u => !u.descoped).length} unit trong phạm vi · {intent.estimate || 0}h
              {units.some(u => u.descoped) ? ' (+' + units.filter(u => u.descoped).length + ' ngoài phạm vi)' : ''}
            </Chip>
            <span onClick={() => onDoc('context-memory/intents/' + intent.id + '/' + intent.doc)} style={{ cursor: 'pointer' }}>
              <IdCode variant="artifact">{intent.doc} ↗</IdCode>
            </span>
          </span>
        </div>
        <div style={{ marginTop: 14 }}><StageStrip current={intent.stage} gate={intent.gate} labels /></div>
      </Panel>

      <Panel pad={false}>
        <div style={{ padding: '0 8px' }}>
          <Tabs tabs={['Units', 'Nguồn', 'Handoff', 'Open Questions', 'Decisions', 'Chỉnh sửa', 'Tài liệu']} active={tab} onChange={setTab} />
        </div>
        <div style={{ padding: 16 }}>
          {tab === 'Units' && (
            units.length ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {units[0] && units[0].provisional && (
                  <Note tone="agent" title="Bản dự kiến (provisional)">
                    Đây là phân rã đề xuất ở phần 3 của <code>intent-plan.md</code>, chưa qua AS-IS.
                    Bản chốt sinh ở stage 5 và được duyệt tại Gate D.
                  </Note>
                )}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 12 }}>
                  {units.map(u => <UnitCard key={u.id} u={u} onOpenUnit={onOpenUnit} onDoc={onDoc} />)}
                </div>
              </div>
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>Chưa có Unit — phân rã dự kiến nằm ở phần 3 của <code>intent-plan.md</code>, bản chốt duyệt tại Gate D.</div>
          )}

          {tab === 'Nguồn' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <Chip tone="done">{c.read || 0} read</Chip>
                <Chip tone={c.planned ? 'active' : 'pending'}>{c.planned || 0} planned</Chip>
                <Chip tone={c.missing ? 'blocked' : 'pending'}>{c.missing || 0} missing</Chip>
                <Chip tone="pending">{c.deferred || 0} deferred</Chip>
                <Chip tone="agent">{c.added || 0} added ngoài plan</Chip>
                <Chip tone={c.conflicts ? 'blocked' : 'pending'}>{c.conflicts || 0} conflict</Chip>
              </div>
              {c.planned > 0 && (
                <Note tone="danger" title="Đang chặn gate">
                  Còn {c.planned} nguồn ở trạng thái <code>planned</code> — theo protocol §4.8, Gate B/D không được đóng
                  khi chưa đọc hết nguồn đã cam kết.
                </Note>
              )}
              <DataTable columns={['#', 'Nguồn', 'Thông tin cần lấy', 'Ưu tiên', 'Trạng thái', 'Evidence']}
                rows={(src.rows || []).map(r => [r.id, r.source, r.need || '—', r.prio || '—',
                  <Chip tone={r.status === 'read' ? 'done' : r.status === 'planned' ? 'active' : r.status === 'missing' ? 'blocked' : 'pending'}>{r.status}{r.added ? ' [ADDED]' : ''}</Chip>,
                  r.evidence || '—'])} />
              {(src.conflicts || []).length > 0 && (
                <>
                  <SectionLabel>Mâu thuẫn giữa các nguồn</SectionLabel>
                  <DataTable columns={['#', 'Nguồn A nói', 'Nguồn B nói', 'Trạng thái']} monoFirst
                    rows={src.conflicts.map(x => [x.id, x.a, x.b, x.status])} />
                </>
              )}
            </div>
          )}

          {tab === 'Handoff' && (
            hofs.length ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ fontSize: 13, color: 'var(--muted)' }}>
                  Chuỗi giao việc giữa các vị trí — nguồn bằng chứng cho retro: việc đi qua tay ai, tắc ở đâu,
                  phải trả lại mấy lần.
                </div>
                {hofs.map(h => (
                  <div key={h.id} onClick={() => onDoc(h.doc)} style={{
                    border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', padding: '10px 13px',
                    background: h.status === 'returned' ? 'var(--danger-bg)' : h.status === 'accepted' ? 'var(--blue-bg)' : 'var(--surface)',
                    cursor: 'pointer'
                  }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                      <IdCode style={{ fontSize: 11.5 }}>{h.id}</IdCode>
                      <Chip tone={h.status === 'done' ? 'done' : h.status === 'returned' ? 'blocked' : h.status === 'accepted' ? 'agent' : 'active'}>{h.status}</Chip>
                      <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>{h.from} → {h.agent}</span>
                      <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{h.re}</span>
                      <span style={{ marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{h.reads} nguồn phải đọc</span>
                    </div>
                    {h.task && <div style={{ fontSize: 13.5, marginTop: 4 }}>{h.task}</div>}
                    {h.pending && h.pending.length > 0 && (
                      <div style={{ fontSize: 12.5, color: 'var(--accent)', marginTop: 3 }}>còn treo: {h.pending.join(' · ')}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>
              Chưa có handoff nào cho intent này. Mỗi lần giao việc cho agent phải là một file
              <code> handoffs/HOF-NNNN.md</code> (protocol §9) — prompt chỉ trỏ tới file.
            </div>
          )}

          {tab === 'Open Questions' && (
            questions.length ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                {[
                  { key: 'business', title: 'Nghiệp vụ — người kinh doanh trả lời', file: 'open-questions-business.md',
                    hint: 'Gate C duyệt file này. Viết bằng lời, không thuật ngữ code (protocol §4.10).' },
                  { key: 'tech', title: 'Kỹ thuật — tech lead / QA / devops trả lời', file: 'open-questions-tech.md',
                    hint: 'Không ra Gate C. Câu CHẶN còn treo thì Unit đó không vào được Gate D.' },
                  { key: 'legacy', title: 'Bản gộp cũ — chưa tách theo người trả lời', file: 'open-questions.md',
                    hint: 'Intent tạo bằng plugin ≤2.2. Tách khi có vòng chỉnh sửa tiếp theo.' },
                ].filter(sec => questions.some(q => q.audience === sec.key)).map(sec => {
                  const rows = questions.filter(q => q.audience === sec.key);
                  const open = rows.filter(q => !/chốt|closed|đã/i.test(q.status));
                  const blk = rows.filter(q => q.blocking);
                  return (
                    <div key={sec.key} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                        <strong style={{ fontSize: 13.5 }}>{sec.title}</strong>
                        <Chip tone={open.length ? 'active' : 'done'}>{open.length} câu chờ</Chip>
                        {blk.length ? <Chip tone="blocked">{blk.length} đang chặn Unit</Chip> : null}
                        <span onClick={() => onDoc && onDoc('context-memory/intents/' + intent.id + '/' + sec.file)}
                          style={{ cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>
                          {sec.file} →
                        </span>
                      </div>
                      <div style={{ fontSize: 11.5, color: 'var(--muted)' }}>{sec.hint}</div>
                      <DataTable columns={['Mã', 'Câu hỏi', 'Ai trả lời', 'Hạn', 'Nếu im lặng', 'Ảnh hưởng', 'Trạng thái']}
                        rows={rows.map(q => [q.code || '—', q.q, q.who || <span style={{ color: 'var(--danger)' }}>chưa rõ người trả lời</span>,
                          q.due, q.fallback || <span style={{ color: 'var(--danger)' }}>thiếu mặc định</span>,
                          q.blocking ? <Chip tone="blocked">{q.impact}</Chip> : q.impact,
                          <Chip tone={/chốt|closed|đã/i.test(q.status) ? 'done' : 'active'}>{q.status}</Chip>])} />
                    </div>
                  );
                })}
              </div>
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>
              Chưa có open question — sinh ở stage 4 (Gate C), tách thành
              <code> open-questions-business.md</code> và <code> open-questions-tech.md</code> (protocol §4.10).
            </div>
          )}

          {tab === 'Decisions' && (
            data.decisions.length ? (
              <DataTable columns={['DEC', 'Thời điểm', 'Gate', 'Ai quyết', 'Nội dung', 'Căn cứ']}
                rows={data.decisions.map(d => [d.id, d.when, <Chip tone="done">{d.gate}</Chip>, d.by, d.what, <IdCode variant="inline">{d.basis}</IdCode>])} />
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>Chưa có DEC nào.</div>
          )}

          {tab === 'Chỉnh sửa' && (
            revs.length ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {revs.map(r => (
                  <div key={r.id} style={{
                    border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', padding: '11px 14px',
                    background: r.status === 'open' ? 'var(--accent-bg)' : 'var(--surface)'
                  }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                      <IdCode style={{ fontSize: 12, color: 'var(--accent)' }}>{r.id}</IdCode>
                      <Chip tone={r.status === 'open' ? 'active' : 'done'}>{r.status}</Chip>
                      <Chip tone="neutral">Gate {r.gate} · {r.doc}{r.version ? ' v' + r.version : ''}</Chip>
                      <span style={{ marginLeft: 'auto', fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)' }}>{r.at}</span>
                    </div>
                    <div style={{ fontSize: 13.5, marginTop: 6 }}>{r.request}</div>
                  </div>
                ))}
              </div>
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>Chưa có vòng chỉnh sửa nào — tài liệu gate được duyệt ngay từ bản đầu.</div>
          )}

          {tab === 'Tài liệu' && (
            docList.length ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: 12 }}>
                {docList.map(d => (
                  <div key={d.path} onClick={() => onDoc(d.path)} style={{
                    border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)',
                    padding: '12px 14px', cursor: 'pointer'
                  }}>
                    <IdCode variant="artifact">{d.name}</IdCode>
                    <div style={{ fontSize: 13.5, marginTop: 6 }}>{d.title}</div>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--muted)', marginTop: 4 }}>
                      {d.version ? 'v' + d.version + ' · ' : ''}{d.updated}
                    </div>
                  </div>
                ))}
              </div>
            ) : <div style={{ color: 'var(--muted)', fontSize: 14 }}>
              Tài liệu gate được nhúng khi gate đang mở. Mở tower bằng <code>/dlc-tower serve</code> để đọc mọi file
              trong <code>.ai-dlc/context-memory/</code>.
            </div>
          )}
        </div>
      </Panel>
    </div>
  );
}
window.IntentDetail = IntentDetail;
})();
