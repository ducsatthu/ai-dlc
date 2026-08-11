import React from 'react';

export function DataTable({ columns = [], rows = [], monoFirst = true, style, ...rest }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--fs-body-sm)', ...style }} {...rest}>
        <thead>
          <tr>{columns.map((c, i) => (
            <th key={i} style={{
              fontFamily: 'var(--mono)', fontSize: '11.5px', letterSpacing: 'var(--ls-label)',
              textTransform: 'uppercase', color: 'var(--muted)', textAlign: 'left',
              padding: '8px 12px', borderBottom: '2px solid var(--ink)', fontWeight: 'var(--fw-medium)', whiteSpace: 'nowrap'
            }}>{c}</th>
          ))}</tr>
        </thead>
        <tbody>
          {rows.map((r, ri) => (
            <tr key={ri}>{r.map((cell, ci) => (
              <td key={ci} style={{
                padding: 'var(--pad-cell)', borderBottom: '1px solid var(--line)', verticalAlign: 'top',
                fontFamily: monoFirst && ci === 0 ? 'var(--mono)' : undefined,
                fontSize: monoFirst && ci === 0 ? 'var(--fs-sm)' : undefined,
                whiteSpace: monoFirst && ci === 0 ? 'nowrap' : undefined
              }}>{cell}</td>
            ))}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
