# Quickstart: Candlestick Chart & Analysis State Persistence

## Prerequisites

- Backend running: `cd backend && uvicorn app.main:app --reload`
- Frontend running: `cd frontend && npm run dev`
- lightweight-charts installed: `cd frontend && npm install lightweight-charts`

## Verify Candlestick Chart (User Story 1)

1. Open the app at http://localhost:5173
2. Select a market (US or Egypt)
3. Enter a valid ticker (e.g., AAPL for US, COMI for Egypt)
4. After validation, a candlestick chart should appear below the stock
   info card showing ~3 months of daily price history
5. Hover over candles — tooltip shows date, O/H/L/C, volume
6. Click time range buttons (1W, 1M, 3M, 6M, 1Y) — chart updates
7. Verify currency label matches market (USD for US, EGP for Egypt)

## Verify State Persistence (User Story 2)

1. Open the app and select a market + ticker (reach Step 2)
2. Click "History" in the sidebar
3. Click "New Analysis" in the sidebar to return
4. **Expected**: You return to Step 2 with market, ticker, and config
   preserved — not reset to Step 0

5. Start an analysis (reach Step 3 with live agent progress)
6. Navigate to "Portfolio" tab
7. Return to "New Analysis"
8. **Expected**: Analysis is still running (or completed) with all
   agent messages visible

9. Click "New Analysis" button explicitly
10. **Expected**: State clears, wizard resets to Step 0

## Verify API Endpoint

```bash
# Fetch 3-month daily OHLC for AAPL
curl "http://localhost:8000/api/stocks/price-history?ticker=AAPL&market_id=us&period=3mo"

# Fetch 1-week intraday for COMI (Egypt)
curl "http://localhost:8000/api/stocks/price-history?ticker=COMI&market_id=egypt&period=1w"

# Invalid ticker — expect 404
curl "http://localhost:8000/api/stocks/price-history?ticker=ZZZZZ&market_id=us"
```
