One-line: the "what's my situation" strip above the gate queue.

```jsx
<KpiStrip items={[
  { value: 2, label: 'Gates chờ tôi', tone: 'gate' },
  { value: 1, label: 'Escalations', tone: 'gate' },
  { value: 2, label: 'Bolts đang chạy', tone: 'agent' },
  { value: 3, label: 'Units done tuần này', tone: 'done' }
]} />
```

Keep it to counts a supervisor can act on. No sparklines, no deltas.
