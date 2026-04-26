# Quickstart: Market Overview & Hot News

**Feature**: 002-market-overview-news  
**Depends on**: 001-trading-web-app (backend + frontend must be running)

## What's New

This feature adds a Market Overview dashboard between market selection and stock input:
- Stock list with live prices for ~50 US / ~30 EGX stocks
- Top Gainers / Top Losers grids
- Market indices (S&P 500, NASDAQ, Dow / EGX 30)
- Hot news feed with market-specific articles
- Ticker-specific news drill-down
- Search/filter stocks by name or ticker

## New Files

### Backend
- `backend/app/data/watchlists.py` — Curated stock lists per market
- `backend/app/services/market_data.py` — Batch price fetching + caching
- `backend/app/services/news.py` — News fetching via existing dataflows
- `backend/app/routers/market_overview.py` — 2 new endpoints

### Frontend
- `frontend/src/components/market-overview/` — 7 new components
- `frontend/src/hooks/useMarketOverview.ts` — Data fetching hook

## Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Select US or Egypt market
5. Verify: stock list loads with prices, gainers/losers grids appear, news section shows articles
6. Click a stock → should navigate to analysis config with ticker pre-filled
7. Search for a stock by name → list filters
8. Click news article → opens in new tab
