# REST API Contract: Market Overview & Hot News

**Version**: 1.0  
**Base URL**: `/api`

---

## Market Overview

### GET /api/market-overview/{market_id}

Returns complete market overview with stock prices, indices, movers, and summary.

**Path Parameters**:
- `market_id` (required): "us" or "egypt"

**Response** `200 OK`:
```json
{
  "market_id": "us",
  "market_status": "closed",
  "last_updated": "2026-04-05T16:00:00Z",
  "indices": [
    {
      "name": "S&P 500",
      "symbol": "^GSPC",
      "value": 5284.30,
      "change": 18.42,
      "change_pct": 0.35
    }
  ],
  "summary": {
    "total_stocks": 50,
    "gainers_count": 32,
    "losers_count": 15,
    "unchanged_count": 3,
    "breadth_pct": 64.0
  },
  "stocks": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "name_ar": null,
      "sector": "Technology",
      "price": 205.40,
      "currency": "USD",
      "change": 2.43,
      "change_pct": 1.20
    }
  ],
  "gainers": [ /* top 7 StockSnapshot sorted by change_pct desc */ ],
  "losers": [ /* top 7 StockSnapshot sorted by change_pct asc */ ]
}
```

**Response** `404 Not Found`:
```json
{ "detail": "Market 'xyz' not found" }
```

---

## Market News

### GET /api/market-overview/{market_id}/news

Returns market-level news articles.

**Path Parameters**:
- `market_id` (required): "us" or "egypt"

**Query Parameters**:
- `limit` (optional, default 15): Max articles to return
- `ticker` (optional): If provided, returns news for this specific ticker instead of market-wide news

**Response** `200 OK`:
```json
{
  "market_id": "us",
  "ticker": null,
  "articles": [
    {
      "title": "Federal Reserve Signals Steady Rates Through Q2",
      "snippet": "Fed Chair indicated no immediate plans for rate adjustments...",
      "source": "Reuters",
      "url": "https://...",
      "published_at": "2026-04-05T14:30:00Z",
      "is_hot": true
    }
  ]
}
```
