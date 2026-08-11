// Shared diagram sources — imported by the docs kit and the component card.
window.CT_DIAGRAMS = {
  contract: `sequenceDiagram
  autonumber
  participant BE as be-dev
  participant FE as fe-dev
  participant TL as tech-lead-reviewer
  BE->>FE: MSG-0057 · handoff — contract.md v1 draft
  FE->>BE: MSG-0058 · clarification — status enum trả code hay label?
  BE->>FE: MSG-0059 · question — FE có bảng i18n sẵn không?
  FE-->>BE: MSG-0060 · answer — chốt: BE trả code, FE map i18n
  BE->>FE: MSG-0061 · handoff — contract.md v2 FROZEN
  Note over BE,FE: TSK-03 chạy song song với mock đúng shape
  FE-->>TL: escalate nếu tranh cãi lộ ra design sai từ gốc`,

  escalation: `flowchart LR
  A["RV lần 1<br/>request-changes"] --> B["be-dev sửa"]
  B --> C["RV lần 2<br/>request-changes"]
  C --> D{"cùng một điểm?"}
  D -- "không" --> B
  D -- "có" --> E["ESCALATION<br/>đẩy lên tower"]
  E --> H["Human quyết<br/>ghi DEC"]
  H --> F["retro-keeper<br/>LL + patch checklist"]
  classDef human fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef agent fill:var(--blue-bg),stroke:var(--blue),color:var(--blue);
  classDef done fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  class E,H human; class A,B,C agent; class F done;`,

  topology: `flowchart LR
  PIPE["<b>Pipeline · 9 agents</b><br/>orchestrator · intent-analyst<br/>context-archaeologist · context-validator<br/>unit-planner · bolt-coordinator<br/>be-dev · fe-dev · acceptance-recorder"]
  REV["<b>Review Board · 7 agents</b><br/>ba · pm-po · tech-lead · security<br/>backend · frontend · qa"]
  RK["<b>Learning</b><br/>retro-keeper"]
  BUS(["<b>Comms Bus</b><br/>mọi MSG · RV · DEC là file có ID"])
  TOWER["<b>Control Tower</b><br/>đọc bus, hiển thị"]
  S["<b>Human supervisor</b><br/>Gate A–G · quyết định"]
  PIPE -- "handoff · question" --> BUS
  REV -- "verdict · finding" --> BUS
  BUS --> TOWER --> S
  S -- "DEC" --> PIPE
  BUS -- "sau release" --> RK
  RK -. "patch checklist" .-> REV
  classDef human fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef review fill:var(--blue-bg),stroke:var(--blue),color:var(--blue);
  classDef learn fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  classDef pipe fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class S,TOWER human; class REV,BUS review; class RK learn; class PIPE pipe;`,

  gates: `flowchart TB
  subgraph R1["Discovery"]
    direction LR
    S1["1 Request"] --> GA{"◇ A"} --> S2["2 Discovery"] --> S3["3 Validation"] --> GB{"◇ B"} --> S4["4 Clarify"] --> GC{"◇ C"}
  end
  subgraph R2["Delivery"]
    direction LR
    S5["5 Units"] --> GD{"◇ D"} --> S6["6 Construction"] --> GE{"◇ E"} --> S7["7 Acceptance"] --> GF{"◇ F"} --> S8["8 Release"] --> GG{"◇ G"}
  end
  R1 --> R2
  classDef gate fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef stage fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class GA,GB,GC,GD,GE,GF,GG gate; class S1,S2,S3,S4,S5,S6,S7,S8 stage;`,

  tasks: `flowchart LR
  T1["TSK-01 · done<br/>API contract freeze<br/>be-dev"] --> T2["TSK-02 · in-progress<br/>BE migration + service<br/>be-dev → backend-reviewer"]
  T1 --> T3["TSK-03 · in-progress<br/>FE SCR-REL-10 (mock)<br/>fe-dev → frontend-reviewer"]
  T2 --> T4["TSK-04 · blocked<br/>FE popup nối API thật<br/>chờ TSK-02 được duyệt"]
  T3 --> T5["TSK-05 · todo<br/>Integration E2E<br/>approver qa-reviewer"]
  T4 --> T5
  classDef done fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  classDef act fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef block fill:var(--danger-bg),stroke:var(--danger),color:var(--danger);
  class T1 done; class T2,T3 act; class T4 block;`,

  trace: `flowchart LR
  C["code"] --> D["design.md"] --> SP["UOW-01/spec.md"] --> DEC["DEC-0015"] --> RV["RV-010"] --> MSG["MSG-0058"] --> INT["INT-001"]
  classDef n fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class C,D,SP,DEC,RV,MSG,INT n;`
};

window.CT_DIAGRAMS.boltFlow = `flowchart TB
  BC(["bolt-coordinator<br/>chia task board · assign approver"])
  T1["<b>TSK-01</b> · done<br/>claim: be-dev<br/>duyệt: fe-dev + tech-lead"]
  T2["<b>TSK-02</b> · in-progress<br/>claim: be-dev<br/>approver: backend-reviewer"]
  T3["<b>TSK-03</b> · in-progress<br/>claim: fe-dev<br/>approver: frontend-reviewer"]
  T4["<b>TSK-04</b> · blocked<br/>chưa claim — fe-dev<br/>approver: frontend-reviewer"]
  T5["<b>TSK-05</b> · todo<br/>Integration E2E<br/>approver: qa-reviewer"]
  GE{"◇ Gate E<br/>người duyệt demo"}
  ESC["escalation<br/>chờ người"]
  BC --> T1
  T1 -- "contract FROZEN v2" --> T2
  T1 -- "mock đúng shape" --> T3
  T2 -- "approver ký" --> T4
  T2 -. "×2 request-changes" .-> ESC
  T3 --> T5
  T4 --> T5
  T5 --> GE
  classDef human fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef done fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  classDef act fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef block fill:var(--danger-bg),stroke:var(--danger),color:var(--danger);
  classDef work fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class GE,ESC human; class T1 done; class T2,T3 act; class T4 block; class T5,BC work;`;

window.CT_DIAGRAMS.taskLifecycle = `flowchart LR
  A["todo<br/>approver đã assign sẵn"] --> B["claimed<br/>agent nhận việc"]
  B --> C["in-progress<br/>code + tests"]
  C --> D["review<br/>gửi review-request (MSG)"]
  D --> E{"approver<br/>verdict"}
  E -- "approve" --> F["done"]
  E -- "request-changes" --> C
  E -- "×2 cùng một điểm" --> G["escalation<br/>người quyết"]
  F --> H["task phụ thuộc<br/>được phép claim"]
  A2["blocked<br/>task phụ thuộc chưa được duyệt"] -.-> A
  classDef human fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef review fill:var(--blue-bg),stroke:var(--blue),color:var(--blue);
  classDef done fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  classDef work fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class G human; class D,E review; class F,H done; class A,B,C work;
  class A2 human;`;

window.CT_DIAGRAMS.hierarchy = `flowchart TB
  CR["<b>Customer Request</b><br/>thứ khách hàng gửi — chỉ là đầu vào"]
  P["<b>Dự án</b> · spoke-project-control-tower"]
  CR --> P
  P --> I1["<b>INT-001</b> · Intent<br/>Phase 2 PCT — phát triển tiếp"]
  P --> I2["<b>INT-004</b> · Intent<br/>Weekly report chậm — Optimize NFR"]
  P --> I3["<b>INT-006</b> · Intent<br/>Sai trạng thái RFE/NOID — Fix defect"]
  I1 --> U1["<b>UOW-01</b> · Unit<br/>Release Planning"]
  I1 --> U2["<b>UOW-02</b> · Unit<br/>Milestone Timeline"]
  I1 --> U3["<b>UOW-03</b> · Unit<br/>Liên kết + badge"]
  I1 --> U4["<b>UOW-04</b> · Unit<br/>Backlog Integration"]
  U1 --> B1(["<b>Bolt 1</b> — một vòng build–validate cho UOW-01<br/>vài giờ đến vài ngày"])
  U2 --> B2(["<b>Bolt 2</b> — cho UOW-02"])
  B1 --> T1["TSK-01 · be-dev<br/>API contract"]
  B1 --> T2["TSK-02 · be-dev → backend-reviewer<br/>migration + service"]
  B1 --> T3["TSK-03 · fe-dev → frontend-reviewer<br/>SCR-REL-10"]
  B1 --> T5["TSK-05 · qa-reviewer<br/>Integration E2E"]
  classDef intent fill:var(--ok-bg),stroke:var(--ok),color:var(--ok);
  classDef unit fill:var(--blue-bg),stroke:var(--blue),color:var(--blue);
  classDef bolt fill:var(--accent-bg),stroke:var(--accent),color:var(--accent);
  classDef work fill:var(--surface-2),stroke:var(--line),color:var(--ink);
  class I1,I2,I3 intent; class U1,U2,U3,U4 unit; class B1,B2 bolt; class T1,T2,T3,T5,P,CR work;`;
