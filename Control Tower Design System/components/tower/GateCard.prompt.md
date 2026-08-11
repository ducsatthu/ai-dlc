One-line: the highest-priority object in the product — everything waiting on the human supervisor is a GateCard.

```jsx
<GateCard gate="D" target="INT-001" defaultExpanded
  title="Duyệt scope 4 Units + DoD v1"
  brief="unit-planner đề xuất 4 Units; pm-po verdict approve-with-notes (RV-010)."
  options={['Approve cả 4 Units — UOW-04 có risk chờ LakeHouse', 'Approve 01–03, quyết riêng 04']}
  recommendation="approve 01–03, quyết riêng 04"
  evidence={['RV-010', 'risks.md']} />
```

`kind="escalation"` for the 2×-request-changes disagreement case. Never add a fourth action; never let a card be dismissed without a decision.
