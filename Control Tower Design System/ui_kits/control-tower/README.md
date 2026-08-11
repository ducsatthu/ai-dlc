# UI kit — Control Tower (web app)

Recreation of the five screens specified in `docs/control-tower-design-prompt.md`. Dark is the default mode (ops console); the top-right toggle switches to light. Vietnamese is the UI language; English terms — Intent, Unit, Bolt, Gate, Task, MSG, RV, DEC, LL — are kept verbatim.

| File | Screen |
|---|---|
| `index.html` | entry — loads tokens + `_ds_bundle.js`, mounts `App.jsx` |
| `Shell.jsx` | sidebar nav, top bar, right drawer, section label |
| `MissionControl.jsx` | Screen 1 — KPI strip, gate queue, pipeline board, live feed |
| `IntentDetail.jsx` | Screen 2 — INT-001 with Units / Open Questions / Decisions / Changelog tabs |
| `BoltBoard.jsx` | Screen 3 — UOW-01 Bolt 1 kanban + list, contract panel, Gate E checkpoint |
| `CommsReviews.jsx` | Screen 4 — filterable MSG table, thread view, RV table |
| `Governance.jsx` | Screen 5 — DoR/DoD + versions, risk & tech-debt registers, lessons |
| `data.js` | sample data, taken from the design prompt and the PCT dry-run — no lorem |

## What is interactive

Sidebar navigation · gate cards expand to the decision brief · Approve clears the gate and writes a DEC toast · Reject requires a reason before it can be sent · pipeline rows open the intent · unit cards open Bolt 1 · task cards and feed rows open the right drawer with the full trace chain · feed and comms type filters · kanban/list toggle · dark/light toggle.

## Not built (absent from the sources)

Gantt rendering for UOW-02 Milestone Timeline, the real dependency graph drawing between tasks, and search. The source documents describe these in words only.
