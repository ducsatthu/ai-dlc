# Control Tower Design System

Design system for the **AI-DLC Control Tower** — the observation console a single Human Supervisor uses to watch a team of 17 AI agents build software through the AI-DLC (AI-Driven Development Lifecycle) process, and for the long-form engineering documents that describe that process.

The supervisor does not code. Their job is to **watch progress, decide at gates, and trace everything the AI did.** Every design decision here serves that job.

## Sources

Everything in this system was derived from an attached, read-only codebase mounted at `docs/`. No Figma file, no repository, no brand book was provided.

| Source | What it gave us |
|---|---|
| `docs/control-tower-design-prompt.md` | The product spec: 5 screens, jobs-to-be-done, colour semantics, sample data, "ops console / air-traffic control" direction |
| `docs/agent-team-blueprint.html` | Ground-truth CSS (the entire token set), the 17-agent roster, the workflow, and an embedded Control Tower mock |
| `docs/simulation-phase2-pct.html` | Ground-truth CSS (identical tokens), the dry-run walkthrough, task-board and timeline patterns, real sample data (INT-001, UOW-01..04, TSK-01..05, MSG-0058, RV-010..013, LL-002, RISK-04) |

Product context: **TechTus**, an outsourcing engineering organisation adopting AWS's AI-DLC method. Work flows through 8 stages (`1 Request → 2 Discovery → 3 Validation → 4 Clarify → 5 Units → 6 Construction → 7 Acceptance → 8 Release`) and **stops at 7 mandatory gates (A–G)** waiting on a human. No mechanism lets an agent pass a gate. The running example throughout the system is *PCT Phase 2 — Release Planning + Milestone + Backlog Integration*.

Two surfaces are represented:

1. **Control Tower** — the web app (dark by default, desktop-first, Vietnamese UI with English domain terms kept verbatim).
2. **Engineering docs** — standalone HTML process documents (light by default, 1100px measure, printed-report feel).

---

## Content fundamentals

**Language.** Vietnamese is the UI and document language. English domain terms are never translated: Intent, Unit of Work, Bolt, Task, Gate, Escalation, contract, approve / reject / request-changes, DoR, DoD, brownfield, AS-IS, backlog.

**Voice.** Second person, formal-respectful: **"anh/chị"** for the human supervisor, never "bạn" in documents (the app's UI chrome may use "bạn" in short labels like *"Gates chờ tôi"* / *"chờ bạn"* — first person is used only for the supervisor's own queue). Agents are named in the third person by their id (`be-dev`, `tech-lead-reviewer`), never anthropomorphised with names or pronouns.

**Register.** Matter-of-fact, engineering-memo. Claims come with an ID attached. Nothing is hyped and nothing is hedged:

> "AI là execution engine. Người giữ context, trade-off và quyết định."
> "Từ đây mới được viết dòng code đầu tiên."
> "Không hỏi ai ở stage này — chỉ đọc."

**Copy patterns.**
- Section headings state the answer, not the topic: *"Bốn nhóm, một nguyên tắc: AI thực thi — người quyết định"*, *"Bảy điểm dừng bắt buộc"*.
- Question-form headings are used for user-facing jobs: *"Cái gì đang chờ TÔI?"*, *"Mọi thứ đang ở đâu?"*
- Em dash for the qualifying clause; middot `·` as the meta separator (`14:22 · fe-dev → be-dev · clarification`).
- Consequences are always spelled out: *"Nếu không quyết → flow đứng ở stage 1."*
- Empty states are reassuring, not blank: *"Không có gì chờ bạn — agents đang làm việc."*

**Casing.** Sentence case for headings and body. UPPERCASE only for mono labels (eyebrows, table headers, status chips, button labels) — never for sans prose. Agent ids and artifact paths stay lowercase-hyphenated.

**Emoji.** Effectively none. One 🧪 appears on a "GIẢ LẬP — CHƯA CHẠY THẬT" chip in the dry-run document; treat that as an outlier, not a pattern. Do not add emoji.

**Numbers and IDs.** Every entity carries a traceable ID and always renders in mono: `INT-001`, `UOW-01`, `TSK-02`, `MSG-0058`, `RV-012`, `DEC-0018`, `LL-002`, `RISK-04`, `BATCH-020`, `Q52`. Screens carry codes too (`SCR-REL-10`). Versions are `v1`, `v2→v3`.

---

## Visual foundations

**Overall.** Ops console: dense but unhurried, flat, monochrome-with-signal. No hero sections, no marketing gestures, no purple gradients, no illustration.

**Colour.** A cold neutral base plus exactly three signal colours whose meanings are fixed system-wide:

- **Amber** `#B96E00` light / `#E9A23B` dark — **a human must decide**. Gates, escalations, the active stage, `request-changes`, primary actions, eyebrows.
- **Blue** `#33689E` / `#7FAEDC` — agent and review activity. Feed entries, comms, agent tags.
- **Green** `#2E7D4F` / `#58B383` — done, approved.
- **Grey muted** — pending, not-yet-your-problem.
- `--danger` (`#A83B2B` / `#E1786A`) is a **derived addition**, not in the sources; it is used only for `blocked` tasks and the Reject action.

Fills are always a ~10–13% tint of the signal colour behind a 1px full-strength border of the same colour. There are no solid colour blocks except the `here` chip and primary button.

**Light and dark.** Both are first-class and use the same token names. The app defaults to dark; documents default to light. The source honours `prefers-color-scheme` and allows an explicit `data-theme` override — keep both.

**Type.** System stacks only — no webfonts anywhere in the sources (see Caveats). Sans (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) for reading; mono (`ui-monospace, "SF Mono", Menlo, Consolas`) for every ID, timestamp, label, status and numeral. That split is the strongest signature of the brand: if it is data, it is mono; if it is a sentence, it is sans. Headings run heavy and tight (750 weight, `-0.02em`); body is 16px/1.6 with a 68ch measure; dense UI text runs 13–14.5px; mono chips go down to 10.5px.

**Spacing and layout.** Documents: 1100px (or 980px) centred, `48px 24px 96px` padding, 64px between sections. App: fixed 232px sidebar, 24px screen padding, 16px between panels, `10px 16px` row padding. Tables and row lists are edge-to-edge inside their panel with no internal padding.

**Backgrounds.** Flat colour only. No images, no textures, no patterns, no gradients — anywhere. The only "imagery" in the sources is hand-authored SVG workflow diagrams inside bordered figures.

**Borders, radii, elevation.** The system is flat and border-defined: 1px `--line` hairlines separate everything; 1.5px amber frames a gate stop; 2px ink rules sit under the masthead and every table head; a 3px left rule marks a callout. Radii: 4px chips, 6px buttons, 8px gate cards, 10px boards and code blocks, 12px panels, 999px status pills. **No shadows** — surfaces separate by a background step (`--surface` on `--bg`) plus a border. The one exception is `--shadow-overlay`, an addition used only for the right-hand drawer and toasts, which float above the page.

**Transparency and blur.** Transparency appears only as the 10–13% status tints. There is no backdrop blur, no glass, no scrim overlays.

**Motion.** Restrained and purposeful. New feed rows slide in over ~220ms with `cubic-bezier(0.2,0,0,1)`. A newly arrived gate highlights once, then goes still. The empty gate queue breathes at ~1.6s — the only looping animation in the system, and its job is to say "the screen is alive" without demanding attention. No bounces, no spring, no parallax.

**Hover and press.** Rows tint to `--surface-2`; buttons drop to 86% opacity; nothing scales, moves or shadows on press. Disabled is 45% opacity. Focus should follow the browser default ring unless a design calls for more.

**Cards.** One card treatment only: `--surface` background, 1px `--line` border, 12px radius, optional sunken `--surface-2` header bar carrying an uppercase mono label on the left and mono meta on the right. Gate cards are the exception — amber border, amber tint, 8px radius — because they are the one thing that must be seen first.

**Layout rules.** Sidebar and top bar are fixed; the live feed column is sticky; the drawer is fixed to the right edge at 460px. Everything else scrolls.

---

## Iconography

**There is no icon library in the sources and no logo.** The documents carry meaning with typography, colour and a small set of unicode marks. This system keeps that approach rather than importing an icon set:

| Glyph | Meaning |
|---|---|
| `◇` | gate / mandatory stop |
| `△` | escalation |
| `●` | status dot (masthead chip, empty-state pulse) |
| `→` | handoff, `from → to`, trace chain |
| `↔` | contract handshake between two agents |
| `∥` | work running in parallel |
| `✓` | AC met, agreement recorded |
| `·` | meta separator |
| `✕` | close (drawer) |

Navigation items use these marks plus their text label; nothing depends on an icon alone. **No SVG icons were drawn for this system, and none should be** — if a future design genuinely needs a glyph set, pull Lucide from CDN at 1.5px stroke and record the substitution here.

**Logo:** none exists in the provided material. Render the product name in plain type (`Control Tower`, 750 weight, `-0.02em`) with an optional amber `◇` before it. Do not draw a mark.

**Images:** none exist in the provided material. No photography, no illustration, no background imagery was supplied — leave image areas out rather than filling them.

---

## Index

**Root**
- `styles.css` — the entry point consumers link; `@import`s only.
- `tokens/colors.css` · `typography.css` · `spacing.css` · `surfaces.css` · `base.css`
- `thumbnail.html` — homepage tile · `SKILL.md` — Agent Skills wrapper · `readme.md` — this file

**Components** — `components/core/` and `components/tower/`, each with `.jsx`, `.d.ts`, `.prompt.md`, plus one card HTML per directory.

Core: **Button** · **Chip** · **StatusChip** · **Tag** · **IdCode** · **Panel** · **Eyebrow** · **Callout** · **DataTable**

Diagrams: **MermaidDiagram** — every process, comms or dependency picture is Mermaid themed from the live tokens; diagram sources live in `components/diagrams/DIAGRAMS.js`. Never hand-draw SVG.

Control Tower: **GateCard** · **GateStop** · **StageStrip** · **PipelineRow** · **TaskRow** · **FeedItem** · **VerdictBadge** · **KpiStrip** · **AgentAvatar** · **AgentWorkCard** · **TraceChain** · **Timeline** / **TimelineItem**

**UI kits**
- `ui_kits/control-tower/` — the 5-screen app, click-through (see its README)
- `ui_kits/engineering-docs/` — the long-form process document, plus `diagrams.html`: six diagrams of how the agents communicate

**Guidelines** — `guidelines/*.html`, 16 specimen cards across Colors, Type, Spacing and Brand.

### Intentional additions

Three things exist here that the sources do not define, each added because the specified product needs it:

- `--danger` / `--danger-bg` — the spec requires a Reject action and a `blocked` task status; the source palette has no red.
- `--shadow-overlay` — the spec requires a task drawer; a floating panel needs separation the flat border system cannot give.
- **AgentAvatar** — the spec calls for "avatar agent đang giữ ball"; the sources contain no avatar treatment, so it is built from the same mono-initial, lane-coloured vocabulary as the rest of the system.

### Caveats

- **Fonts are system stacks.** The sources declare no `@font-face` and ship no font binaries, so none are bundled. If TechTus has real brand fonts, send the files and the stacks will be replaced.
- The workflow SVG diagrams in `docs/agent-team-blueprint.html` were not traced pixel-for-pixel; their content is re-expressed as Mermaid on `ui_kits/engineering-docs/diagrams.html`.
- Mermaid 11 loads from CDN (`cdn.jsdelivr.net`) on first diagram render — diagrams need network access.
