# API Contracts: 010 — 7 Trading Engines + Smart Picks + Danger Alerts

**Date**: 2026-04-25

## New Endpoints

### GET /api/engines/score/{ticker}

Compute all 7 engine scores for a single stock.

**Path parameters**: `ticker` (string) — stock ticker (e.g., "ETEL")

**Query parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `market_id` | string | Yes | — | Market identifier ("egypt", "us") |
| `days` | int | No | 7 | Monte Carlo simulation horizon |

**Response** (200):
```json
{
  "ticker": "ETEL",
  "market_id": "egypt",
  "computed_at": "2026-04-25T10:30:00Z",
  "combined_score": 78,
  "combined_signal": "BUY",
  "engines": {
    "monte_carlo": { "score": 71, "verdict": "BULLISH", "prob_up": 63.2, "expected_change": 1.8, "best_case": 6.2, "worst_case": -4.8 },
    "momentum": { "score": 87, "verdict": "BULLISH", "roc_5d": 4.2, "roc_20d": 8.7, "trend_strength": 90 },
    "volume": { "score": 82, "verdict": "BULLISH", "volume_ratio": 3.2, "is_real_move": true },
    "support_resistance": { "score": 75, "verdict": "BULLISH", "support": 18.50, "resistance": 21.00, "risk_reward": 1.7 },
    "mean_reversion": { "score": 60, "verdict": "NEUTRAL", "distance_pct": 3.2, "is_oversold": false },
    "bollinger": { "score": 78, "verdict": "BULLISH", "band_width": "expanding", "position": "upper" },
    "correlation": { "score": 72, "verdict": "BULLISH", "sector": "Telecom", "peers_bullish": 3, "peers_total": 4 }
  },
  "news_sentiment": { "score": 65, "article_count": 5, "avg_sentiment": 42 }
}
```

**Error responses**: 400 (invalid ticker), 404 (no price data), 500 (engine failure)

---

### GET /api/engines/smart-picks

Get today's ranked stock opportunities.

**Query parameters**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `market_id` | string | No | "egypt" | Market to scan |
| `limit` | int | No | 10 | Max results |

**Response** (200):
```json
{
  "market_id": "egypt",
  "computed_at": "2026-04-25T10:30:00Z",
  "cache_expires_at": "2026-04-25T11:30:00Z",
  "picks": [
    {
      "rank": 1,
      "ticker": "COMI",
      "company_name": "Commercial International Bank",
      "combined_score": 82,
      "signal": "STRONG BUY",
      "mc_probability": 71.0,
      "news_sentiment": 82,
      "news_count": 8,
      "technical_verdict": "BULLISH",
      "primary_catalyst": "Q1 profit jump +28%",
      "current_price": 129.40,
      "change_pct": 1.15
    }
  ]
}
```

---

### GET /api/engines/danger-alerts

Get danger alerts for all open portfolio positions.

**Response** (200):
```json
{
  "computed_at": "2026-04-25T10:30:00Z",
  "alerts": [
    {
      "position_id": "abc-123",
      "ticker": "EAST",
      "alert_level": "red",
      "combined_score": 28,
      "primary_reason": "Broke below 50-day support, volume spike 4x selling",
      "engines": { ... }
    },
    {
      "position_id": "def-456",
      "ticker": "COMI",
      "alert_level": "green",
      "combined_score": 82,
      "primary_reason": "All signals positive, above moving averages",
      "engines": { ... }
    }
  ]
}
```

## Modified Endpoints

### GET /api/analysis/{session_id}

**Change**: Response now includes `engine_scores` field (nullable JSON).

```json
{
  "id": "...",
  "ticker": "ETEL",
  "engine_scores": { ... },
  "reports": [ ... ]
}
```

Backward-compatible: old sessions return `engine_scores: null`.
