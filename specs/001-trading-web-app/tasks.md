# Tasks: Trading Web Application

**Input**: Design documents from `/specs/001-trading-web-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend and frontend projects with dependencies and build tooling

- [ ] T001 Create backend project directory structure per plan: `backend/app/routers/`, `backend/app/models/`, `backend/app/services/`, `backend/tests/`
- [ ] T002 Create `backend/requirements.txt` with FastAPI, uvicorn, SQLAlchemy, httpx, python-dotenv, websockets, and reference to parent tradingagents package
- [ ] T003 Create `backend/.env.example` with placeholder env vars (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- [ ] T004 Initialize frontend React+TypeScript project with Vite in `frontend/` (package.json, tsconfig.json, vite.config.ts, index.html)
- [ ] T005 Install frontend dependencies: react, react-dom, react-router-dom, zustand, and dev deps (typescript, @types/react, vite)
- [ ] T006 [P] Create `frontend/src/styles/globals.css` with CSS variables and dark theme matching prototype design
- [ ] T007 [P] Create `frontend/src/types/index.ts` with TypeScript interfaces for all API schemas (Market, AnalysisSession, AgentReport, SimulationResult, WebSocket events) per contracts

**Checkpoint**: Both projects build and run (empty shells). `uvicorn` serves FastAPI, `npm run dev` serves Vite.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can begin

**CRITICAL**: No user story work until this phase is complete

- [ ] T008 Create FastAPI app entry with CORS middleware in `backend/app/main.py` — mount all routers, configure CORS for localhost frontend
- [ ] T009 Create SQLite database setup with SQLAlchemy engine and session factory in `backend/app/database.py`
- [ ] T010 Create SQLAlchemy ORM models (AnalysisSession, AgentReport, SimulationResult, UserSettings) in `backend/app/models/database.py` per data-model.md
- [ ] T011 Create Pydantic request/response schemas matching REST API contract in `backend/app/models/schemas.py`
- [ ] T012 Create app config with env var loading in `backend/app/config.py` (API keys, DB path, frontend URL)
- [ ] T013 [P] Implement settings service (CRUD for UserSettings key-value store) in `backend/app/services/settings.py`
- [ ] T014 [P] Implement settings router (GET /api/settings, PATCH /api/settings) in `backend/app/routers/settings.py` per REST contract
- [ ] T015 [P] Implement LLM providers router (GET /api/llm-providers) in `backend/app/routers/llm_providers.py` — read provider/model lists from tradingagents default_config
- [ ] T016 Create frontend app shell: `frontend/src/App.tsx` with React Router (routes: /, /history, /performance, /settings), `frontend/src/main.tsx` entry point
- [ ] T017 [P] Create layout components: `frontend/src/components/layout/Sidebar.tsx` (nav items, market indicator) and `frontend/src/components/layout/Topbar.tsx` (page title, badges)
- [ ] T018 [P] Create `frontend/src/services/api.ts` — fetch-based HTTP client with base URL config and typed wrapper functions for all REST endpoints
- [ ] T019 [P] Create Settings page in `frontend/src/pages/Settings.tsx` — API key inputs (masked), default config dropdowns, save button calling PATCH /api/settings

**Checkpoint**: Backend serves API at :8000, frontend renders shell with sidebar navigation. Settings page functional end-to-end.

---

## Phase 3: User Story 1 — Market & Stock Selection (Priority: P1) MVP

**Goal**: User selects a market (US/EGX) and validates a stock ticker, seeing its name and price.

**Independent Test**: Open app → select market → enter ticker (e.g., AAPL) → see stock name, price, change%. Invalid ticker shows error.

### Implementation

- [ ] T020 [P] [US1] Implement markets router (GET /api/markets) in `backend/app/routers/markets.py` — return market configs derived from tradingagents MARKET_REGIONS
- [ ] T021 [P] [US1] Implement stock validation service in `backend/app/services/stock_info.py` — validate ticker via yfinance, return name/price/change for given market (handle .CA suffix for EGX)
- [ ] T022 [US1] Implement stocks router (GET /api/stocks/validate) in `backend/app/routers/stocks.py` — query params: ticker, market; returns stock info or 404 per REST contract
- [ ] T023 [P] [US1] Create MarketSelector component in `frontend/src/components/analysis/MarketSelector.tsx` — two clickable cards (US/EGX) with flags, exchange names, example tickers
- [ ] T024 [P] [US1] Create TickerInput component in `frontend/src/components/analysis/TickerInput.tsx` — text input, validate button, stock info display card, error state
- [ ] T025 [US1] Create step wizard container in `frontend/src/pages/NewAnalysis.tsx` — step indicator (5 steps), step routing, state management for selected market/ticker
- [ ] T026 [US1] Wire MarketSelector and TickerInput into NewAnalysis page — market selection calls GET /api/markets, ticker validation calls GET /api/stocks/validate, stock info displays on success

**Checkpoint**: User can select US or EGX market, enter a ticker, see validated stock info. Invalid tickers show error. This is the MVP entry point.

---

## Phase 4: User Story 2 — Configure & Run Analysis (Priority: P1)

**Goal**: User configures analysis parameters and runs the full multi-agent pipeline with real-time progress streaming.

**Independent Test**: Select stock → configure horizon/analysts/depth/LLM → start analysis → see live pipeline stages updating → see final BUY/SELL/HOLD recommendation with confidence.

### Implementation

- [ ] T027 [P] [US2] Implement analysis service in `backend/app/services/analysis.py` — wrap TradingAgentsGraph: create config from request params, run propagate() as asyncio task, track session state in memory
- [ ] T028 [P] [US2] Implement streaming adapter in `backend/app/services/streaming.py` — convert LangGraph stream chunks to WebSocket event JSON (agent_started, agent_message, agent_completed, debate_round, stats_update, analysis_completed, analysis_failed) per WS contract
- [ ] T029 [US2] Implement analysis router in `backend/app/routers/analysis.py` — POST /api/analysis (create session, start background task, return session_id + ws_url), WebSocket endpoint WS /api/ws/analysis/{session_id} (stream events from adapter)
- [ ] T030 [US2] Add session persistence: on analysis completion, save AnalysisSession + AgentReports to SQLite and Markdown reports to disk in `backend/app/services/analysis.py`
- [ ] T031 [P] [US2] Create ConfigPanel component in `frontend/src/components/analysis/ConfigPanel.tsx` — trade horizon options, analyst team checkboxes, research depth, LLM provider grid, model dropdowns, analysis date picker
- [ ] T032 [P] [US2] Create useWebSocket hook in `frontend/src/hooks/useWebSocket.ts` — connect to WS URL, parse events, handle reconnection, expose typed event stream
- [ ] T033 [P] [US2] Create Zustand analysis store in `frontend/src/stores/analysisStore.ts` — track: pipeline stages, agent messages, stats, reports, recommendation, status
- [ ] T034 [P] [US2] Create PipelineStage component in `frontend/src/components/analysis/PipelineStage.tsx` — icon, name, detail, status (waiting/active/done) with spinner animation
- [ ] T035 [P] [US2] Create MessageLog component in `frontend/src/components/analysis/MessageLog.tsx` — scrollable log of agent messages with timestamps, agent name coloring
- [ ] T036 [P] [US2] Create StatsBar component in `frontend/src/components/analysis/StatsBar.tsx` — agents completed, LLM calls, tools, tokens, reports chips
- [ ] T037 [P] [US2] Create ResultHero component in `frontend/src/components/analysis/ResultHero.tsx` — large BUY/SELL/HOLD text with color, confidence percentage, ticker/market/date label
- [ ] T038 [US2] Create AnalysisProgress component in `frontend/src/components/analysis/AnalysisProgress.tsx` — compose PipelineStage list, StatsBar, MessageLog; consume WebSocket events from store
- [ ] T039 [US2] Wire steps 3-5 into NewAnalysis page: ConfigPanel → POST /api/analysis → AnalysisProgress (WS streaming) → ResultHero (on completion) in `frontend/src/pages/NewAnalysis.tsx`
- [ ] T040 [US2] Implement analysis cancellation: cancel button in AnalysisProgress sends WS `{type:"cancel"}`, backend handles graceful shutdown in `backend/app/services/analysis.py`

**Checkpoint**: Full end-to-end flow works: market → stock → config → live analysis with pipeline stages → BUY/SELL/HOLD result. Core app value delivered.

---

## Phase 5: User Story 3 — View Detailed Analysis Reports (Priority: P2)

**Goal**: User can drill into each agent's report after analysis completes.

**Independent Test**: Complete an analysis → expand each report section (Market, News, Sentiment, Fundamentals, Bull/Bear, Risk, Portfolio) → see full content.

### Implementation

- [ ] T041 [P] [US3] Implement GET /api/analysis/{session_id} in `backend/app/routers/analysis.py` — return full session with all AgentReports loaded from DB + disk
- [ ] T042 [P] [US3] Create ReportSection component in `frontend/src/components/analysis/ReportSection.tsx` — collapsible accordion with header (icon + name), expandable Markdown body
- [ ] T043 [US3] Add report sections list to results view in `frontend/src/pages/NewAnalysis.tsx` step 5 — render ReportSection for each agent report from completed analysis
- [ ] T044 [US3] Implement GET /api/analysis/{session_id}/export in `backend/app/routers/analysis.py` — combine all reports into single Markdown file, return as text/markdown download

**Checkpoint**: After analysis, user can expand/collapse each phase report. Export downloads full report as Markdown.

---

## Phase 6: User Story 4 — Analysis History & Comparison (Priority: P2)

**Goal**: User browses past analyses with filters and compares two analyses side by side.

**Independent Test**: Run 2+ analyses → navigate to History → see chronological list → filter by market → select two and compare side by side.

### Implementation

- [ ] T045 [P] [US4] Implement GET /api/analysis (list) in `backend/app/routers/analysis.py` — query params: market, ticker, recommendation, from_date, to_date, limit, offset; return paginated list with simulation summary
- [ ] T046 [P] [US4] Implement DELETE /api/analysis/{session_id} in `backend/app/routers/analysis.py` — cancel running or delete completed session
- [ ] T047 [P] [US4] Create FilterBar component in `frontend/src/components/history/FilterBar.tsx` — market filter pills, recommendation filter, date range inputs
- [ ] T048 [P] [US4] Create HistoryTable component in `frontend/src/components/history/HistoryTable.tsx` — sortable table with date, ticker, market tag, horizon, recommendation tag, confidence, outcome, view button
- [ ] T049 [US4] Create History page in `frontend/src/pages/History.tsx` — compose FilterBar + HistoryTable, fetch from GET /api/analysis with filter params, handle pagination
- [ ] T050 [US4] Add comparison mode to History page in `frontend/src/pages/History.tsx` — checkbox selection of 2 analyses, compare button, side-by-side modal/view showing reports and recommendation differences

**Checkpoint**: History page shows all past analyses. Filters work. Comparison view shows two analyses side by side.

---

## Phase 7: User Story 5 — Result Simulation & Performance Tracking (Priority: P3)

**Goal**: App simulates past recommendations against actual market data and shows aggregate performance.

**Independent Test**: View a past analysis whose horizon has elapsed → see simulated P&L → navigate to Performance → see win rate, avg return, by-market and by-horizon breakdowns.

### Implementation

- [ ] T051 [P] [US5] Implement simulation service in `backend/app/services/simulation.py` — fetch exit price via yfinance at horizon end date, compute return_pct, determine is_win, persist SimulationResult
- [ ] T052 [US5] Implement POST /api/analysis/{session_id}/simulate in `backend/app/routers/analysis.py` — validate horizon elapsed, call simulation service, return result per REST contract
- [ ] T053 [US5] Implement performance router (GET /api/performance) in `backend/app/routers/performance.py` — aggregate from SimulationResults: total, win_rate, avg_return, by_market, by_horizon
- [ ] T054 [P] [US5] Create PerfCard component in `frontend/src/components/performance/PerfCard.tsx` — large number with label (Total Analyses, Win Rate, Avg Return, Risk/Reward)
- [ ] T055 [P] [US5] Create MarketPerf component in `frontend/src/components/performance/MarketPerf.tsx` — per-market and per-horizon performance bars with win rates
- [ ] T056 [P] [US5] Create SimulationTable component in `frontend/src/components/performance/SimulationTable.tsx` — table of simulated results: stock, market, rec, entry/exit price, return, correct signals
- [ ] T057 [US5] Create Performance page in `frontend/src/pages/Performance.tsx` — compose PerfCard grid + MarketPerf + SimulationTable, fetch from GET /api/performance
- [ ] T058 [US5] Add simulation trigger to analysis detail view — if horizon elapsed and no simulation exists, show "Simulate" button calling POST /api/analysis/{id}/simulate; display result inline

**Checkpoint**: Simulation computes actual vs predicted. Performance dashboard shows aggregate stats. Each analysis can be individually simulated.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements across all stories

- [ ] T059 [P] Add error boundary and loading states to all pages in `frontend/src/App.tsx`
- [ ] T060 [P] Add API key validation check before analysis start — warn user if selected provider key is missing via GET /api/settings
- [ ] T061 [P] Add market-closed banner to analysis flow — detect non-trading hours per market config, show "Market Closed" with last close time
- [ ] T062 Handle WebSocket reconnection in `frontend/src/hooks/useWebSocket.ts` — auto-reconnect on disconnect, replay missed events from server
- [ ] T063 Add responsive styles for tablet/mobile in `frontend/src/styles/globals.css` — hide sidebar on mobile, stack grids
- [ ] T064 Validate quickstart.md — follow setup steps end-to-end, verify both servers start and a full analysis completes
- [ ] T065 Add Egypt-specific display: EGP currency formatting, Arabic company names, Sun-Thu trading week labels throughout frontend components

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 + US1 (needs market/stock selection flow)
- **Phase 5 (US3)**: Depends on US2 (needs completed analysis with reports)
- **Phase 6 (US4)**: Depends on Phase 2 (history endpoints independent of analysis flow)
- **Phase 7 (US5)**: Depends on US4 (needs history data to simulate)
- **Phase 8 (Polish)**: Depends on all desired stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no story dependencies
- **US2 (P1)**: After US1 — needs market/stock selection to exist
- **US3 (P2)**: After US2 — needs completed analysis to display reports
- **US4 (P2)**: After Foundational — can parallelize with US1/US2 (backend-only initially)
- **US5 (P3)**: After US4 — needs history entries to simulate

### Within Each User Story

- Backend models/services before routers
- Routers before frontend components
- Frontend components before page integration
- Page integration before wiring/polish

### Parallel Opportunities

**Phase 2** — T013, T014, T015, T017, T018, T019 can all run in parallel

**US1** — T020 + T021 in parallel (backend), T023 + T024 in parallel (frontend)

**US2** — T027 + T028 in parallel (backend services), T031-T037 all in parallel (7 independent frontend components)

**US4** — T045 + T046 + T047 + T048 all in parallel

**US5** — T054 + T055 + T056 in parallel (frontend components)

---

## Parallel Example: User Story 2

```
# Backend services (parallel):
T027: analysis service in backend/app/services/analysis.py
T028: streaming adapter in backend/app/services/streaming.py

# Frontend components (7 parallel):
T031: ConfigPanel
T032: useWebSocket hook
T033: Zustand store
T034: PipelineStage
T035: MessageLog
T036: StatsBar
T037: ResultHero

# Then sequential integration:
T038: AnalysisProgress (composes T034+T035+T036)
T039: Wire into NewAnalysis page
T040: Cancellation support
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup (~7 tasks)
2. Complete Phase 2: Foundational (~12 tasks)
3. Complete Phase 3: US1 — Market & Stock Selection (~7 tasks)
4. Complete Phase 4: US2 — Configure & Run Analysis (~14 tasks)
5. **STOP and VALIDATE**: Full analysis flow works end-to-end
6. This is a usable product: select market → pick stock → configure → analyze → see recommendation

### Incremental Delivery

1. Setup + Foundational → Shell running
2. + US1 → Market selection + stock validation working
3. + US2 → Full analysis pipeline streaming in browser (MVP!)
4. + US3 → Drill into detailed reports
5. + US4 → Browse and compare past analyses
6. + US5 → Simulation and performance tracking
7. Polish → Error handling, responsive, Egypt-specific formatting

---

## Notes

- No tests generated (not explicitly requested in spec). Add test phases if TDD desired.
- Backend imports `TradingAgentsGraph` from existing `tradingagents` package — zero changes to existing code.
- WebSocket streaming is the most complex task (T027-T029). Start here early.
- Frontend components are highly parallelizable — 7 components in US2 alone can be built simultaneously.
