# Tasks: 7 Trading Engines + Smart Picks + Danger Alerts

**Input**: Design documents from `/specs/010-engines-smart-picks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/rest-api.md, quickstart.md

**Tests**: Not requested — manual verification per constitution.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4, US5)

---

## Phase 1: Setup

**Purpose**: Install dependencies, create directory structure, add DB column

- [ ] T001 Verify numpy is installed in backend environment (pip install numpy if needed)
- [ ] T002 Create backend/app/services/engines/ directory with __init__.py
- [ ] T003 Add engine_scores JSON column (nullable) to AnalysisSession model in backend/app/models/database.py
- [ ] T004 Add engine score Pydantic schemas (EngineScoreResponse, SmartPickResponse, DangerAlertResponse) in backend/app/models/schemas.py
- [ ] T005 Migrate existing SQLite database — ALTER TABLE analysis_sessions ADD COLUMN engine_scores TEXT

**Checkpoint**: Directory exists, DB column added, schemas defined.

---

## Phase 2: Foundational (7 Engine Modules)

**Purpose**: Build all 7 engine computation functions. MUST complete before any user story.

**CRITICAL**: Each engine is a pure function — prices/volumes in, score dict out. No API calls, no DB, no side effects.

- [ ] T006 [P] Create Monte Carlo engine: 10K GBM simulations → prob_up, expected_change, best_case, worst_case, score in backend/app/services/engines/monte_carlo.py
- [ ] T007 [P] Create Momentum engine: 5-day ROC, 20-day ROC, trend strength → score in backend/app/services/engines/momentum.py
- [ ] T008 [P] Create Volume Confirmation engine: volume ratio vs 20-day avg, is_real_move → score in backend/app/services/engines/volume.py
- [ ] T009 [P] Create Support/Resistance engine: find S/R levels from price history, risk_reward ratio → score in backend/app/services/engines/support_resistance.py
- [ ] T010 [P] Create Mean Reversion engine: distance from 50-SMA, is_oversold/overbought → score in backend/app/services/engines/mean_reversion.py
- [ ] T011 [P] Create Bollinger Bands engine: band width, squeeze detection, position → score in backend/app/services/engines/bollinger.py
- [ ] T012 [P] Create Correlation engine: 90-day sector peer correlation, peers_bullish count → score in backend/app/services/engines/correlation.py
- [ ] T013 Create engine orchestrator: compute_all_engines(ticker, market_id) fetches prices via yfinance, runs all 7 engines, returns combined dict in backend/app/services/engines/__init__.py
- [ ] T014 Create combined score calculator: weighted average (MC 40% + News 30% + Tech 30%), handle N/A engines, classify signal (BUY/HOLD/SELL) in backend/app/services/engines/__init__.py
- [ ] T015 Verify: run compute_all_engines("ETEL", "egypt") from Python shell — all 7 scores return valid numbers

**Checkpoint**: All 7 engines compute independently. Orchestrator returns combined score for any ticker.

---

## Phase 3: User Story 1 — Smart Picks Page (Priority: P1) 🎯 MVP

**Goal**: Show ranked list of top stocks sourced from news + movers, scored by all engines.

**Independent Test**: Open Smart Picks page → see 5-10 ranked stocks with scores, MC prob, news sentiment, signal. Click Analyze → goes to analysis page.

### Implementation for User Story 1

- [ ] T016 [US1] Create news sentiment scoring service: fetch news for a ticker, use LLM to score sentiment (-100 to +100) in backend/app/services/news_sentiment.py
- [ ] T017 [US1] Create smart picks service: discover candidates from news + movers, score each with engines, rank by combined score, cache 1 hour, limit 15 in backend/app/services/smart_picks.py
- [ ] T018 [US1] Create engines router with GET /api/engines/score/{ticker} endpoint in backend/app/routers/engines.py
- [ ] T019 [US1] Add GET /api/engines/smart-picks endpoint to engines router in backend/app/routers/engines.py
- [ ] T020 [US1] Register engines router in backend/app/main.py
- [ ] T021 [US1] Create engine API functions (getEngineScore, getSmartPicks, getDangerAlerts) in frontend/src/services/api.ts
- [ ] T022 [P] [US1] Create English engines translation file in frontend/src/locales/en/engines.json
- [ ] T023 [P] [US1] Create Arabic engines translation file in frontend/src/locales/ar/engines.json
- [ ] T024 [US1] Register engines namespace in frontend/src/i18n.ts
- [ ] T025 [US1] Create SmartPicksTable component: ranked table with score, MC prob, news, signal, Analyze button in frontend/src/components/engines/SmartPicksTable.tsx
- [ ] T026 [US1] Create SmartPicks page: title, refresh button, loading state, SmartPicksTable, news feed sidebar in frontend/src/pages/SmartPicks.tsx
- [ ] T027 [US1] Add SmartPicks route (/smart-picks) in frontend/src/App.tsx
- [ ] T028 [US1] Add Smart Picks nav item (🎯) to sidebar in frontend/src/components/layout/Sidebar.tsx
- [ ] T029 [US1] Verify: open /smart-picks → see ranked stocks → click Analyze → navigates to /analysis with ticker prefilled

**Checkpoint**: Smart Picks page shows ranked stocks from news + movers. Fully functional MVP.

---

## Phase 4: User Story 2 — 7 Engine Breakdown (Priority: P1)

**Goal**: Show expandable 7-engine breakdown with detailed data for any stock.

**Independent Test**: Open any stock's engine breakdown → see 7 gauge bars → click each to expand → see MC histogram, volume bars, S/R chart.

### Implementation for User Story 2

- [ ] T030 [US2] Create EngineBreakdown component: combined score display + 7 engine gauge bars with expand/collapse in frontend/src/components/engines/EngineBreakdown.tsx
- [ ] T031 [P] [US2] Create MonteCarloPanel component: probability stats + histogram chart (Recharts BarChart) in frontend/src/components/engines/MonteCarloPanel.tsx
- [ ] T032 [P] [US2] Create VolumePanel component: 6-day volume bar chart + Real/Fake verdict in frontend/src/components/engines/VolumePanel.tsx
- [ ] T033 [P] [US2] Create SupportResistPanel component: S/R levels visual + risk/reward ratio in frontend/src/components/engines/SupportResistPanel.tsx
- [ ] T034 [US2] Add EngineBreakdown to SmartPicks page: click a stock row to expand its engine detail in frontend/src/pages/SmartPicks.tsx
- [ ] T035 [US2] Create engine scores Zustand store in frontend/src/stores/engineStore.ts
- [ ] T036 [US2] Verify: click any stock in Smart Picks → engine breakdown expands → all 7 engines show score + verdict → click MC to see histogram

**Checkpoint**: Full 7-engine breakdown visible for any stock with expandable detail panels.

---

## Phase 5: User Story 3 — Danger Alerts (Priority: P1)

**Goal**: Show red/yellow/green alerts for all open portfolio positions.

**Independent Test**: Open Danger Alerts with positions → each shows color-coded alert → full engine breakdown per position.

### Implementation for User Story 3

- [ ] T037 [US3] Add GET /api/engines/danger-alerts endpoint: fetch open positions, run engines on each, classify red/yellow/green in backend/app/routers/engines.py
- [ ] T038 [US3] Create DangerAlerts component: alert cards (red/yellow/green) with score + reason + expand for breakdown in frontend/src/components/engines/DangerAlerts.tsx
- [ ] T039 [US3] Add Danger Alerts section to SmartPicks page (below Smart Picks table) in frontend/src/pages/SmartPicks.tsx
- [ ] T040 [US3] Verify: with open positions → Danger Alerts shows correct color for each → engine breakdown available

**Checkpoint**: Danger Alerts monitors all open positions with color-coded alerts.

---

## Phase 6: User Story 4 — News-Driven Discovery (Priority: P2)

**Goal**: Auto-discover candidate stocks from news + EGX top movers.

**Independent Test**: Smart Picks shows stocks that are in today's news. News feed sidebar shows articles with sentiment.

### Implementation for User Story 4

- [ ] T041 [US4] Create news discovery function: fetch news from existing sources, extract ticker mentions using EGX ticker database matching in backend/app/services/smart_picks.py
- [ ] T042 [US4] Create EGX top movers function: fetch top gainers/losers/volume from yfinance batch download in backend/app/services/smart_picks.py
- [ ] T043 [US4] Add news feed display to SmartPicks page: show today's articles with ticker, sentiment, timestamp in frontend/src/pages/SmartPicks.tsx
- [ ] T044 [US4] Verify: Smart Picks candidates come from news mentions + movers (not hardcoded)

**Checkpoint**: Stocks in Smart Picks are discovered from real news + market activity.

---

## Phase 7: User Story 5 — Engine Scores in Analysis Page (Priority: P2)

**Goal**: Show engine breakdown alongside AI agent reports on analysis results page.

**Independent Test**: Run full analysis → results show combined score + 7 engines above the agent reports.

### Implementation for User Story 5

- [ ] T045 [US5] Compute and store engine scores when analysis completes: call compute_all_engines in analysis service, save to engine_scores column in backend/app/services/analysis.py
- [ ] T046 [US5] Include engine_scores in GET /api/analysis/{session_id} response in backend/app/models/schemas.py
- [ ] T047 [US5] Add EngineBreakdown component above Detailed Reports section in frontend/src/pages/NewAnalysis.tsx
- [ ] T048 [US5] Verify: run new analysis → results page shows engine scores above agent reports → viewing from History shows same scores

**Checkpoint**: Engine scores integrated into analysis workflow and persisted.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, verification, translations

- [ ] T049 [P] Add manual "Score Any Stock" input on Smart Picks page: ticker input + market select + Score button in frontend/src/pages/SmartPicks.tsx
- [ ] T050 Verify frontend build: cd frontend && npx tsc --noEmit && npm run build
- [ ] T051 Verify backend lint: cd backend && ruff check .
- [ ] T052 Full regression smoke test: all existing pages still work, Smart Picks loads, Danger Alerts shows, engines compute
- [ ] T053 Verify Arabic translations: switch to Arabic → all engine labels display in Arabic

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 Smart Picks (Phase 3)**: Depends on Phase 2 (needs engines)
- **US2 Engine Breakdown (Phase 4)**: Depends on Phase 3 (needs Smart Picks page to embed into)
- **US3 Danger Alerts (Phase 5)**: Depends on Phase 2 only (can run parallel with US1/US2)
- **US4 News Discovery (Phase 6)**: Depends on Phase 3 (enhances Smart Picks)
- **US5 Analysis Integration (Phase 7)**: Depends on Phase 2 (needs engine orchestrator)
- **Polish (Phase 8)**: Depends on all stories complete

### User Story Dependencies

- **US1 (Smart Picks)**: Foundation only — fully independent MVP
- **US2 (Engine Breakdown)**: Depends on US1 (needs page to display in)
- **US3 (Danger Alerts)**: Foundation only — can parallel with US1
- **US4 (News Discovery)**: Depends on US1 (enhances Smart Picks candidates)
- **US5 (Analysis Integration)**: Foundation only — can parallel with US1

### Parallel Opportunities

- T006-T012: All 7 engine modules (different files, no dependencies)
- T022+T023: English + Arabic translation files
- T031+T032+T033: MC, Volume, S/R panel components
- US3 (Danger Alerts) can run parallel with US1 (Smart Picks)
- US5 (Analysis Integration) can run parallel with US1

---

## Parallel Example: Phase 2 Engines

```bash
# All 7 engines in parallel (different files):
Task: "Monte Carlo engine" (T006)
Task: "Momentum engine" (T007)
Task: "Volume engine" (T008)
Task: "Support/Resistance engine" (T009)
Task: "Mean Reversion engine" (T010)
Task: "Bollinger engine" (T011)
Task: "Correlation engine" (T012)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup (T001-T005)
2. Phase 2: 7 Engines (T006-T015)
3. Phase 3: Smart Picks page (T016-T029)
4. **STOP**: Smart Picks works end-to-end. Users can see ranked stocks.

### Incremental Delivery

1. Setup + Engines → Foundation
2. US1: Smart Picks → MVP! Users can see today's best chances
3. US2: Engine Breakdown → Users can see WHY each stock scored high
4. US3: Danger Alerts → Users can protect open positions
5. US4: News Discovery → Automatic stock discovery
6. US5: Analysis Integration → Engines in analysis flow
7. Polish → Ship

---

## Notes

- Each engine is ~20-30 lines of Python — simple numpy functions
- All engines use yfinance OHLCV data (free, already installed)
- Smart Picks candidates limited to max 15 stocks
- Cache: Smart Picks cached 1 hour, Danger Alerts computed fresh each time
- Engine scores stored as JSON on AnalysisSession — backward compatible (NULL for old sessions)
