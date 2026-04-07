# Tasks: Candlestick Chart & Analysis State Persistence

**Input**: Design documents from `/specs/004-candlestick-analysis-view/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/rest-api.md, quickstart.md

**Tests**: Not requested — manual verification per quickstart.md.

**Organization**: Tasks grouped by user story. Both stories are P1 and independent — can be implemented in either order or in parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`

---

## Phase 1: Setup

**Purpose**: Install new dependency and add shared types/schemas

- [ ] T001 Install lightweight-charts in frontend: `cd frontend && npm install lightweight-charts`
- [ ] T002 [P] Add OHLCBar and PriceHistoryResponse types in frontend/src/types/index.ts
- [ ] T003 [P] Add OHLCBar and PriceHistoryResponse Pydantic schemas in backend/app/models/schemas.py

---

## Phase 2: User Story 1 — Candlestick Chart on Ticker Selection (P1)

**Goal**: After validating a ticker, display an interactive candlestick chart with volume and time range selection.

**Independent Test**: Select AAPL on US market → candlestick chart renders with 3-month daily candles, hover tooltip shows OHLC + volume, time range buttons switch periods, EGX tickers show EGP currency.

### Backend

- [ ] T004 [US1] Add `get_price_history(ticker, market_id, period)` function in backend/app/services/market_data.py — uses yf.download() with period-to-interval mapping (1w→15m, else→1d), applies market suffix, returns list of OHLCBar dicts
- [ ] T005 [US1] Add `GET /api/stocks/price-history` endpoint in backend/app/routers/stocks.py — accepts ticker, market_id, period query params, calls get_price_history service, returns PriceHistoryResponse (depends on T003, T004)

### Frontend

- [ ] T006 [US1] Add `getPriceHistory(ticker, marketId, period)` API function in frontend/src/services/api.ts — calls GET /api/stocks/price-history, returns PriceHistoryResponse (depends on T002)
- [ ] T007 [US1] Create CandlestickChart component in frontend/src/components/analysis/CandlestickChart.tsx — uses lightweight-charts to render candlestick series + volume histogram, accepts ticker/marketId/currency props, includes time range selector buttons (1W, 1M, 3M, 6M, 1Y), fetches data via getPriceHistory on mount and range change, shows loading skeleton and empty state (depends on T001, T006)
- [ ] T008 [US1] Integrate CandlestickChart into NewAnalysis.tsx — render chart below the stock info card on Step 1 after ticker validation, pass selectedStock ticker/market/currency as props, keep chart visible on Step 2 for context (depends on T007)

**Checkpoint**: Candlestick chart works end-to-end. Validate with AAPL (US) and COMI (Egypt). Test all 5 time ranges. Verify tooltip, loading state, and error empty state.

---

## Phase 3: User Story 2 — Persist Analysis State Across Navigation (P1)

**Goal**: Fix the bug where navigating away from the analysis page and returning loses all wizard state.

**Independent Test**: Start analysis → navigate to History → return → analysis still running with all progress. Also test: select ticker + config on Step 2 → navigate away → return → still on Step 2 with selections preserved.

### Zustand Store

- [ ] T009 [US2] Create wizardStore in frontend/src/stores/wizardStore.ts — state: step, selectedMarket, selectedStock, tradeHorizon, analysisDate, showCustomTicker, wsUrl; actions: setStep, setMarket, setStock, setTradeHorizon, setAnalysisDate, setShowCustomTicker, setWsUrl, reset (clears all to defaults)

### Migration

- [ ] T010 [US2] Migrate NewAnalysis.tsx from local useState to wizardStore — replace all useState declarations (step, selectedMarket, selectedStock, tradeHorizon, analysisDate, showCustomTicker, wsUrl) with useWizardStore() selectors and actions; ensure all handlers (handleMarketSelect, handleStockValidated, handleStartAnalysis, etc.) update the store instead of local state; keep starting/startError/loadingSession/tradeModalOpen as local state (transient UI-only) (depends on T009)
- [ ] T011 [US2] Update "New Analysis" sidebar link behavior — when clicking the nav link for analysis, if wizardStore has active state (step > 0), navigate to "/" without resetting; add explicit "New Analysis" button/action that calls wizardStore.reset() + analysisStore.reset() to start fresh (depends on T010)
- [ ] T012 [US2] Handle WebSocket reconnection on return — when NewAnalysis mounts and wizardStore has wsUrl + analysisStore has sessionId with status "running", re-establish WebSocket connection; if analysisStore status is "completed", skip to Step 4 directly (depends on T010)

**Checkpoint**: Navigate away and back at every step (0-4). Verify state preserved. Verify explicit "New Analysis" resets. Verify WebSocket reconnects for in-progress analysis.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final integration and edge case handling

- [ ] T013 [P] Add loading skeleton CSS for chart area in frontend/src/styles/globals.css — match existing design system skeleton patterns
- [ ] T014 Verify quickstart.md scenarios end-to-end — run through all manual test steps in specs/004-candlestick-analysis-view/quickstart.md, fix any issues found

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on T001 (lightweight-charts), T002 (types), T003 (schemas)
- **US2 (Phase 3)**: No dependency on Phase 1 or Phase 2 — can start in parallel
- **Polish (Phase 4)**: Depends on both US1 and US2 complete

### User Story Dependencies

- **US1 (Candlestick Chart)**: Independent — does not depend on US2
- **US2 (State Persistence)**: Independent — does not depend on US1
- Both can be implemented in parallel or in any order

### Within Each User Story

- Backend before frontend (API must exist before UI calls it)
- Models/schemas before services before endpoints
- Store before migration (US2)
- Core implementation before integration

### Parallel Opportunities

```bash
# Phase 1 — all parallelizable after T001:
T002 (frontend types) || T003 (backend schemas)

# Phase 2 (US1) — backend tasks parallelizable:
T004 (service) + T003 (schemas) → T005 (endpoint)
T006 (api function) → T007 (chart component) → T008 (integration)

# Phase 3 (US2) — sequential (each depends on prior):
T009 → T010 → T011 + T012

# Phase 4 — after both stories:
T013 (CSS) || T014 (verification)
```

---

## Implementation Strategy

### MVP First (Either Story)

1. Complete Phase 1: Setup (install dep, add types)
2. Pick either US1 or US2 (both are P1)
3. Complete chosen story end-to-end
4. **STOP and VALIDATE**: Test per quickstart.md
5. Proceed to second story

### Parallel Strategy

1. Complete Phase 1: Setup
2. US1 backend (T004-T005) in parallel with US2 store (T009-T010)
3. US1 frontend (T006-T008) in parallel with US2 reconnection (T011-T012)
4. Phase 4: Polish both stories together

---

## Notes

- [P] tasks = different files, no dependencies
- [US1]/[US2] labels map tasks to user stories
- No test tasks — manual verification per quickstart.md
- lightweight-charts is the only new dependency
- No database changes — no migrations needed
- Commit after each task or logical group
