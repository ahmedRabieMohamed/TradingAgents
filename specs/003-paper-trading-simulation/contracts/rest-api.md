# REST API Contract: Paper Trading & Portfolio

**Version**: 1.0  
**Base URL**: `/api`

---

## Portfolio

### GET /api/portfolio

Returns the user's portfolio summary with open positions.

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "starting_balance": 100000.00,
  "cash_balance": 78500.00,
  "currency": "USD",
  "total_value": 105230.50,
  "total_pnl": 5230.50,
  "total_pnl_pct": 5.23,
  "open_positions_count": 3,
  "open_positions": [
    {
      "id": "uuid",
      "ticker": "AAPL",
      "market_id": "us",
      "direction": "long",
      "quantity": 50,
      "entry_price": 205.40,
      "entry_date": "2026-04-05T10:30:00Z",
      "current_price": 210.20,
      "unrealized_pnl": 240.00,
      "unrealized_pnl_pct": 2.34,
      "days_held": 3,
      "analysis_session_id": "uuid",
      "recommendation": "BUY",
      "confidence": 85
    }
  ]
}
```

### POST /api/portfolio/reset

Resets the portfolio — closes all positions, clears history, resets to starting balance.

**Response** `200 OK`:
```json
{
  "message": "Portfolio reset to $100,000.00",
  "starting_balance": 100000.00
}
```

---

## Trades

### POST /api/portfolio/trade

Executes a virtual trade (open a new position).

**Request Body**:
```json
{
  "ticker": "AAPL",
  "market_id": "us",
  "direction": "long",
  "quantity": 50,
  "analysis_session_id": "uuid"
}
```

**Response** `201 Created`:
```json
{
  "position_id": "uuid",
  "ticker": "AAPL",
  "direction": "long",
  "quantity": 50,
  "entry_price": 205.40,
  "total_cost": 10270.00,
  "remaining_cash": 68230.00
}
```

**Response** `400 Bad Request`:
```json
{ "error": "Insufficient cash. Required: $10,270.00, Available: $5,000.00" }
```

### POST /api/portfolio/positions/{position_id}/close

Closes an open position at current market price.

**Response** `200 OK`:
```json
{
  "position_id": "uuid",
  "ticker": "AAPL",
  "direction": "long",
  "entry_price": 205.40,
  "exit_price": 210.20,
  "quantity": 50,
  "realized_pnl": 240.00,
  "realized_pnl_pct": 2.34,
  "hold_days": 3,
  "cash_balance": 78740.00
}
```

---

## Trade History

### GET /api/portfolio/trades

Returns closed trades history.

**Query Parameters**:
- `market` (optional): Filter by market
- `limit` (optional, default 50)
- `offset` (optional, default 0)

**Response** `200 OK`:
```json
{
  "total": 15,
  "trades": [
    {
      "id": "uuid",
      "ticker": "AAPL",
      "market_id": "us",
      "direction": "long",
      "quantity": 50,
      "entry_price": 205.40,
      "exit_price": 210.20,
      "entry_date": "2026-04-02T10:30:00Z",
      "exit_date": "2026-04-05T14:00:00Z",
      "realized_pnl": 240.00,
      "realized_pnl_pct": 2.34,
      "hold_days": 3,
      "recommendation": "BUY",
      "confidence": 85
    }
  ]
}
```

---

## Analytics

### GET /api/portfolio/analytics

Returns portfolio performance analytics.

**Response** `200 OK`:
```json
{
  "total_trades": 15,
  "win_rate": 0.73,
  "avg_return_pct": 2.8,
  "total_realized_pnl": 4250.00,
  "best_trade": { "ticker": "NVDA", "pnl": 1200.00, "pnl_pct": 8.5 },
  "worst_trade": { "ticker": "TSLA", "pnl": -450.00, "pnl_pct": -3.2 },
  "by_market": {
    "us": { "count": 10, "win_rate": 0.70, "avg_return_pct": 2.5 },
    "egypt": { "count": 5, "win_rate": 0.80, "avg_return_pct": 3.4 }
  },
  "equity_curve": [
    { "date": "2026-03-20", "value": 100000.00 },
    { "date": "2026-03-25", "value": 101200.00 },
    { "date": "2026-04-01", "value": 103500.00 },
    { "date": "2026-04-05", "value": 105230.50 }
  ]
}
```

### GET /api/portfolio/ai-comparison

Returns "Followed AI vs Ignored AI" comparison.

**Response** `200 OK`:
```json
{
  "followed": {
    "count": 10,
    "avg_return_pct": 3.2,
    "win_rate": 0.80,
    "total_pnl": 4250.00
  },
  "ignored": {
    "count": 8,
    "avg_simulated_return_pct": 1.5,
    "simulated_win_rate": 0.50,
    "simulated_total_pnl": 1800.00
  },
  "difference": {
    "return_advantage_pct": 1.7,
    "win_rate_advantage": 0.30,
    "message": "Following AI recommendations earned 1.7% more per trade on average"
  }
}
```
