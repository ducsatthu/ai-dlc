import React from 'react';
import { Chip } from '../core/Chip.jsx';

export const STAGES = ['1 Request','2 Discovery','3 Validation','4 Clarify','5 Units','6 Construction','7 Acceptance','8 Release'];

export function StageStrip({ current = 1, gate, labels = false, compact = false, style, ...rest }) {
  return (
    <div style={{ display: 'flex', gap: 'var(--gap-chip)', alignItems: 'center', flexWrap: 'wrap', ...style }} {...rest}>
      {STAGES.map((s, i) => {
        const n = i + 1;
        const tone = n < current ? 'done' : n === current ? 'active' : 'pending';
        const text = labels ? s : String(n);
        return <Chip key={n} tone={tone}>{n === current && gate ? text + ' ◇' + gate : text}</Chip>;
      })}
      {compact && null}
    </div>
  );
}
