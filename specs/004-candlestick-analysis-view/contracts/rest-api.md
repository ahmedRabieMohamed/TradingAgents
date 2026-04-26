# REST API Contract: Price History

**Feature**: 004-candlestick-analysis-view

## Endpoints

### GET /api/stocks/price-history

Fetch OHLC candlestick data for a validated ticker.

**Query Parameters**:

| Parameter  | Type   | Required | Default | Validation                          |
|------------|--------|----------|---------|-------------------------------------|
| ticker     | string | yes      | —       | 1-10 alphanumeric chars             |
| market_id  | string | yes      | —       | "us" or "egypt"                     |
| period     | string | no       | "3mo"   | One of: 1w, 1mo, 3mo, 6mo, 1y      |

**Response 200**:

```json
{
  "ticker": "AAPL",
  "market_id": "us",
  "currency": "USD",
  "period": "3mo",
  "interval": "1d",
  "bars": [
    {
      "timestamp": "2026-01-07T00:00:00",
      "open": 185.50,
      "high": 187.20,
      "low": 184.80,
      "close": 186.90,
      "volume": 45230100
    }
  ]
}
```

**Response 404** (invalid ticker):

```json
{
  "detail": "Ticker INVALID not found in us market"
}
```

**Response 400** (invalid period):

```json
{
  "detail": "Invalid period. Must be one of: 1w, 1mo, 3mo, 6mo, 1y"
}
```

**Response 500** (data provider error):

```json
{
  "detail": "Unable to fetch price history. Please try again."
}
```

**Notes**:
- Interval is derived from period (1w → 15m, everything else → 1d)
- Egypt tickers get `.CA` suffix appended automatically (existing pattern)
- Bars are ordered chronologically (oldest first)
- Empty bars array with 200 status if ticker is valid but no data available
  for the requested period
