One-line: the step-by-step walkthrough used in blueprint and dry-run documents.

```jsx
<Timeline>
  <TimelineItem actor="intent-analyst + ba-reviewer" heading="Stage 1 · Request → Intent">…</TimelineItem>
  <TimelineItem actor="Validation Mob" lane="human" heading="Stage 3 · Context Validation" last>…</TimelineItem>
</Timeline>
```

Human steps get the solid amber node; every stop inside a step is a `GateStop`.
