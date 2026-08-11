/* @ds-bundle: {"format":4,"namespace":"ControlTowerDesignSystem_68131c","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Callout","sourcePath":"components/core/Callout.jsx"},{"name":"Chip","sourcePath":"components/core/Chip.jsx"},{"name":"DataTable","sourcePath":"components/core/DataTable.jsx"},{"name":"Eyebrow","sourcePath":"components/core/Eyebrow.jsx"},{"name":"IdCode","sourcePath":"components/core/IdCode.jsx"},{"name":"Panel","sourcePath":"components/core/Panel.jsx"},{"name":"StatusChip","sourcePath":"components/core/StatusChip.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"MermaidDiagram","sourcePath":"components/diagrams/MermaidDiagram.jsx"},{"name":"AgentAvatar","sourcePath":"components/tower/AgentAvatar.jsx"},{"name":"AgentWorkCard","sourcePath":"components/tower/AgentWorkCard.jsx"},{"name":"FeedItem","sourcePath":"components/tower/FeedItem.jsx"},{"name":"GateCard","sourcePath":"components/tower/GateCard.jsx"},{"name":"GateStop","sourcePath":"components/tower/GateStop.jsx"},{"name":"KpiStrip","sourcePath":"components/tower/KpiStrip.jsx"},{"name":"PipelineRow","sourcePath":"components/tower/PipelineRow.jsx"},{"name":"STAGES","sourcePath":"components/tower/StageStrip.jsx"},{"name":"StageStrip","sourcePath":"components/tower/StageStrip.jsx"},{"name":"TaskRow","sourcePath":"components/tower/TaskRow.jsx"},{"name":"TimelineItem","sourcePath":"components/tower/TimelineItem.jsx"},{"name":"Timeline","sourcePath":"components/tower/TimelineItem.jsx"},{"name":"TraceChain","sourcePath":"components/tower/TraceChain.jsx"},{"name":"VerdictBadge","sourcePath":"components/tower/VerdictBadge.jsx"}],"sourceHashes":{"components/core/Button.jsx":"70eb08ee13fa","components/core/Callout.jsx":"29eef8cf9ceb","components/core/Chip.jsx":"6652d45c0a40","components/core/DataTable.jsx":"c8e87e1b6a66","components/core/Eyebrow.jsx":"bd3e09f77d1c","components/core/IdCode.jsx":"0b397a54e70e","components/core/Panel.jsx":"01ec1d4b2698","components/core/StatusChip.jsx":"8acb90e04f82","components/core/Tag.jsx":"200805c08813","components/diagrams/DIAGRAMS.js":"25dad37eae2e","components/diagrams/MermaidDiagram.jsx":"0b6485cf054d","components/tower/AgentAvatar.jsx":"98d28630804e","components/tower/AgentWorkCard.jsx":"449e86abb656","components/tower/FeedItem.jsx":"df892ef53a88","components/tower/GateCard.jsx":"a3f3bcc85dcd","components/tower/GateStop.jsx":"5d23d458cff8","components/tower/KpiStrip.jsx":"cee977030a8d","components/tower/PipelineRow.jsx":"09e37fca490e","components/tower/StageStrip.jsx":"1ba7bcee7a3b","components/tower/TaskRow.jsx":"5a98d7b3af58","components/tower/TimelineItem.jsx":"145c2b006c3f","components/tower/TraceChain.jsx":"4e0d73230d88","components/tower/VerdictBadge.jsx":"53ff345a977d","ui_kits/control-tower/App.jsx":"882ed35c9943","ui_kits/control-tower/BoltBoard.jsx":"8b4b03bf0ab4","ui_kits/control-tower/CommsReviews.jsx":"29acd26f1b67","ui_kits/control-tower/Governance.jsx":"e340c2906e66","ui_kits/control-tower/IntentDetail.jsx":"b4e809e55559","ui_kits/control-tower/IntentList.jsx":"3fe75b45e97d","ui_kits/control-tower/MissionControl.jsx":"7e17c4066be6","ui_kits/control-tower/Shell.jsx":"5bc2603cb2a3","ui_kits/control-tower/data.js":"41cedb719337","ui_kits/engineering-docs/BlueprintDoc.jsx":"e9a5c5b4692e"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.ControlTowerDesignSystem_68131c = window.ControlTowerDesignSystem_68131c || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const SIZES = {
  sm: {
    padding: '5px 12px',
    fontSize: 'var(--fs-mono-xs)',
    letterSpacing: 'var(--ls-chip)'
  },
  md: {
    padding: '8px 16px',
    fontSize: 'var(--fs-sm)',
    letterSpacing: '0.04em'
  },
  lg: {
    padding: '10px 20px',
    fontSize: 'var(--fs-body-sm)',
    letterSpacing: '0.04em'
  }
};
const VARIANTS = {
  primary: {
    color: 'var(--on-accent)',
    background: 'var(--accent)',
    borderColor: 'var(--accent)'
  },
  secondary: {
    color: 'var(--ink)',
    background: 'var(--surface)',
    borderColor: 'var(--line)'
  },
  ghost: {
    color: 'var(--muted)',
    background: 'transparent',
    borderColor: 'transparent'
  },
  danger: {
    color: 'var(--danger)',
    background: 'var(--danger-bg)',
    borderColor: 'var(--danger)'
  },
  ok: {
    color: 'var(--ok)',
    background: 'var(--ok-bg)',
    borderColor: 'var(--ok)'
  }
};
function Button({
  variant = 'secondary',
  size = 'md',
  disabled = false,
  full = false,
  children,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const v = VARIANTS[variant] || VARIANTS.secondary;
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    disabled: disabled,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      fontFamily: 'var(--mono)',
      fontWeight: 'var(--fw-medium)',
      textTransform: 'uppercase',
      borderRadius: 'var(--radius-sm)',
      borderWidth: 1,
      borderStyle: 'solid',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.45 : hover ? 0.86 : 1,
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--sp-3)',
      width: full ? '100%' : undefined,
      justifyContent: 'center',
      transition: 'opacity var(--dur-fast) var(--ease-standard)',
      ...SIZES[size],
      ...v,
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Callout.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  agent: 'var(--blue)',
  gate: 'var(--accent)',
  done: 'var(--ok)'
};
const BGS = {
  agent: 'var(--blue-bg)',
  gate: 'var(--accent-bg)',
  done: 'var(--ok-bg)'
};
function Callout({
  tone = 'agent',
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      borderLeft: '3px solid ' + TONES[tone],
      background: BGS[tone],
      borderRadius: '0 var(--radius-lg) var(--radius-lg) 0',
      padding: '12px 18px',
      margin: '16px 0',
      fontSize: 'var(--fs-body-sm)',
      maxWidth: 'var(--measure-note)',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Callout });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Callout.jsx", error: String((e && e.message) || e) }); }

// components/core/Chip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  pending: {
    color: 'var(--muted)',
    background: 'transparent',
    borderColor: 'var(--line)'
  },
  done: {
    color: 'var(--ok)',
    background: 'var(--ok-bg)',
    borderColor: 'var(--ok)'
  },
  active: {
    color: 'var(--accent)',
    background: 'var(--accent-bg)',
    borderColor: 'var(--accent)'
  },
  agent: {
    color: 'var(--blue)',
    background: 'var(--blue-bg)',
    borderColor: 'var(--blue)'
  },
  blocked: {
    color: 'var(--danger)',
    background: 'var(--danger-bg)',
    borderColor: 'var(--danger)'
  },
  here: {
    color: 'var(--text-invert)',
    background: 'var(--accent)',
    borderColor: 'var(--accent)',
    fontWeight: 'var(--fw-bold)'
  },
  neutral: {
    color: 'var(--ink)',
    background: 'var(--surface-2)',
    borderColor: 'var(--line)'
  }
};
function Chip({
  tone = 'pending',
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-micro)',
      padding: '3px 7px',
      borderRadius: 'var(--radius-chip)',
      borderWidth: 1,
      borderStyle: 'solid',
      whiteSpace: 'nowrap',
      display: 'inline-block',
      ...TONES[tone],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Chip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Chip.jsx", error: String((e && e.message) || e) }); }

// components/core/DataTable.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function DataTable({
  columns = [],
  rows = [],
  monoFirst = true,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      overflowX: 'auto'
    }
  }, /*#__PURE__*/React.createElement("table", _extends({
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      fontSize: 'var(--fs-body-sm)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, columns.map((c, i) => /*#__PURE__*/React.createElement("th", {
    key: i,
    style: {
      fontFamily: 'var(--mono)',
      fontSize: '11.5px',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      textAlign: 'left',
      padding: '8px 12px',
      borderBottom: '2px solid var(--ink)',
      fontWeight: 'var(--fw-medium)',
      whiteSpace: 'nowrap'
    }
  }, c)))), /*#__PURE__*/React.createElement("tbody", null, rows.map((r, ri) => /*#__PURE__*/React.createElement("tr", {
    key: ri
  }, r.map((cell, ci) => /*#__PURE__*/React.createElement("td", {
    key: ci,
    style: {
      padding: 'var(--pad-cell)',
      borderBottom: '1px solid var(--line)',
      verticalAlign: 'top',
      fontFamily: monoFirst && ci === 0 ? 'var(--mono)' : undefined,
      fontSize: monoFirst && ci === 0 ? 'var(--fs-sm)' : undefined,
      whiteSpace: monoFirst && ci === 0 ? 'nowrap' : undefined
    }
  }, cell)))))));
}
Object.assign(__ds_scope, { DataTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/DataTable.jsx", error: String((e && e.message) || e) }); }

// components/core/Eyebrow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Eyebrow({
  children,
  rule = true,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--sp-6)',
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-caption)',
      letterSpacing: 'var(--ls-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--accent)',
      marginBottom: 'var(--sp-4)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", null, children), rule && /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      borderTop: '1px solid var(--line)',
      transform: 'translateY(-3px)'
    }
  }));
}
Object.assign(__ds_scope, { Eyebrow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Eyebrow.jsx", error: String((e && e.message) || e) }); }

// components/core/IdCode.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function IdCode({
  variant = 'plain',
  children,
  style,
  ...rest
}) {
  const base = {
    fontFamily: 'var(--mono)',
    whiteSpace: 'nowrap'
  };
  const variants = {
    plain: {
      fontSize: 'var(--fs-sm)',
      color: 'var(--muted)'
    },
    inline: {
      fontSize: '0.92em',
      color: 'var(--ink)',
      background: 'var(--surface-2)',
      padding: '1px 5px',
      borderRadius: 'var(--radius-chip)'
    },
    artifact: {
      fontSize: 'var(--fs-caption)',
      color: 'var(--ink)',
      background: 'var(--surface-2)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-sm)',
      padding: '2px 8px',
      display: 'inline-block',
      margin: '2px 4px 2px 0'
    }
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      ...base,
      ...variants[variant],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { IdCode });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/IdCode.jsx", error: String((e && e.message) || e) }); }

// components/core/Panel.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Panel({
  title,
  meta,
  pad = true,
  flush = false,
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: 'var(--surface)',
      border: '1px solid var(--line)',
      borderRadius: flush ? 0 : 'var(--radius-xl)',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      minHeight: 0,
      ...style
    }
  }, rest), title && /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 'var(--sp-6)',
      padding: '10px 16px',
      borderBottom: '1px solid var(--line)',
      background: 'var(--surface-2)'
    }
  }, /*#__PURE__*/React.createElement("h5", {
    style: {
      margin: 0,
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      fontWeight: 'var(--fw-medium)'
    }
  }, title), meta && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--muted)'
    }
  }, meta)), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: pad ? '16px 20px' : 0,
      minHeight: 0,
      overflow: 'auto',
      flex: 1
    }
  }, children));
}
Object.assign(__ds_scope, { Panel });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Panel.jsx", error: String((e && e.message) || e) }); }

// components/core/StatusChip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  gate: 'var(--accent)',
  agent: 'var(--blue)',
  done: 'var(--ok)',
  danger: 'var(--danger)',
  muted: 'var(--muted)'
};
const BGS = {
  gate: 'var(--accent-bg)',
  agent: 'var(--blue-bg)',
  done: 'var(--ok-bg)',
  danger: 'var(--danger-bg)',
  muted: 'transparent'
};
function StatusChip({
  tone = 'gate',
  dot = true,
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-caption)',
      letterSpacing: 'var(--ls-chip)',
      color: TONES[tone],
      background: BGS[tone],
      border: '1px solid ' + TONES[tone],
      padding: '5px 12px',
      borderRadius: 'var(--radius-pill)',
      whiteSpace: 'nowrap',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--sp-3)',
      ...style
    }
  }, rest), dot && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 7,
      height: 7,
      borderRadius: '50%',
      background: TONES[tone],
      flex: 'none'
    }
  }), children);
}
Object.assign(__ds_scope, { StatusChip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/StatusChip.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const KINDS = {
  pipeline: {
    color: 'var(--ink)',
    background: 'var(--surface-2)',
    borderColor: 'var(--line)'
  },
  review: {
    color: 'var(--blue)',
    background: 'var(--blue-bg)',
    borderColor: 'var(--blue)'
  },
  human: {
    color: 'var(--accent)',
    background: 'var(--accent-bg)',
    borderColor: 'var(--accent)'
  },
  learning: {
    color: 'var(--ok)',
    background: 'var(--ok-bg)',
    borderColor: 'var(--ok)'
  }
};
function Tag({
  kind = 'pipeline',
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: '0.04em',
      padding: '2px 8px',
      borderRadius: 'var(--radius-chip)',
      borderWidth: 1,
      borderStyle: 'solid',
      display: 'inline-block',
      ...KINDS[kind],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/diagrams/DIAGRAMS.js
try { (() => {
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
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/diagrams/DIAGRAMS.js", error: String((e && e.message) || e) }); }

// components/diagrams/MermaidDiagram.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CDN = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js';
let loader = null;
function loadMermaid() {
  if (window.mermaid) return Promise.resolve(window.mermaid);
  if (!loader) {
    loader = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = CDN;
      s.onload = () => resolve(window.mermaid);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  return loader;
}
function tokens() {
  const cs = getComputedStyle(document.documentElement);
  const v = n => (cs.getPropertyValue(n) || '').trim();
  return {
    ink: v('--ink') || '#18222C',
    muted: v('--muted') || '#5B6874',
    line: v('--line') || '#CFD7DE',
    surface: v('--surface') || '#FFFFFF',
    surface2: v('--surface-2') || '#E9EDF1',
    bg: v('--bg') || '#F2F4F6',
    accent: v('--accent') || '#B96E00',
    blue: v('--blue') || '#33689E',
    ok: v('--ok') || '#2E7D4F',
    mono: v('--mono') || 'ui-monospace, monospace'
  };
}

/* Brand theme: flat surfaces, hairline borders, mono labels, amber = human decision. */
function themeConfig(t) {
  return {
    startOnLoad: false,
    securityLevel: 'loose',
    fontFamily: t.mono,
    theme: 'base',
    themeVariables: {
      background: 'transparent',
      primaryColor: t.surface2,
      primaryTextColor: t.ink,
      primaryBorderColor: t.line,
      secondaryColor: t.surface,
      secondaryTextColor: t.ink,
      secondaryBorderColor: t.line,
      tertiaryColor: t.surface,
      tertiaryTextColor: t.muted,
      tertiaryBorderColor: t.line,
      lineColor: t.muted,
      textColor: t.ink,
      mainBkg: t.surface2,
      nodeBorder: t.line,
      clusterBkg: t.bg,
      clusterBorder: t.line,
      titleColor: t.muted,
      edgeLabelBackground: t.surface,
      fontSize: '13px',
      actorBkg: t.surface2,
      actorBorder: t.line,
      actorTextColor: t.ink,
      actorLineColor: t.line,
      signalColor: t.ink,
      signalTextColor: t.muted,
      labelBoxBkg: t.surface2,
      labelBoxBorderColor: t.accent,
      labelTextColor: t.ink,
      loopTextColor: t.muted,
      noteBkgColor: t.surface,
      noteBorderColor: t.accent,
      noteTextColor: t.ink,
      sequenceNumberColor: t.surface,
      transitionColor: t.muted,
      stateBkg: t.surface2,
      stateLabelColor: t.ink,
      altBackground: t.bg,
      compositeBackground: t.bg,
      compositeBorder: t.line,
      innerEndBackground: t.ink,
      pie1: t.accent,
      pie2: t.blue,
      pie3: t.ok
    },
    flowchart: {
      curve: 'basis',
      padding: 12,
      nodeSpacing: 34,
      rankSpacing: 46,
      useMaxWidth: false
    },
    sequence: {
      useMaxWidth: false,
      actorMargin: 46,
      boxMargin: 8,
      mirrorActors: false,
      messageFontSize: 12,
      noteFontSize: 12
    }
  };
}

/* Mermaid's classDef parser rejects var(--x); resolve token references to literal colours first. */
function toHex(v) {
  const m = /^rgba?\(([^)]+)\)$/i.exec(v.trim());
  if (!m) return v;
  const p = m[1].split(/[\s,\/]+/).filter(Boolean);
  const h = n => Math.round(parseFloat(n)).toString(16).padStart(2, '0');
  const a = p[3] === undefined ? '' : Math.round(parseFloat(p[3]) * 255).toString(16).padStart(2, '0');
  return '#' + h(p[0]) + h(p[1]) + h(p[2]) + a;
}
function resolveVars(src) {
  const cs = getComputedStyle(document.documentElement);
  return String(src).replace(/var\(\s*(--[\w-]+)\s*\)/g, (m, name) => {
    const v = (cs.getPropertyValue(name) || '').trim();
    return v ? toHex(v) : m;
  });
}
let seq = 0;
function MermaidDiagram({
  chart,
  caption,
  scroll = true,
  style,
  ...rest
}) {
  const ref = React.useRef(null);
  const [err, setErr] = React.useState(null);
  const id = React.useRef('mmd-' + ++seq);
  React.useEffect(() => {
    let alive = true;
    loadMermaid().then(m => {
      if (!alive || !chart) return;
      const t = tokens();
      m.initialize(themeConfig(t));
      return m.render(id.current, resolveVars(chart.trim())).then(({
        svg
      }) => {
        if (!alive || !ref.current) return;
        ref.current.innerHTML = svg;
        const el = ref.current.querySelector('svg');
        // Natural size only: forcing width/height rescales text away from the document's type sizes.
        if (el) {
          el.style.display = 'block';
        }
      });
    }).catch(e => alive && setErr(String(e && e.message || e)));
    return () => {
      alive = false;
    };
  }, [chart]);
  return /*#__PURE__*/React.createElement("figure", _extends({
    style: {
      margin: '24px 0 8px',
      background: 'var(--surface)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-xl)',
      padding: 20,
      overflowX: scroll ? 'auto' : 'visible',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    ref: ref
  }), err && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 12,
      color: 'var(--danger)'
    }
  }, "Diagram l\u1ED7i: ", err), caption && /*#__PURE__*/React.createElement("figcaption", {
    style: {
      fontSize: 13.5,
      color: 'var(--muted)',
      marginTop: 14,
      maxWidth: '80ch'
    }
  }, caption));
}
Object.assign(__ds_scope, { MermaidDiagram });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/diagrams/MermaidDiagram.jsx", error: String((e && e.message) || e) }); }

// components/tower/AgentAvatar.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const LANES = {
  pipeline: {
    color: 'var(--ink)',
    border: 'var(--line)',
    bg: 'var(--surface-2)'
  },
  review: {
    color: 'var(--blue)',
    border: 'var(--blue)',
    bg: 'var(--blue-bg)'
  },
  human: {
    color: 'var(--accent)',
    border: 'var(--accent)',
    bg: 'var(--accent-bg)'
  },
  learning: {
    color: 'var(--ok)',
    border: 'var(--ok)',
    bg: 'var(--ok-bg)'
  }
};
function initials(name = '') {
  const parts = String(name).split('-').filter(Boolean);
  return (parts.length > 1 ? parts[0][0] + parts[1][0] : String(name).slice(0, 2)).toUpperCase();
}
function AgentAvatar({
  name = '',
  lane = 'pipeline',
  size = 22,
  withName = false,
  style,
  ...rest
}) {
  const l = LANES[lane] || LANES.pipeline;
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--sp-3)',
      ...style
    },
    title: name
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      width: size,
      height: size,
      borderRadius: '50%',
      flex: 'none',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'var(--mono)',
      fontSize: Math.round(size * 0.42),
      fontWeight: 'var(--fw-medium)',
      color: l.color,
      background: l.bg,
      border: '1px solid ' + l.border
    }
  }, initials(name)), withName && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--muted)'
    }
  }, name));
}
Object.assign(__ds_scope, { AgentAvatar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/AgentAvatar.jsx", error: String((e && e.message) || e) }); }

// components/tower/AgentWorkCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const STEP_MARK = {
  done: '✓',
  doing: '●',
  todo: '·'
};
const STEP_COLOR = {
  done: 'var(--ok)',
  doing: 'var(--accent)',
  todo: 'var(--muted)'
};
function AgentWorkCard({
  taskId,
  title,
  agent,
  lane = 'pipeline',
  status = 'in-progress',
  elapsed,
  doing,
  target,
  steps = [],
  messages = [],
  waitingOn,
  onOpenTask,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-lg)',
      background: 'var(--surface)',
      display: 'flex',
      flexDirection: 'column',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--sp-4)',
      padding: '10px 14px',
      borderBottom: '1px solid var(--line)',
      background: 'var(--surface-2)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.AgentAvatar, {
    name: agent,
    lane: lane,
    size: 20
  }), /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    style: {
      fontSize: 'var(--fs-caption)'
    }
  }, taskId), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-sm)',
      flex: 1,
      minWidth: 120
    }
  }, title), /*#__PURE__*/React.createElement(__ds_scope.Chip, {
    tone: status === 'done' ? 'done' : status === 'blocked' ? 'blocked' : 'active'
  }, status), elapsed && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--muted)'
    }
  }, elapsed)), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '12px 14px',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--sp-5)'
    }
  }, doing && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      marginBottom: 4
    }
  }, "\u0110ang l\xE0m"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-body-sm)'
    }
  }, doing), target && /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    variant: "artifact",
    style: {
      marginTop: 6
    }
  }, target)), steps.length > 0 && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      marginBottom: 4
    }
  }, "C\xE1c b\u01B0\u1EDBc \xB7 ", steps.filter(s => s.state === 'done').length, "/", steps.length), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0,
      display: 'flex',
      flexDirection: 'column',
      gap: 3
    }
  }, steps.map((s, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      display: 'flex',
      gap: 8,
      fontSize: 'var(--fs-sm)',
      color: s.state === 'todo' ? 'var(--muted)' : 'var(--ink)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      color: STEP_COLOR[s.state],
      width: 12,
      flex: 'none'
    }
  }, STEP_MARK[s.state]), /*#__PURE__*/React.createElement("span", null, s.label))))), messages.length > 0 && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      marginBottom: 4
    }
  }, "Trao \u0111\u1ED5i g\u1EA7n nh\u1EA5t"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }
  }, messages.map(m => /*#__PURE__*/React.createElement("div", {
    key: m.id,
    style: {
      borderLeft: '2px solid var(--blue)',
      paddingLeft: 10
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--blue)'
    }
  }, m.id, " \xB7 ", m.from, " \u2192 ", m.to, " \xB7 ", m.type), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-sm)'
    }
  }, m.body))))), waitingOn && /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--accent)',
      background: 'var(--accent-bg)',
      color: 'var(--accent)',
      borderRadius: 'var(--radius-sm)',
      padding: '6px 10px',
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)'
    }
  }, "ch\u1EDD \xB7 ", waitingOn), onOpenTask && /*#__PURE__*/React.createElement("span", {
    onClick: onOpenTask,
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--muted)',
      cursor: 'pointer'
    }
  }, "m\u1EDF to\xE0n b\u1ED9 task \u2192")));
}
Object.assign(__ds_scope, { AgentWorkCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/AgentWorkCard.jsx", error: String((e && e.message) || e) }); }

// components/tower/FeedItem.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TYPES = {
  'review-request': 'agent',
  finding: 'gate',
  question: 'agent',
  answer: 'agent',
  clarification: 'agent',
  handoff: 'pipeline',
  note: 'muted',
  decision: 'done',
  escalation: 'gate'
};
const COLOR = {
  agent: 'var(--blue)',
  gate: 'var(--accent)',
  done: 'var(--ok)',
  pipeline: 'var(--ink)',
  muted: 'var(--muted)'
};
function FeedItem({
  time,
  id,
  from,
  to,
  type = 'note',
  summary,
  onClick,
  isNew = false,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const c = COLOR[TYPES[type] || 'muted'];
  return /*#__PURE__*/React.createElement("div", _extends({
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-caption)',
      lineHeight: 1.5,
      padding: '7px 12px',
      borderBottom: '1px solid var(--line)',
      background: hover && onClick ? 'var(--surface-2)' : 'transparent',
      cursor: onClick ? 'pointer' : 'default',
      borderLeft: isNew ? '2px solid var(--accent)' : '2px solid transparent',
      animation: isNew ? 'none' : undefined,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--sp-4)',
      alignItems: 'baseline',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--muted)'
    }
  }, time), id && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--muted)'
    }
  }, id), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--blue)'
    }
  }, from, to ? ' → ' + to : ''), /*#__PURE__*/React.createElement("span", {
    style: {
      color: c,
      border: '1px solid ' + c,
      borderRadius: 'var(--radius-chip)',
      padding: '0 5px',
      fontSize: 'var(--fs-micro)'
    }
  }, type)), summary && /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--ink)',
      marginTop: 2,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, summary));
}
Object.assign(__ds_scope, { FeedItem });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/FeedItem.jsx", error: String((e && e.message) || e) }); }

// components/tower/GateCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function GateCard({
  gate,
  target,
  title,
  brief,
  options = [],
  recommendation,
  evidence = [],
  kind = 'gate',
  expanded: expandedProp,
  defaultExpanded = false,
  onApprove,
  onReject,
  onDiscuss,
  style,
  ...rest
}) {
  const [open, setOpen] = React.useState(defaultExpanded);
  const [rejecting, setRejecting] = React.useState(false);
  const [reason, setReason] = React.useState('');
  const expanded = expandedProp === undefined ? open : expandedProp;
  const isEsc = kind === 'escalation';
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      border: '1px solid var(--accent)',
      background: 'var(--accent-bg)',
      borderRadius: 'var(--radius-md)',
      marginBottom: 'var(--sp-4)',
      fontSize: 'var(--fs-row)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("header", {
    onClick: () => setOpen(v => !v),
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: 'var(--sp-5)',
      padding: '10px 12px',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--accent)',
      fontFamily: 'var(--mono)',
      fontSize: 13,
      lineHeight: '20px',
      flex: 'none',
      width: 12,
      textAlign: 'center'
    }
  }, isEsc ? '△' : '◇'), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 'var(--fw-semibold)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    style: {
      color: 'var(--accent)',
      fontSize: 'var(--fs-caption)',
      marginRight: 6
    }
  }, isEsc ? 'ESCALATION' : 'Gate ' + gate, target ? ' · ' + target : ''), title), !expanded && brief && /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--muted)',
      fontSize: 'var(--fs-sm)',
      marginTop: 2,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, brief)), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--accent)',
      flex: 'none'
    }
  }, expanded ? '−' : '+')), expanded && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 12px 12px 34px',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--sp-5)'
    }
  }, brief && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      color: 'var(--ink)',
      maxWidth: 'var(--measure-note)'
    }
  }, brief), options.length > 0 && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      marginBottom: 4
    }
  }, "Ph\u01B0\u01A1ng \xE1n \xB7 trade-off"), /*#__PURE__*/React.createElement("ul", {
    style: {
      margin: 0,
      paddingLeft: 18,
      fontSize: 'var(--fs-body-sm)'
    }
  }, options.map((o, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      marginBottom: 4
    }
  }, o)))), recommendation && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-body-sm)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)',
      marginRight: 8
    }
  }, "Khuy\u1EBFn ngh\u1ECB"), recommendation), evidence.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--sp-2)',
      flexWrap: 'wrap'
    }
  }, evidence.map((e, i) => /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    key: i,
    variant: "artifact"
  }, e))), rejecting ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--sp-4)'
    }
  }, /*#__PURE__*/React.createElement("textarea", {
    value: reason,
    onChange: e => setReason(e.target.value),
    rows: 2,
    placeholder: "L\xFD do reject (b\u1EAFt bu\u1ED9c)",
    style: {
      width: '100%',
      fontFamily: 'var(--sans)',
      fontSize: 'var(--fs-sm)',
      color: 'var(--ink)',
      background: 'var(--surface)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-sm)',
      padding: '8px 10px',
      resize: 'vertical'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--sp-4)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "danger",
    size: "sm",
    disabled: !reason.trim(),
    onClick: () => {
      onReject && onReject(reason);
      setRejecting(false);
      setReason('');
    }
  }, "G\u1EEDi reject"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "ghost",
    size: "sm",
    onClick: () => setRejecting(false)
  }, "Hu\u1EF7"))) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--sp-4)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "ok",
    size: "sm",
    onClick: onApprove
  }, "Approve"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "danger",
    size: "sm",
    onClick: () => setRejecting(true)
  }, "Reject"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "ghost",
    size: "sm",
    onClick: onDiscuss
  }, "C\u1EA7n th\u1EA3o lu\u1EADn"))));
}
Object.assign(__ds_scope, { GateCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/GateCard.jsx", error: String((e && e.message) || e) }); }

// components/tower/GateStop.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function GateStop({
  label,
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      border: '1.5px solid var(--accent)',
      background: 'var(--accent-bg)',
      borderRadius: 'var(--radius-lg)',
      padding: '14px 18px',
      marginTop: 'var(--sp-4)',
      fontSize: 'var(--fs-body-sm)',
      maxWidth: 'var(--measure-note)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      color: 'var(--accent)',
      fontWeight: 'var(--fw-bold)',
      display: 'block',
      marginBottom: 'var(--sp-3)'
    }
  }, label), children);
}
Object.assign(__ds_scope, { GateStop });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/GateStop.jsx", error: String((e && e.message) || e) }); }

// components/tower/KpiStrip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function KpiStrip({
  items = [],
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      alignItems: 'stretch',
      gap: 0,
      border: '1px solid var(--line)',
      background: 'var(--surface)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      ...style
    }
  }, rest), items.map((it, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      padding: '10px 18px',
      flex: 1,
      minWidth: 0,
      borderLeft: i ? '1px solid var(--line)' : 'none',
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--sp-4)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 22,
      fontWeight: 'var(--fw-bold)',
      lineHeight: 1,
      color: it.tone === 'gate' ? 'var(--accent)' : it.tone === 'done' ? 'var(--ok)' : it.tone === 'agent' ? 'var(--blue)' : 'var(--ink)'
    }
  }, it.value), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      color: 'var(--muted)'
    }
  }, it.label))));
}
Object.assign(__ds_scope, { KpiStrip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/KpiStrip.jsx", error: String((e && e.message) || e) }); }

// components/tower/StageStrip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const STAGES = ['1 Request', '2 Discovery', '3 Validation', '4 Clarify', '5 Units', '6 Construction', '7 Acceptance', '8 Release'];
function StageStrip({
  current = 1,
  gate,
  labels = false,
  compact = false,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      gap: 'var(--gap-chip)',
      alignItems: 'center',
      flexWrap: 'wrap',
      ...style
    }
  }, rest), STAGES.map((s, i) => {
    const n = i + 1;
    const tone = n < current ? 'done' : n === current ? 'active' : 'pending';
    const text = labels ? s : String(n);
    return /*#__PURE__*/React.createElement(__ds_scope.Chip, {
      key: n,
      tone: tone
    }, n === current && gate ? text + ' ◇' + gate : text);
  }), compact && null);
}
Object.assign(__ds_scope, { STAGES, StageStrip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/StageStrip.jsx", error: String((e && e.message) || e) }); }

// components/tower/PipelineRow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function PipelineRow({
  id,
  name,
  current = 1,
  gate,
  holder,
  holderLane = 'pipeline',
  onClick,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", _extends({
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--sp-6)',
      flexWrap: 'wrap',
      padding: '10px 16px',
      borderBottom: '1px solid var(--line)',
      background: hover && onClick ? 'var(--surface-2)' : 'transparent',
      cursor: onClick ? 'pointer' : 'default',
      transition: 'background var(--dur-fast) var(--ease-standard)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    style: {
      width: 72,
      flex: 'none',
      fontSize: 'var(--fs-caption)'
    }
  }, id), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-sm)',
      flex: '1 1 220px',
      minWidth: 0
    }
  }, name), /*#__PURE__*/React.createElement(__ds_scope.StageStrip, {
    current: current,
    gate: gate
  }), holder && /*#__PURE__*/React.createElement(__ds_scope.AgentAvatar, {
    name: holder,
    lane: holderLane
  }));
}
Object.assign(__ds_scope, { PipelineRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/PipelineRow.jsx", error: String((e && e.message) || e) }); }

// components/tower/TaskRow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const STATUS_TONE = {
  done: 'done',
  'in-progress': 'active',
  review: 'active',
  claimed: 'agent',
  blocked: 'blocked',
  todo: 'pending'
};
function TaskRow({
  id,
  title,
  status = 'todo',
  claimedBy,
  approver,
  dependsOn,
  msgCount,
  onClick,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const meta = [claimedBy ? 'claim: ' + claimedBy : 'chưa claim', approver ? 'approver: ' + approver : null, dependsOn ? 'depends: ' + dependsOn : null, msgCount ? msgCount + ' MSG' : null].filter(Boolean).join(' · ');
  return /*#__PURE__*/React.createElement("div", _extends({
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'flex',
      gap: 'var(--sp-5)',
      padding: '10px 14px',
      borderBottom: '1px solid var(--line)',
      fontSize: 'var(--fs-sm)',
      alignItems: 'flex-start',
      flexWrap: 'wrap',
      background: hover && onClick ? 'var(--surface-2)' : 'transparent',
      cursor: onClick ? 'pointer' : 'default',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.IdCode, {
    style: {
      width: 64,
      flex: 'none',
      fontSize: 'var(--fs-caption)'
    }
  }, id), /*#__PURE__*/React.createElement(__ds_scope.Chip, {
    tone: STATUS_TONE[status] || 'pending',
    style: {
      width: 78,
      textAlign: 'center',
      flex: 'none'
    }
  }, status), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 240
    }
  }, /*#__PURE__*/React.createElement("div", null, title), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      color: 'var(--muted)',
      marginTop: 2
    }
  }, meta)));
}
Object.assign(__ds_scope, { TaskRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/TaskRow.jsx", error: String((e && e.message) || e) }); }

// components/tower/TimelineItem.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function TimelineItem({
  actor,
  lane = 'agent',
  heading,
  children,
  last = false,
  style,
  ...rest
}) {
  const color = lane === 'human' ? 'var(--accent)' : 'var(--blue)';
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      position: 'relative',
      marginBottom: last ? 0 : 30,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: -33,
      top: 6,
      width: 12,
      height: 12,
      borderRadius: '50%',
      background: lane === 'human' ? 'var(--accent)' : 'var(--surface)',
      border: '2.5px solid ' + color,
      boxSizing: 'border-box'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 'var(--fw-semibold)',
      fontSize: '15.5px',
      display: 'flex',
      gap: 'var(--sp-5)',
      alignItems: 'baseline',
      flexWrap: 'wrap'
    }
  }, actor && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      padding: '2px 8px',
      borderRadius: 'var(--radius-chip)',
      color,
      background: lane === 'human' ? 'var(--accent-bg)' : 'var(--blue-bg)',
      border: '1px solid ' + color
    }
  }, actor), /*#__PURE__*/React.createElement("span", null, heading)), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-body-sm)',
      color: 'var(--muted)',
      maxWidth: '74ch',
      marginTop: 4
    }
  }, children));
}
function Timeline({
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      borderLeft: '2px solid var(--line)',
      marginLeft: 10,
      paddingLeft: 26,
      marginTop: 'var(--sp-9)',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { TimelineItem, Timeline });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/TimelineItem.jsx", error: String((e && e.message) || e) }); }

// components/tower/TraceChain.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const KINDS = {
  code: {
    label: 'code',
    color: 'var(--ink)',
    bg: 'var(--surface-2)',
    border: 'var(--line)'
  },
  design: {
    label: 'design',
    color: 'var(--ink)',
    bg: 'var(--surface-2)',
    border: 'var(--line)'
  },
  spec: {
    label: 'spec',
    color: 'var(--ink)',
    bg: 'var(--surface-2)',
    border: 'var(--line)'
  },
  task: {
    label: 'task',
    color: 'var(--ink)',
    bg: 'var(--surface-2)',
    border: 'var(--line)'
  },
  dec: {
    label: 'decision',
    color: 'var(--accent)',
    bg: 'var(--accent-bg)',
    border: 'var(--accent)'
  },
  gate: {
    label: 'gate',
    color: 'var(--accent)',
    bg: 'var(--accent-bg)',
    border: 'var(--accent)'
  },
  rv: {
    label: 'review',
    color: 'var(--blue)',
    bg: 'var(--blue-bg)',
    border: 'var(--blue)'
  },
  msg: {
    label: 'message',
    color: 'var(--blue)',
    bg: 'var(--blue-bg)',
    border: 'var(--blue)'
  },
  intent: {
    label: 'intent',
    color: 'var(--ok)',
    bg: 'var(--ok-bg)',
    border: 'var(--ok)'
  }
};
function Node({
  step,
  active,
  onClick
}) {
  const k = KINDS[step.kind] || KINDS.code;
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      border: '1px solid ' + k.border,
      background: k.bg,
      color: k.color,
      borderRadius: 'var(--radius-md)',
      padding: '7px 10px',
      minWidth: 116,
      flex: 'none',
      cursor: onClick ? 'pointer' : 'default',
      outline: active ? '1px solid ' + k.border : 'none',
      outlineOffset: 2,
      opacity: hover && onClick ? 0.86 : 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-micro)',
      letterSpacing: 'var(--ls-label)',
      textTransform: 'uppercase',
      opacity: 0.75
    }
  }, k.label), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-sm)',
      fontWeight: 'var(--fw-medium)',
      marginTop: 2,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, step.id), step.note && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11.5,
      color: 'var(--muted)',
      marginTop: 3,
      maxWidth: 190
    }
  }, step.note));
}
function TraceChain({
  steps = [],
  direction = 'horizontal',
  activeId,
  onSelect,
  style,
  ...rest
}) {
  const vertical = direction === 'vertical';
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      flexDirection: vertical ? 'column' : 'row',
      alignItems: vertical ? 'stretch' : 'flex-start',
      gap: 0,
      overflowX: vertical ? 'visible' : 'auto',
      paddingBottom: vertical ? 0 : 4,
      ...style
    }
  }, rest), steps.map((s, i) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: s.id + i
  }, i > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 'none',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'var(--muted)',
      fontFamily: 'var(--mono)',
      fontSize: 12,
      width: vertical ? 'auto' : 26,
      height: vertical ? 18 : 44
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      borderTop: vertical ? 'none' : '1px dashed var(--line)',
      borderLeft: vertical ? '1px dashed var(--line)' : 'none',
      width: vertical ? 0 : '100%',
      height: vertical ? '100%' : 0,
      marginLeft: vertical ? 22 : 0
    }
  })), /*#__PURE__*/React.createElement(Node, {
    step: s,
    active: activeId === s.id,
    onClick: onSelect ? () => onSelect(s) : undefined
  }))));
}
Object.assign(__ds_scope, { TraceChain });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/TraceChain.jsx", error: String((e && e.message) || e) }); }

// components/tower/VerdictBadge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const V = {
  approve: {
    label: 'approve',
    color: 'var(--ok)',
    bg: 'var(--ok-bg)'
  },
  'approve-with-notes': {
    label: 'approve-with-notes',
    color: 'var(--ok)',
    bg: 'var(--ok-bg)'
  },
  'request-changes': {
    label: 'request-changes',
    color: 'var(--accent)',
    bg: 'var(--accent-bg)'
  }
};
function VerdictBadge({
  id,
  reviewer,
  verdict = 'approve',
  style,
  ...rest
}) {
  const v = V[verdict] || V.approve;
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      fontFamily: 'var(--mono)',
      fontSize: 'var(--fs-mono-xs)',
      padding: '2px 8px',
      borderRadius: 'var(--radius-chip)',
      color: v.color,
      background: v.bg,
      border: '1px solid ' + v.color,
      display: 'inline-block',
      whiteSpace: 'nowrap',
      ...style
    }
  }, rest), [id, reviewer, v.label].filter(Boolean).join(' · '));
}
Object.assign(__ds_scope, { VerdictBadge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tower/VerdictBadge.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/App.jsx
try { (() => {
(function () {
  const NSa = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    IdCode: AId,
    Chip: AChip,
    VerdictBadge: AVerdict,
    Button: ABtn,
    StatusChip,
    TraceChain: ATrace
  } = NSa;
  function TaskDrawerBody({
    task,
    data
  }) {
    if (!task) return null;
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 14
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 650
      }
    }, task.title), /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        color: 'var(--muted)',
        lineHeight: 1.9
      }
    }, /*#__PURE__*/React.createElement("div", null, "status \xB7 ", task.status), /*#__PURE__*/React.createElement("div", null, "claimed_by \xB7 ", task.claimedBy || '—'), /*#__PURE__*/React.createElement("div", null, "approver \xB7 ", task.approver), /*#__PURE__*/React.createElement("div", null, "depends_on \xB7 ", task.dependsOn || '—')), /*#__PURE__*/React.createElement(SectionLabel, null, "Comms c\u1EE7a task"), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 10
      }
    }, data.feed.slice(0, 3).map(m => /*#__PURE__*/React.createElement("div", {
      key: m.id,
      style: {
        borderLeft: '2px solid var(--line)',
        paddingLeft: 10
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--blue)'
      }
    }, m.id, " \xB7 ", m.from, " \u2192 ", m.to, " \xB7 ", m.type), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13
      }
    }, m.summary)))), /*#__PURE__*/React.createElement(SectionLabel, null, "Chu\u1ED7i truy v\u1EBFt"), /*#__PURE__*/React.createElement(ATrace, {
      direction: "vertical",
      steps: data.trace
    }));
  }
  function App() {
    const data = window.CT_DATA;
    const [screen, setScreen] = React.useState('mission');
    const [intentId, setIntentId] = React.useState('INT-001');
    const [theme, setTheme] = React.useState('dark');
    const [gates, setGates] = React.useState(data.gates);
    const [drawer, setDrawer] = React.useState(null);
    const [toast, setToast] = React.useState(null);
    React.useEffect(() => {
      document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);
    const decide = (key, action, reason) => {
      setGates(g => g.filter(x => x.key !== key));
      setToast(action === 'approve' ? 'Đã approve — ghi DEC-0019, stage 6 mở khoá' : action === 'reject' ? 'Đã reject — lý do gửi về orchestrator: "' + reason + '"' : 'Đã chuyển sang thảo luận — MSG gửi tới ba-reviewer');
      setTimeout(() => setToast(null), 3200);
    };
    const titles = {
      mission: ['Mission Control', 'cái gì đang chờ tôi · mọi thứ đang ở đâu'],
      intents: ['Intents', data.intents.length + ' intent đang mở · lọc theo trạng thái, loại brownfield, người yêu cầu'],
      intent: [intentId + ' · ' + (data.intents.find(x => x.id === intentId) || data.intents[0]).name, 'Units · Open questions · Decisions · Changelog'],
      bolt: ['UOW-01 · Bolt 1 — Release Planning', 'task board · contract · checkpoint Gate E'],
      comms: ['Comms & Reviews', 'mọi trao đổi là văn bản truy vết được'],
      gov: ['Governance & Learning', 'DoR/DoD · risk · tech-debt · lessons']
    };
    const crumbs = {
      intents: [{
        label: 'Dự án · spoke-project-control-tower'
      }, {
        label: 'Intents'
      }],
      intent: [{
        label: 'Intents',
        to: 'intents'
      }, {
        label: intentId
      }],
      bolt: [{
        label: 'Intents',
        to: 'intents'
      }, {
        label: intentId,
        to: 'intent'
      }, {
        label: 'UOW-01'
      }, {
        label: 'Bolt 1'
      }],
      comms: [{
        label: 'Dự án'
      }, {
        label: 'Comms & Reviews'
      }],
      gov: [{
        label: 'Dự án'
      }, {
        label: 'Governance & Learning'
      }]
    };
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        height: '100vh',
        overflow: 'hidden',
        background: 'var(--bg)',
        color: 'var(--ink)'
      }
    }, /*#__PURE__*/React.createElement(Sidebar, {
      screen: screen,
      setScreen: setScreen,
      gateCount: gates.length,
      intentCount: data.intents.length
    }), /*#__PURE__*/React.createElement("main", {
      style: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement(TopBar, {
      title: titles[screen][0],
      subtitle: titles[screen][1],
      theme: theme,
      setTheme: setTheme,
      crumbs: crumbs[screen],
      onCrumb: setScreen,
      right: /*#__PURE__*/React.createElement(StatusChip, {
        tone: gates.length ? 'gate' : 'done'
      }, gates.length ? gates.length + ' MỤC CHỜ BẠN' : 'KHÔNG CÓ GÌ CHỜ BẠN')
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        overflow: 'auto'
      }
    }, screen === 'mission' && /*#__PURE__*/React.createElement(MissionControl, {
      data: data,
      gates: gates,
      onDecision: decide,
      onOpenIntent: id => {
        setIntentId(id);
        setScreen('intent');
      },
      onOpenFeed: m => setDrawer({
        kind: 'msg',
        m
      })
    }), screen === 'intents' && /*#__PURE__*/React.createElement(IntentList, {
      data: data,
      onOpenIntent: id => {
        setIntentId(id);
        setScreen('intent');
      }
    }), screen === 'intent' && /*#__PURE__*/React.createElement(IntentDetail, {
      data: data,
      intentId: intentId,
      onOpenBolt: () => setScreen('bolt'),
      onOpenList: () => setScreen('intents'),
      onSelectIntent: setIntentId
    }), screen === 'bolt' && /*#__PURE__*/React.createElement(BoltBoard, {
      data: data,
      onOpenTask: t => setDrawer({
        kind: 'task',
        t
      })
    }), screen === 'comms' && /*#__PURE__*/React.createElement(CommsReviews, {
      data: data,
      onOpenFeed: m => setDrawer({
        kind: 'msg',
        m
      })
    }), screen === 'gov' && /*#__PURE__*/React.createElement(Governance, {
      data: data
    }))), /*#__PURE__*/React.createElement(Drawer, {
      open: !!drawer,
      onClose: () => setDrawer(null),
      title: drawer ? drawer.kind === 'task' ? drawer.t.id + ' · task detail' : drawer.m.id + ' · message' : ''
    }, drawer && drawer.kind === 'task' && /*#__PURE__*/React.createElement(TaskDrawerBody, {
      task: drawer.t,
      data: data
    }), drawer && drawer.kind === 'msg' && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        color: 'var(--muted)'
      }
    }, drawer.m.time, " \xB7 ", drawer.m.from, " \u2192 ", drawer.m.to, " \xB7 ", drawer.m.type), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 14.5
      }
    }, drawer.m.summary), /*#__PURE__*/React.createElement(SectionLabel, {
      style: {
        marginTop: 8
      }
    }, "Truy ng\u01B0\u1EE3c t\u1EEB message n\xE0y"), /*#__PURE__*/React.createElement(ATrace, {
      direction: "vertical",
      steps: [{
        kind: 'msg',
        id: drawer.m.id,
        note: drawer.m.type
      }, {
        kind: 'task',
        id: 'TSK-01',
        note: 'API contract draft + freeze'
      }, {
        kind: 'design',
        id: 'UOW-01/contract.md',
        note: 'v2 FROZEN'
      }, {
        kind: 'spec',
        id: 'UOW-01/spec.md'
      }, {
        kind: 'intent',
        id: 'INT-001'
      }]
    }))), toast && /*#__PURE__*/React.createElement("div", {
      style: {
        position: 'fixed',
        bottom: 20,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 30,
        background: 'var(--surface)',
        border: '1px solid var(--ok)',
        color: 'var(--ok)',
        borderRadius: 'var(--radius-md)',
        padding: '10px 16px',
        fontFamily: 'var(--mono)',
        fontSize: 12,
        boxShadow: 'var(--shadow-overlay)'
      }
    }, toast));
  }
  const rootEl = document.getElementById('root');
  if (rootEl) ReactDOM.createRoot(rootEl).render(/*#__PURE__*/React.createElement(App, null));
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/BoltBoard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
(function () {
  const NSb = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    TaskRow,
    Chip,
    IdCode,
    Button,
    MermaidDiagram,
    AgentAvatar,
    AgentWorkCard
  } = NSb;
  function BoltBoard({
    data,
    onOpenTask
  }) {
    const [view, setView] = React.useState('hoạt động');
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "UOW-01 \xB7 Bolt 1 \u2014 Release Planning",
      meta: "1/5 done",
      pad: false
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        padding: '8px 14px',
        borderBottom: '1px solid var(--line)'
      }
    }, ['hoạt động', 'flow', 'lifecycle', 'list'].map(v => /*#__PURE__*/React.createElement("span", {
      key: v,
      onClick: () => setView(v),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: view === v ? 'agent' : 'pending'
    }, v)))), view === 'hoạt động' && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(340px,1fr))',
        gap: 12,
        padding: 14
      }
    }, data.work.map(w => /*#__PURE__*/React.createElement(AgentWorkCard, _extends({
      key: w.taskId
    }, w, {
      lane: w.agent.includes('reviewer') ? 'review' : 'pipeline',
      onOpenTask: () => onOpenTask(data.tasks.find(t => t.id === w.taskId) || {
        id: w.taskId,
        title: w.title,
        status: w.status,
        approver: '—'
      })
    })))), view === 'list' && data.tasks.map(t => /*#__PURE__*/React.createElement(TaskRow, _extends({
      key: t.id
    }, t, {
      onClick: () => onOpenTask(t)
    }))), view === 'flow' && /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '0 14px 8px'
      }
    }, /*#__PURE__*/React.createElement(MermaidDiagram, {
      chart: window.CT_DIAGRAMS.boltFlow,
      style: {
        marginTop: 14
      },
      caption: "Ai b\xE0n giao cho ai trong Bolt 1. \xD4 xanh d\u01B0\u01A1ng l\xE0 \u0111i\u1EC3m m\u1ED9t reviewer ph\u1EA3i k\xFD; TSK-04 kh\xF4ng ch\u1EDD BE code xong m\xE0 ch\u1EDD backend-reviewer duy\u1EC7t."
    })), view === 'lifecycle' && /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '0 14px 8px'
      }
    }, /*#__PURE__*/React.createElement(MermaidDiagram, {
      chart: window.CT_DIAGRAMS.taskLifecycle,
      style: {
        marginTop: 14
      },
      caption: "V\xF2ng \u0111\u1EDDi c\u1EE7a m\u1ED9t task: claim \u2192 code \u2192 review \u2192 verdict. Hai l\u1EA7n request-changes c\xF9ng m\u1ED9t \u0111i\u1EC3m th\xEC vi\u1EC7c chuy\u1EC3n th\xE0nh escalation c\u1EE7a ng\u01B0\u1EDDi."
    }))), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))',
        gap: 16,
        alignItems: 'start'
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "API contract"
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        marginBottom: 10
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: "done"
    }, "FROZEN v2"), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)'
      }
    }, "be-dev \u2713 \xB7 fe-dev \u2713 \xB7 tech-lead \u2713")), /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 12,
        color: 'var(--ink)',
        lineHeight: 1.9
      }
    }, "GET/POST/PATCH /api/releases"), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 4,
        flexWrap: 'wrap',
        marginTop: 8
      }
    }, ['MSG-0058', 'MSG-0059', 'MSG-0060', 'MSG-0061'].map(m => /*#__PURE__*/React.createElement(IdCode, {
      key: m,
      variant: "artifact"
    }, m)))), /*#__PURE__*/React.createElement(Panel, {
      title: "Checkpoint \xB7 Gate E"
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 10
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 10
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: "done"
    }, "\u2713"), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13
      }
    }, "Design + contract OK")), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 10
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: "pending"
    }, "\u25C7"), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13,
        color: 'var(--muted)'
      }
    }, "Demo SCR-REL-10/11 sau review"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "sm",
      style: {
        marginLeft: 'auto'
      }
    }, "M\u1EDF demo")))))));
  }
  window.BoltBoard = BoltBoard;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/BoltBoard.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/CommsReviews.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
(function () {
  const NSc = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    DataTable,
    Chip,
    IdCode,
    VerdictBadge,
    FeedItem,
    AgentAvatar,
    TraceChain
  } = NSc;
  const THREAD = [{
    id: 'MSG-0058',
    from: 'fe-dev',
    to: 'be-dev',
    type: 'clarification',
    body: 'status enum trả code hay label? i18n phía nào?'
  }, {
    id: 'MSG-0059',
    from: 'be-dev',
    to: 'fe-dev',
    type: 'question',
    body: 'FE có bảng i18n sẵn cho status không, hay cần BE trả label theo locale?'
  }, {
    id: 'MSG-0060',
    from: 'fe-dev',
    to: 'be-dev',
    type: 'answer',
    body: 'FE có next-intl sẵn — chốt: BE trả code, FE map i18n.'
  }, {
    id: 'MSG-0061',
    from: 'be-dev',
    to: 'fe-dev',
    type: 'handoff',
    body: 'contract.md v2 cập nhật, FREEZE. TSK-03 chạy được với mock đúng shape.'
  }];
  function CommsReviews({
    data,
    onOpenFeed
  }) {
    const [tab, setTab] = React.useState('Comms');
    const [type, setType] = React.useState('all');
    const rows = data.feed.filter(m => type === 'all' || m.type === type);
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 2
      }
    }, ['Comms', 'Reviews'].map(t => /*#__PURE__*/React.createElement("button", {
      key: t,
      onClick: () => setTab(t),
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        padding: '8px 14px',
        cursor: 'pointer',
        background: 'transparent',
        border: 'none',
        borderBottom: '2px solid ' + (tab === t ? 'var(--accent)' : 'var(--line)'),
        color: tab === t ? 'var(--ink)' : 'var(--muted)',
        flex: 'none'
      }
    }, t)), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        borderBottom: '2px solid var(--line)'
      }
    })), tab === 'Comms' ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Panel, {
      title: "Truy v\u1EBFt \u2014 MSG-0058 n\u1EB1m \u1EDF \u0111\xE2u trong chu\u1ED7i quy\u1EBFt \u0111\u1ECBnh",
      meta: "click m\u1ED9t m\u1EAFt x\xEDch \u0111\u1EC3 m\u1EDF"
    }, /*#__PURE__*/React.createElement(TraceChain, {
      activeId: "MSG-0058",
      onSelect: () => {},
      steps: [{
        kind: 'intent',
        id: 'INT-001',
        note: 'Phase 2 PCT'
      }, {
        kind: 'dec',
        id: 'DEC-0015',
        note: 'Gate A · scope'
      }, {
        kind: 'spec',
        id: 'UOW-01/spec.md',
        note: 'AC-03 unique name'
      }, {
        kind: 'task',
        id: 'TSK-01',
        note: 'contract draft + freeze'
      }, {
        kind: 'msg',
        id: 'MSG-0058',
        note: 'fe-dev hỏi status enum'
      }, {
        kind: 'design',
        id: 'contract.md v2',
        note: 'FROZEN'
      }, {
        kind: 'rv',
        id: 'RV-010',
        note: 'pm-po · notes'
      }, {
        kind: 'code',
        id: 'releases/service.py',
        note: '409 unique name'
      }]
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(0,1.2fr) minmax(320px,1fr)',
        gap: 16,
        alignItems: 'start',
        marginTop: 16
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "Messages",
      meta: rows.length + ' MSG',
      pad: false
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        padding: '8px 12px',
        borderBottom: '1px solid var(--line)',
        flexWrap: 'wrap'
      }
    }, ['all', 'clarification', 'answer', 'handoff', 'finding', 'review-request', 'decision'].map(t => /*#__PURE__*/React.createElement("span", {
      key: t,
      onClick: () => setType(t),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: type === t ? 'agent' : 'pending'
    }, t)))), rows.map(m => /*#__PURE__*/React.createElement(FeedItem, _extends({
      key: m.id
    }, m, {
      onClick: () => onOpenFeed(m)
    })))), /*#__PURE__*/React.createElement(Panel, {
      title: "Thread \xB7 re: contract /api/releases",
      meta: "4 MSG"
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }
    }, THREAD.map(m => /*#__PURE__*/React.createElement("div", {
      key: m.id,
      style: {
        borderLeft: '2px solid var(--line)',
        paddingLeft: 12
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'center',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(AgentAvatar, {
      name: m.from,
      size: 18
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--blue)'
      }
    }, m.from, " \u2192 ", m.to), /*#__PURE__*/React.createElement(IdCode, {
      style: {
        fontSize: 10.5
      }
    }, m.id), /*#__PURE__*/React.createElement(Chip, {
      tone: "agent"
    }, m.type)), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13.5,
        marginTop: 4
      }
    }, m.body))))))) : /*#__PURE__*/React.createElement(Panel, {
      title: "Review verdicts",
      meta: data.reviews.length + ' RV'
    }, /*#__PURE__*/React.createElement(DataTable, {
      columns: ['RV', 'Reviewer', 'Target', 'Verdict', 'Checklist version', 'Findings'],
      rows: data.reviews.map(r => [r.id, r.reviewer, r.target, /*#__PURE__*/React.createElement(VerdictBadge, {
        verdict: r.verdict
      }), /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, r.checklist), r.findings])
    })));
  }
  window.CommsReviews = CommsReviews;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/CommsReviews.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/Governance.jsx
try { (() => {
(function () {
  const NSg = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    DataTable,
    Chip,
    IdCode,
    Button,
    Callout
  } = NSg;
  function DefList({
    title,
    version,
    items
  }) {
    return /*#__PURE__*/React.createElement(Panel, {
      title: title,
      meta: version
    }, /*#__PURE__*/React.createElement("ul", {
      style: {
        margin: 0,
        paddingLeft: 18,
        fontSize: 13.5,
        lineHeight: 1.7
      }
    }, items.map((i, k) => /*#__PURE__*/React.createElement("li", {
      key: k
    }, i))));
  }
  function Governance({
    data
  }) {
    const g = data.governance;
    const sev = s => /*#__PURE__*/React.createElement(Chip, {
      tone: s === 'high' ? 'blocked' : s === 'med' ? 'active' : 'pending'
    }, s);
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(DefList, {
      title: "Definition of Ready",
      version: g.dor.version,
      items: g.dor.items
    }), /*#__PURE__*/React.createElement(DefList, {
      title: "Definition of Done",
      version: g.dod.version,
      items: g.dod.items
    })), /*#__PURE__*/React.createElement(Panel, {
      title: "Changelog \u2014 governance",
      pad: false
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 16
      }
    }, /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Version', 'Khi nào', 'Ai đổi', 'DEC', 'Từ lesson'],
      rows: g.changelog.map(c => [c.v, c.when, c.by, /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, c.dec), c.from])
    }))), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(340px,1fr))',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "Risk register",
      meta: data.risks.length + ' risks'
    }, /*#__PURE__*/React.createElement(DataTable, {
      columns: ['ID', 'Severity', 'Nội dung', 'Owner'],
      rows: data.risks.map(r => [r.id, sev(r.sev), r.text, r.owner])
    })), /*#__PURE__*/React.createElement(Panel, {
      title: "Tech-debt register",
      meta: data.debt.length + ' items'
    }, /*#__PURE__*/React.createElement(DataTable, {
      columns: ['ID', 'Severity', 'Nội dung', 'Owner'],
      rows: data.debt.map(r => [r.id, sev(r.sev), r.text, r.owner])
    }))), /*#__PURE__*/React.createElement(Panel, {
      title: "Lessons learned",
      meta: "retro-keeper"
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))',
        gap: 12
      }
    }, data.lessons.map(l => /*#__PURE__*/React.createElement("div", {
      key: l.id,
      style: {
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-lg)',
        padding: '12px 14px',
        background: 'var(--surface)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 8
      }
    }, /*#__PURE__*/React.createElement(IdCode, {
      style: {
        fontSize: 12
      }
    }, l.id), /*#__PURE__*/React.createElement(Chip, {
      tone: l.status === 'applied' ? 'done' : 'active'
    }, l.status), /*#__PURE__*/React.createElement("span", {
      style: {
        marginLeft: 'auto',
        fontFamily: 'var(--mono)',
        fontSize: 10.5,
        color: 'var(--muted)'
      }
    }, l.patch)), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12.5,
        color: 'var(--muted)',
        marginTop: 8
      }
    }, "Trigger: ", l.trigger), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13.5,
        marginTop: 4
      }
    }, l.lesson), l.status === 'proposed' && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 8,
        marginTop: 10
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "ok",
      size: "sm"
    }, "Duy\u1EC7t patch"), /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      size: "sm"
    }, "Xem diff checklist"))))), /*#__PURE__*/React.createElement(Callout, {
      tone: "gate",
      style: {
        maxWidth: 'none'
      }
    }, "Patch ch\u1EC9 \u0111\u01B0\u1EE3c apply sau ", /*#__PURE__*/React.createElement("strong", null, "Gate G"), " \u2014 m\u1ED7i l\u1EA7n apply ghi version m\u1EDBi v\xE0o changelog c\u1EE7a skill \u0111\xF3.")));
  }
  window.Governance = Governance;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/Governance.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/IntentDetail.jsx
try { (() => {
(function () {
  const NSi = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    StageStrip,
    DataTable,
    Chip,
    IdCode,
    VerdictBadge,
    AgentAvatar
  } = NSi;
  function Tabs({
    tabs,
    active,
    onChange
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 2,
        borderBottom: '1px solid var(--line)'
      }
    }, tabs.map(t => /*#__PURE__*/React.createElement("button", {
      key: t,
      onClick: () => onChange(t),
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        padding: '8px 14px',
        cursor: 'pointer',
        background: 'transparent',
        border: 'none',
        borderBottom: '2px solid ' + (active === t ? 'var(--accent)' : 'transparent'),
        color: active === t ? 'var(--ink)' : 'var(--muted)'
      }
    }, t)));
  }
  function UnitCard({
    u,
    onOpenBolt
  }) {
    const tone = u.status === 'in-bolt' ? 'active' : u.status === 'blocked' ? 'blocked' : 'pending';
    return /*#__PURE__*/React.createElement("div", {
      onClick: () => u.bolt === 'Bolt 1' && onOpenBolt(),
      style: {
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-lg)',
        background: 'var(--surface)',
        padding: '12px 14px',
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
        cursor: u.bolt === 'Bolt 1' ? 'pointer' : 'default'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 8
      }
    }, /*#__PURE__*/React.createElement(IdCode, {
      style: {
        fontSize: 12
      }
    }, u.id), /*#__PURE__*/React.createElement(Chip, {
      tone: tone
    }, u.status), /*#__PURE__*/React.createElement("span", {
      style: {
        marginLeft: 'auto',
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)'
      }
    }, u.bolt)), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 14,
        fontWeight: 600
      }
    }, u.name), /*#__PURE__*/React.createElement("div", {
      style: {
        height: 4,
        background: 'var(--surface-2)',
        borderRadius: 2,
        overflow: 'hidden'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: u.done + '%',
        height: '100%',
        background: u.done ? 'var(--ok)' : 'transparent'
      }
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        alignItems: 'center',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 10.5,
        color: 'var(--muted)'
      }
    }, u.done, "% task done"), u.risks.map(r => /*#__PURE__*/React.createElement(Chip, {
      key: r,
      tone: "blocked"
    }, r))));
  }
  function IntentDetail({
    data,
    intentId,
    onOpenBolt,
    onOpenList,
    onSelectIntent
  }) {
    const intent = data.intents.find(x => x.id === intentId) || data.intents[0];
    const units = intent.id === 'INT-001' ? data.units : data.unitsByIntent[intent.id] || [];
    const [tab, setTab] = React.useState('Units');
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'center',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement("span", {
      onClick: onOpenList,
      style: {
        cursor: 'pointer',
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        color: 'var(--muted)'
      }
    }, "\u2190 t\u1EA5t c\u1EA3 intents"), /*#__PURE__*/React.createElement("span", {
      style: {
        width: 1,
        height: 14,
        background: 'var(--line)'
      }
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        flexWrap: 'wrap'
      }
    }, data.intents.map(x => /*#__PURE__*/React.createElement("span", {
      key: x.id,
      onClick: () => onSelectIntent && onSelectIntent(x.id),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: x.id === intent.id ? 'agent' : x.gate ? 'active' : 'pending'
    }, x.id))))), /*#__PURE__*/React.createElement(Panel, null, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 12,
        alignItems: 'baseline',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(IdCode, {
      style: {
        fontSize: 13,
        color: 'var(--accent)'
      }
    }, intent.id), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 20,
        fontWeight: 700,
        letterSpacing: '-0.01em'
      }
    }, intent.name), /*#__PURE__*/React.createElement("span", {
      style: {
        marginLeft: 'auto',
        display: 'flex',
        gap: 8,
        alignItems: 'center'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: "neutral"
    }, "brownfield \xB7 ", intent.brownfield), /*#__PURE__*/React.createElement(IdCode, {
      variant: "artifact"
    }, intent.doc))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 14
      }
    }, /*#__PURE__*/React.createElement(StageStrip, {
      current: intent.stage,
      gate: intent.gate,
      labels: true
    }))), /*#__PURE__*/React.createElement(Panel, {
      pad: false
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '0 8px'
      }
    }, /*#__PURE__*/React.createElement(Tabs, {
      tabs: ['Units', 'Open Questions', 'Decisions', 'Changelog'],
      active: tab,
      onChange: setTab
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 16
      }
    }, tab === 'Units' && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))',
        gap: 12
      }
    }, units.length ? units.map(u => /*#__PURE__*/React.createElement(UnitCard, {
      key: u.id,
      u: u,
      onOpenBolt: onOpenBolt
    })) : /*#__PURE__*/React.createElement("div", {
      style: {
        color: 'var(--muted)',
        fontSize: 14
      }
    }, "Ch\u01B0a t\u1EDBi stage 5 \u2014 ch\u01B0a c\xF3 Unit n\xE0o \u0111\u01B0\u1EE3c chia.")), tab === 'Open Questions' && /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Câu hỏi', 'Ai trả lời', 'Deadline', 'Ảnh hưởng nếu chưa trả lời', 'Trạng thái'],
      monoFirst: false,
      rows: data.questions.map(q => [q.q, q.who, q.due, q.impact, /*#__PURE__*/React.createElement(Chip, {
        tone: q.status === 'đã chốt' ? 'done' : 'active'
      }, q.status)])
    }), tab === 'Decisions' && /*#__PURE__*/React.createElement(DataTable, {
      columns: ['DEC', 'Thời điểm', 'Gate', 'Ai quyết', 'Nội dung', 'Căn cứ'],
      rows: data.decisions.map(d => [d.id, d.when, /*#__PURE__*/React.createElement(Chip, {
        tone: "done"
      }, d.gate), d.by, d.what, /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, d.basis)])
    }), tab === 'Changelog' && /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Khi nào', 'Thay đổi', 'Nguồn'],
      monoFirst: false,
      rows: [['11/08 13:12', 'Gate C đóng — Backlog đi mock-first', /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, "DEC-0017")], ['11/08 11:05', 'AS-IS được Validation Mob xác nhận', /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, "DEC-0016")], ['11/08 09:20', 'Scope Phase 2 chốt (không gồm Quality Gate)', /*#__PURE__*/React.createElement(IdCode, {
        variant: "inline"
      }, "DEC-0015")]]
    }))));
  }
  window.IntentDetail = IntentDetail;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/IntentDetail.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/IntentList.jsx
try { (() => {
(function () {
  const NSl = window.ControlTowerDesignSystem_68131c;
  const {
    Panel,
    PipelineRow,
    Chip,
    IdCode,
    KpiStrip,
    AgentAvatar,
    StageStrip,
    MermaidDiagram
  } = NSl;
  const FILTERS = [{
    key: 'all',
    label: 'tất cả'
  }, {
    key: 'gate',
    label: 'chờ tôi'
  }, {
    key: 'running',
    label: 'đang chạy'
  }, {
    key: 'done',
    label: 'đã release'
  }];
  const BROWNFIELD = ['Add feature', 'Optimize NFR', 'Technical debt', 'Fix defect'];
  function IntentList({
    data,
    onOpenIntent
  }) {
    const [showMap, setShowMap] = React.useState(false);
    const [filter, setFilter] = React.useState('all');
    const [type, setType] = React.useState('all');
    const [q, setQ] = React.useState('');
    const rows = data.intents.filter(i => {
      const byState = filter === 'all' ? true : filter === 'gate' ? !!i.gate : filter === 'running' ? i.stage < 8 && !i.gate : i.stage === 8;
      const byType = type === 'all' || i.brownfield === type;
      const byQ = !q.trim() || (i.id + ' ' + i.name + ' ' + i.owner).toLowerCase().includes(q.toLowerCase());
      return byState && byType && byQ;
    });
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(KpiStrip, {
      items: [{
        value: data.intents.length,
        label: 'Intents đang mở',
        tone: 'neutral'
      }, {
        value: data.intents.filter(i => i.gate).length,
        label: 'Có gate chờ tôi',
        tone: 'gate'
      }, {
        value: data.intents.filter(i => i.stage === 6).length,
        label: 'Đang Construction',
        tone: 'agent'
      }, {
        value: data.intents.filter(i => i.stage === 8).length,
        label: 'Đã release',
        tone: 'done'
      }]
    }), /*#__PURE__*/React.createElement(Panel, {
      title: "C\u1EA5u tr\xFAc c\xF4ng vi\u1EC7c \u2014 d\u1EF1 \xE1n \u203A intent \u203A unit \u203A bolt \u203A task",
      meta: /*#__PURE__*/React.createElement("span", {
        onClick: () => setShowMap(v => !v),
        style: {
          cursor: 'pointer',
          color: 'var(--accent)'
        }
      }, showMap ? 'thu gọn' : 'xem sơ đồ')
    }, showMap ? /*#__PURE__*/React.createElement(MermaidDiagram, {
      chart: window.CT_DIAGRAMS.hierarchy,
      style: {
        margin: 0
      },
      caption: "M\u1ED9t d\u1EF1 \xE1n c\xF3 nhi\u1EC1u Intent (ph\xE1t tri\u1EC3n ti\u1EBFp ho\u1EB7c ph\u1EA7n m\u1EDBi). M\u1ED7i Intent chia th\xE0nh nhi\u1EC1u Unit of Work; m\u1ED7i Unit ch\u1EA1y \u0111\xFAng m\u1ED9t Bolt \u2014 m\u1ED9t v\xF2ng build\u2013validate v\xE0i gi\u1EDD t\u1EDBi v\xE0i ng\xE0y; trong Bolt l\xE0 c\xE1c Task, m\u1ED7i task c\xF3 agent claim v\xE0 approver \u0111\u01B0\u1EE3c assign s\u1EB5n."
    }) : /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13.5,
        color: 'var(--muted)',
        maxWidth: '76ch'
      }
    }, "D\u1EF1 \xE1n \u2192 ", /*#__PURE__*/React.createElement("strong", {
      style: {
        color: 'var(--ok)'
      }
    }, "Intent"), " \u2192 ", /*#__PURE__*/React.createElement("strong", {
      style: {
        color: 'var(--blue)'
      }
    }, "Unit of Work"), " \u2192 ", /*#__PURE__*/React.createElement("strong", {
      style: {
        color: 'var(--accent)'
      }
    }, "Bolt"), " \u2192 Task. M\u1ED9t Intent c\xF3 nhi\u1EC1u Unit; m\u1ED7i Unit ch\u1EA1y \u0111\xFAng m\u1ED9t Bolt.")), /*#__PURE__*/React.createElement(Panel, {
      title: "Intents",
      meta: rows.length + '/' + data.intents.length,
      pad: false
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'center',
        padding: '10px 14px',
        borderBottom: '1px solid var(--line)',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6
      }
    }, FILTERS.map(f => /*#__PURE__*/React.createElement("span", {
      key: f.key,
      onClick: () => setFilter(f.key),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: filter === f.key ? 'agent' : 'pending'
    }, f.label)))), /*#__PURE__*/React.createElement("span", {
      style: {
        width: 1,
        height: 18,
        background: 'var(--line)'
      }
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement("span", {
      onClick: () => setType('all'),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: type === 'all' ? 'neutral' : 'pending'
    }, "m\u1ECDi lo\u1EA1i")), BROWNFIELD.map(b => /*#__PURE__*/React.createElement("span", {
      key: b,
      onClick: () => setType(b),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: type === b ? 'neutral' : 'pending'
    }, b)))), /*#__PURE__*/React.createElement("input", {
      value: q,
      onChange: e => setQ(e.target.value),
      placeholder: "t\xECm intent, ng\u01B0\u1EDDi y\xEAu c\u1EA7u\u2026",
      style: {
        marginLeft: 'auto',
        minWidth: 200,
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        color: 'var(--ink)',
        background: 'var(--surface-2)',
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-sm)',
        padding: '6px 10px'
      }
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: '84px minmax(220px,1fr) 132px 96px 110px',
        gap: 12,
        padding: '8px 16px',
        borderBottom: '2px solid var(--ink)',
        fontFamily: 'var(--mono)',
        fontSize: 11,
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        color: 'var(--muted)'
      }
    }, /*#__PURE__*/React.createElement("span", null, "Intent"), /*#__PURE__*/React.createElement("span", null, "T\xEAn \xB7 v\u1ECB tr\xED"), /*#__PURE__*/React.createElement("span", null, "Lo\u1EA1i"), /*#__PURE__*/React.createElement("span", null, "Units"), /*#__PURE__*/React.createElement("span", null, "C\u1EADp nh\u1EADt")), rows.map(i => /*#__PURE__*/React.createElement("div", {
      key: i.id,
      onClick: () => onOpenIntent(i.id),
      style: {
        display: 'grid',
        gridTemplateColumns: '84px minmax(220px,1fr) 132px 96px 110px',
        gap: 12,
        padding: '12px 16px',
        borderBottom: '1px solid var(--line)',
        alignItems: 'center',
        cursor: 'pointer',
        fontSize: 13
      }
    }, /*#__PURE__*/React.createElement(IdCode, {
      style: {
        fontSize: 12,
        color: i.gate ? 'var(--accent)' : 'var(--muted)'
      }
    }, i.id), /*#__PURE__*/React.createElement("div", {
      style: {
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        marginBottom: 6
      }
    }, i.name), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'center',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(StageStrip, {
      current: i.stage,
      gate: i.gate
    }), /*#__PURE__*/React.createElement(AgentAvatar, {
      name: i.holder,
      size: 18
    }))), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)'
      }
    }, i.brownfield), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11.5,
        color: 'var(--muted)'
      }
    }, i.units[0] ? i.units[1] + '/' + i.units[0] : '—', i.risk && /*#__PURE__*/React.createElement(Chip, {
      tone: i.risk === 'high' ? 'blocked' : 'active',
      style: {
        marginLeft: 6
      }
    }, "risk")), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)'
      }
    }, /*#__PURE__*/React.createElement("div", null, i.updated), /*#__PURE__*/React.createElement("div", null, i.owner)))), rows.length === 0 && /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '28px 16px',
        textAlign: 'center',
        color: 'var(--muted)',
        fontSize: 14
      }
    }, "Kh\xF4ng c\xF3 intent n\xE0o kh\u1EDBp b\u1ED9 l\u1ECDc.")));
  }
  window.IntentList = IntentList;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/IntentList.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/MissionControl.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
(function () {
  const NSm = window.ControlTowerDesignSystem_68131c;
  const {
    KpiStrip,
    GateCard,
    Panel,
    PipelineRow,
    FeedItem,
    VerdictBadge,
    Chip,
    IdCode: Id
  } = NSm;
  function MissionControl({
    data,
    gates,
    onDecision,
    onOpenIntent,
    onOpenFeed
  }) {
    const filters = ['all', 'comms', 'review', 'decision'];
    const [filter, setFilter] = React.useState('all');
    const feed = data.feed.filter(x => filter === 'all' ? true : filter === 'comms' ? ['clarification', 'question', 'answer', 'handoff', 'note'].includes(x.type) : filter === 'review' ? ['review-request', 'finding'].includes(x.type) : x.type === 'decision');
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        minHeight: 0
      }
    }, /*#__PURE__*/React.createElement(KpiStrip, {
      items: [{
        value: gates.filter(g => g.kind === 'gate').length,
        label: 'Gates chờ tôi',
        tone: 'gate'
      }, {
        value: gates.filter(g => g.kind === 'escalation').length,
        label: 'Escalations',
        tone: 'gate'
      }, {
        value: 2,
        label: 'Bolts đang chạy',
        tone: 'agent'
      }, {
        value: 3,
        label: 'Units done tuần này',
        tone: 'done'
      }]
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(0,1.55fr) minmax(320px,1fr)',
        gap: 16,
        alignItems: 'start'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "Gate queue \u2014 ch\u1EDD quy\u1EBFt \u0111\u1ECBnh c\u1EE7a b\u1EA1n",
      meta: gates.length + ' mục'
    }, gates.length === 0 ? /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '28px 8px',
        textAlign: 'center',
        color: 'var(--muted)'
      }
    }, /*#__PURE__*/React.createElement("style", null, '@keyframes ct-breathe{0%,100%{opacity:.45}50%{opacity:1}}'), /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 22,
        color: 'var(--ok)',
        animation: 'ct-breathe 1600ms ease-in-out infinite'
      }
    }, "\u25CF"), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 8,
        fontSize: 14.5
      }
    }, "Kh\xF4ng c\xF3 g\xEC ch\u1EDD b\u1EA1n \u2014 agents \u0111ang l\xE0m vi\u1EC7c")) : gates.map(g => /*#__PURE__*/React.createElement(GateCard, _extends({
      key: g.key
    }, g, {
      defaultExpanded: g.key === 'g1',
      onApprove: () => onDecision(g.key, 'approve'),
      onReject: r => onDecision(g.key, 'reject', r),
      onDiscuss: () => onDecision(g.key, 'discuss')
    })))), /*#__PURE__*/React.createElement(Panel, {
      title: "Pipeline board",
      meta: "2 intents",
      pad: false
    }, data.intents.map(i => /*#__PURE__*/React.createElement(PipelineRow, {
      key: i.id,
      id: i.id,
      name: i.name,
      current: i.stage,
      gate: i.gate,
      holder: i.holder,
      onClick: () => onOpenIntent(i.id)
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        padding: '10px 16px',
        flexWrap: 'wrap'
      }
    }, data.reviews.slice(0, 3).map(r => /*#__PURE__*/React.createElement(VerdictBadge, {
      key: r.id,
      id: r.id,
      reviewer: r.reviewer.replace('-reviewer', ''),
      verdict: r.verdict
    }))))), /*#__PURE__*/React.createElement(Panel, {
      title: "Live feed",
      meta: "activity + comms",
      pad: false,
      style: {
        position: 'sticky',
        top: 0,
        maxHeight: 'calc(100vh - 190px)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        padding: '8px 12px',
        borderBottom: '1px solid var(--line)',
        flexWrap: 'wrap'
      }
    }, filters.map(x => /*#__PURE__*/React.createElement("span", {
      key: x,
      onClick: () => setFilter(x),
      style: {
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement(Chip, {
      tone: filter === x ? 'agent' : 'pending'
    }, x)))), feed.map((x, i) => /*#__PURE__*/React.createElement(FeedItem, _extends({
      key: x.id
    }, x, {
      isNew: i === 0,
      onClick: () => onOpenFeed(x)
    }))))));
  }
  window.MissionControl = MissionControl;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/MissionControl.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/Shell.jsx
try { (() => {
(function () {
  const NS = window.ControlTowerDesignSystem_68131c;
  const {
    StatusChip,
    IdCode
  } = NS;
  const NAV = [{
    key: 'mission',
    label: 'Mission Control',
    mark: '◇'
  }, {
    key: 'intents',
    label: 'Intents',
    mark: '▤'
  }, {
    key: 'intent',
    label: 'Intent Detail',
    mark: '·'
  }, {
    key: 'bolt',
    label: 'Bolt / Task Board',
    mark: '▦'
  }, {
    key: 'comms',
    label: 'Comms & Reviews',
    mark: '→'
  }, {
    key: 'gov',
    label: 'Governance & Learning',
    mark: '△'
  }];
  function Sidebar({
    screen,
    setScreen,
    gateCount,
    intentCount
  }) {
    return /*#__PURE__*/React.createElement("nav", {
      style: {
        width: 232,
        flex: 'none',
        borderRight: '1px solid var(--line)',
        background: 'var(--surface)',
        display: 'flex',
        flexDirection: 'column',
        padding: '16px 0'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '0 18px 16px',
        borderBottom: '1px solid var(--line)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'baseline',
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        color: 'var(--accent)',
        fontFamily: 'var(--mono)'
      }
    }, "\u25C7"), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 17,
        fontWeight: 750,
        letterSpacing: '-0.02em'
      }
    }, "Control Tower")), /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 10.5,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color: 'var(--muted)',
        marginTop: 4
      }
    }, "AI-DLC \xB7 17 agents")), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexDirection: 'column',
        padding: '10px 8px',
        gap: 2
      }
    }, NAV.map(n => {
      const on = screen === n.key;
      return /*#__PURE__*/React.createElement("button", {
        key: n.key,
        onClick: () => setScreen(n.key),
        style: {
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          textAlign: 'left',
          padding: '8px 10px',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          border: '1px solid ' + (on ? 'var(--line)' : 'transparent'),
          background: on ? 'var(--surface-2)' : 'transparent',
          color: on ? 'var(--ink)' : 'var(--muted)',
          fontFamily: 'var(--sans)',
          fontSize: 13.5,
          paddingLeft: n.key === 'intent' ? 30 : 10
        }
      }, /*#__PURE__*/React.createElement("span", {
        style: {
          fontFamily: 'var(--mono)',
          fontSize: 12,
          color: on ? 'var(--accent)' : 'var(--muted)',
          width: 12
        }
      }, n.mark), /*#__PURE__*/React.createElement("span", {
        style: {
          flex: 1
        }
      }, n.label), n.key === 'intents' && intentCount ? /*#__PURE__*/React.createElement("span", {
        style: {
          fontFamily: 'var(--mono)',
          fontSize: 10.5,
          color: 'var(--muted)'
        }
      }, intentCount) : null, n.key === 'mission' && gateCount > 0 && /*#__PURE__*/React.createElement("span", {
        style: {
          fontFamily: 'var(--mono)',
          fontSize: 10.5,
          color: 'var(--accent)',
          border: '1px solid var(--accent)',
          background: 'var(--accent-bg)',
          borderRadius: 999,
          padding: '0 6px'
        }
      }, gateCount));
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 'auto',
        padding: '12px 18px 0',
        borderTop: '1px solid var(--line)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 10.5,
        color: 'var(--muted)',
        lineHeight: 1.8
      }
    }, /*#__PURE__*/React.createElement("div", null, "supervisor \xB7 Human"), /*#__PURE__*/React.createElement("div", null, "spoke-project-control-tower"))));
  }
  function TopBar({
    title,
    subtitle,
    crumbs,
    onCrumb,
    right,
    theme,
    setTheme
  }) {
    return /*#__PURE__*/React.createElement("header", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        flexWrap: 'wrap',
        padding: '12px 24px',
        borderBottom: '1px solid var(--line)',
        background: 'var(--surface)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, crumbs && crumbs.length > 0 && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        alignItems: 'center',
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)',
        marginBottom: 3,
        flexWrap: 'wrap'
      }
    }, crumbs.map((c, i) => /*#__PURE__*/React.createElement(React.Fragment, {
      key: c.label + i
    }, i > 0 && /*#__PURE__*/React.createElement("span", {
      style: {
        opacity: 0.6
      }
    }, "\u203A"), /*#__PURE__*/React.createElement("span", {
      onClick: () => c.to && onCrumb && onCrumb(c.to),
      style: {
        cursor: c.to ? 'pointer' : 'default',
        color: i === crumbs.length - 1 ? 'var(--ink)' : 'var(--muted)'
      }
    }, c.label)))), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 17,
        fontWeight: 700,
        letterSpacing: '-0.01em'
      }
    }, title), subtitle && /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: 'var(--muted)',
        marginTop: 2
      }
    }, subtitle)), right, /*#__PURE__*/React.createElement("button", {
      onClick: () => setTheme(theme === 'dark' ? 'light' : 'dark'),
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 10.5,
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        color: 'var(--muted)',
        background: 'transparent',
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-sm)',
        padding: '5px 10px',
        cursor: 'pointer'
      }
    }, theme === 'dark' ? 'dark' : 'light'));
  }
  function Drawer({
    open,
    title,
    onClose,
    children
  }) {
    if (!open) return null;
    return /*#__PURE__*/React.createElement("aside", {
      style: {
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: 460,
        maxWidth: '92vw',
        zIndex: 20,
        background: 'var(--surface)',
        borderLeft: '1px solid var(--line)',
        boxShadow: 'var(--shadow-overlay)',
        display: 'flex',
        flexDirection: 'column'
      }
    }, /*#__PURE__*/React.createElement("header", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '12px 18px',
        borderBottom: '1px solid var(--line)',
        background: 'var(--surface-2)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        flex: 1,
        fontFamily: 'var(--mono)',
        fontSize: 12,
        letterSpacing: '0.08em'
      }
    }, title), /*#__PURE__*/React.createElement("button", {
      onClick: onClose,
      style: {
        background: 'transparent',
        border: 'none',
        color: 'var(--muted)',
        cursor: 'pointer',
        fontFamily: 'var(--mono)',
        fontSize: 14
      }
    }, "\u2715")), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '16px 18px',
        overflow: 'auto'
      }
    }, children));
  }
  function SectionLabel({
    children,
    style
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 11,
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        color: 'var(--muted)',
        marginBottom: 8,
        ...style
      }
    }, children);
  }
  Object.assign(window, {
    Sidebar,
    TopBar,
    Drawer,
    SectionLabel,
    NAV
  });
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/Shell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/control-tower/data.js
try { (() => {
// Sample data — taken verbatim from docs/control-tower-design-prompt.md and docs/simulation-phase2-pct.html
window.CT_DATA = {
  intents: [{
    id: 'INT-001',
    name: 'Triển khai Phase 2 PCT (Release + Milestone + Backlog)',
    stage: 5,
    gate: 'D',
    holder: 'unit-planner',
    brownfield: 'Add feature',
    doc: 'wiki/docs/phase2-screens.md',
    owner: 'PMO Túy',
    updated: '14:22 hôm nay',
    units: [4, 0],
    risk: 'high'
  }, {
    id: 'INT-002',
    name: 'Slack reminder FB-012',
    stage: 2,
    holder: 'context-archaeologist',
    brownfield: 'Add feature',
    doc: 'FEEDBACK_TRACKER.md',
    owner: 'APM Hà',
    updated: '13:05 hôm nay',
    units: [0, 0],
    risk: null
  }, {
    id: 'INT-003',
    name: 'Quality Gate P1.2 — đóng nốt BATCH-020',
    stage: 6,
    holder: 'be-dev',
    brownfield: 'Add feature',
    doc: 'plans/phase-1/batch-020.md',
    owner: 'CTO',
    updated: '11:40 hôm nay',
    units: [3, 2],
    risk: null
  }, {
    id: 'INT-004',
    name: 'Weekly report export PDF chậm > 30s',
    stage: 6,
    gate: 'E',
    holder: 'tech-lead-reviewer',
    brownfield: 'Optimize NFR',
    doc: 'FEEDBACK_TRACKER.md#FB-031',
    owner: 'APM Hà',
    updated: 'hôm qua',
    units: [2, 1],
    risk: 'med'
  }, {
    id: 'INT-005',
    name: 'Gỡ mock layer SCR-REL-10 sau khi nối API thật',
    stage: 3,
    holder: 'context-validator',
    brownfield: 'Technical debt',
    doc: 'DEBT-03',
    owner: 'tech-lead',
    updated: 'hôm qua',
    units: [0, 0],
    risk: null
  }, {
    id: 'INT-006',
    name: 'Sai trạng thái RFE/NOID khi close case cũ',
    stage: 8,
    holder: 'acceptance-recorder',
    brownfield: 'Fix defect',
    doc: 'wiki/docs/use-cases.md',
    owner: 'Client SME',
    updated: '09/08',
    units: [2, 2],
    risk: null
  }],
  unitsByIntent: {
    'INT-003': [{
      id: 'UOW-01',
      name: 'Checklist gate cho batch',
      status: 'in-bolt',
      bolt: 'Bolt 1',
      done: 80,
      risks: []
    }, {
      id: 'UOW-02',
      name: 'Badge trạng thái gate trên milestone',
      status: 'in-bolt',
      bolt: 'Bolt 2',
      done: 40,
      risks: []
    }, {
      id: 'UOW-03',
      name: 'Export báo cáo gate',
      status: 'pending-gate',
      bolt: 'Bolt 3',
      done: 0,
      risks: []
    }],
    'INT-004': [{
      id: 'UOW-01',
      name: 'Cache query weekly report',
      status: 'in-bolt',
      bolt: 'Bolt 1',
      done: 65,
      risks: ['DEBT-02']
    }, {
      id: 'UOW-02',
      name: 'Render PDF nền (job queue)',
      status: 'blocked',
      bolt: 'Bolt 2',
      done: 10,
      risks: []
    }],
    'INT-006': [{
      id: 'UOW-01',
      name: 'Lifecycle rules cho terminal status',
      status: 'done',
      bolt: 'Bolt 1',
      done: 100,
      risks: []
    }, {
      id: 'UOW-02',
      name: 'Data migration case cũ',
      status: 'done',
      bolt: 'Bolt 2',
      done: 100,
      risks: []
    }]
  },
  gates: [{
    key: 'g1',
    kind: 'gate',
    gate: 'D',
    target: 'INT-001',
    title: 'Duyệt scope 4 Units + DoD v1',
    brief: 'unit-planner đề xuất 4 Units; pm-po verdict approve-with-notes (RV-010).',
    options: ['Approve cả 4 Units — UOW-04 Backlog phụ thuộc dữ liệu LakeHouse chưa nối (RISK-01)', 'Defer UOW-04 Backlog nếu chờ LakeHouse; 01–03 chạy ngay'],
    recommendation: 'approve 01–03, quyết riêng 04',
    evidence: ['RV-010', 'units/UOW-01..04/spec.md', 'risks.md']
  }, {
    key: 'g2',
    kind: 'escalation',
    target: 'UOW-03',
    title: 'tech-lead vs be-dev bất đồng: sync call legacy API sẽ timeout batch >500',
    brief: 'Đề xuất chuyển sang queue. 2× request-changes cùng một điểm (RV-012) → tự động escalate.',
    options: ['Giữ sync call, giới hạn batch 500 ở FE', 'Chuyển sang queue — thêm ~1 ngày, bỏ giới hạn batch'],
    recommendation: 'tech-lead: chuyển queue',
    evidence: ['RV-012', 'MSG-0074']
  }],
  units: [{
    id: 'UOW-01',
    name: 'Release Planning',
    status: 'in-bolt',
    bolt: 'Bolt 1',
    done: 60,
    risks: []
  }, {
    id: 'UOW-02',
    name: 'Milestone Timeline',
    status: 'in-bolt',
    bolt: 'Bolt 2',
    done: 25,
    risks: []
  }, {
    id: 'UOW-03',
    name: 'Release ↔ Milestone liên kết + badge',
    status: 'blocked',
    bolt: 'Bolt 3',
    done: 0,
    risks: ['escalation']
  }, {
    id: 'UOW-04',
    name: 'Backlog Integration View',
    status: 'pending-gate',
    bolt: 'Bolt 4',
    done: 0,
    risks: ['RISK-01 LakeHouse']
  }],
  tasks: [{
    id: 'TSK-01',
    title: 'API contract draft + freeze',
    status: 'done',
    claimedBy: 'be-dev',
    approver: 'fe-dev + tech-lead',
    msgCount: 4
  }, {
    id: 'TSK-02',
    title: 'BE: migration + model + service + router + tests',
    status: 'in-progress',
    claimedBy: 'be-dev',
    approver: 'backend-reviewer',
    dependsOn: 'TSK-01',
    msgCount: 2
  }, {
    id: 'TSK-03',
    title: 'FE: SCR-REL-10 list + filter (bỏ cột QG theo Q52)',
    status: 'in-progress',
    claimedBy: 'fe-dev',
    approver: 'frontend-reviewer',
    dependsOn: 'TSK-01',
    msgCount: 1
  }, {
    id: 'TSK-04',
    title: 'FE: SCR-REL-11 popup tạo/sửa nối API thật',
    status: 'blocked',
    approver: 'frontend-reviewer',
    dependsOn: 'TSK-02'
  }, {
    id: 'TSK-05',
    title: 'Integration + E2E theo AC',
    status: 'todo',
    approver: 'qa-reviewer',
    dependsOn: 'TSK-03, TSK-04'
  }],
  work: [{
    taskId: 'TSK-02',
    title: 'BE: migration + model + service + router + tests',
    agent: 'be-dev',
    status: 'in-progress',
    elapsed: '18 phút',
    doing: 'Viết migration cho bảng release — ràng buộc unique (project_id, name) để trả 409 đúng AC-03',
    target: 'app-be/migrations/003_release.py',
    steps: [{
      label: 'Đọc pattern router→service→model của app-be',
      state: 'done'
    }, {
      label: 'Migration + rollback script',
      state: 'doing'
    }, {
      label: 'Model Release + status enum 4 giá trị',
      state: 'todo'
    }, {
      label: 'Service + router theo contract v2',
      state: 'todo'
    }, {
      label: 'Unit tests theo AC-01..05',
      state: 'todo'
    }],
    messages: [{
      id: 'MSG-0060',
      from: 'be-dev',
      to: 'fe-dev',
      type: 'answer',
      body: 'Chốt: BE trả status code, FE map i18n.'
    }, {
      id: 'MSG-0062',
      from: 'be-dev',
      to: 'tech-lead-reviewer',
      type: 'question',
      body: 'Migration cần rollback script riêng hay dùng downgrade() của alembic là đủ?'
    }],
    waitingOn: 'backend-reviewer ký sau khi tests xanh'
  }, {
    taskId: 'TSK-03',
    title: 'FE: SCR-REL-10 list + filter',
    agent: 'fe-dev',
    status: 'in-progress',
    elapsed: '26 phút',
    doing: 'Dựng bảng release với mock theo contract v2 — bỏ cột Quality Gate theo Q52',
    target: 'app-fe/features/release/ReleaseList.tsx',
    steps: [{
      label: 'Mock data theo shape contract v2',
      state: 'done'
    }, {
      label: 'Bảng + filter status/phase',
      state: 'doing'
    }, {
      label: 'i18n key cho 4 status',
      state: 'todo'
    }, {
      label: 'Component tests',
      state: 'todo'
    }],
    messages: [{
      id: 'MSG-0058',
      from: 'fe-dev',
      to: 'be-dev',
      type: 'clarification',
      body: 'status enum trả code hay label? i18n phía nào?'
    }, {
      id: 'MSG-0063',
      from: 'fe-dev',
      to: 'frontend-reviewer',
      type: 'review-request',
      body: 'Xin review sớm phần state của filter trước khi nối API thật.'
    }],
    waitingOn: null
  }, {
    taskId: 'TSK-04',
    title: 'FE: SCR-REL-11 popup tạo/sửa nối API thật',
    agent: 'fe-dev',
    status: 'blocked',
    elapsed: '—',
    doing: 'Chưa claim — luật claim chặn: task phụ thuộc chưa được approver duyệt',
    steps: [{
      label: 'TSK-02 done',
      state: 'todo'
    }, {
      label: 'backend-reviewer duyệt TSK-02',
      state: 'todo'
    }, {
      label: 'Nối form với POST/PATCH /api/releases',
      state: 'todo'
    }],
    messages: [{
      id: 'MSG-0064',
      from: 'bolt-coordinator',
      to: 'fe-dev',
      type: 'note',
      body: 'TSK-04 mở khoá ngay khi RV của TSK-02 là approve.'
    }],
    waitingOn: 'TSK-02 done + backend-reviewer duyệt'
  }, {
    taskId: 'TSK-01',
    title: 'API contract draft + freeze',
    agent: 'be-dev',
    status: 'done',
    elapsed: 'xong 13:40',
    doing: 'Đã freeze contract v2 sau 4 lượt trao đổi với fe-dev',
    target: 'UOW-01/contract.md',
    steps: [{
      label: 'Draft v1',
      state: 'done'
    }, {
      label: 'fe-dev review + hỏi làm rõ',
      state: 'done'
    }, {
      label: 'Chốt v2 + FREEZE',
      state: 'done'
    }],
    messages: [{
      id: 'MSG-0061',
      from: 'be-dev',
      to: 'fe-dev',
      type: 'handoff',
      body: 'contract.md v2 FROZEN — TSK-03 chạy được với mock đúng shape.'
    }],
    waitingOn: null
  }],
  feed: [{
    time: '14:22',
    id: 'MSG-0058',
    from: 'fe-dev',
    to: 'be-dev',
    type: 'clarification',
    summary: 'status enum trả code hay label? i18n phía nào?'
  }, {
    time: '14:20',
    id: 'MSG-0060',
    from: 'be-dev',
    to: 'fe-dev',
    type: 'answer',
    summary: 'chốt: trả code, FE map i18n'
  }, {
    time: '14:11',
    id: 'RV-011',
    from: 'security-reviewer',
    to: 'UOW-01',
    type: 'review-request',
    summary: 'threat model OK — 0 MUST finding'
  }, {
    time: '13:58',
    id: 'RV-012',
    from: 'tech-lead-reviewer',
    to: 'be-dev',
    type: 'finding',
    summary: 'sync call legacy API sẽ timeout batch >500 — request-changes lần 2'
  }, {
    time: '13:40',
    id: 'MSG-0055',
    from: 'bolt-coordinator',
    to: 'fe-dev',
    type: 'handoff',
    summary: 'contract v2 FROZEN — TSK-03 có thể chạy với mock'
  }, {
    time: '13:12',
    id: 'DEC-0017',
    from: 'orchestrator',
    to: 'INT-001',
    type: 'decision',
    summary: 'Gate C đóng — Backlog đi mock-first'
  }, {
    time: '12:50',
    id: 'MSG-0049',
    from: 'qa-reviewer',
    to: 'unit-planner',
    type: 'question',
    summary: 'AC của UOW-02: Gantt cần zoom tuần không?'
  }],
  trace: [{
    kind: 'code',
    id: 'app-be/releases/service.py',
    note: 'validate unique name → 409'
  }, {
    kind: 'design',
    id: 'UOW-01/design.md',
    note: 'entity Release · status enum 4 giá trị'
  }, {
    kind: 'spec',
    id: 'UOW-01/spec.md',
    note: 'AC-03'
  }, {
    kind: 'dec',
    id: 'DEC-0015',
    note: 'Gate A — scope Phase 2 không gồm QG'
  }, {
    kind: 'rv',
    id: 'RV-010',
    note: 'pm-po · approve-with-notes'
  }, {
    kind: 'msg',
    id: 'MSG-0058',
    note: 'fe-dev hỏi status enum'
  }, {
    kind: 'intent',
    id: 'INT-001',
    note: 'Triển khai Phase 2 PCT'
  }],
  reviews: [{
    id: 'RV-010',
    reviewer: 'pm-po-reviewer',
    target: 'INT-001 · unit breakdown',
    verdict: 'approve-with-notes',
    checklist: 'plan-review v2',
    findings: 'SHOULD: ghi rõ thứ tự Bolt trong spec'
  }, {
    id: 'RV-011',
    reviewer: 'security-reviewer',
    target: 'UOW-01 · design',
    verdict: 'approve',
    checklist: 'review-threat-model v4',
    findings: '—'
  }, {
    id: 'RV-012',
    reviewer: 'tech-lead-reviewer',
    target: 'UOW-03 · approach',
    verdict: 'request-changes',
    checklist: 'review-approach v2',
    findings: 'MUST: batch >500 timeout — chuyển queue'
  }, {
    id: 'RV-013',
    reviewer: 'qa-reviewer',
    target: 'UOW-01 · test strategy',
    verdict: 'approve',
    checklist: 'review-ac-coverage v3',
    findings: '—'
  }],
  decisions: [{
    id: 'DEC-0015',
    when: '11/08 09:20',
    gate: 'A',
    by: 'Human supervisor',
    what: 'Scope Phase 2 = Release + Milestone + Backlog, không gồm Quality Gate',
    basis: 'RV-008'
  }, {
    id: 'DEC-0016',
    when: '11/08 11:05',
    gate: 'B',
    by: 'Validation Mob',
    what: 'AS-IS đúng; tracker mới nhất do PMO giữ',
    basis: 'MSG-0031'
  }, {
    id: 'DEC-0017',
    when: '11/08 13:12',
    gate: 'C',
    by: 'CTO',
    what: 'Backlog đi mock-first, không chờ LakeHouse',
    basis: 'open-questions.md#Q56'
  }],
  questions: [{
    q: 'Backlog: làm UI trước với mock hay chờ LakeHouse nối xong?',
    who: 'CTO',
    due: '11/08',
    impact: 'UOW-04 không vào được Bolt',
    status: 'đã chốt'
  }, {
    q: 'Release "Cancelled" có cho sửa milestone gắn kèm không?',
    who: 'PMO',
    due: '13/08',
    impact: 'AC của UOW-03',
    status: 'đang chờ'
  }, {
    q: 'Gantt milestone: cần zoom tuần/tháng ngay đợt này?',
    who: 'APM đại diện',
    due: '13/08',
    impact: 'scope UOW-02',
    status: 'đang chờ'
  }],
  risks: [{
    id: 'RISK-01',
    sev: 'high',
    text: 'LakeHouse chưa nối — dữ liệu backlog chưa có thật',
    owner: 'CTO'
  }, {
    id: 'RISK-02',
    sev: 'med',
    text: 'FEEDBACK_TRACKER.md trên repo là bản cũ, bản mới PMO giữ',
    owner: 'PMO'
  }, {
    id: 'RISK-04',
    sev: 'high',
    text: 'Migration case cũ chưa có câu trả lời từ client',
    owner: 'BA'
  }],
  debt: [{
    id: 'DEBT-02',
    sev: 'med',
    text: 'app-be chưa có rollback script cho migration release',
    owner: 'tech-lead-reviewer'
  }, {
    id: 'DEBT-03',
    sev: 'low',
    text: 'FE mock layer của SCR-REL-10 cần gỡ sau khi nối API thật',
    owner: 'fe-dev'
  }],
  lessons: [{
    id: 'LL-001',
    trigger: 'Phase mapping đổi theo quyết định CTO ngoài repo',
    lesson: 'Luôn hỏi bản tracker/plan mới nhất nằm ở đâu — repo hay PMO giữ',
    patch: 'review-intent v1→v2',
    status: 'applied'
  }, {
    id: 'LL-002',
    trigger: 'Legacy API có batch limit không tài liệu hóa',
    lesson: 'Hỏi batch limit/timeout của mọi external call ngay ở Domain Design',
    patch: 'review-approach v2→v3',
    status: 'proposed'
  }],
  governance: {
    dor: {
      version: 'v3',
      items: ['AC đo được, có ví dụ số liệu', 'Open questions liên quan đã đóng hoặc có working-assumption gắn nhãn', 'Đã xác định approver cho từng task', 'Phụ thuộc Unit khác được ghi rõ']
    },
    dod: {
      version: 'v1',
      items: ['Tests pass, coverage AC 100%', 'Security MUST findings = 0', 'Acceptance evidence đầy đủ (AC ✓, test output, screenshots, limitations)', 'Trace chain code → design → spec → DEC → RV → MSG → intent đủ']
    },
    changelog: [{
      v: 'DoR v3',
      when: '02/08',
      by: 'Human supervisor',
      dec: 'DEC-0011',
      from: 'LL-001'
    }, {
      v: 'DoD v1',
      when: '11/08',
      by: 'Human supervisor',
      dec: 'DEC-0018',
      from: '—'
    }]
  }
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/control-tower/data.js", error: String((e && e.message) || e) }); }

// ui_kits/engineering-docs/BlueprintDoc.jsx
try { (() => {
(function () {
  const NSd = window.ControlTowerDesignSystem_68131c;
  const {
    Eyebrow,
    StatusChip,
    Tag,
    DataTable,
    Callout,
    Panel,
    Timeline,
    TimelineItem,
    GateStop,
    IdCode,
    Chip,
    PipelineRow,
    FeedItem,
    GateCard,
    VerdictBadge
  } = NSd;
  const ROSTER_PIPELINE = [['orchestrator', 'xuyên suốt', 'Điều phối flow, giữ state, enforce gate — không cho stage sau chạy khi gate trước chưa có quyết định.', 'status.md · decisions-log.md'], ['intent-analyst', '1 · Request', 'Capture problem · outcome · priority; nhận diện brownfield type và vùng ảnh hưởng.', 'intent.md'], ['context-archaeologist', '2 · Discovery', 'Đọc code · docs · tickets · tests · DB → AS-IS model.', 'as-is/'], ['context-validator', '3–4 · Validation + Clarify', 'Trình bày AS-IS cho Validation Mob; generate open questions.', 'open-questions.md'], ['unit-planner', '5 · Unit Definition', 'Chia Intent thành Units theo business capability; reject pseudo-unit.', 'units/UOW-xx/spec.md'], ['bolt-coordinator', '6 · Construction', 'Điều phối một Bolt cho một Unit: chia task board, enforce luật claim.', 'tasks.md + design.md'], ['be-dev', '6 · Construction', 'API contract draft, service, DB migration, tests.', 'code BE + contract.md'], ['fe-dev', '6 · Construction', 'Review contract trước khi code, component, state, tests.', 'code FE'], ['acceptance-recorder', '7–8 · Acceptance + Release', 'Gom Acceptance Evidence; trace decision → requirement → design → code.', 'evidence/ · changelog.md']];
  const ROSTER_REVIEW = [['ba-reviewer', 'Business Analyst', 'Góc nhìn business stage 1–4; soạn decision brief cho gate A–D.', 'review-intent · business-validation · decision-brief'], ['pm-po-reviewer', 'PM / PO', 'Plan & task breakdown, risk register mỗi bolt, DoD/DoR compliance ở gate D.', 'plan-review · risk-register · quality-gate'], ['tech-lead-reviewer', 'Technical Leader', 'Technical approach & design trước khi viết code; giữ tech-debt-register.', 'review-approach · review-infra · review-techstack'], ['security-reviewer', 'Security / DevSecOps', 'Threat model, code security, dependency, CI/CD. Có quyền block release.', 'review-threat-model · review-code-security · review-pipeline'], ['backend-reviewer', 'Dev góc nhìn BE', 'Code BE trong bolt: API contract, DB migration, performance.', 'review-api · review-db · review-perf'], ['frontend-reviewer', 'Dev góc nhìn FE', 'Code FE: kiến trúc component, state, accessibility, nhất quán UX.', 'review-component · review-state · review-a11y'], ['qa-reviewer', 'QA / QC', 'DoR check trước Bolt, test strategy trong bolt, verify Acceptance Evidence stage 7.', 'review-test-strategy · review-ac-coverage · qc-evidence']];
  function BlueprintDoc() {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        maxWidth: 1100,
        margin: '0 auto',
        padding: '48px 24px 96px'
      }
    }, /*#__PURE__*/React.createElement("header", {
      style: {
        borderBottom: '2px solid var(--ink)',
        paddingBottom: 24,
        marginBottom: 8
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        gap: 16,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontFamily: 'var(--mono)',
        fontSize: 12,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color: 'var(--muted)'
      }
    }, "AI-DLC \xB7 Engineering process \xB7 TechTus"), /*#__PURE__*/React.createElement(StatusChip, {
      tone: "gate"
    }, "B\u1EA2N THI\u1EBET K\u1EBE v3 \u2014 CH\u1EDC DUY\u1EC6T")), /*#__PURE__*/React.createElement("h1", {
      style: {
        fontSize: 'clamp(28px,4.5vw,44px)',
        fontWeight: 750,
        letterSpacing: '-0.02em',
        lineHeight: 1.12,
        margin: '10px 0 12px'
      }
    }, "Agent Team & Control Tower"), /*#__PURE__*/React.createElement("p", {
      style: {
        maxWidth: '68ch',
        color: 'var(--muted)',
        fontSize: 17,
        margin: 0
      }
    }, "B\u1EA3n thi\u1EBFt k\u1EBF \u0111\u1EA7y \u0111\u1EE7 tr\u01B0\u1EDBc khi tri\u1EC3n khai: 9 pipeline agents ch\u1EA1y flow 8 stage, 7 review agents \u0111\u1ED9c l\u1EADp theo vai tr\xF2, task board trong t\u1EEBng Unit v\u1EDBi dependency \u2014 claim \u2014 approver, v\xF2ng retro \u2014 lesson learned, v\xE0 Control Tower theo d\xF5i to\xE0n b\u1ED9. M\u1ECDi quy\u1EBFt \u0111\u1ECBnh v\xE0 thay \u0111\u1ED5i c\u1EE7a AI \u0111\u1EC1u th\xE0nh t\xE0i li\u1EC7u truy v\u1EBFt \u0111\u01B0\u1EE3c.")), /*#__PURE__*/React.createElement("section", {
      style: {
        marginTop: 64
      }
    }, /*#__PURE__*/React.createElement(Eyebrow, null, "01 \xB7 \u0110\u1ED9i h\xECnh"), /*#__PURE__*/React.createElement("h2", {
      style: {
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: '-0.01em',
        marginBottom: 12
      }
    }, "B\u1ED1n nh\xF3m, m\u1ED9t nguy\xEAn t\u1EAFc: AI th\u1EF1c thi \u2014 ng\u01B0\u1EDDi quy\u1EBFt \u0111\u1ECBnh"), /*#__PURE__*/React.createElement("p", {
      style: {
        maxWidth: '68ch',
        marginBottom: 12
      }
    }, "\u0110\u1ED9i h\xECnh chia b\u1ED1n nh\xF3m. ", /*#__PURE__*/React.createElement("strong", null, "Pipeline agents"), " \u0111\u1EA9y c\xF4ng vi\u1EC7c qua 8 stage c\u1EE7a AI-DLC. ", /*#__PURE__*/React.createElement("strong", null, "Review Board"), " \u2014 c\xE1c agent \u0111\u1ED9c l\u1EADp theo vai tr\xF2, kh\xF4ng tham gia th\u1EF1c thi, ch\u1EC9 review \u0111\xFAng \u0111o\u1EA1n thu\u1ED9c chuy\xEAn m\xF4n v\xE0 ra verdict. ", /*#__PURE__*/React.createElement("strong", null, "Learning"), " \u2014 retro-keeper bi\u1EBFn lesson learned th\xE0nh n\xE2ng c\u1EA5p skill cho agent."), /*#__PURE__*/React.createElement("h3", {
      style: {
        fontSize: 18,
        fontWeight: 650,
        margin: '28px 0 8px',
        display: 'flex',
        gap: 10,
        alignItems: 'baseline'
      }
    }, /*#__PURE__*/React.createElement(Tag, {
      kind: "pipeline"
    }, "PIPELINE"), " \u2014 9 agents th\u1EF1c thi theo stage"), /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Agent', 'Stage', 'Trách nhiệm', 'Output'],
      rows: ROSTER_PIPELINE
    }), /*#__PURE__*/React.createElement("h3", {
      style: {
        fontSize: 18,
        fontWeight: 650,
        margin: '28px 0 8px',
        display: 'flex',
        gap: 10,
        alignItems: 'baseline'
      }
    }, /*#__PURE__*/React.createElement(Tag, {
      kind: "review"
    }, "REVIEW BOARD"), " \u2014 7 agents review \u0111\u1ED9c l\u1EADp"), /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Agent', 'Vai trò', 'Review cái gì · khi nào', 'Bộ skill chuyên biệt'],
      rows: ROSTER_REVIEW
    }), /*#__PURE__*/React.createElement("h3", {
      style: {
        fontSize: 18,
        fontWeight: 650,
        margin: '28px 0 8px',
        display: 'flex',
        gap: 10,
        alignItems: 'baseline'
      }
    }, /*#__PURE__*/React.createElement(Tag, {
      kind: "learning"
    }, "LEARNING"), " \u2014 1 agent gi\u1EEF v\xF2ng h\u1ECDc"), /*#__PURE__*/React.createElement(DataTable, {
      columns: ['Agent', 'Khi nào chạy', 'Trách nhiệm', 'Output'],
      rows: [['retro-keeper', 'Sau mỗi Release (stage 8)', 'Phân tích comms + verdicts + escalations → rút lesson learned → đề xuất patch vào checklist. Patch chỉ apply sau Gate G.', 'lessons-learned/LL-xx.md · skill patch + version']]
    }), /*#__PURE__*/React.createElement("p", {
      style: {
        maxWidth: '68ch',
        color: 'var(--muted)',
        fontSize: 14.5,
        marginTop: 16
      }
    }, "M\u1ED7i b\u1ED9 skill l\xE0 m\u1ED9t checklist file c\xF3 version trong ", /*#__PURE__*/React.createElement(IdCode, {
      variant: "inline"
    }, ".claude/skills/"), " \u2014 ti\xEAu ch\xED \u0111\xE1nh gi\xE1 \u0111\u01B0\u1EE3c chu\u1EA9n h\xF3a v\xE0 ti\u1EBFn h\xF3a c\xF3 ki\u1EC3m so\xE1t qua retro.")), /*#__PURE__*/React.createElement("section", {
      style: {
        marginTop: 64
      }
    }, /*#__PURE__*/React.createElement(Eyebrow, null, "02 \xB7 H\xE0nh tr\xECnh"), /*#__PURE__*/React.createElement("h2", {
      style: {
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: '-0.01em',
        marginBottom: 12
      }
    }, "T\u1EEB c\xE2u l\u1EC7nh c\u1EE7a anh/ch\u1ECB t\u1EDBi danh s\xE1ch Unit \u0111\u01B0\u1EE3c duy\u1EC7t"), /*#__PURE__*/React.createElement(Callout, {
      tone: "agent"
    }, /*#__PURE__*/React.createElement("strong", null, "Ph\xE1t hi\u1EC7n quan tr\u1ECDng ngay \u1EDF b\u01B0\u1EDBc \u0111\u1ECDc"), ": t\xE0i li\u1EC7u c\u0169 n\xF3i Phase 2 g\u1ED3m Quality Gate, nh\u01B0ng mapping CTO 2026-08-11 \u0111\xE3 k\xE9o nh\xF3m QG l\xEAn Phase 1.2. \"Phase 2 th\u1EADt\" = Release Planning + Milestone + Backlog Integration."), /*#__PURE__*/React.createElement(Timeline, null, /*#__PURE__*/React.createElement(TimelineItem, {
      actor: "intent-analyst + ba-reviewer",
      heading: "Stage 1 \xB7 Request \u2192 Intent"
    }, "Capture problem, outcome, brownfield type v\xE0 v\xF9ng \u1EA3nh h\u01B0\u1EDFng. ba-reviewer so\u1EA1n decision brief cho Gate A.", /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 6
      }
    }, /*#__PURE__*/React.createElement(IdCode, {
      variant: "artifact"
    }, "INT-001/intent.md"), /*#__PURE__*/React.createElement(IdCode, {
      variant: "artifact"
    }, "decision-brief-A.md")), /*#__PURE__*/React.createElement(GateStop, {
      label: "\u25C7 GATE A \u2014 D\u1EEANG, CH\u1EDC ANH/CH\u1ECA (l\u1EA7n confirm #1)"
    }, "Scope Phase 2 = Release + Milestone + Backlog, kh\xF4ng g\u1ED3m Quality Gate \u2014 \u0111\xFAng kh\xF4ng? Outcome \u0111o b\u1EB1ng g\xEC? Backlog Integration thu\u1ED9c \u0111\u1EE3t n\xE0y hay defer?")), /*#__PURE__*/React.createElement(TimelineItem, {
      actor: "context-archaeologist",
      heading: "Stage 2 \xB7 Context Discovery (AS-IS)"
    }, "\u0110\u1ECDc code + docs \u2192 d\u1EF1ng AS-IS model: schema hi\u1EC7n t\u1EA1i, pattern router\u2192service\u2192model c\u1EE7a app-be, pattern component + i18n c\u1EE7a app-fe. Kh\xF4ng h\u1ECFi ai \u1EDF stage n\xE0y \u2014 ch\u1EC9 \u0111\u1ECDc."), /*#__PURE__*/React.createElement(TimelineItem, {
      actor: "Validation Mob",
      lane: "human",
      heading: "Stage 3 \xB7 Context Validation"
    }, "AI tr\xECnh b\xE0y understanding; ba-reviewer \u0111\u1ED1i chi\u1EBFu t\u1EEBng kh\u1EB3ng \u0111\u1ECBnh v\u1EDBi wiki + Q&A, g\u1EAFn nh\xE3n ph\u1EA7n n\xE0o l\xE0 suy lu\u1EADn ch\u01B0a c\xF3 c\u0103n c\u1EE9.", /*#__PURE__*/React.createElement(GateStop, {
      label: "\u25C7 GATE B \u2014 D\u1EEANG, CH\u1EDC ANH/CH\u1ECA (l\u1EA7n confirm #2)"
    }, "QG P1.2 \u0111\xE3 ship t\u1EDBi \u0111\xE2u? B\u1EA3n tracker tr\xEAn repo l\xE0 b\u1EA3n c\u0169 \u2014 AS-IS c\xF3 thi\u1EBFu batch n\xE0o kh\xF4ng?")), /*#__PURE__*/React.createElement(TimelineItem, {
      actor: "unit-planner \u2192 pm-po-reviewer",
      heading: "Stage 5 \xB7 Unit Definition",
      last: true
    }, "Chia Intent th\xE0nh 4 Units theo business capability; pm-po l\u1EADp risk register; qa check DoR.", /*#__PURE__*/React.createElement(GateStop, {
      label: "\u25C7 GATE D \u2014 D\u1EEANG, CH\u1EDC ANH/CH\u1ECA (l\u1EA7n confirm #4 \u2014 quan tr\u1ECDng nh\u1EA5t)"
    }, "Approve scope + DoD \u2192 c\xE1c Unit unlocked, ghi ", /*#__PURE__*/React.createElement(IdCode, {
      variant: "inline"
    }, "DEC"), ". T\u1EEB \u0111\xE2y m\u1EDBi \u0111\u01B0\u1EE3c vi\u1EBFt d\xF2ng code \u0111\u1EA7u ti\xEAn.")))), /*#__PURE__*/React.createElement("section", {
      style: {
        marginTop: 64
      }
    }, /*#__PURE__*/React.createElement(Eyebrow, null, "03 \xB7 Control Tower"), /*#__PURE__*/React.createElement("h2", {
      style: {
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: '-0.01em',
        marginBottom: 12
      }
    }, "M\u1ED9t m\xE0n h\xECnh tr\u1EA3 l\u1EDDi: \u0111ang \u1EDF \u0111\xE2u, ai \u0111ang l\xE0m g\xEC, c\xE1i g\xEC ch\u1EDD t\xF4i"), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(0,1.1fr) minmax(280px,1fr)',
        gap: 16,
        marginTop: 20
      }
    }, /*#__PURE__*/React.createElement(Panel, {
      title: "Gate queue"
    }, /*#__PURE__*/React.createElement(GateCard, {
      gate: "D",
      target: "INT-001",
      title: "Duy\u1EC7t scope 4 Units + DoD v1",
      brief: "pm-po-reviewer verdict: approve-with-notes (RV-010)."
    }), /*#__PURE__*/React.createElement(GateCard, {
      kind: "escalation",
      target: "UOW-03",
      title: "tech-lead vs be-dev: queue vs sync call",
      brief: "2\xD7 request-changes (RV-012)."
    })), /*#__PURE__*/React.createElement(Panel, {
      title: "Pipeline board",
      pad: false
    }, /*#__PURE__*/React.createElement(PipelineRow, {
      id: "INT-001",
      name: "Phase 2 PCT",
      current: 5,
      gate: "D",
      holder: "unit-planner"
    }), /*#__PURE__*/React.createElement(PipelineRow, {
      id: "INT-002",
      name: "Slack reminder FB-012",
      current: 2,
      holder: "context-archaeologist"
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 6,
        padding: '10px 16px',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(VerdictBadge, {
      id: "RV-011",
      reviewer: "security",
      verdict: "approve"
    }), /*#__PURE__*/React.createElement(VerdictBadge, {
      id: "RV-012",
      reviewer: "tech-lead",
      verdict: "request-changes"
    })))), /*#__PURE__*/React.createElement("p", {
      style: {
        maxWidth: '68ch',
        color: 'var(--muted)',
        fontSize: 14.5,
        marginTop: 14
      }
    }, "Ngo\xE0i 7 lo\u1EA1i \u0111i\u1EC3m d\u1EEBng n\xE0y, agents kh\xF4ng h\u1ECFi v\u1EB7t \u2014 m\u1ECDi th\u1EE9 kh\xE1c t\u1EF1 ch\u1EA1y v\xE0 t\u1EF1 ghi l\u1EA1i.")), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 56,
        border: '2px solid var(--accent)',
        borderRadius: 12,
        background: 'var(--accent-bg)',
        padding: '24px 28px'
      }
    }, /*#__PURE__*/React.createElement("h2", {
      style: {
        fontSize: 26,
        fontWeight: 700,
        marginBottom: 8
      }
    }, "Ch\u1EDD anh/ch\u1ECB duy\u1EC7t"), /*#__PURE__*/React.createElement("p", {
      style: {
        marginBottom: 6,
        maxWidth: '68ch'
      }
    }, "N\u1EBFu b\u1EA3n thi\u1EBFt k\u1EBF n\xE0y \u0111\xFAng \xFD, b\u01B0\u1EDBc ti\u1EBFp theo l\xE0 scaffold b\u1ED9 agent r\u1ED3i ch\u1EA1y th\u1EADt ", /*#__PURE__*/React.createElement(IdCode, {
      variant: "inline"
    }, "/intent"), " cho PCT Phase 2 \u2014 d\u1EEBng \u1EDF Gate A ch\u1EDD anh/ch\u1ECB.")));
  }
  const rootEl = document.getElementById('root');
  if (rootEl) ReactDOM.createRoot(rootEl).render(/*#__PURE__*/React.createElement(BlueprintDoc, null));
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/engineering-docs/BlueprintDoc.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Callout = __ds_scope.Callout;

__ds_ns.Chip = __ds_scope.Chip;

__ds_ns.DataTable = __ds_scope.DataTable;

__ds_ns.Eyebrow = __ds_scope.Eyebrow;

__ds_ns.IdCode = __ds_scope.IdCode;

__ds_ns.Panel = __ds_scope.Panel;

__ds_ns.StatusChip = __ds_scope.StatusChip;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.MermaidDiagram = __ds_scope.MermaidDiagram;

__ds_ns.AgentAvatar = __ds_scope.AgentAvatar;

__ds_ns.AgentWorkCard = __ds_scope.AgentWorkCard;

__ds_ns.FeedItem = __ds_scope.FeedItem;

__ds_ns.GateCard = __ds_scope.GateCard;

__ds_ns.GateStop = __ds_scope.GateStop;

__ds_ns.KpiStrip = __ds_scope.KpiStrip;

__ds_ns.PipelineRow = __ds_scope.PipelineRow;

__ds_ns.STAGES = __ds_scope.STAGES;

__ds_ns.StageStrip = __ds_scope.StageStrip;

__ds_ns.TaskRow = __ds_scope.TaskRow;

__ds_ns.TimelineItem = __ds_scope.TimelineItem;

__ds_ns.Timeline = __ds_scope.Timeline;

__ds_ns.TraceChain = __ds_scope.TraceChain;

__ds_ns.VerdictBadge = __ds_scope.VerdictBadge;

})();
