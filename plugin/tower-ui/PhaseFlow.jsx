(function () {
const NSpf = window.ControlTowerDesignSystem_68131c;
const { Panel, IdCode, Chip, StatusChip, Button } = NSpf;

const MARK = { done: '●', active: '◐', pending: '○', open: '◇', passed: '●', warn: '△', blocked: '△',
  returned: '↩' };
const COLOR = {
  done: 'var(--ok)', passed: 'var(--ok)', active: 'var(--blue)', open: 'var(--accent)',
  warn: 'var(--accent)', blocked: 'var(--danger)', pending: 'var(--muted)', returned: 'var(--danger)'
};

function StepRow({ step, onDoc, onGate }) {
  const st = step.status || 'pending';
  const isGate = !!step.gate;
  const clickable = (step.doc && onDoc) || (isGate && st === 'open' && onGate);
  return (
    <div onClick={() => {
      if (isGate && st === 'open' && onGate) onGate(step.gate);
      else if (step.doc && onDoc) onDoc(step.doc);
    }} style={{
      display: 'flex', gap: 10, alignItems: 'flex-start', padding: '9px 12px',
      borderTop: '1px solid var(--line)', cursor: clickable ? 'pointer' : 'default',
      background: isGate && st === 'open' ? 'var(--accent-bg)' : 'transparent'
    }}>
      <span style={{
        fontFamily: 'var(--mono)', fontSize: 13, lineHeight: '18px', width: 12, flex: 'none',
        color: COLOR[st] || 'var(--muted)'
      }}>{MARK[st] || '○'}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', gap: 7, alignItems: 'baseline', flexWrap: 'wrap' }}>
          <span style={{
            fontSize: 13.5, fontWeight: isGate ? 650 : 500,
            color: st === 'pending' ? 'var(--muted)' : 'var(--ink)'
          }}>{step.label}</span>
          {isGate && st === 'open' && <Chip tone="active">chờ bạn quyết</Chip>}
          {isGate && st === 'passed' && <Chip tone="done">đã qua</Chip>}
          {step.blocked && <Chip tone="blocked">bị chặn</Chip>}
          {step.doc && <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--blue)' }}>đọc ↗</span>}
        </div>
        {step.meta && <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>{step.meta}</div>}
      </div>
    </div>
  );
}

function PhaseColumn({ phase, current, onDoc, onGate }) {
  const isNow = current === phase.label.toLowerCase();
  return (
    <section style={{
      background: 'var(--surface)', border: '1px solid ' + (isNow ? 'var(--accent)' : 'var(--line)'),
      borderRadius: 'var(--radius-xl)', overflow: 'hidden', display: 'flex', flexDirection: 'column'
    }}>
      <header style={{
        padding: '11px 14px', background: isNow ? 'var(--accent-bg)' : 'var(--surface-2)',
        display: 'flex', alignItems: 'center', gap: 8
      }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: '-0.01em' }}>{phase.label}</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--muted)' }}>{phase.stages}</div>
        </div>
        {isNow && <StatusChip tone="gate">ĐANG Ở ĐÂY</StatusChip>}
      </header>
      {phase.steps.map(s => <StepRow key={s.key} step={s} onDoc={onDoc} onGate={onGate} />)}
    </section>
  );
}

function LaneCell({ cell, tone }) {
  const st = cell.state || 'pending';
  /* Ô Construction mang thêm mạch điểm dừng: ai đang giữ việc, và điểm dừng nào đã bị đi qua.
     Chấm nhỏ = một điểm dừng; hổ phách = chờ NGƯỜI, xanh = chờ agent, đỏ = trả lại/bỏ qua. */
  const stops = cell.stops || [];
  const dot = s => (s.state === 'passed' ? 'var(--ok)'
    : s.state === 'returned' || s.state === 'skipped' ? 'var(--danger)'
    : s.state === 'waiting' ? (s.holder === 'human' ? 'var(--accent)' : 'var(--blue)') : 'var(--line)');
  return (
    <div style={{
      padding: '8px 10px', borderLeft: '1px solid var(--line)', minWidth: 0,
      background: st === 'warn' ? 'var(--accent-bg)' : 'transparent'
    }}>
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: COLOR[st] || 'var(--muted)' }}>{MARK[st] || '○'}</span>
        <span style={{ fontSize: 12, color: st === 'pending' ? 'var(--muted)' : 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{cell.meta}</span>
        {cell.holder === 'human' && <Chip tone="active">người</Chip>}
      </div>
      {stops.length > 0 && (
        <div style={{ display: 'flex', gap: 3, marginTop: 5, alignItems: 'center' }}>
          {stops.map(s => (
            <span key={s.key} title={s.label + ' — ' + (s.state === 'waiting'
              ? (s.holder === 'human' ? 'đang chờ NGƯỜI' : 'đang chờ agent')
              : s.state === 'skipped' ? 'ĐÃ ĐI QUA MÀ KHÔNG DỪNG' : s.state) + ': ' + s.meta}
              style={{ width: 6, height: 6, borderRadius: 999, background: dot(s), flex: 'none' }} />
          ))}
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--muted)', marginLeft: 2 }}>điểm dừng</span>
        </div>
      )}
      {typeof cell.pct === 'number' && cell.pct > 0 && (
        <div style={{ height: 3, background: 'var(--surface-2)', borderRadius: 2, marginTop: 6, overflow: 'hidden' }}>
          <div style={{ width: cell.pct + '%', height: '100%', background: 'var(--ok)' }} />
        </div>
      )}
    </div>
  );
}

function UnitLanes({ lanes, onOpenUnit }) {
  if (!lanes.length) {
    return (
      <div style={{ padding: '28px 16px', textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>
        Chưa có Unit nào — Unit xuất hiện sau khi Intent Plan (Gate A) được duyệt và phân rã chốt tại Gate D.
      </div>
    );
  }
  return (
    <div>
      <div style={{
        display: 'grid', gridTemplateColumns: '220px repeat(3, minmax(0,1fr))',
        fontFamily: 'var(--mono)', fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase',
        color: 'var(--muted)', background: 'var(--surface-2)', borderBottom: '1px solid var(--line)'
      }}>
        <div style={{ padding: '7px 12px' }}>Unit</div>
        <div style={{ padding: '7px 10px', borderLeft: '1px solid var(--line)' }}>Inception</div>
        <div style={{ padding: '7px 10px', borderLeft: '1px solid var(--line)' }}>Construction</div>
        <div style={{ padding: '7px 10px', borderLeft: '1px solid var(--line)' }}>Operations</div>
      </div>
      {lanes.map(l => (
        <div key={l.id} onClick={() => onOpenUnit && onOpenUnit(l.id)} style={{
          display: 'grid', gridTemplateColumns: '220px repeat(3, minmax(0,1fr))',
          borderBottom: '1px solid var(--line)', cursor: onOpenUnit ? 'pointer' : 'default'
        }}>
          <div style={{ padding: '8px 12px', minWidth: 0 }}>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <IdCode style={{ fontSize: 11.5 }}>{l.id}</IdCode>
              <span style={{
                fontFamily: 'var(--mono)', fontSize: 10.5,
                color: l.estimate > 5 ? 'var(--danger)' : 'var(--muted)'
              }}>{l.estimate ? l.estimate.toFixed(1) + 'h' : '—'}</span>
              {l.provisional && <Chip tone="agent">dự kiến</Chip>}
            </div>
            <div style={{ fontSize: 12.5, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{l.name}</div>
            {l.problems && l.problems.length > 0 && (
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--danger)', marginTop: 3 }}>△ {l.problems.join(' · ')}</div>
            )}
          </div>
          <LaneCell cell={l.inception} />
          <LaneCell cell={l.construction} />
          <LaneCell cell={l.operations} />
        </div>
      ))}
    </div>
  );
}

function PhaseFlow({ data, intentId, gates, onDoc, onGate, onOpenUnit, onSelectIntent, onMetric }) {
  const flow = (data.flowByIntent || {})[intentId];
  const src = (data.sourcesByIntent || {})[intentId];
  const intent = data.intents.find(x => x.id === intentId) || data.intents[0];
  if (!flow || !intent) {
    return <div style={{ padding: 24, color: 'var(--muted)' }}>Chưa có intent nào trong <code>.ai-dlc/</code>. Chạy <code>/dlc-intent</code> để bắt đầu.</div>;
  }
  const c = (src && src.counts) || {};
  const met = (data.metricsByIntent || {})[intentId] || {};
  const units = data.unitsByIntent[intentId] || [];
  const overEst = units.filter(u => u.estimate > 5).length;
  const incomplete = units.filter(u => u.problems && u.problems.length).length;

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        {data.intents.map(x => (
          <span key={x.id} onClick={() => onSelectIntent && onSelectIntent(x.id)} style={{ cursor: 'pointer' }}>
            <Chip tone={x.id === intentId ? 'agent' : x.gate ? 'active' : 'pending'}>{x.id} · {x.name.slice(0, 34)}</Chip>
          </span>
        ))}
      </div>

      {/* thanh sức khỏe của luồng — ba con số quyết định chất lượng đầu vào */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))',
        border: '1px solid var(--line)', borderRadius: 'var(--radius-lg)', background: 'var(--surface)', overflow: 'hidden'
      }}>
        {['sources.read', 'sources.planned', 'sources.conflicts', 'units.count', 'units.estimate',
          'units.problems', 'units.releasable', 'tasks.done', 'units.done', 'units.oneSession',
          'units.reviewed', 'units.artifacts',
          'phase.consistency']
          .map(key => met[key]).filter(Boolean).map((k, i) => (
          <div key={k.key} onClick={() => onMetric && onMetric(k)} title="Bấm để xem số này ở đâu ra"
            style={{
              padding: '10px 16px', borderLeft: i ? '1px solid var(--line)' : 'none',
              cursor: onMetric ? 'pointer' : 'default'
            }}>
            <div style={{
              fontFamily: 'var(--mono)', fontSize: 21, fontWeight: 700, lineHeight: 1.1,
              color: k.tone === 'gate' ? 'var(--accent)' : k.tone === 'done' ? 'var(--ok)' : 'var(--blue)'
            }}>{k.value}{(k.warnings || []).length ? <span style={{ color: 'var(--accent)', fontSize: 13 }}> ⚠</span> : null}</div>
            <div style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: 3 }}>
              {k.label} <span style={{ opacity: 0.55 }}>ⓘ</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 14, alignItems: 'start' }}>
        {flow.phases.map(p => (
          <PhaseColumn key={p.label} phase={p} current={flow.current} onDoc={onDoc} onGate={onGate} />
        ))}
      </div>

      <Panel title="Mạch từng Unit xuyên ba pha" meta={units.length + ' unit' } pad={false}>
        <UnitLanes lanes={flow.lanes} onOpenUnit={onOpenUnit} />
      </Panel>

      {src && src.rows && src.rows.length > 0 && (
        <Panel title="Nguồn đã lên kế hoạch đọc" meta={(c.read || 0) + ' read · ' + (c.planned || 0) + ' planned · ' + (c.missing || 0) + ' missing'} pad={false}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 12.5 }}>
              <thead>
                <tr style={{ background: 'var(--surface-2)' }}>
                  {['#', 'Nguồn', 'Thông tin cần lấy', 'Ưu tiên', 'Trạng thái', 'Evidence / phát hiện'].map(h => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '7px 10px', fontFamily: 'var(--mono)', fontSize: 10.5,
                      letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--muted)',
                      borderBottom: '1px solid var(--line)', whiteSpace: 'nowrap'
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {src.rows.map(r => {
                  const tone = r.status === 'read' ? 'done' : r.status === 'planned' ? 'active'
                    : r.status === 'missing' ? 'blocked' : 'pending';
                  return (
                    <tr key={r.id}>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)', fontFamily: 'var(--mono)', color: 'var(--blue)' }}>{r.id}</td>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)', fontFamily: 'var(--mono)', fontSize: 11.5 }}>{r.source}</td>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)', color: 'var(--muted)' }}>{r.need}</td>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)' }}>{r.prio}</td>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)' }}>
                        <Chip tone={tone}>{r.status}{r.added ? ' [ADDED]' : ''}</Chip>
                      </td>
                      <td style={{ padding: '7px 10px', borderBottom: '1px solid var(--line)', color: 'var(--muted)' }}>{r.evidence || '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  );
}

window.PhaseFlow = PhaseFlow;
window.UnitLanes = UnitLanes;
})();
