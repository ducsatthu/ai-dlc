import React from 'react';
import { IdCode } from '../core/IdCode.jsx';
import { StageStrip } from './StageStrip.jsx';
import { AgentAvatar } from './AgentAvatar.jsx';

export function PipelineRow({ id, name, current = 1, gate, holder, holderLane = 'pipeline', onClick, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'flex', alignItems: 'center', gap: 'var(--sp-6)', flexWrap: 'wrap',
        padding: '10px 16px', borderBottom: '1px solid var(--line)',
        background: hover && onClick ? 'var(--surface-2)' : 'transparent',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'background var(--dur-fast) var(--ease-standard)', ...style
      }} {...rest}>
      <IdCode style={{ width: 72, flex: 'none', fontSize: 'var(--fs-caption)' }}>{id}</IdCode>
      <span style={{ fontSize: 'var(--fs-sm)', flex: '1 1 220px', minWidth: 0 }}>{name}</span>
      <StageStrip current={current} gate={gate} />
      {holder && <AgentAvatar name={holder} lane={holderLane} />}
    </div>
  );
}
