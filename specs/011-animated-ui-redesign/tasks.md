---

description: "Task list for Animated & Motion-Driven Frontend UI"
---

# Tasks: Animated & Motion-Driven Frontend UI

**Input**: Design documents from `/specs/011-animated-ui-redesign/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/motion-tokens.md, quickstart.md

**Tests**: Tests were not explicitly requested by the user. Verification is manual per `quickstart.md` plus the existing frontend lint/build pipeline (`npm run lint`, `npm run build`).

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently. Reduced-motion mechanics live in Foundational because every motion primitive depends on them; US4 (Accessibility & Performance) is the verification phase that exercises and signs off on those mechanics.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5)
- All paths are absolute from repo root: `/Users/ahmedmohamed/Desktop/Trading26/TradingAgents/...`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the new dependency and scaffold the motion module directory.

- [ ] T001 Add `motion` (Framer Motion successor, v11+) to `frontend/package.json` dependencies and run `npm install` from `frontend/`
- [ ] T002 [P] Create directory `frontend/src/motion/` with empty `index.ts` re-export barrel
- [ ] T003 [P] Create directory `frontend/src/motion/primitives/`

**Checkpoint**: New dependency installed; module directories exist; project still builds (`npm run build` succeeds with no new errors).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Token catalog, reduced-motion hook, and direction hook. Every primitive in later phases consumes these — they MUST exist before any user story phase begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Implement default motion-token catalog matching `data-model.md` Entity 1 in `frontend/src/motion/tokens.ts` (export `defaultTokens` with the full `MotionTokens` shape from `contracts/motion-tokens.md`)
- [ ] T005 Implement reduced-motion overrides matching `data-model.md` Entity 2 in `frontend/src/motion/tokens.ts` (export `reducedTokens`; cap all decorative durations at ≤ 150 ms per SC-006)
- [ ] T006 Implement `useMotionTokens()` hook in `frontend/src/motion/reducedMotion.ts` that wraps `motion`'s `useReducedMotion()` and returns either `defaultTokens` or `reducedTokens`
- [ ] T007 [P] Implement `useDirection()` hook in `frontend/src/motion/direction.ts` that reads `i18n.dir()` and returns `{ dir: 'ltr' | 'rtl', dirSign: 1 | -1 }`
- [ ] T008 [P] Add global CSS reduced-motion fallback (`@media (prefers-reduced-motion: reduce)`) in `frontend/src/styles/globals.css` — disables CSS keyframe animations not driven by `motion`
- [ ] T009 Re-export the public motion API (`useMotionTokens`, `useDirection`, primitives barrel) from `frontend/src/motion/index.ts`
- [ ] T010 Verify the contract surface compiles end-to-end: `cd frontend && npx tsc --noEmit` succeeds

**Checkpoint**: Token catalog, reduced-motion swap, and RTL sign helper are available via `import { ... } from '@/motion'`. No user-facing change yet.

---

## Phase 3: User Story 1 - Animated First Impression Across Existing Pages (Priority: P1) 🎯 MVP

**Goal**: Every existing primary page (Dashboard, New Analysis, Portfolio, Watchlist, Smart Picks, Performance, History, Settings) renders with coordinated entrance motion and animated transitions between pages, with zero regression of existing features.

**Independent Test**: Walk Section 3 / Story 1 of `quickstart.md`. Confirm (a) every page animates in within 600 ms, (b) page-to-page transitions play continuously without flash, (c) every existing control, table, chart, and data point is present and unchanged.

### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement `<PageTransition>` primitive in `frontend/src/motion/primitives/PageTransition.tsx` (wraps children in `<motion.div>` with `page.enter` / `page.exit` tokens; `dirSign`-aware `x`)
- [ ] T012 [P] [US1] Implement `<EnterStagger>` primitive in `frontend/src/motion/primitives/EnterStagger.tsx` (parent variants apply `stagger.card.delayStep`, capped at `stagger.card.maxItems`)
- [ ] T013 [US1] Wrap `<Routes>` in `<AnimatePresence mode="wait">` with `useLocation().pathname` key in `frontend/src/App.tsx` (depends on T011)
- [ ] T014 [P] [US1] Wrap Dashboard root with `<PageTransition>` and apply `<EnterStagger>` around primary panels in `frontend/src/pages/Dashboard.tsx`
- [ ] T015 [P] [US1] Wrap New Analysis root with `<PageTransition>` in `frontend/src/pages/NewAnalysis.tsx`
- [ ] T016 [P] [US1] Wrap Portfolio root with `<PageTransition>` and stagger summary cards in `frontend/src/pages/Portfolio.tsx`
- [ ] T017 [P] [US1] Wrap Watchlist root with `<PageTransition>` in `frontend/src/pages/Watchlist.tsx`
- [ ] T018 [P] [US1] Wrap Smart Picks root with `<PageTransition>` and stagger pick cards in `frontend/src/pages/SmartPicks.tsx`
- [ ] T019 [P] [US1] Wrap Performance root with `<PageTransition>` and stagger perf cards in `frontend/src/pages/Performance.tsx`
- [ ] T020 [P] [US1] Wrap History root with `<PageTransition>` in `frontend/src/pages/History.tsx`
- [ ] T021 [P] [US1] Wrap Settings root with `<PageTransition>` in `frontend/src/pages/Settings.tsx`
- [ ] T022 [US1] Sidebar/Topbar entrance polish in `frontend/src/components/layout/Sidebar.tsx` and `frontend/src/components/layout/Topbar.tsx` (subtle slide on first mount only — not on every route change)
- [ ] T023 [US1] Feature-parity walkthrough per `quickstart.md` §3 Story 1 — verify each of the 8 pages renders all existing data and controls

**Checkpoint**: User Story 1 fully functional. The redesign is visibly live on every page; no feature is missing. This is the MVP slice — could ship here.

---

## Phase 4: User Story 4 - Accessibility & Performance Respect (Priority: P1)

**Goal**: With `prefers-reduced-motion: reduce` enabled at the OS level, every page in the redesign is fully usable, decorative motion is suppressed (≤ 150 ms), and input is never blocked by animation.

**Independent Test**: Walk Section 3 / Story 4 of `quickstart.md`. Toggle macOS Reduce Motion → reload → confirm AC-1, AC-2, AC-3.

**Why P1 and ordered after US1**: The reduced-motion mechanics already live in Foundational (T005, T006). US1 primitives consume them automatically. This phase is the **verification + last-mile fallback hardening** — it must complete with US1 to ship the MVP responsibly.

### Implementation for User Story 4

- [ ] T024 [US4] Verify `<PageTransition>` and `<EnterStagger>` produce ≤ 150 ms motion under `useReducedMotion() === true`; if a primitive bypasses the token hook, fix it in `frontend/src/motion/primitives/PageTransition.tsx` and `frontend/src/motion/primitives/EnterStagger.tsx`
- [ ] T025 [US4] Audit all `<motion.*>` usages in `frontend/src/motion/primitives/` for `pointer-events` traps — ensure no animation sets `pointer-events: none` on elements with interactive children (FR-010 / SC-006 AC-2)
- [ ] T026 [US4] Confirm focus order is preserved through page transitions (keyboard-Tab through Sidebar → main content survives a route change without losing focus mid-transition) — fix in `frontend/src/App.tsx` or `frontend/src/motion/primitives/PageTransition.tsx` if broken
- [ ] T027 [US4] Performance check: record DevTools Performance during Dashboard load + a page navigation; confirm sustained ≥ 55 fps with no dropped-frame spike > 100 ms (SC-005). If violated, reduce `page.enter.duration` or simplify entrance variants in `frontend/src/motion/tokens.ts`
- [ ] T028 [US4] Run `quickstart.md` §3 Story 4 acceptance scenarios end-to-end; document results in PR description

**Checkpoint**: P1 complete — MVP is shippable. Redesign is accessible, performant, and feature-parity-clean.

---

## Phase 5: User Story 2 - Motion as Feedback for User Actions (Priority: P2)

**Goal**: Every primary user action (button press, list add/remove, modal open/close, analysis start, value update) triggers a brief, purposeful motion response.

**Independent Test**: Walk Section 3 / Story 2 of `quickstart.md`. Trigger each action class and confirm motion responses match AC-1…AC-4.

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement `<PressFeedback>` primitive in `frontend/src/motion/primitives/PressFeedback.tsx` (wraps a button or arbitrary element; applies `press.scale` and `press.duration` via `whileTap`)
- [ ] T030 [P] [US2] Implement `<AnimatedList>` primitive in `frontend/src/motion/primitives/AnimatedList.tsx` (renders `<AnimatePresence>` + `motion.li`; applies `list.item.enter` / `list.item.exit` tokens, `dirSign`-aware)
- [ ] T031 [P] [US2] Implement `<ValueFlash>` primitive in `frontend/src/motion/primitives/ValueFlash.tsx` (count-up + color flash on `value` prop change; under reduced motion, color flash only — count-up suppressed per data-model.md)
- [ ] T032 [P] [US2] Implement `<SkeletonShimmer>` primitive in `frontend/src/motion/primitives/SkeletonShimmer.tsx` (CSS gradient sweep gated by `skeleton.shimmer.duration` token; under reduced motion, static skeleton)
- [ ] T033 [US2] Apply `<PressFeedback>` to primary action buttons across the app — start with the New Analysis "Run" button in `frontend/src/components/analysis/ConfigPanel.tsx`, the Add to Watchlist control in the appropriate market-overview/watchlist component, and the Trade button in `frontend/src/components/portfolio/TradeModal.tsx`
- [ ] T034 [US2] Replace static list rendering with `<AnimatedList>` in the watchlist row list (page: `frontend/src/pages/Watchlist.tsx`)
- [ ] T035 [US2] Replace static row rendering with `<AnimatedList>` in `frontend/src/components/history/HistoryTable.tsx` (only newly entering/leaving rows animate; long lists must not re-stagger every render — depends on T030)
- [ ] T036 [US2] Replace static row rendering with `<AnimatedList>` in `frontend/src/components/portfolio/PositionsTable.tsx` (depends on T030)
- [ ] T037 [US2] Replace static result rendering with `<AnimatedList>` in `frontend/src/pages/SmartPicks.tsx` (depends on T030)
- [ ] T038 [US2] Wrap live numeric values with `<ValueFlash>` in `frontend/src/components/portfolio/PortfolioSummary.tsx` (totals, P&L) and in price cells of `frontend/src/components/portfolio/PositionsTable.tsx`
- [ ] T039 [US2] Wrap live numeric values with `<ValueFlash>` in `frontend/src/components/market-overview/IndexBar.tsx` and `frontend/src/components/market-overview/StockTable.tsx` price cells
- [ ] T040 [US2] Replace static loading placeholders with `<SkeletonShimmer>` in `frontend/src/components/analysis/AnalysisProgress.tsx` and any other component currently rendering a static loading state for an operation > 200 ms
- [ ] T041 [US2] Apply existing AntD Modal motion or wrap modals (e.g., `frontend/src/components/history/CompareModal.tsx`, `frontend/src/components/portfolio/TradeModal.tsx`) with `modal.enter` / `modal.exit` tokens to ensure consistent timing
- [ ] T042 [US2] Walk `quickstart.md` §3 Story 2 acceptance scenarios end-to-end

**Checkpoint**: User Story 2 complete. Action feedback is consistent across the app.

---

## Phase 6: User Story 3 - Animated Data Visualizations (Priority: P2)

**Goal**: Charts and data-heavy panels animate on first render and ease between states on data updates.

**Independent Test**: Walk Section 3 / Story 3 of `quickstart.md`. Open candlestick view, equity curve, performance dashboard, smart-picks rankings; trigger a refresh; confirm animation per AC-1, AC-2.

### Implementation for User Story 3

- [ ] T043 [P] [US3] Wire Recharts `isAnimationActive`, `animationDuration`, and `animationEasing` from `chart.enter` tokens in `frontend/src/components/portfolio/EquityCurve.tsx` (depends on `useMotionTokens()`)
- [ ] T044 [P] [US3] Wire Recharts animation tokens in `frontend/src/components/performance/MarketPerf.tsx` and `frontend/src/components/performance/PerfCard.tsx`
- [ ] T045 [P] [US3] Wire Recharts animation tokens in any Smart Picks chart components rendered by `frontend/src/pages/SmartPicks.tsx`
- [ ] T046 [US3] Wrap the lightweight-charts container with a `motion.div` applying `chart.container.enter.duration` (fade + subtle scale on mount and on data-source change) in `frontend/src/components/analysis/CandlestickChart.tsx`
- [ ] T047 [US3] Reduced-motion behavior for charts: when `useReducedMotion() === true`, set Recharts `isAnimationActive={false}` and skip the lightweight-charts container animation. Confirm in `frontend/src/components/portfolio/EquityCurve.tsx`, `frontend/src/components/performance/MarketPerf.tsx`, `frontend/src/components/performance/PerfCard.tsx`, `frontend/src/components/analysis/CandlestickChart.tsx`
- [ ] T048 [US3] Walk `quickstart.md` §3 Story 3 acceptance scenarios end-to-end

**Checkpoint**: User Story 3 complete. Charts animate on entry and ease on update.

---

## Phase 7: User Story 5 - Internationalization & RTL Motion (Priority: P3)

**Goal**: When the active language is right-to-left (Arabic), directional motion mirrors so transitions read naturally.

**Independent Test**: Walk Section 3 / Story 5 of `quickstart.md`. Toggle Arabic in Settings → repeat Story 1 walkthrough → confirm directional slides mirror.

### Implementation for User Story 5

- [ ] T049 [US5] Confirm every `*.x` token usage in primitives (`frontend/src/motion/primitives/PageTransition.tsx`, `frontend/src/motion/primitives/AnimatedList.tsx`) multiplies by `dirSign` from `useDirection()`. Patch any direct token reads. (Most should already be correct from T011 / T030)
- [ ] T050 [US5] Walk Story 5 acceptance scenarios in Arabic locale per `quickstart.md` §3 Story 5; capture before/after side-by-side screenshots for the PR description
- [ ] T051 [US5] Verify Arabic-mode reduced-motion path (combination edge case): both RTL and reduce-motion enabled → no directional slide, fades only (interaction of FR-009 + FR-011)

**Checkpoint**: User Story 5 complete. RTL motion polished.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, regression sweep, and merge readiness.

- [ ] T052 [P] Run `cd frontend && npm run lint` — zero new lint errors (Constitution Quality Gate "Before merge")
- [ ] T053 [P] Run `cd frontend && npm run build` (which runs `tsc -b && vite build`) — zero new TypeScript errors and successful production build
- [ ] T054 [P] Inspect Vite production bundle output: `motion` library contribution stays within ≤ 25 kB gzipped budget; record actual size in PR description
- [ ] T055 Edge-case sweep per `quickstart.md` §4: rapid navigation (no orphan transitions), long lists (only delta items animate), modal stacking (no double-animate), theme switch (no entrance replay)
- [ ] T056 Run the full `quickstart.md` walkthrough end-to-end as final pre-merge sign-off
- [ ] T057 [P] Update `frontend/README.md` (or add a section in the project README if no frontend-specific README exists) with a one-paragraph note on the motion module and a pointer to `specs/011-animated-ui-redesign/contracts/motion-tokens.md`
- [ ] T058 Final feature-parity diff against `main` for the 8 primary pages — no removed or behavior-changed features (FR-001 / SC-001)

**Checkpoint**: Branch is merge-ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup. **Blocks all user stories.**
- **User Story 1 (Phase 3)**: Depends on Foundational. P1 — MVP slice.
- **User Story 4 (Phase 4)**: Depends on Foundational + Phase 3 (verifies the primitives US1 introduced). P1 — must ship with MVP.
- **User Story 2 (Phase 5)**: Depends on Foundational. P2 — independent of US1/US3/US5; can run in parallel with US3 once Foundational is done.
- **User Story 3 (Phase 6)**: Depends on Foundational. P2 — can run in parallel with US2.
- **User Story 5 (Phase 7)**: Depends on Foundational + every primitive that uses directional tokens (US1's `<PageTransition>` and US2's `<AnimatedList>`). P3.
- **Polish (Phase 8)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Foundational only.
- **US4 (P1)**: Foundational + US1 primitives in place to verify against.
- **US2 (P2)**: Foundational only.
- **US3 (P2)**: Foundational only.
- **US5 (P3)**: Foundational + the directional primitives shipped by US1 (PageTransition) and US2 (AnimatedList).

### Within Each User Story

- Primitives before consumers.
- All `[P]` tasks within a story can run in parallel.
- Pages/components that touch different files run in parallel.

### Parallel Opportunities

- **Phase 1**: T002, T003 in parallel.
- **Phase 2**: T007, T008 in parallel after T004–T006.
- **Phase 3 (US1)**: T011, T012 in parallel; T014–T021 all in parallel after T013.
- **Phase 5 (US2)**: T029, T030, T031, T032 in parallel; T033–T041 in parallel where they touch different files.
- **Phase 6 (US3)**: T043, T044, T045 in parallel.
- **Phase 8**: T052, T053, T054, T057 in parallel.
- **Cross-phase**: Once Foundational completes, US1, US2, US3 phases can be staffed by different developers in parallel.

---

## Parallel Example: User Story 1

```bash
# After Foundational completes (T004–T010), launch primitives in parallel:
Task: "Implement <PageTransition> in frontend/src/motion/primitives/PageTransition.tsx"   # T011
Task: "Implement <EnterStagger> in frontend/src/motion/primitives/EnterStagger.tsx"        # T012

# Then T013 (single edit to App.tsx) — sequential.

# Then page wrappers, all in parallel because they touch different files:
Task: "Wrap Dashboard with <PageTransition>"     # T014
Task: "Wrap New Analysis with <PageTransition>"  # T015
Task: "Wrap Portfolio with <PageTransition>"     # T016
Task: "Wrap Watchlist with <PageTransition>"     # T017
Task: "Wrap Smart Picks with <PageTransition>"   # T018
Task: "Wrap Performance with <PageTransition>"   # T019
Task: "Wrap History with <PageTransition>"       # T020
Task: "Wrap Settings with <PageTransition>"      # T021
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 4)

P1 is split across two stories because reduced-motion is non-negotiable. The MVP cut is:

1. Phase 1 — Setup
2. Phase 2 — Foundational
3. Phase 3 — US1 (animated pages)
4. Phase 4 — US4 (accessibility & perf verification)
5. **STOP & VALIDATE**: walk `quickstart.md` Story 1 + Story 4. If both pass, this is shippable.

### Incremental Delivery

1. Setup + Foundational → primitives ready (no user-visible change).
2. + US1 + US4 → animated pages, accessible, performant. **MVP demo-ready.**
3. + US2 → action-feedback layer (button press, lists, value flash, skeletons).
4. + US3 → chart animations.
5. + US5 → RTL polish.
6. + Polish → merge-ready.

### Parallel Team Strategy

After Foundational (T004–T010) completes:

- Developer A: US1 (Phase 3) → US4 (Phase 4)
- Developer B: US2 (Phase 5)
- Developer C: US3 (Phase 6)
- Then any developer: US5 (Phase 7), Polish (Phase 8)

Stories converge cleanly because every consumer goes through `useMotionTokens()` and the primitives barrel — no cross-story file conflicts.

---

## Notes

- `[P]` tasks touch different files and have no incomplete dependencies.
- Tests are not included in this plan (not requested by the user). Verification is manual per `quickstart.md` plus existing automated lint/build (FR-014).
- The Constitution's "Tests are written when explicitly requested" clause applies; if a regression appears, add a focused test then, per the project's TDD-on-regression rule.
- Commit after each task or per logical group. Keep commits scoped so failed acceptance reviews can revert just one slice.
- Stop at any checkpoint to validate; this is a UI feature where staring at it is the test.
