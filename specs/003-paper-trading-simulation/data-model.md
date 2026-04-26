# Data Model: Paper Trading & Portfolio Simulation

**Feature**: 003-paper-trading-simulation  
**Date**: 2026-04-05

## New Entities (SQLite tables)

### Portfolio

The user's virtual trading account.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key |
| starting_balance | float | Default 100,000. Configurable. |
| cash_balance | float | Current available cash |
| currency | string | Display currency ("USD") |
| created_at | datetime | When portfolio was created |
| reset_at | datetime | Nullable — last reset timestamp |

**Notes**: Single row per user. Created on first trade or app init.

---

### Position

An open or closed virtual trade.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key |
| portfolio_id | string | FK → Portfolio.id |
| analysis_session_id | string | FK → AnalysisSession.id (nullable for manual trades) |
| ticker | string | Stock symbol |
| market_id | string | "us" or "egypt" |
| direction | enum | "long" or "short" |
| quantity | integer | Number of shares |
| entry_price | float | Price at trade execution |
| entry_date | datetime | When position was opened |
| exit_price | float | Nullable — price at close |
| exit_date | datetime | Nullable — when position was closed |
| status | enum | "open" or "closed" |
| realized_pnl | float | Nullable — set when closed |
| realized_pnl_pct | float | Nullable — percentage return |

**Relationships**: Belongs to Portfolio. Optionally linked to AnalysisSession.

**State Transitions**:
```
open → closed (on position close)
```

---

### EquitySnapshot

Daily snapshot of portfolio value for the equity curve.

| Field | Type | Constraints |
|-------|------|------------|
| id | string (UUID) | Primary key |
| portfolio_id | string | FK → Portfolio.id |
| date | date | Snapshot date (unique per portfolio) |
| total_value | float | Portfolio value at snapshot time |
| cash_balance | float | Cash at snapshot time |
| positions_value | float | Sum of open positions value |

**Notes**: One row per day per portfolio. Created on each trade event and once daily.

---

## Modified Entities

### AnalysisSession (existing)

No schema changes. Positions reference AnalysisSession via `analysis_session_id` FK.

## Relationships

```
Portfolio (1) ←——— (many) Position
Portfolio (1) ←——— (many) EquitySnapshot
AnalysisSession (1) ←——— (0..many) Position
```

## Validation Rules

- **Position.quantity**: Must be positive integer
- **Position.entry_price**: Must be positive
- **Portfolio.cash_balance**: Cannot go negative (trade rejected if insufficient)
- **Position.direction**: "long" for BUY recommendations, "short" for SELL recommendations
- **Position close**: Only open positions can be closed
