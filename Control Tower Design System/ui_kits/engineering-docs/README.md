# UI kit — Engineering docs

Recreation of the long-form process documents TechTus publishes as standalone HTML: `docs/agent-team-blueprint.html` (v3 blueprint) and `docs/simulation-phase2-pct.html` (dry-run walkthrough). Both share one layout, so this kit builds the blueprint and the dry-run's timeline pattern in a single page.

| File | Contents |
|---|---|
| `index.html` | entry — light theme by default (documents read light; the console runs dark) |
| `diagrams.html` | six Mermaid diagrams of how the agents communicate — topology, gate flow, contract handshake, escalation, task graph, trace chain |
| `BlueprintDoc.jsx` | masthead + status chip, numbered sections, roster tables, gate timeline, embedded tower mock, approval box |

Layout rules copied from the source: 1100px max width (980px for the dry-run), `48px 24px 96px` page padding, 64px between sections, 68ch prose measure, 2px ink rule under the masthead and every table head.

The blueprint's large hand-authored SVG workflow diagrams are not redrawn as SVG. Their content is instead expressed as Mermaid in `components/diagrams/DIAGRAMS.js` and rendered on `diagrams.html` — editing text edits the picture.
