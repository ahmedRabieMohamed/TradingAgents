# Implementation Plan: Animated & Motion-Driven Frontend UI

**Branch**: `011-animated-ui-redesign` | **Date**: 2026-04-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-animated-ui-redesign/spec.md`

## Summary

Layer purposeful, performant motion onto the existing React frontend so every current page (Dashboard, New Analysis, Portfolio, Watchlist, Smart Picks, Performance, History, Settings) gains coordinated entrance, transition, list, value-update, and chart animations — without removing any feature, regressing performance, or violating accessibility. Motion is centralized in a single token catalog plus a thin set of shared primitives that wrap existing components rather than replacing them. Approach: introduce one animation library (Framer Motion / `motion`), a motion-token module, route-level `AnimatePresence` for page transitions, list/`AnimatePresence` for dynamic items, count-up/flash for live values, library-native chart animations for charts, and a global `useReducedMotion`-aware adapter that downgrades all motion under `prefers-reduced-motion`.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.10+ (backend — unchanged for this feature)
**Primary Dependencies**: React 19, React Router 7, Ant Design 6.x, Zustand 5, react-i18next 17, recharts 3, lightweight-charts 5 (existing); **`motion` v11+** (new — Framer Motion successor, React 19 compatible), **`@react-spring/web`** considered and rejected (see research.md)
**Storage**: N/A (frontend-only feature; no schema or persistence changes)
**Testing**: Manual feature-parity walkthrough across all 8 pages + existing frontend test suite (must remain green); optional Playwright smoke for transition/reduced-motion paths
**Target Platform**: Modern desktop and laptop browsers (Chromium, Firefox, Safari) — same as current app
**Project Type**: Web application (frontend + backend repo). This feature touches frontend only.
**Performance Goals**: First-meaningful-paint Dashboard ≤ 1.5 s; page-to-page transition ≤ 400 ms; entrance ≤ 800 ms; interactive feedback within 100 ms; sustained ≥ 55 fps; no dropped-frame spike > 100 ms (matches SC-002…SC-005).
**Constraints**: No backend API changes, no new persistent entities, no removal of existing features, `prefers-reduced-motion` honored, RTL-aware, input never blocked on animation, no regressions in existing tests.
**Scale/Scope**: 8 primary pages, ~30 existing components, 1 new motion-token module, ~6 shared motion primitives, 0 new entities.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | ✅ Pass | One new dependency (`motion`). Single token module. Shared primitives wrap existing components rather than replacing them. No speculative abstractions. |
| II. Correctness Over Speed | ✅ Pass | Animations are presentational only. Data flow, formatting, and precision are unchanged. Performance budgets defined and measurable (SC-002…SC-005). |
| III. Separation of Concerns | ✅ Pass | Frontend-only. No backend, no API, no service-layer changes. Motion primitives live in their own module (`frontend/src/motion/`). |
| IV. Incremental Delivery | ✅ Pass | 5 user stories, each independently testable; P1 stories deliver an MVP slice (basic page animation + reduced-motion). |
| V. Data Integrity | ✅ Pass | No DB or schema changes. Analysis results, portfolio, trades all untouched. |

**Gate result**: PASS. No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/011-animated-ui-redesign/
├── plan.md              # This file
├── research.md          # Phase 0 — library/decision rationale
├── data-model.md        # Phase 1 — motion-token catalog (UX entity)
├── quickstart.md        # Phase 1 — how to run/verify the redesign
├── contracts/
│   └── motion-tokens.md # Phase 1 — public motion-token contract
└── checklists/
    └── requirements.md  # Spec quality checklist (already created)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── motion/                       # NEW — motion infrastructure
│   │   ├── tokens.ts                 # Duration/easing/distance catalog
│   │   ├── reducedMotion.ts          # useReducedMotion hook + helpers
│   │   ├── direction.ts              # RTL-aware sign helpers
│   │   ├── primitives/
│   │   │   ├── PageTransition.tsx    # Wraps Routes with AnimatePresence
│   │   │   ├── EnterStagger.tsx      # Coordinated entrance for grids/cards
│   │   │   ├── AnimatedList.tsx      # Item enter/exit (used by watchlist, history, etc.)
│   │   │   ├── ValueFlash.tsx        # Brief flash/count-up for changed numbers
│   │   │   ├── PressFeedback.tsx     # Click/scale wrapper for primary buttons
│   │   │   └── SkeletonShimmer.tsx   # Animated loading skeleton
│   │   └── index.ts
│   ├── components/                   # EXISTING — minor edits to wrap with primitives
│   │   ├── analysis/                 # AnalysisProgress, CandlestickChart, …
│   │   ├── history/                  # HistoryTable, FilterBar, CompareModal
│   │   ├── layout/                   # Sidebar, Topbar — focused entrance polish
│   │   ├── market-overview/          # IndexBar, MoverGrid, NewsSection, …
│   │   ├── performance/              # PerfCard, MarketPerf, SimulationTable
│   │   └── portfolio/                # PositionsTable, EquityCurve, TradeHistory, …
│   ├── pages/                        # EXISTING — wrap each with PageTransition
│   ├── App.tsx                       # EDIT — mount <AnimatePresence> around <Routes>
│   ├── styles/globals.css            # EDIT — @media (prefers-reduced-motion) rules
│   └── i18n.ts                       # UNCHANGED
└── package.json                      # EDIT — add `motion` dependency

backend/
└── (untouched)
```

**Structure Decision**: Web-application layout (Option 2 in template). Backend is untouched. Frontend gets a new `motion/` directory that owns tokens, hooks, and shared primitives; existing components are edited surgically to wrap with primitives or apply tokens — no large rewrites.

## Phase 0 — Research

Open questions to resolve in `research.md`:

1. **Animation library choice** for React 19 + AntD 6 + Vite — Framer Motion (`motion` v11+) vs `motion` Mini vs `@react-spring/web` vs CSS-only.
2. **Page-transition strategy** under React Router 7 (AnimatePresence + `useLocation` keying vs route loaders).
3. **Chart animation strategy** for two heterogeneous chart libraries: `recharts` (built-in `isAnimationActive`) and `lightweight-charts` (no built-in tweening) — decide what "animated" means per library.
4. **Reduced-motion fallback strategy** — single hook that swaps token sets vs library-native `useReducedMotion`.
5. **RTL/Arabic mirroring** — direction-aware sign in `motion/direction.ts` derived from existing `dir` attribute.

## Phase 1 — Design & Contracts

**Prerequisites**: `research.md` complete.

1. **Entities → `data-model.md`**: This feature has no persistent entities. The "data model" documents the UX-level entity introduced by the spec — the **Motion Token Set** and **Reduced-Motion Profile** — with named tokens, default values, and the reduced-motion overrides.
2. **Contracts → `contracts/motion-tokens.md`**: The public contract is the motion-token vocabulary that components in the rest of the codebase consume. Documents the named tokens (`page.enter.duration`, `list.item.enter.distance`, `value.flash.color`, etc.), their semantics, and the rules for adding new ones. This is the equivalent of a UI contract for an internal interface, per the plan template's guidance.
3. **Quickstart → `quickstart.md`**: One-page "run + verify" guide so reviewers can pull the branch, run the frontend, and walk through the acceptance scenarios in order.
4. **Agent context update**: Run `.specify/scripts/bash/update-agent-context.sh claude` after the artifacts above exist so `CLAUDE.md` records the new `motion` dependency under Active Technologies.

**Output**: `research.md`, `data-model.md`, `contracts/motion-tokens.md`, `quickstart.md`, plus regenerated `CLAUDE.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Section intentionally empty.
