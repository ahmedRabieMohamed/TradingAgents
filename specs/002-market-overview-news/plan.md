# Implementation Plan: Market Overview & Hot News

**Branch**: `002-market-overview-news` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-market-overview-news/spec.md`

## Summary

Add a market overview dashboard that appears after market selection, showing a curated stock list with live prices, top gainers/losers grids, market index performance, summary analytics, and a hot news feed. This is an enhancement to the existing Trading Web Application (001-trading-web-app) — new backend endpoints and frontend components added to the existing `backend/` and `frontend/` directories.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, yfinance (backend); React 18, Zustand (frontend) — all already installed from 001  
**Storage**: In-memory caching for stock prices (refreshed on demand); existing news infrastructure reused  
**Testing**: pytest (backend), Vitest (frontend) — from 001  
**Target Platform**: Desktop/laptop browsers; server runs locally  
**Project Type**: Web application enhancement (adds endpoints + components to existing app)  
**Performance Goals**: Market overview loads within 5 seconds for 50 stocks; news section loads within 3 seconds  
**Constraints**: Must not modify existing `tradingagents/` package; yfinance cannot enumerate exchange listings (curated watchlists); 15-minute data delay acceptable  
**Scale/Scope**: 2 markets, ~50 US stocks + ~30 EGX stocks, 3 new API endpoints, 1 new page section with tabs

## Constitution Check

Constitution file contains only placeholder templates — no gates defined. **PASS**.

**Post-Phase 1 Re-Check**: Still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/002-market-overview-news/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Data structures
├── quickstart.md        # Phase 1: Setup additions
└── contracts/
    └── rest-api.md      # New endpoints
```

### Source Code (additions to existing 001 structure)

```text
backend/
├── app/
│   ├── routers/
│   │   └── market_overview.py   # NEW: GET /market-overview/{market_id}, GET /market-overview/{market_id}/news
│   ├── services/
│   │   ├── market_data.py       # NEW: Fetch batch stock prices, compute gainers/losers, index data
│   │   └── news.py              # NEW: Fetch market/ticker news via existing tradingagents dataflows
│   └── data/
│       └── watchlists.py        # NEW: Curated US + EGX stock watchlists
└── ...

frontend/
├── src/
│   ├── pages/
│   │   └── NewAnalysis.tsx      # MODIFIED: Add market overview step between market selection and stock input
│   ├── components/
│   │   └── market-overview/     # NEW directory
│   │       ├── MarketOverview.tsx    # Container with tabs
│   │       ├── IndexBar.tsx         # Market indices display
│   │       ├── MarketSummary.tsx    # Gainers/losers/breadth stats
│   │       ├── StockTable.tsx       # Full stock list with search
│   │       ├── MoverGrid.tsx        # Top gainers/losers side-by-side
│   │       ├── NewsSection.tsx      # Hot news feed
│   │       └── TickerNews.tsx       # Single-stock news panel
│   ├── hooks/
│   │   └── useMarketOverview.ts # NEW: Fetch + cache market overview data
│   └── types/
│       └── index.ts             # MODIFIED: Add market overview types
└── ...
```

**Structure Decision**: Enhancement to existing 001 web app. New files only — no structural changes. Backend adds 1 new router + 2 services + 1 data file. Frontend adds 1 new component directory with 7 components + 1 hook.

## Complexity Tracking

No constitution violations — table not needed.
