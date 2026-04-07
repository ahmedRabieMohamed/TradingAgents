# Data Model: Candlestick Chart & Analysis State Persistence

**Feature**: 004-candlestick-analysis-view
**Date**: 2026-04-07

## Entities

### OHLCBar

Represents a single price bar (candlestick) for a ticker.

| Field     | Type     | Constraints              | Description                    |
|-----------|----------|--------------------------|--------------------------------|
| timestamp | string   | ISO 8601 datetime        | Bar open time                  |
| open      | float    | > 0                      | Opening price                  |
| high      | float    | >= open, >= close        | Highest price in period        |
| low       | float    | <= open, <= close, > 0   | Lowest price in period         |
| close     | float    | > 0                      | Closing price                  |
| volume    | integer  | >= 0                     | Number of shares traded        |

**Notes**: Not persisted in the database. Fetched on-demand from yfinance
and returned via the API. No caching in MVP (yfinance has its own internal
cache for short periods).

### PriceHistoryResponse

API response envelope for OHLC data.

| Field     | Type          | Description                          |
|-----------|---------------|--------------------------------------|
| ticker    | string        | Ticker symbol as requested           |
| market_id | string       | "us" or "egypt"                      |
| currency  | string        | "USD" or "EGP"                       |
| period    | string        | Requested period (1w, 1mo, 3mo, etc) |
| interval  | string        | Candle interval (15m, 1d)            |
| bars      | list[OHLCBar] | Ordered chronologically              |

### WizardState (Frontend Zustand Store)

In-memory state for the analysis wizard. Not persisted to backend or
storage — lives only in Zustand for the browser session lifetime.

| Field           | Type                  | Default  | Description                      |
|-----------------|-----------------------|----------|----------------------------------|
| step            | number (0-4)          | 0        | Current wizard step              |
| selectedMarket  | string or null        | null     | "us" or "egypt"                  |
| selectedStock   | StockValidation/null  | null     | Validated stock info             |
| tradeHorizon    | TradeHorizon          | "short-term" | Analysis time horizon        |
| analysisDate    | string                | ""       | Selected analysis date           |
| showCustomTicker| boolean               | false    | Toggle custom ticker input       |
| wsUrl           | string or null        | null     | WebSocket URL for active session |

**State transitions**:
- Step 0 → 1: Market selected → sets `selectedMarket`
- Step 1 → 2: Stock validated → sets `selectedStock`
- Step 2 → 3: Analysis started → sets `wsUrl`, `analysisDate`
- Step 3 → 4: Analysis completed → read from analysisStore
- Reset: Explicit "New Analysis" → clears all fields to defaults

## Relationships

```text
WizardState                    AnalysisStore (existing)
┌──────────────┐              ┌─────────────────┐
│ step         │              │ sessionId        │
│ selectedMarket│             │ status           │
│ selectedStock │             │ stages[]         │
│ tradeHorizon │              │ messages[]       │
│ analysisDate │              │ reports{}        │
│ wsUrl ───────┼──references──│ recommendation   │
│              │              │ confidence       │
└──────────────┘              └─────────────────┘

PriceHistoryResponse (API)
┌──────────────┐
│ ticker       │
│ market_id    │
│ bars[] ──────┼── OHLCBar[]
│ currency     │
│ period       │
└──────────────┘
```

No database schema changes required. All new data is either API-only
(OHLC) or frontend-only (wizard state).
