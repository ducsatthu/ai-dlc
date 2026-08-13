(function(){
const NSb = window.ControlTowerDesignSystem_68131c;
const { Panel, TaskRow, Chip, IdCode, Button, MermaidDiagram } = NSb;

/* Bảng task của ĐÚNG unit đang chọn ở sidebar. Mỗi con số ở đây đọc từ một file có thật và
   file đó được in ra — cùng luật với KPI (protocol §4.11): không có số nào không truy được. */
/* Điểm dừng trong Bolt: chỗ công việc PHẢI dừng lại chờ ai đó ký.
   Màu theo semantic DS: xanh dương = chờ agent · hổ phách = chờ NGƯỜI · đỏ = trả lại/bỏ qua ·
   xanh lá = đã qua · xám nhạt = chưa tới. "Bỏ qua" là trạng thái đắt nhất và im lặng nhất. */
const STOP_TONE = {
  waiting: { agent: 'var(--blue)', human: 'var(--accent)' },
  passed: { agent: 'var(--ok)', human: 'var(--ok)' },
  returned: { agent: 'var(--danger)', human: 'var(--danger)' },
  skipped: { agent: 'var(--danger)', human: 'var(--danger)' },
  pending: { agent: 'var(--line)', human: 'var(--line)' }
};
const STOP_MARK = { waiting: '⏸', passed: '✓', returned: '↩', skipped: '⚠', pending: '·' };
const STOP_WORD = {
  waiting: h => (h === 'human' ? 'ĐANG CHỜ NGƯỜI' : 'đang chờ agent'),
  passed: () => 'đã qua', returned: () => 'bị trả lại',
  skipped: () => 'ĐÃ BỎ QUA', pending: () => 'chưa tới'
};

function StopCard({ s, onDoc }) {
  const color = (STOP_TONE[s.state] || STOP_TONE.pending)[s.holder] || 'var(--line)';
  const loud = s.state === 'skipped' || (s.state === 'waiting' && s.holder === 'human') || s.state === 'returned';
  return (
    <div title={s.why} style={{
      flex: '1 1 150px', minWidth: 0, padding: '7px 10px', borderRadius: 'var(--radius-sm)',
      border: '1px ' + (s.state === 'pending' ? 'dashed' : 'solid') + ' ' + color,
      background: loud ? 'color-mix(in srgb, ' + color + ' 10%, transparent)' : 'transparent'
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color }}>{STOP_MARK[s.state]}</span>
        <span style={{ fontSize: 12.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.label}</span>
      </div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, letterSpacing: '0.1em', textTransform: 'uppercase', color, marginTop: 2 }}>
        {STOP_WORD[s.state](s.holder)}
      </div>
      <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 2, lineHeight: 1.45 }}>{s.meta}</div>
      {(s.evidence || []).length > 0 && (
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
          {s.evidence.slice(0, 4).map(e => (
            <span key={e.id} onClick={() => e.path && onDoc && onDoc(e.path)}
              style={{ cursor: e.path && onDoc ? 'pointer' : 'default' }}>
              <IdCode variant="inline">{e.id}</IdCode>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

/* Mạch của một Bolt: chặng → điểm dừng → chặng. Vẽ cả hai trên cùng một dòng, vì cái đắt nhất
   không phải chặng nào chưa xong mà là điểm dừng nào đã bị đi qua. */
function BoltTrack({ steps, stops, onDoc }) {
  const at = k => stops.filter(s => s.key === k);
  const order = [
    { kind: 'step', keys: ['domain-design.md'] },
    { kind: 'step', keys: ['logical-design.md', 'adr/'] },
    { kind: 'stop', keys: ['design-review'] },
    { kind: 'step', keys: ['contract.md'] },
    { kind: 'stop', keys: ['contract-freeze', 'gate-E-a'] },
    { kind: 'step', keys: ['tasks.md'] },
    { kind: 'stop', keys: ['code-review'] },
    { kind: 'step', keys: ['evidence/'] },
    { kind: 'stop', keys: ['gate-E-b'] }
  ];
  const extra = stops.filter(s => ['escalation', 'open-question'].includes(s.key));
  return (
    <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'stretch', flexWrap: 'wrap', gap: 6 }}>
        {order.map((o, i) => {
          const items = o.kind === 'step'
            ? steps.filter(s => o.keys.includes(s.key))
            : o.keys.flatMap(at);
          if (!items.length) return null;
          return (
            <React.Fragment key={o.keys.join('-')}>
              {i > 0 && <span style={{ alignSelf: 'center', color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 11 }}>→</span>}
              {o.kind === 'step'
                ? items.map(s => <StepCard key={s.key} s={s} onDoc={onDoc} />)
                : items.map(s => <StopCard key={s.key} s={s} onDoc={onDoc} />)}
            </React.Fragment>
          );
        })}
      </div>
      {extra.length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 8 }}>
          {extra.map(s => <StopCard key={s.key} s={s} onDoc={onDoc} />)}
        </div>
      )}
      <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 8, lineHeight: 1.5 }}>
        Ô có viền là <strong>điểm dừng</strong> — chỗ công việc phải đứng lại chờ ai đó ký:
        <span style={{ color: 'var(--blue)' }}> xanh = chờ agent</span> ·
        <span style={{ color: 'var(--accent)' }}> hổ phách = chờ NGƯỜI</span> ·
        <span style={{ color: 'var(--danger)' }}> đỏ = bị trả lại, hoặc đã đi qua mà không dừng</span>.
        Trạng thái suy từ `reviews/` · `comms/` · `escalations/` · `gate_open`, không từ trạng thái tự khai.
      </div>
    </div>
  );
}

/* Các chặng trong một Bolt, đúng thứ tự phương pháp. Đây là thứ phải nhìn thấy được:
   Bolt không phải một cái nhãn, nó là bốn chặng có thật trên đĩa. */
function StepCard({ s, onDoc }) {
  return (
    <div onClick={() => s.doc && onDoc && onDoc(s.doc)} title={s.hint + (s.exists ? '' : ' — CHƯA CÓ trên đĩa')}
      style={{
        flex: '1 1 128px', minWidth: 0, padding: '7px 10px', borderRadius: 'var(--radius-sm)',
        border: '1px solid ' + (s.exists ? 'var(--line)' : 'transparent'),
        background: s.exists ? 'var(--surface-2)' : 'transparent',
        cursor: s.doc && onDoc ? 'pointer' : 'default', opacity: s.exists ? 1 : 0.65
      }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: s.exists ? 'var(--ok)' : 'var(--muted)' }}>{s.exists ? '✓' : '○'}</span>
        <span style={{ fontSize: 12.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.label}</span>
      </div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>
        {s.exists ? (s.meta || s.key) : 'chưa có'}
      </div>
    </div>
  );
}

function BoltBoard({ data, intentId, unitId, onOpenTask, onOpenUnit, onDoc }) {
  const [view, setView] = React.useState('list');
  const units = (data.unitsByIntent || {})[intentId] || [];
  const unit = units.find(u => u.id === unitId) || null;
  /* Bolt đọc từ CHÍNH unit đang chọn (`unit.boltDetails`), không tra bằng mã unit trần:
     hai intent có thể cùng có UOW-01, tra theo mã là lấy nhầm bolt của intent khác. */
  const byUnit = (unit && unit.boltDetails) || [];
  const [boltIdx, setBoltIdx] = React.useState(0);
  React.useEffect(() => { setBoltIdx(0); }, [unitId, intentId]);

  const bolt = byUnit[Math.min(boltIdx, Math.max(0, byUnit.length - 1))] || null;
  const rows = bolt ? bolt.tasks : [];
  const done = rows.filter(t => t.status === 'done').length;

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {!unit && (
        <div style={{ border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', padding: '12px 14px', fontSize: 13.5, color: 'var(--muted)' }}>
          {units.length
            ? 'Chưa chọn Unit nào — chọn một Unit ở cây bên trái.'
            : intentId + ' chưa được phân rã thành Unit — intent còn ở pha Inception.'}
        </div>
      )}

      {unit && (
        <Panel
          title={unit.id + (bolt ? ' · ' + bolt.id : '') + ' — ' + unit.name}
          meta={bolt
            ? bolt.stepsDone + '/' + bolt.stepsTotal + ' chặng · ' + done + '/' + rows.length + ' task done'
            : 'chưa có bolt nào'}
          pad={false}>
          <div style={{ display: 'flex', gap: 6, padding: '8px 14px', borderBottom: '1px solid var(--line)', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>
              {byUnit.length} bolt của {unit.id}
            </span>
            {byUnit.map((b, i) => (
              <span key={b.path} onClick={() => setBoltIdx(i)} style={{ cursor: 'pointer' }}
                title={b.path + ' · ' + b.stepsDone + '/' + b.stepsTotal + ' chặng có thật'}>
                <Chip tone={i === boltIdx ? 'agent' : 'pending'}>{b.id} · {b.stepsDone}/{b.stepsTotal}</Chip>
              </span>
            ))}
            <span style={{ width: 1, height: 16, background: 'var(--line)', margin: '0 4px' }} />
            {['list', 'flow', 'lifecycle'].map(v => (
              <span key={v} onClick={() => setView(v)} style={{ cursor: 'pointer' }}><Chip tone={view === v ? 'agent' : 'pending'}>{v}</Chip></span>
            ))}
          </div>

          {bolt && <BoltTrack steps={bolt.steps} stops={unit.stops || []} onDoc={onDoc} />}
          {!bolt && (unit.stops || []).some(s => s.state !== 'pending') && (
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {unit.stops.map(s => <StopCard key={s.key} s={s} onDoc={onDoc} />)}
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 8 }}>
                Không có bolt nên không có chặng nào để vẽ — nhưng các điểm dừng vẫn tính, vì việc vẫn
                được làm. Đây là chỗ nhìn ra unit đã đi qua những chỗ lẽ ra phải dừng.
              </div>
            </div>
          )}
          {!bolt && (
            <div style={{ padding: '16px 16px 6px', fontSize: 13.5, color: 'var(--muted)', lineHeight: 1.65 }}>
              <strong style={{ color: 'var(--accent)' }}>Unit này không có Bolt nào.</strong> Mỗi Unit phải chạy
              qua ít nhất một Bolt (<code style={{ fontFamily: 'var(--mono)' }}>units/{unit.id}/bolts/BOLT-NN/</code>),
              và trong Bolt là bốn chặng: Domain Design → Logical Design + ADR → Code + Unit Test.
              Thiếu thư mục bolt nghĩa là các chặng đó **không xảy ra** — hoặc xảy ra mà không để lại gì.
              Đừng dựng bù: design viết ngược từ code đã chạy là mô tả code đội lốt quyết định thiết kế.
            </div>
          )}

          {view === 'list' && (rows.length
            ? rows.map(t => <TaskRow key={t.id} {...t} onClick={() => onOpenTask(t)} />)
            : (
              <div style={{ padding: '16px 16px 18px', fontSize: 13.5, color: 'var(--muted)', lineHeight: 1.65 }}>
                {bolt
                  ? <React.Fragment>
                      Bolt <code style={{ fontFamily: 'var(--mono)' }}>{bolt.id}</code> chưa có
                      <code style={{ fontFamily: 'var(--mono)' }}> tasks.md</code>. Bảng trống vì
                      <strong> chưa lập file task</strong>, không phải vì chưa ai làm gì —
                      {unit.status === 'done'
                        ? ' unit đã đóng, nhiều khả năng nó chạy trước khi có luật ghi task xuống file.'
                        : ' /dlc-bolt sinh file này khi bolt bắt đầu.'}
                    </React.Fragment>
                  : 'Chưa có bolt thì cũng chưa có task board — task sinh ra bên trong bolt (chặng 5/6).'}
              </div>
            ))}

          {view === 'flow' && (
            <div style={{ padding: '0 14px 8px' }}>
              <MermaidDiagram chart={window.CT_DIAGRAMS.boltFlow} style={{ marginTop: 14 }}
                caption="Sơ đồ mẫu của một Bolt: ai bàn giao cho ai, và chỗ nào một reviewer phải ký trước khi đi tiếp. Đây là hình minh hoạ phương pháp, không phải task thật của unit này." />
            </div>
          )}
          {view === 'lifecycle' && (
            <div style={{ padding: '0 14px 8px' }}>
              <MermaidDiagram chart={window.CT_DIAGRAMS.taskLifecycle} style={{ marginTop: 14 }}
                caption="Vòng đời một task: claim → code → review → verdict. Hai lần request-changes cùng một điểm thì việc chuyển thành escalation của người." />
            </div>
          )}
        </Panel>
      )}

      {unit && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 16, alignItems: 'start' }}>
          <Panel title="Unit này" meta={unit.status}>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
              <Chip tone={unit.estimate > 5 ? 'blocked' : unit.estimate ? 'done' : 'pending'}>
                {unit.estimate ? unit.estimate.toFixed(1) + 'h' : 'chưa ước lượng'}
              </Chip>
              <Chip tone={unit.stories ? 'done' : 'blocked'}>{unit.stories} user story</Chip>
              <Chip tone={unit.nfrs ? 'done' : 'blocked'}>{unit.nfrs} NFR</Chip>
              <Chip tone={unit.riskCount ? 'done' : 'blocked'}>{unit.riskCount} rủi ro</Chip>
              {unit.descoped && <Chip tone="blocked">ngoài phạm vi</Chip>}
            </div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.9 }}>
              <div>trạng thái · {unit.status}{unit.rawStatus ? ' (spec.md ghi "' + unit.rawStatus + '")' : ''}</div>
              <div>bolt · {unit.bolts && unit.bolts.length ? unit.bolts.join(', ') : '— chưa vào construction'}</div>
              <div>task · {unit.tasks[0]}/{unit.tasks[1]} done</div>
              <div>evidence · {unit.evidence} file</div>
              <div>nguồn · {(unit.sources || []).join(', ') || '— chưa khai `sources:`'}</div>
            </div>
            {unit.problems && unit.problems.length > 0 && (
              <div style={{ marginTop: 10, fontSize: 12.5, color: 'var(--danger)' }}>Chưa đạt DoR: {unit.problems.join(' · ')}</div>
            )}
            <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
              {unit.specPath && <Button variant="secondary" size="sm" onClick={() => onDoc && onDoc(unit.specPath)}>Đọc spec.md</Button>}
              {onOpenUnit && <Button variant="ghost" size="sm" onClick={() => onOpenUnit(unit)}>Chi tiết unit →</Button>}
            </div>
          </Panel>

          <Panel title="Bolt của unit này" meta={byUnit.length + ' bolt'}>
            {byUnit.length ? byUnit.map(b => (
              <div key={b.path} style={{ padding: '6px 0', borderBottom: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
                  <IdCode variant="inline">{b.id}</IdCode>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }} title={b.path}>{b.path}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: b.stepsDone === b.stepsTotal ? 'var(--ok)' : 'var(--accent)' }}>
                    {b.stepsDone}/{b.stepsTotal} chặng
                  </span>
                </div>
                <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 2 }}>
                  {b.steps.filter(s => !s.exists).length
                    ? 'thiếu: ' + b.steps.filter(s => !s.exists).map(s => s.label).join(' · ')
                    : 'đủ cả sáu chặng'}
                </div>
              </div>
            )) : (
              <div style={{ fontSize: 13, color: 'var(--muted)', lineHeight: 1.6 }}>
                Không thư mục <code style={{ fontFamily: 'var(--mono)' }}>bolts/</code> nào trong
                <code style={{ fontFamily: 'var(--mono)' }}> units/{unit.id}/</code>. Đây là phép đo có/không
                trên đĩa — không suy từ tên bolt ghi trong HOF, vì tên đó là chuỗi tự do.
              </div>
            )}
          </Panel>
        </div>
      )}
    </div>
  );
}
window.BoltBoard = BoltBoard;
})();
