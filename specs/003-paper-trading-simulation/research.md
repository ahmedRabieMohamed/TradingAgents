# Research: Paper Trading & Portfolio Simulation

**Feature**: 003-paper-trading-simulation  
**Date**: 2026-04-05

## Decision 1: Portfolio Data Model

**Decision**: New SQLite tables — Portfolio, Position, Trade — linked to existing AnalysisSession

**Rationale**:
- Portfolio needs persistence across sessions (unlike analysis streaming which is ephemeral)
- Positions and trades have clear relational structure: Portfolio → Positions → Trades
- SQLAlchemy ORM already in use for AnalysisSession — extend the same pattern
- Foreign key from Position to AnalysisSession enables "see the analysis that triggered this trade"

**Alternatives Considered**:
- JSON file storage: No querying, no aggregation for analytics
- In-memory only: Lost on server restart

## Decision 2: P&L Calculation Strategy

**Decision**: Compute unrealized P&L on-the-fly from current yfinance prices; store realized P&L on close

**Rationale**:
- Unrealized P&L changes constantly — storing it would require constant updates
- Current prices already available via the market_data service (with 5-min cache)
- Realized P&L is fixed at close time — store it for fast aggregation
- Equity curve snapshots stored daily (or on each trade event) for the chart

**Alternatives Considered**:
- Real-time price streaming: yfinance doesn't support it; 15-min delay is acceptable for paper trading
- Pre-compute all P&L on a schedule: Adds complexity with no benefit for single-user app

## Decision 3: Equity Curve Chart Library

**Decision**: Recharts (React charting library)

**Rationale**:
- Lightweight, React-native, good for line/area charts
- No external dependencies or CDN — installs via npm
- Simple API for the equity curve (date on X axis, portfolio value on Y)
- Already used widely in financial dashboards

**Alternatives Considered**:
- Chart.js: More complex setup with React wrapper needed
- D3.js: Overkill for a single line chart
- No chart (table only): Equity curve is best visualized as a chart, not numbers

## Decision 4: Short Selling Implementation

**Decision**: Allow SELL positions (short) — profit when price drops

**Rationale**:
- When AI recommends SELL, the user should be able to act on it
- Short position P&L: (entry_price - current_price) * quantity
- Long position P&L: (current_price - entry_price) * quantity
- Cash impact: short selling adds entry_price * quantity to cash (proceeds), closing deducts exit_price * quantity

## Decision 5: "Followed vs Ignored" Comparison

**Decision**: Compare analyses with linked trades vs analyses without trades, using simulated horizon-end prices

**Rationale**:
- "Followed" = analyses where the user executed a trade → use actual trade P&L
- "Ignored" = completed analyses with no linked trade → simulate what would have happened using horizon-end price (already computed by existing simulation service)
- Simple comparison: average return of followed vs average return of ignored
- Leverages the existing SimulationResult infrastructure from 001
