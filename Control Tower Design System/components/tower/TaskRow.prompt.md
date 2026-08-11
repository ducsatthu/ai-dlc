One-line: task board row; always show claim, approver and dependency — that trio is the governance rule made visible.

```jsx
<TaskRow id="TSK-04" status="blocked" title="FE: SCR-REL-11 popup nối API thật"
  approver="frontend-reviewer" dependsOn="TSK-02" />
```

Statuses map to fixed tones: done=green, in-progress/review=amber, claimed=blue, blocked=red, todo=grey.
