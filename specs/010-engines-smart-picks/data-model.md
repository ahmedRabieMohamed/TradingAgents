# Data Model: 010 — 7 Trading Engines + Smart Picks + Danger Alerts

**Date**: 2026-04-25

## Entity Changes

### Modified: AnalysisSession

Add `engine_scores` field to store computed engine results.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `engine_scores` | JSON (nullable) | `NULL` | JSON object containing all 7 engine scores + combined score. NULL for sessions created before this feature. |

**JSON structure of `engine_scores`**:
```json
{
  "computed_at": "2026-04-25T10:30:00Z",
  "combined_score": 78,
  "combined_signal": "BUY",
  "engines": {
    "monte_carlo": {
      "score": 71,
      "verdict": "BULLISH",
      "prob_up": 63.2,
      "expected_change": 1.8,
      "best_case": 6.2,
      "worst_case": -4.8
    },
    "momentum": {
      "score": 87,
      "verdict": "BULLISH",
      "roc_5d": 4.2,
      "roc_20d": 8.7,
      "trend_strength": 90
    },
    "volume": {
      "score": 82,
      "verdict": "BULLISH",
      "volume_ratio": 3.2,
      "is_real_move": true
    },
    "support_resistance": {
      "score": 75,
      "verdict": "BULLISH",
      "support": 18.50,
      "resistance": 21.00,
      "current": 19.42,
      "risk_reward": 1.7
    },
    "mean_reversion": {
      "score": 60,
      "verdict": "NEUTRAL",
      "distance_from_sma50_pct": 3.2,
      "is_oversold": false
    },
    "bollinger": {
      "score": 78,
      "verdict": "BULLISH",
      "band_width": "expanding",
      "position": "upper"
    },
    "correlation": {
      "score": 72,
      "verdict": "BULLISH",
      "sector": "Telecom",
      "peers_bullish": 3,
      "peers_total": 4
    }
  },
  "news_sentiment": {
    "score": 65,
    "article_count": 5,
    "avg_sentiment": 42
  }
}
```

**Migration**: Add nullable JSON column — all existing sessions get NULL (no engine scores).

### New: SmartPick (Transient — NOT stored in DB)

Smart picks are computed on-the-fly and cached in memory. No database table.

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | string | Stock ticker |
| `company_name` | string | Company name (en/ar) |
| `market_id` | string | Market identifier |
| `combined_score` | int (0-100) | Weighted score from all engines |
| `signal` | string | BUY / HOLD / SELL / AVOID |
| `mc_probability` | float | Monte Carlo probability up % |
| `news_sentiment` | int (-100 to +100) | Average news sentiment |
| `news_count` | int | Number of articles today |
| `technical_verdict` | string | Bullish / Neutral / Bearish |
| `engines` | dict | Individual engine scores |

Cache duration: 1 hour. Recomputed on demand.

### New: DangerAlert (Transient — computed per request)

| Field | Type | Description |
|-------|------|-------------|
| `position_id` | string | Portfolio position ID |
| `ticker` | string | Stock ticker |
| `alert_level` | string | red / yellow / green |
| `combined_score` | int (0-100) | Current engine score |
| `primary_reason` | string | Main reason for alert level |
| `engines` | dict | Full engine breakdown |

## Relationships

```
AnalysisSession
  └── engine_scores: JSON  ← computed when analysis runs or on-demand
                              persisted for historical viewing

Smart Picks (memory cache)
  ├── sourced from: news mentions + EGX top movers
  ├── scored by: 7 engines + news sentiment
  └── ranked by: combined_score descending

Danger Alerts (computed per request)
  ├── sourced from: open Portfolio positions
  ├── scored by: 7 engines on each position's ticker
  └── classified by: score thresholds (< 35 red, 35-55 yellow, > 55 green)
```
