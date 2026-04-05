# REST API Contract: Trading Web Application

**Version**: 1.0  
**Base URL**: `/api`

---

## Markets

### GET /api/markets

Returns available markets with their configuration.

**Response** `200 OK`:
```json
{
  "markets": [
    {
      "id": "us",
      "name": "US Market",
      "exchange": "NYSE/NASDAQ",
      "currency": "USD",
      "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "example_tickers": ["AAPL", "NVDA", "TSLA", "MSFT", "SPY"]
    },
    {
      "id": "egypt",
      "name": "Egypt Market",
      "exchange": "EGX",
      "currency": "EGP",
      "trading_days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
      "example_tickers": ["COMI", "HRHO", "TMGH", "EFIH", "SWDY"]
    }
  ]
}
```

---

## Stocks

### GET /api/stocks/validate?ticker={ticker}&market={market_id}

Validates a ticker symbol and returns stock info.

**Query Parameters**:
- `ticker` (required): Stock symbol (e.g., "AAPL")
- `market` (required): Market ID ("us" or "egypt")

**Response** `200 OK`:
```json
{
  "valid": true,
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "price": 205.40,
  "currency": "USD",
  "change_pct": 1.2,
  "market_id": "us"
}
```

**Response** `404 Not Found`:
```json
{
  "valid": false,
  "error": "Ticker 'XYZ' not found in US market"
}
```

---

## Analysis

### POST /api/analysis

Creates and starts a new analysis session.

**Request Body**:
```json
{
  "ticker": "AAPL",
  "market_id": "us",
  "analysis_date": "2026-04-04",
  "trade_horizon": "short-term",
  "analysts": ["market", "social", "news", "fundamentals"],
  "research_depth": "medium",
  "llm_provider": "openai",
  "quick_think_model": "gpt-5-mini",
  "deep_think_model": "gpt-5.2"
}
```

**Response** `201 Created`:
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "running",
  "websocket_url": "/api/ws/analysis/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Validation Errors** `422 Unprocessable Entity`:
```json
{
  "detail": [
    { "field": "analysts", "error": "At least one analyst must be selected" }
  ]
}
```

### GET /api/analysis/{session_id}

Returns the full analysis session with reports.

**Response** `200 OK`:
```json
{
  "id": "a1b2c3d4-...",
  "ticker": "AAPL",
  "market_id": "us",
  "stock_name": "Apple Inc.",
  "analysis_date": "2026-04-04",
  "created_at": "2026-04-04T10:30:00Z",
  "completed_at": "2026-04-04T10:35:42Z",
  "status": "completed",
  "trade_horizon": "short-term",
  "research_depth": "medium",
  "analysts": ["market", "social", "news", "fundamentals"],
  "llm_provider": "openai",
  "recommendation": "BUY",
  "confidence": 0.85,
  "reports": [
    {
      "agent_name": "market_analyst",
      "phase": "analyst",
      "content": "## Market Analysis\n\nSMA(20) shows bullish crossover...",
      "sequence": 1
    }
  ],
  "simulation": null
}
```

### GET /api/analysis

Lists analysis history with filtering.

**Query Parameters**:
- `market` (optional): Filter by market ID
- `ticker` (optional): Filter by ticker
- `recommendation` (optional): Filter by "BUY", "SELL", "HOLD"
- `from_date` (optional): Start date filter
- `to_date` (optional): End date filter
- `limit` (optional, default 50): Max results
- `offset` (optional, default 0): Pagination offset

**Response** `200 OK`:
```json
{
  "total": 24,
  "items": [
    {
      "id": "a1b2c3d4-...",
      "ticker": "AAPL",
      "market_id": "us",
      "stock_name": "Apple Inc.",
      "analysis_date": "2026-04-04",
      "status": "completed",
      "trade_horizon": "short-term",
      "recommendation": "BUY",
      "confidence": 0.85,
      "simulation": { "return_pct": 4.2, "is_win": true }
    }
  ]
}
```

### DELETE /api/analysis/{session_id}

Cancels a running analysis or deletes a completed one.

**Response** `204 No Content`

---

## Analysis Export

### GET /api/analysis/{session_id}/export

Exports the full analysis report as a single Markdown file.

**Response** `200 OK` (Content-Type: text/markdown):
```
# Analysis Report: AAPL - 2026-04-04
...
```

---

## Simulation

### POST /api/analysis/{session_id}/simulate

Triggers simulation for a completed analysis whose trade horizon has elapsed.

**Response** `200 OK`:
```json
{
  "session_id": "a1b2c3d4-...",
  "entry_price": 205.40,
  "exit_price": 214.02,
  "horizon_end_date": "2026-04-09",
  "return_pct": 4.2,
  "is_win": true,
  "simulated_at": "2026-04-10T08:00:00Z"
}
```

**Response** `400 Bad Request`:
```json
{
  "error": "Trade horizon has not elapsed yet. Ends on 2026-04-09."
}
```

---

## Performance

### GET /api/performance

Returns aggregate performance statistics.

**Query Parameters**:
- `market` (optional): Filter by market ID

**Response** `200 OK`:
```json
{
  "total_analyses": 24,
  "simulated_count": 18,
  "win_rate": 0.71,
  "avg_return_pct": 3.8,
  "by_market": {
    "us": { "count": 14, "win_rate": 0.68, "avg_return_pct": 3.2 },
    "egypt": { "count": 10, "win_rate": 0.75, "avg_return_pct": 4.6 }
  },
  "by_horizon": {
    "intraday": { "count": 4, "win_rate": 0.58 },
    "short-term": { "count": 10, "win_rate": 0.73 },
    "medium-term": { "count": 5, "win_rate": 0.78 },
    "long-term": { "count": 5, "win_rate": 0.80 }
  }
}
```

---

## Settings

### GET /api/settings

Returns all user settings.

**Response** `200 OK`:
```json
{
  "default_market": "us",
  "default_horizon": "short-term",
  "default_depth": "medium",
  "default_llm_provider": "openai",
  "api_keys": {
    "openai": true,
    "anthropic": false,
    "google": false,
    "xai": false,
    "serper": false
  }
}
```

**Note**: API key values are never returned — only whether they are configured (boolean).

### PATCH /api/settings

Updates user settings.

**Request Body**:
```json
{
  "default_market": "egypt",
  "api_keys": {
    "openai": "sk-proj-..."
  }
}
```

**Response** `200 OK`: Same as GET /api/settings

---

## LLM Providers

### GET /api/llm-providers

Returns available LLM providers and their models.

**Response** `200 OK`:
```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "configured": true,
      "quick_models": ["gpt-5-mini", "gpt-5-nano", "gpt-5.4", "gpt-4.1"],
      "deep_models": ["gpt-5.2", "gpt-5.4", "gpt-5-mini", "gpt-5.4-pro"]
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "configured": false,
      "quick_models": ["claude-sonnet-4-6", "claude-haiku-4-5"],
      "deep_models": ["claude-opus-4-6", "claude-sonnet-4-6"]
    }
  ]
}
```
