One-line: use this for every process, comms or dependency diagram — never hand-draw SVG.

```jsx
<MermaidDiagram caption="Contract handshake giữa be-dev và fe-dev — mọi message có ID."
  chart={`sequenceDiagram
  participant FE as fe-dev
  participant BE as be-dev
  FE->>BE: MSG-0058 · clarification
  BE-->>FE: MSG-0060 · answer
`} />
```

Conventions that keep diagrams on-brand:
- Label nodes and edges with the real IDs (`MSG-0058`, `TSK-02`, `RV-012`) — mono is already the diagram font.
- Colour by meaning with `classDef`: amber `--accent` for anything waiting on a human (gates, escalation), blue `--blue` for agent/review activity, green `--ok` for done, default grey for pending.
- Keep lanes to the four agent groups (Pipeline · Review Board · Human · Learning) using `subgraph`.
- One idea per diagram; a caption sentence explains what the reader should take away.
