---

description: "Task list for Smart Picks Overhaul"
---

# Tasks: Smart Picks Overhaul

**Input**: Design documents from `/specs/012-smart-picks-overhaul/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/engines-api.md, contracts/engine-reference.md, quickstart.md

**Tests**: The plan explicitly calls for **unit tests on each new engine** (constitution principle II — financial correctness is non-negotiable). The frontend redesign is verified manually per `quickstart.md`. There are no API contract tests — the API extension is additive and verified by the engine unit tests + the determinism diff in `quickstart.md`.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently. The MVP slice is **US1 + US2** (P1 + P1) — redesigned page + inline engine education — and is shippable without any new engine.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies).
- **[Story]**: User story label (US1, US2, US3, US4, US5).
- All paths are absolute from repo root: `/Users/ahmedmohamed/Desktop/Trading26/TradingAgents/...`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold directories and stub files needed by later phases. No behavior change.

- [ ] T001 [P] Create directory `frontend/src/components/smart-picks/` for the new pick components
- [ ] T002 [P] Create empty `frontend/src/locales/en/engines.json` and `frontend/src/locales/ar/engines.json` with `{ "engines": {} }` skeleton
- [ ] T003 Wire the new `engines` namespace into `frontend/src/i18n.ts` so `t('engines.<name>.label')` resolves
- [ ] T004 [P] Create directory `backend/tests/services/engines/` if it does not already exist (with `__init__.py`)

**Checkpoint**: Directories and i18n namespace exist; project still builds (`cd frontend && npm run build` succeeds).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend shared types and the orchestrator's contract so later phases plug into a stable interface. **No user-facing change yet.**

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Extend the `EngineResult` TypeScript type in `frontend/src/types/index.ts` (or wherever Smart Picks types live) to include `data_sufficient: boolean`, `weight: number`, and the new per-engine extras documented in `data-model.md` (`rsi_value`, `macd_line`, `signal_line`, `histogram`, `crossover_age_bars`, `realized_vol_annualized`, `regime_tag`, `pull_alpha`)
- [ ] T006 Extend the `SmartPick` TypeScript type to include `combined_score_raw: number` and `volatility_regime_tag: 'calm' | 'normal' | 'elevated' | 'extreme'`
- [ ] T007 Update `frontend/src/services/api.ts` typings for `getSmartPicks` and `getEngineScore` to return the extended types from T005 / T006
- [ ] T008 Add the `data_sufficient` flag and `weight` field to every existing engine's return shape in `backend/app/services/engines/{momentum,volume,support_resistance,mean_reversion,bollinger,correlation,monte_carlo}.py` — for now hard-code `data_sufficient: True` and `weight: 0.0` (real weights are computed by the orchestrator); this only locks the shape so frontend types match
- [ ] T009 Update `backend/app/services/engines/__init__.py` so the orchestrator emits `combined_score_raw` (pre-dampening) alongside `combined_score`. For Phase 2, `combined_score_raw == combined_score` (no dampening yet); the field is wired so frontend can begin reading it
- [ ] T010 Verify the contract surface: `cd backend && ruff check app/services/engines` exits 0 and `cd frontend && npx tsc --noEmit` exits 0

**Checkpoint**: Types extended end-to-end. The Smart Picks page still renders exactly as before. New fields exist but carry placeholder values.

---

## Phase 3: User Story 1 - Redesigned Smart Picks Page (Priority: P1) 🎯 MVP

**Goal**: A clean, scannable Smart Picks page that fits a 1280-px viewport in both LTR and RTL, with secondary metrics behind expand-rows and a detail drawer.

**Independent Test**: Walk `quickstart.md` §2 Story 1. Confirm primary columns visible without horizontal page scroll, sidebar visible, every pre-redesign data point reachable.

### Implementation for User Story 1

- [ ] T011 [US1] Inventory every metric currently visible on the existing Smart Picks page (`frontend/src/pages/SmartPicks.tsx`) and classify each as `primary` (always visible), `expanded` (in expand-row), or `drawer` (in detail drawer); record the classification as a comment block at the top of `frontend/src/components/smart-picks/PickRow.tsx`
- [ ] T012 [P] [US1] Implement `<PickRow>` in `frontend/src/components/smart-picks/PickRow.tsx` rendering the primary columns: rank, ticker (+ company name, locale-aware), market badge, signal badge, combined-score chip, volatility-regime badge slot (placeholder until US3), expand toggle
- [ ] T013 [P] [US1] Implement `<VolatilityBadge>` in `frontend/src/components/smart-picks/VolatilityBadge.tsx` that renders a calm/normal/elevated/extreme pill from the `volatility_regime_tag` field (renders a neutral placeholder when the tag is missing — needed before US3 lands)
- [ ] T014 [P] [US1] Implement `<PickRowExpanded>` in `frontend/src/components/smart-picks/PickRowExpanded.tsx` that renders the `expanded`-classified metrics inside an AntD `Table` `expandedRowRender` slot
- [ ] T015 [P] [US1] Implement `<PickDetailDrawer>` skeleton in `frontend/src/components/smart-picks/PickDetailDrawer.tsx` — opens, shows ticker + combined score, lists each engine name with its score and weight, "close" button. Detail population is finished in US5
- [ ] T016 [US1] Rewrite `frontend/src/pages/SmartPicks.tsx` to use the new components: AntD `Table` with `columns` set to primary only, `expandable.expandedRowRender={PickRowExpanded}`, drawer mounted at the page level and opened by clicking a ticker. Preserve existing refresh button, manual scoring, market filter, sort, pagination
- [ ] T017 [US1] Verify viewport fit: open the page at 1280×800 in both LTR and RTL; confirm no page-level horizontal scroll. If overflow appears, prune column count or shorten labels — don't relax the budget
- [ ] T018 [US1] Walk `quickstart.md` §2 Story 1 acceptance scenarios end-to-end (LTR + RTL + feature-parity check)

**Checkpoint**: User Story 1 fully functional. The redesigned page is live; no engine work is required to ship this.

---

## Phase 4: User Story 2 - Per-Engine Education Inline (Priority: P1)

**Goal**: Every engine score chip has a hover/click popover that explains what it measures, score-range meaning, and why it matters — in the active locale.

**Independent Test**: Walk `quickstart.md` §2 Story 2. Hover any engine score; popover appears within 200 ms with the four content fields. Switch to Arabic; same popover renders in Arabic.

### Implementation for User Story 2

- [ ] T019 [US2] Populate `frontend/src/locales/en/engines.json` with the existing 7 engines (`momentum`, `volume`, `support_resistance`, `mean_reversion`, `bollinger`, `correlation`, `monte_carlo`) — each with `label`, `category`, `measures`, `scoreRange`, `whyMatters` per `contracts/engine-reference.md`. Plain language; no formulas
- [ ] T020 [US2] Translate the 7 entries from T019 into `frontend/src/locales/ar/engines.json`. Same key shape, Arabic content. Maintain locale parity per SC-010
- [ ] T021 [P] [US2] Implement `<EngineCell>` in `frontend/src/components/smart-picks/EngineCell.tsx` — renders the engine label and 0–100 score chip; has accessible `aria-describedby` pointing at the popover trigger
- [ ] T022 [P] [US2] Implement `<EngineEducationPopover>` in `frontend/src/components/smart-picks/EngineEducationPopover.tsx` — reads `t('engines.<name>.{label,category,measures,scoreRange,whyMatters}')`; renders an AntD `Popover` triggered by hover (desktop) and click (touch); appears within 200 ms; "Learn more" footer link opens the detail drawer
- [ ] T023 [US2] Wire `<EngineCell>` and `<EngineEducationPopover>` into `<PickRowExpanded>` so every engine chip in the expand-row is now educational
- [ ] T024 [US2] Add a graceful-fallback path in `<EngineEducationPopover>` so a future engine that lacks an i18n entry shows the engine name plus "no description available" rather than raw `engines.foo.measures`-style keys
- [ ] T025 [US2] Walk `quickstart.md` §2 Story 2 acceptance scenarios end-to-end (LTR + Arabic + 10-second test)

**Checkpoint**: P1 slice complete. The page is shippable. New engines and integration follow.

---

## Phase 5: User Story 3 - Add New Quantitative Engines (Priority: P2)

**Goal**: Three new engines (RSI, MACD, Volatility Regime) appear in the orchestrator output with score, signal, rationale, and `data_sufficient` flag.

**Independent Test**: Walk `quickstart.md` §2 Story 3. Inspect any pick in the detail drawer; the three new engines appear. Backend tests pass.

### Implementation for User Story 3

- [ ] T026 [P] [US3] Implement RSI(14) Wilder engine in `backend/app/services/engines/rsi.py` per research §R1 — input `prices: np.ndarray`, output `{score, signal, reason, data_sufficient, weight, rsi_value}`. Insufficient when `len(prices) < 15`
- [ ] T027 [P] [US3] Implement MACD(12,26,9) engine in `backend/app/services/engines/macd.py` per research §R2 — output includes `macd_line`, `signal_line`, `histogram`, `crossover_age_bars`. Insufficient when `len(prices) < 35`
- [ ] T028 [P] [US3] Implement Volatility Regime engine in `backend/app/services/engines/volatility_regime.py` per research §R3 — output includes `realized_vol_annualized`, `regime_tag`, `pull_alpha`. `score` is the inverse-vol display score; `weight` is always `0.0` (does not vote in combined sum). Insufficient when `len(prices) < 60` → defaults to `regime_tag = 'normal'`, `pull_alpha = 0.0`
- [ ] T029 [P] [US3] Unit tests for RSI in `backend/tests/services/engines/test_rsi.py` — known oversold case (final RSI ≤ 30), overbought case, neutral case, insufficient-data case
- [ ] T030 [P] [US3] Unit tests for MACD in `backend/tests/services/engines/test_macd.py` — bullish-crossover case, bearish-crossover case, no-cross-recent case, insufficient-data case
- [ ] T031 [P] [US3] Unit tests for Volatility Regime in `backend/tests/services/engines/test_volatility_regime.py` — calm / normal / elevated / extreme cases (constructed via synthetic price series with known stddev), insufficient-data fallback
- [ ] T032 [US3] Add the three new engines to `run_all_engines` (and the per-ticker orchestrator) in `backend/app/services/engines/__init__.py`. Each new engine populates a key in the returned `engines` dict (`rsi`, `macd`, `volatility_regime`)
- [ ] T033 [US3] Run `cd backend && pytest tests/services/engines/` — all engine tests pass
- [ ] T034 [US3] Add `engines.rsi`, `engines.macd`, `engines.volatility_regime` entries to `frontend/src/locales/en/engines.json` AND `frontend/src/locales/ar/engines.json` (locale parity per SC-010)
- [ ] T035 [US3] Wire the three new engines into the existing `bullish_engines / total_engines` count emitted by the orchestrator. Note: `volatility_regime` is excluded from this count because it does not vote
- [ ] T036 [US3] Walk `quickstart.md` §2 Story 3 acceptance scenarios end-to-end

**Checkpoint**: New engines visible in API and UI. Combined score is unchanged yet (US4 covers integration).

---

## Phase 6: User Story 4 - New Engines Integrated into the Combined Score (Priority: P2)

**Goal**: RSI and MACD enter the technical-average term of the combined score; Volatility Regime dampens the final number toward NEUTRAL in `elevated` / `extreme` regimes — without inverting signal direction.

**Independent Test**: Walk `quickstart.md` §2 Story 4. Compare `combined_score_raw` vs `combined_score`; confirm dampening only in elevated / extreme, never inverted. Run pipeline twice; results identical.

### Implementation for User Story 4

- [ ] T037 [US4] Update `_compute_combined_score` in `backend/app/services/engines/__init__.py` per research §R5 — `tech_engines` list now includes `rsi` and `macd` (8 engines total in the technical average)
- [ ] T038 [US4] After computing the weighted blend in `_compute_combined_score`, apply the volatility-regime dampener per research §R4: `adjusted = 50 + (raw - 50) * (1 - alpha)`, where `alpha` comes from `engines.volatility_regime.pull_alpha`. Emit BOTH `combined_score_raw` (pre-dampening) and `combined_score` (post-dampening) on the orchestrator output
- [ ] T039 [US4] Implement weight reporting per `contracts/engines-api.md` — for each engine that participates in the combined score, set its `weight` field to its actual fractional share (after redistribution if some engines reported `data_sufficient: false`). Volatility Regime always reports `weight: 0.0`
- [ ] T040 [US4] Unit tests for the combined-score logic in `backend/tests/services/engines/test_combined_score.py`:
  - reweighting: removing one engine redistributes weights so they sum to 1.0
  - dampening: `extreme` regime reduces `|combined - 50|` by exactly 30%
  - **no-invert** (the spec's hard rule, FR-008): for every `raw_score ∈ {10, 20, 30, 40, 60, 70, 80, 90}` and every regime tag, `sign(adjusted - 50) == sign(raw - 50)`
  - calibration spot-check: build a fixture with the same engine outputs as a known existing pick, confirm the new score is within ±10 points of the old (SC-005 sanity)
- [ ] T041 [US4] Run `cd backend && pytest tests/services/engines/test_combined_score.py` — all pass
- [ ] T042 [US4] Update the `<PickRow>` to render the post-dampening `combined_score` (already the default field) AND add a small "raw N → final M" hover-tooltip when `combined_score_raw != combined_score`, so users can see the dampening was applied
- [ ] T043 [US4] Update `<VolatilityBadge>` so the actual `regime_tag` from the engine drives the badge color — calm (gray), normal (gray), elevated (amber), extreme (red)
- [ ] T044 [US4] Walk `quickstart.md` §2 Story 4 acceptance scenarios end-to-end, including the determinism diff in §3 and the `raw vs adjusted` cross-check

**Checkpoint**: Combined score now reflects all 9 voting engines + dampener. SC-005 (±10-point calibration), SC-006 (dampening verified), SC-009 (determinism) all green.

---

## Phase 7: User Story 5 - Score Transparency Drill-Down (Priority: P3)

**Goal**: Clicking a pick row opens a drawer showing every engine's score, weight, contribution to the combined score, and rationale.

**Independent Test**: Walk `quickstart.md` §2 Story 5. Open drawer; every engine listed; close drawer; previous filter/sort preserved.

### Implementation for User Story 5

- [ ] T045 [US5] Flesh out `<PickDetailDrawer>` in `frontend/src/components/smart-picks/PickDetailDrawer.tsx` — list every engine with: name (via i18n), category badge, score chip, weight %, signal badge, one-line `reason` text. `volatility_regime` is rendered in a separate "Regime" section above the engines list (since `weight: 0.0` would otherwise be confusing)
- [ ] T046 [US5] Add a "Score breakdown" panel inside `<PickDetailDrawer>` showing `combined_score_raw → adjusted` arrow with per-engine contribution bars (each engine's `weight × score / 100` rendered as a small horizontal bar)
- [ ] T047 [US5] Wire each engine row in the drawer to open `<EngineEducationPopover>` on hover — same primitive as the inline US2 popover, no duplication
- [ ] T048 [US5] Preserve filter/sort state across drawer open/close in `frontend/src/pages/SmartPicks.tsx` — keep filter/sort in the page-level state (not the drawer's), so opening/closing the drawer is a no-op for the table
- [ ] T049 [US5] Walk `quickstart.md` §2 Story 5 acceptance scenarios end-to-end

**Checkpoint**: All 5 user stories functional and independently testable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, regression sweep, and merge readiness.

- [ ] T050 [P] Run `cd backend && ruff check .` — zero new errors (Constitution "Quality Gates: Before merge")
- [ ] T051 [P] Run `cd backend && pytest backend/tests/services/engines/ -v` — all engine tests green
- [ ] T052 [P] Run `cd frontend && npx eslint src/pages/SmartPicks.tsx src/components/smart-picks/` — zero new errors
- [ ] T053 [P] Run `cd frontend && npm run build` — successful production build, no new TypeScript errors
- [ ] T054 Run the locale-parity Python script from `quickstart.md` §3 — output `OK`
- [ ] T055 Run the determinism diff from `quickstart.md` §3 — `diff` returns empty
- [ ] T056 Run the calibration spot-check from `quickstart.md` §4: pull `combined_score` for ~20 representative tickers from `main` branch and from this branch; tabulate; confirm at least 90% are within ±10 points (SC-005)
- [ ] T057 Edge-case sweep per `quickstart.md` §3: insufficient-history pick, engine-outage simulation, conflicting-engines case, long-list scroll perf
- [ ] T058 Feature-parity diff: list every metric that was on Smart Picks before this branch and confirm it's still reachable somewhere (table, expand-row, or drawer) — verifies SC-002. Document the mapping in the PR description
- [ ] T059 [P] Add a CHANGELOG entry describing: 3 new engines, redesigned page, inline engine education, dampening rule
- [ ] T060 Run the full `quickstart.md` walkthrough end-to-end as final pre-merge sign-off

**Checkpoint**: Branch is merge-ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup. **Blocks all user stories.**
- **US1 (Phase 3)**: Depends on Foundational. P1 — first half of MVP.
- **US2 (Phase 4)**: Depends on Foundational. P1 — second half of MVP. Depends on US1 only because the popover lives inside the expand-row that US1 builds; the i18n content (T019, T020) can be authored in parallel with US1.
- **US3 (Phase 5)**: Depends on Foundational. P2 — independent of US1/US2 work.
- **US4 (Phase 6)**: Depends on US3 (engines must exist before they can be integrated). P2.
- **US5 (Phase 7)**: Depends on US1 (drawer skeleton lives there) and US4 (weights and `combined_score_raw` need to be populated for the breakdown panel). P3.
- **Polish (Phase 8)**: Depends on all desired user stories.

### User Story Dependencies (graph)

```text
Foundational (P2 phase)
   ├── US1 (page redesign)             ──┐
   ├── US2 (engine education)             ├── US5 (drill-down)
   └── US3 (new engines) ── US4 (combined score) ──┘
```

### Within Each User Story

- Within US1: types and components are parallelizable; the page rewrite (T016) sequences after the components.
- Within US2: i18n authoring (T019, T020) parallelizes with component work (T021, T022); the wire-up (T023) sequences after both.
- Within US3: the three engine modules + their tests are fully parallelizable; orchestrator wire-up (T032) sequences after.
- Within US4: orchestrator update (T037, T038, T039) sequences before the combined-score test (T040); UI wire-up (T042, T043) is parallel.
- Within US5: drawer flesh-out (T045) sequences before the breakdown panel (T046).

### Parallel Opportunities

- **Phase 1**: T001, T002, T004 in parallel.
- **Phase 2**: T005 / T006 / T008 touch different files.
- **Phase 3 (US1)**: T012, T013, T014, T015 — four components in parallel.
- **Phase 4 (US2)**: T019 + T020 in parallel; T021 + T022 in parallel.
- **Phase 5 (US3)**: T026 / T027 / T028 (three engine modules) in parallel; T029 / T030 / T031 (three test files) in parallel.
- **Phase 8**: T050 / T051 / T052 / T053 / T059 in parallel.
- **Cross-phase**: After Foundational, US1, US2 (i18n content portion), and US3 can all be staffed in parallel by different developers.

---

## Parallel Example: User Story 3

```bash
# After Foundational completes, launch the three engine modules in parallel:
Task: "Implement RSI(14) Wilder in backend/app/services/engines/rsi.py"          # T026
Task: "Implement MACD(12,26,9) in backend/app/services/engines/macd.py"          # T027
Task: "Implement Volatility Regime in backend/app/services/engines/volatility_regime.py"  # T028

# Their test files are independent — also parallel:
Task: "Unit tests for RSI in backend/tests/services/engines/test_rsi.py"         # T029
Task: "Unit tests for MACD in backend/tests/services/engines/test_macd.py"       # T030
Task: "Unit tests for Vol Regime in backend/tests/services/engines/test_volatility_regime.py"  # T031

# Then orchestrator wire-up — sequential.
Task: "Add new engines to run_all_engines in __init__.py"                         # T032
```

---

## Implementation Strategy

### MVP First (US1 + US2)

The P1 slice is shippable on its own:

1. Phase 1 — Setup
2. Phase 2 — Foundational
3. Phase 3 — US1 (redesigned page with placeholder volatility badge)
4. Phase 4 — US2 (engine education for the existing 7 engines)
5. **STOP & VALIDATE**: walk `quickstart.md` Stories 1 and 2. If both pass, this is shippable as a UI improvement. The new engines and dampening can land in a follow-up PR.

### Incremental Delivery

1. Setup + Foundational → infrastructure ready, no user-visible change.
2. + US1 + US2 → MVP demo-ready: clean page + inline education for existing engines.
3. + US3 → three new engines visible (in API + UI), but combined score unchanged.
4. + US4 → new engines fully integrated, dampening live; **scoring is the new model**.
5. + US5 → drill-down panel and breakdown bars; trader can audit every score.
6. + Polish → merge-ready.

### Parallel Team Strategy

After Foundational (T005–T010) completes:

- Developer A: US1 (Phase 3) + US2 (Phase 4) → MVP track
- Developer B: US3 (Phase 5) — three engine modules + tests
- Developer C: starts on US4 (Phase 6) once US3 is in
- Then any developer: US5 (Phase 7), Polish (Phase 8)

Stories converge cleanly because every engine goes through the same `EngineResult` shape and every text string flows through `t('engines.<name>.<field>')` — no cross-story file conflicts.

---

## Notes

- `[P]` tasks touch different files and have no incomplete dependencies.
- Tests are included **only** for the three new engines and the combined-score logic — per the constitution's principle II (financial correctness must be tested) and the project's "tests on regression" rule for everything else.
- `tradingagents.db` MUST NOT be committed in any of these tasks. The `.gitignore` should be updated as a follow-up chore (out of scope here).
- Commit cadence: one commit per task or per logical group. Keep commits scoped so a failed acceptance review can revert one slice without unraveling the rest.
- Stop at any checkpoint to validate; the engine tests + `quickstart.md` walkthroughs are the primary verification surface.
