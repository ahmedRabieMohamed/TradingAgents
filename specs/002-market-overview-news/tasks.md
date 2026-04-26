# Tasks: Market Overview & Hot News

**Input**: Design documents from `/specs/002-market-overview-news/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: 001-trading-web-app (backend + frontend already built and running)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Data & Services)

**Purpose**: Create the foundational data files and services that all user stories depend on

- [ ] T001 Create `backend/app/data/` directory and `backend/app/data/__init__.py`
- [ ] T002 Create curated US stock watchlist (~50 tickers) with name and sector in `backend/app/data/watchlists.py` — include FAANG, major indices (SPY, QQQ, DIA), top S&P 500 components across sectors
- [ ] T003 [P] Add EGX stock watchlist to `backend/app/data/watchlists.py` — import from existing `tradingagents/dataflows/egypt_tickers.py`, include English name, Arabic name, and sector for each
- [ ] T004 [P] Add market index definitions to `backend/app/data/watchlists.py` — US: {name:"S&P 500", symbol:"^GSPC"}, {name:"NASDAQ", symbol:"^IXIC"}, {name:"Dow Jones", symbol:"^DJI"}; Egypt: {name:"EGX 30", symbol:"^CASE"}
- [ ] T005 [P] Add MarketOverview, StockSnapshot, IndexData, MarketSummary, NewsArticle, MarketNewsResponse Pydantic schemas to `backend/app/models/schemas.py` per data-model.md
- [ ] T006 [P] Add frontend TypeScript types for market overview (MarketOverviewResponse, StockSnapshot, IndexData, MarketSummary, NewsArticle, MarketNewsResponse) to `frontend/src/types/index.ts`

**Checkpoint**: Watchlists, schemas, and types ready. No endpoints yet.

---

## Phase 2: Foundational (Backend Services)

**Purpose**: Backend services that multiple user stories share — MUST complete before frontend work

- [ ] T007 Implement market data service in `backend/app/services/market_data.py` — `get_market_overview(market_id)` that batch-fetches prices for all watchlist stocks via yfinance `download()`, computes daily change/change_pct, fetches index data, computes summary stats (gainers/losers/breadth), sorts gainers and losers top 7, applies 5-minute in-memory cache with TTL
- [ ] T008 [P] Implement news service in `backend/app/services/news.py` — `get_market_news(market_id, limit)` and `get_ticker_news(ticker, market_id, limit)` wrapping existing `tradingagents.dataflows` functions (yfinance for US, egypt_news for Egypt), normalize output to NewsArticle schema, 10-minute cache
- [ ] T009 Implement market overview router in `backend/app/routers/market_overview.py` — GET /market-overview/{market_id} (calls market_data service), GET /market-overview/{market_id}/news (calls news service with optional ?ticker= query param)
- [ ] T010 Register market_overview router in `backend/app/main.py` — add `from app.routers.market_overview import router` and `app.include_router(router, prefix="/api")`
- [ ] T011 [P] Add `fetchMarketOverview(marketId)` and `fetchMarketNews(marketId, ticker?, limit?)` to `frontend/src/services/api.ts`

**Checkpoint**: Backend endpoints return real data. Frontend can call them.

---

## Phase 3: User Story 1 — Market Overview Dashboard (Priority: P1) MVP

**Goal**: After selecting a market, user sees a stock list with prices, changes, and can click to analyze.

**Independent Test**: Select US → see 50 stocks with prices. Select EGX → see 30 stocks with EGP prices. Click stock → goes to config step.

### Implementation

- [ ] T012 [P] [US1] Create StockTable component in `frontend/src/components/market-overview/StockTable.tsx` — sortable table with columns: Ticker (bold), Name (+ Arabic for EGX), Price, Change, Change%, Sector, "Analyze" button; search input at top for filtering by ticker/name; click row or button to select stock
- [ ] T013 [P] [US1] Create useMarketOverview hook in `frontend/src/hooks/useMarketOverview.ts` — fetches market overview on mount or when marketId changes, exposes loading/error/data state, provides refresh function
- [ ] T014 [US1] Create MarketOverview container in `frontend/src/components/market-overview/MarketOverview.tsx` — uses useMarketOverview hook, renders tab bar (Stocks | Movers | News), renders StockTable in Stocks tab, passes stock click handler up
- [ ] T015 [US1] Insert market overview step into `frontend/src/pages/NewAnalysis.tsx` — after market selection (step 0), show MarketOverview as new step 1; clicking a stock sets selectedStock and jumps to config (step 2); add "Enter custom ticker" link to fall back to manual input; update step indicator labels

**Checkpoint**: Select market → see stock list → click stock → goes to config. MVP working.

---

## Phase 4: User Story 2 — Top Movers Grid (Priority: P1)

**Goal**: Gainers/Losers grids on the market overview, sorted by % change.

**Independent Test**: View market overview → Movers tab → see top 7 gainers (green) and top 7 losers (red). Click any → goes to config.

### Implementation

- [ ] T016 [P] [US2] Create MoverGrid component in `frontend/src/components/market-overview/MoverGrid.tsx` — two side-by-side cards: "Top Gainers" (green header) and "Top Losers" (red header); each shows up to 7 rows with ticker, name, price, change% badge (green/red); click row to select stock
- [ ] T017 [US2] Add MoverGrid to MarketOverview Movers tab in `frontend/src/components/market-overview/MarketOverview.tsx` — pass gainers/losers arrays from useMarketOverview data

**Checkpoint**: Movers tab shows gainers/losers grids. Click navigates to config.

---

## Phase 5: User Story 3 — Hot News Section (Priority: P1)

**Goal**: News feed with market-relevant articles, clickable to original source.

**Independent Test**: View market overview → News tab → see 10+ articles with headline, source, date. Click → opens in new tab. Refresh button fetches fresh articles.

### Implementation

- [ ] T018 [P] [US3] Create NewsSection component in `frontend/src/components/market-overview/NewsSection.tsx` — list of news cards with: headline (bold), source name (accent color), publication time (relative: "2h ago"), snippet text, "HOT" badge for is_hot articles; click opens URL in new tab; refresh button at top
- [ ] T019 [US3] Add NewsSection to MarketOverview News tab in `frontend/src/components/market-overview/MarketOverview.tsx` — fetch news via fetchMarketNews on tab activation, loading/error states

**Checkpoint**: News tab shows live market articles. Links work. Refresh works.

---

## Phase 6: User Story 4 — Market Analytics Summary (Priority: P2)

**Goal**: Market indices and summary stats displayed at the top of the overview.

**Independent Test**: View market overview → see index cards (S&P 500/NASDAQ/Dow for US, EGX 30 for Egypt) with values and change. See summary bar with stock count, gainers, losers, breadth%.

### Implementation

- [ ] T020 [P] [US4] Create IndexBar component in `frontend/src/components/market-overview/IndexBar.tsx` — horizontal grid of index cards; each shows name, value (large number), change and change% (green/red coloring)
- [ ] T021 [P] [US4] Create MarketSummary component in `frontend/src/components/market-overview/MarketSummary.tsx` — 4 stat cards: Stocks Tracked, Gainers (green), Losers (red), Market Breadth%; compact layout
- [ ] T022 [US4] Add IndexBar and MarketSummary to top of MarketOverview in `frontend/src/components/market-overview/MarketOverview.tsx` — render above tabs, always visible regardless of active tab
- [ ] T023 [US4] Add market-closed banner to MarketOverview in `frontend/src/components/market-overview/MarketOverview.tsx` — if market_status is "closed", show yellow banner with "Market Closed — showing last close data"

**Checkpoint**: Indices and summary stats visible at top. Market-closed banner shows outside hours.

---

## Phase 7: User Story 5 — Ticker-Specific News (Priority: P3)

**Goal**: View news for a specific stock from the market overview.

**Independent Test**: Click news icon on a stock row → see articles about that company. EGX stock shows English + Arabic sources.

### Implementation

- [ ] T024 [P] [US5] Create TickerNews component in `frontend/src/components/market-overview/TickerNews.tsx` — modal/slide-out panel showing news for a specific ticker; fetches via fetchMarketNews(marketId, ticker); shows articles list or "No recent news" empty state; close button
- [ ] T025 [US5] Add news icon/button to StockTable rows in `frontend/src/components/market-overview/StockTable.tsx` — 📰 icon next to Analyze button; on click, opens TickerNews panel for that stock
- [ ] T026 [US5] Wire TickerNews into MarketOverview in `frontend/src/components/market-overview/MarketOverview.tsx` — manage selected ticker state, render TickerNews when a ticker is selected

**Checkpoint**: News icon on stock rows opens ticker-specific news. Works for both US and EGX.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements

- [ ] T027 [P] Add EGP currency formatting and Arabic name display throughout all market-overview components
- [ ] T028 [P] Add loading skeletons to MarketOverview while data fetches in `frontend/src/components/market-overview/MarketOverview.tsx`
- [ ] T029 [P] Handle news API fallback: if Serper.dev key not configured, news service in `backend/app/services/news.py` silently falls back to RSS — verify no error shown to user
- [ ] T030 Validate quickstart.md — follow steps end-to-end for both US and Egypt markets

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 (uses same data); can parallelize with US1
- **Phase 5 (US3)**: Depends on Phase 2 (news service)
- **Phase 6 (US4)**: Depends on Phase 2 (uses overview data)
- **Phase 7 (US5)**: Depends on US3 (extends news UI) + US1 (extends stock table)
- **Phase 8 (Polish)**: After all stories

### User Story Dependencies

- **US1 (P1)**: After Foundational — no story dependencies. MVP.
- **US2 (P1)**: After Foundational — independent of US1 (uses same backend data)
- **US3 (P1)**: After Foundational — independent (different UI component)
- **US4 (P2)**: After Foundational — independent (top-level display components)
- **US5 (P3)**: After US1 + US3 — extends stock table (US1) and news pattern (US3)

### Parallel Opportunities

**Phase 1**: T002 + T003 + T004 + T005 + T006 all parallel (different files)

**Phase 2**: T007 + T008 parallel (different services); T011 parallel with backend work

**US1-US4**: All can start simultaneously after Phase 2 (US1, US2, US3, US4 touch different component files)

**US4**: T020 + T021 parallel (different components)

---

## Parallel Example: After Phase 2 Completes

```
# All four user stories can start in parallel (different files):
US1: StockTable + useMarketOverview + MarketOverview container
US2: MoverGrid component
US3: NewsSection component
US4: IndexBar + MarketSummary components

# Then integrate:
US1: Wire into NewAnalysis.tsx
US2: Add to MarketOverview Movers tab
US3: Add to MarketOverview News tab
US4: Add IndexBar + MarketSummary to top of MarketOverview
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (5 tasks)
3. Complete Phase 3: US1 — Stock list with click-to-analyze (4 tasks)
4. **STOP and VALIDATE**: Select market → see stocks → click → config
5. This alone replaces the blank ticker input with an informative stock browser

### Incremental Delivery

1. Setup + Foundational → Backend ready
2. + US1 → Stock list (MVP!)
3. + US2 → Gainers/losers grids
4. + US3 → Hot news feed
5. + US4 → Market indices and summary stats
6. + US5 → Ticker-specific news drill-down
7. Polish → Currency formatting, loading states, fallbacks

---

## Notes

- No tests generated (not requested in spec)
- All backend work reuses existing `tradingagents.dataflows` — zero changes to core package
- yfinance batch `download()` is key performance decision — fetches 50 stocks in ~2 seconds
- News has two tiers: yfinance (US, free) and Serper→RSS fallback (Egypt)
- Stock watchlists are static Python lists — easy to extend later
