# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **documentation/research repository** (no code, no build) inside the `company-research/rd` monorepo. It captures how **AWS's AI-DLC (AI-Driven Development Lifecycle)** method would change the way Mynavi TechTus Vietnam's teams divide and accept work, compared with their current Agile/Sprint and ticket-driven processes.

Primary content: `docs/ai-dlc-changes-with-techtus.md` — extracted from the slide deck `AI-DLC-changes-with-techtus.html` (source: AWS AI-DLC Method Definition). Documentation is written in Vietnamese with English technical terms kept as-is; follow that convention when editing or adding docs.

## Key Concepts (AI-DLC vocabulary)

Use this terminology consistently across documents in this repo:

- **Business Intent** — the input unit, replacing backlog items / customer tickets. A customer ticket is only input for context discovery, not an execution unit.
- **Unit of Work (UOW)** — a deliverable business capability (replaces Epic). A Unit must be an *observable outcome* — "Update DB" / "Add API" / "Update UI" are tasks, not Units.
- **Bolt** — the build–validate cycle of hours to a few days (replaces Sprint).
- Hierarchy: **Customer Request → Intent → Unit → Bolt → Task**.
- Role inversion: AI is the execution engine (analyze intent, ask open questions, generate requirements/design/code/tests); humans keep context, trade-offs, and decisions (validate, review, approve, deploy).

## The 8-Stage Brownfield Flow

The doc's central artifact is an 8-stage flow across three lanes (Client / Delivery Team / AI Agents):

- **Discovery**: 1 Request → 2 Context Discovery → 3 Context Validation → 4 Clarification
- **Delivery**: 5 Unit Definition → 6 Construction → 7 Acceptance → 8 Release (persists artifacts to **Context Memory**)

Stages 2–3 (Context Discovery + Validation, producing an AS-IS model before any TO-BE discussion) are the additions to vanilla AI-DLC for projects requiring reverse engineering — mandatory when two or more brownfield signals apply (no up-to-date docs, inherited codebase, business rules only in code, low test coverage, etc.).

## Related Context

The parent monorepo (`../CLAUDE.md`) documents the Project Knowledge Bot sub-projects (`project-knowledge-bot-be`, `project-knowledge-bot-fe`, `rag-bot`, etc.). This repo is process research, not part of that codebase, but the same team/audience applies.
