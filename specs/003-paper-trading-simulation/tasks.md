# Tasks: Paper Trading & Portfolio Simulation

**Input**: Design documents from `/specs/003-paper-trading-simulation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: 001-trading-web-app (backend + frontend fully built)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

---

## Phase 1: Setup (New Dependencies)

**Purpose**: Add new dependency and prepare directory structure

- [ ] T001 Install recharts in frontend: `cd frontend && npm install recharts` and create `frontend/src/components/portfolio/` directory
- [ ] T002 [P] Add portfolio TypeScript types to `frontend/src/types/index.ts` — PortfolioResponse, PositionResponse, TradeResponse, TradeRequest, PortfolioAnalytics, EquityPoint, AIComparisonResponse per contracts/rest-api.md
- [ ] T003 [P] Add portfolio API functions to `frontend/src/services/api.ts` — getPortfolio(), executeTrade(), closePosition(), getTradeHistory(), getPortfolioAnalytics(), getAIComparison(), resetPortfolio()

**Checkpoint**: Frontend types and API client ready. Recharts installed.

---

## Phase 2: Foundational (Backend Models + Service + Router)

**Purpose**: Database models, service, and endpoints that all stories depend on

- [ ] T004 Add Portfolio, Position, EquitySnapshot SQLAlchemy models to `backend/app/models/database.py` per data-model.md — Portfolio (id, starting_balance, cash_balance, currency, created_at, reset_at), Position (id, portfolio_id FK, analysis_session_id FK nullable, ticker, market_id, direction, quantity, entry_price, entry_date, exit_price, exit_date, status, realized_pnl, realized_pnl_pct), EquitySnapshot (id, portfolio_id FK, date, total_value, cash_balance, positions_value)
- [ ] T005 Add Pydantic schemas for portfolio responses to `backend/app/models/schemas.py` — PositionResponse, PortfolioResponse, TradeRequest, TradeExecutionResponse, ClosePositionResponse, TradeHistoryItem, TradeHistoryResponse, PortfolioAnalyticsResponse, EquityPointSchema, AIComparisonResponse per contracts
- [ ] T006 Implement portfolio service in `backend/app/services/portfolio.py` — get_or_create_portfolio(db), execute_trade(db, request) validates cash sufficiency + creates Position + updates cash + records EquitySnapshot, close_position(db, position_id) fetches current price via yfinance + computes realized P&L + updates position status + updates cash + records snapshot, get_portfolio_with_positions(db) loads portfolio + open positions with live unrealized P&L from market_data service, get_trade_history(db, filters), get_analytics(db) computes win_rate/avg_return/best_worst/by_market/equity_curve, get_ai_comparison(db) joins analyses with/without linked positions + uses existing simulation data for ignored analyses, reset_portfolio(db)
- [ ] T007 Implement portfolio router in `backend/app/routers/portfolio.py` — GET /portfolio, POST /portfolio/trade, POST /portfolio/positions/{id}/close, GET /portfolio/trades, GET /portfolio/analytics, GET /portfolio/ai-comparison, POST /portfolio/reset per REST contract
- [ ] T008 Register portfolio router in `backend/app/main.py` — add import and include_router with /api prefix

**Checkpoint**: All 7 backend endpoints working. Can execute trades, close positions, view portfolio via API.

---

## Phase 3: User Story 1 — Execute Virtual Trade (Priority: P1) MVP

**Goal**: "Execute Trade" button on analysis results → opens trade modal → confirms trade → position created.

**Independent Test**: Complete analysis → click Execute Trade → set quantity → confirm → trade recorded.

### Implementation

- [ ] T009 [P] [US1] Create TradeModal component in `frontend/src/components/portfolio/TradeModal.tsx` — modal overlay with: ticker + recommendation display, direction auto-set (BUY→long, SELL→short), quantity input (shares), calculated total cost (price * qty), available cash display, confirm/cancel buttons; calls executeTrade API on confirm; shows success/error feedback
- [ ] T010 [US1] Add "Execute Trade" button to analysis results in `frontend/src/pages/NewAnalysis.tsx` step 4 (results) — button next to "Save Report", disabled for HOLD recommendations; on click opens TradeModal with ticker, market, recommendation, current price from analysis store; on success shows green confirmation toast

**Checkpoint**: Analysis → BUY → Execute Trade → trade recorded. MVP of paper trading.

---

## Phase 4: User Story 2 — Portfolio Dashboard (Priority: P1)

**Goal**: Portfolio page showing balance, open positions with live P&L, and summary.

**Independent Test**: Execute trades → navigate to Portfolio → see positions, P&L, cash balance.

### Implementation

- [ ] T011 [P] [US2] Create PortfolioSummary component in `frontend/src/components/portfolio/PortfolioSummary.tsx` — top bar with: starting balance, current value (large), total P&L (green/red, amount + %), cash remaining, open positions count; gradient background similar to ResultHero
- [ ] T012 [P] [US2] Create PositionsTable component in `frontend/src/components/portfolio/PositionsTable.tsx` — table of open positions: ticker (bold), market tag, direction (Long/Short badge), qty, entry price, current price, unrealized P&L (green/red), P&L % (green/red), days held, linked recommendation tag (BUY/SELL), "Close" button per row; empty state when no positions
- [ ] T013 [P] [US2] Create usePortfolio hook in `frontend/src/hooks/usePortfolio.ts` — fetches getPortfolio() on mount, exposes data/loading/error/refresh, auto-refreshes every 60 seconds for live P&L updates
- [ ] T014 [US2] Create Portfolio page in `frontend/src/pages/Portfolio.tsx` — compose Topbar + PortfolioSummary + tab bar (Positions | Trade History | Analytics) + PositionsTable in Positions tab; loading/error/empty states
- [ ] T015 [US2] Add Portfolio route and nav item — add /portfolio route in `frontend/src/App.tsx`, add Portfolio nav item in `frontend/src/components/layout/Sidebar.tsx` under Analysis section with 💰 icon

**Checkpoint**: Full portfolio dashboard with live P&L. Positions table shows unrealized gains.

---

## Phase 5: User Story 3 — Close Position (Priority: P1)

**Goal**: Close button on positions → confirm at market price → realize P&L → update balance.

**Independent Test**: Have open position → click Close → see confirmation → confirm → position moves to history, cash updated.

### Implementation

- [ ] T016 [US3] Add close position flow to PositionsTable in `frontend/src/components/portfolio/PositionsTable.tsx` — "Close" button triggers confirmation modal showing: ticker, exit price (current), realized P&L preview, return %; on confirm calls closePosition API; on success refreshes portfolio data and shows success toast
- [ ] T017 [P] [US3] Create TradeHistory component in `frontend/src/components/portfolio/TradeHistory.tsx` — table of closed trades: ticker, market, direction, qty, entry price, exit price, realized P&L (green/red), return %, hold duration (days), linked recommendation tag; fetches from getTradeHistory()
- [ ] T018 [US3] Add TradeHistory to Portfolio page Trade History tab in `frontend/src/pages/Portfolio.tsx`

**Checkpoint**: Full trade lifecycle: execute → track → close → see in history.

---

## Phase 6: User Story 4 — Portfolio Performance Analytics (Priority: P2)

**Goal**: Win rate, avg return, equity curve, best/worst trades, by-market breakdown.

**Independent Test**: Have 5+ closed trades → view Analytics tab → see all metrics + equity curve chart.

### Implementation

- [ ] T019 [P] [US4] Create EquityCurve component in `frontend/src/components/portfolio/EquityCurve.tsx` — Recharts AreaChart with date on X axis, portfolio value on Y; gradient fill (green if up from start, red if down); responsive; tooltip shows date + value
- [ ] T020 [P] [US4] Create PortfolioAnalytics component in `frontend/src/components/portfolio/PortfolioAnalytics.tsx` — fetches getPortfolioAnalytics(); displays: stat cards (total trades, win rate, avg return, total P&L), best/worst trade cards, by-market breakdown bars, EquityCurve chart; loading/empty states
- [ ] T021 [US4] Add PortfolioAnalytics to Portfolio page Analytics tab in `frontend/src/pages/Portfolio.tsx`

**Checkpoint**: Full analytics dashboard with equity curve chart.

---

## Phase 7: User Story 5 — Followed AI vs Ignored Comparison (Priority: P3)

**Goal**: Compare outcomes of trades the user executed vs analyses they skipped.

**Independent Test**: Have analyses with and without trades → view AI Comparison → see clear metric difference.

### Implementation

- [ ] T022 [P] [US5] Create AIComparison component in `frontend/src/components/portfolio/AIComparison.tsx` — fetches getAIComparison(); displays two columns: "Followed AI" (count, win rate, avg return, total P&L in green) vs "Ignored AI" (same metrics in gray/orange); bottom banner showing the difference ("Following AI earned X% more per trade"); empty state if not enough data
- [ ] T023 [US5] Add AI Comparison as a section on the Portfolio Analytics tab or as its own tab in `frontend/src/pages/Portfolio.tsx`

**Checkpoint**: Users can see the value of following vs ignoring AI recommendations.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T024 [P] Add portfolio starting balance configuration to Settings page in `frontend/src/pages/Settings.tsx` — number input for starting balance, persisted via settings API
- [ ] T025 [P] Add "Reset Portfolio" button to Portfolio page with confirmation dialog in `frontend/src/pages/Portfolio.tsx` — calls POST /portfolio/reset, refreshes page
- [ ] T026 [P] Add position count badge to Portfolio nav item in `frontend/src/components/layout/Sidebar.tsx` — show number of open positions next to nav label
- [ ] T027 Add "Execute Trade" button to History page View modal — when viewing a past completed analysis from History, show Execute Trade option if no position is linked

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — Execute Trade button on results
- **Phase 4 (US2)**: Depends on Phase 2 — Portfolio dashboard
- **Phase 5 (US3)**: Depends on US2 (close button is on positions table)
- **Phase 6 (US4)**: Depends on US3 (needs closed trades for analytics)
- **Phase 7 (US5)**: Depends on US4 (extends analytics section)
- **Phase 8 (Polish)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — MVP, no story deps
- **US2 (P1)**: After Foundational — can parallelize with US1 (different pages)
- **US3 (P1)**: After US2 — close button is in PositionsTable
- **US4 (P2)**: After US3 — needs trade history data
- **US5 (P3)**: After US4 — extends analytics

### Parallel Opportunities

**Phase 1**: T002 + T003 parallel

**Phase 2**: T004 + T005 parallel (models + schemas); then T006 → T007 → T008 sequential

**US1 + US2**: Can start simultaneously (different files — TradeModal vs PortfolioSummary/PositionsTable)

**US4**: T019 + T020 parallel (EquityCurve + PortfolioAnalytics are separate components)

---

## Parallel Example: US1 + US2

```
# Start simultaneously after Phase 2:
US1: T009 TradeModal → T010 Wire into NewAnalysis results
US2: T011 PortfolioSummary + T012 PositionsTable + T013 usePortfolio (parallel) → T014 Portfolio page → T015 Route+nav
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1: Setup (3 tasks)
2. Phase 2: Foundational — backend models, service, router (5 tasks)
3. Phase 3: US1 — Execute Trade from results (2 tasks)
4. Phase 4: US2 — Portfolio dashboard (5 tasks)
5. **STOP and VALIDATE**: Execute trade → see it on portfolio → P&L updates live

### Incremental Delivery

1. Setup + Foundational → Backend ready
2. + US1 → Can execute trades from analysis results (MVP!)
3. + US2 → Portfolio dashboard with live positions
4. + US3 → Close positions, see trade history
5. + US4 → Full analytics with equity curve
6. + US5 → AI comparison ("was following the AI worth it?")
7. Polish → Settings, reset, nav badge

---

## Notes

- Recharts is the only new frontend dependency (for equity curve chart)
- Backend adds 3 new DB tables — auto-created by SQLAlchemy on startup
- P&L uses existing yfinance/market_data prices — no new data fetching needed
- AI comparison leverages existing SimulationResult data for "ignored" analyses
- Short selling supported: SELL recommendation → short position → profit when price drops
