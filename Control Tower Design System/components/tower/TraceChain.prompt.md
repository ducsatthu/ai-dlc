One-line: use wherever a trace chain would otherwise be written as `a → b → c` text — drawers, evidence panels, message details.

```jsx
<TraceChain direction="vertical" steps={[
  { kind: 'code', id: 'releases.service.ts', note: 'dòng 42 — validate unique name' },
  { kind: 'spec', id: 'UOW-01/spec.md', note: 'AC-03' },
  { kind: 'dec', id: 'DEC-0015', note: 'Gate A — scope Phase 2' },
  { kind: 'intent', id: 'INT-001' }
]} />
```

Colour follows the system: amber = a human decision (dec, gate), blue = agent/review record (rv, msg), green = the intent it all rolls up to, grey = artifacts. Vertical in a drawer, horizontal in a full-width panel.
