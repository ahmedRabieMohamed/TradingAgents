# Research: Candlestick Chart & Analysis State Persistence

**Feature**: 004-candlestick-analysis-view
**Date**: 2026-04-07

## R1: Candlestick Charting Library

**Decision**: Use `lightweight-charts` (TradingView) for the candlestick chart.

**Rationale**: recharts (v3.8.1, already installed) does not have a native
candlestick/OHLC chart type. Workarounds using ComposedChart + custom shapes
are brittle and lack financial chart features (crosshair, price scale,
time axis formatting). lightweight-charts is purpose-built for financial
charting, supports candlestick + volume histogram natively, is ~40KB gzipped,
and has first-class React bindings via `lightweight-charts-react-wrapper`.

**Alternatives considered**:
- recharts with custom shapes: Rejected — no native OHLC support, poor
  crosshair/tooltip behavior for financial data.
- apexcharts: Rejected — heavier bundle (~120KB), overkill for a single
  candlestick chart. Adds a second charting paradigm alongside recharts.
- d3 custom: Rejected — too much effort for a standard candlestick chart.

**Constitution note**: New dependency justified per Principle I (Simplicity)
and Development Standards (new deps MUST solve a real problem). Recharts
cannot solve this; lightweight-charts does with minimal overhead.

---

## R2: OHLC Data Source (Backend)

**Decision**: Add a new `GET /api/stocks/price-history` endpoint using
the existing yfinance integration.

**Rationale**: yfinance is already installed and used in `market_data.py`
(`yf.download()`) and `simulation.py`. The `.history()` / `yf.download()`
methods return OHLC + Volume DataFrames. No new data provider needed.

**Alternatives considered**:
- Alpha Vantage / Polygon.io: Rejected — adds external API dependency,
  requires API keys. yfinance is already in use and sufficient.
- Frontend-only fetch via a JS finance library: Rejected — violates
  Principle III (Separation of Concerns). Backend owns data fetching.

**Period-to-interval mapping**:
| Period | yfinance `period` | yfinance `interval` | Candle count |
|--------|-------------------|---------------------|-------------|
| 1W     | 5d                | 15m                 | ~130        |
| 1M     | 1mo               | 1d                  | ~22         |
| 3M     | 3mo               | 1d                  | ~65         |
| 6M     | 6mo               | 1d                  | ~130        |
| 1Y     | 1y                | 1d                  | ~252        |

---

## R3: State Persistence Strategy

**Decision**: Move all wizard state from local `useState` in
NewAnalysis.tsx into a new Zustand store (`wizardStore`).

**Rationale**: The bug root cause is that NewAnalysis.tsx uses local
`useState` for step, selectedMarket, selectedStock, tradeHorizon,
analysisDate, wsUrl, etc. When the user navigates to another route
(`/history`, `/portfolio`), React Router unmounts the component and
all local state is destroyed. Zustand stores survive component
unmount/remount because they live outside the React tree.

**Alternatives considered**:
- Keep component mounted (display:none): Rejected — wasteful,
  WebSocket stays open, DOM stays in memory. Violates Simplicity.
- sessionStorage persistence: Rejected — overkill for in-session
  navigation. Zustand in-memory is sufficient; a full page refresh
  resetting state is acceptable per spec assumptions.
- Merge into existing analysisStore: Rejected — analysisStore handles
  pipeline results. Wizard navigation (step, market, ticker, config)
  is a separate concern. Merging would bloat one store.

**WebSocket connection handling**: The existing `useWebSocket` hook
properly closes on unmount. When the user returns and the store still
has a `wsUrl` + `sessionId` with status "running", the hook should
reconnect. If the analysis completed while away, the component should
detect `status === 'completed'` from the store and jump to Step 4.

---

## R4: Chart Placement in Wizard

**Decision**: Show the candlestick chart on Step 1 (after ticker
validation), below the stock info card. The chart persists into Step 2
(configuration) as context.

**Rationale**: The user wants to see price action before committing to
analysis. Showing it immediately after validation gives maximum context
with minimum friction. Keeping it visible during configuration reinforces
the visual context while the user sets parameters.

**Alternatives considered**:
- Separate chart page/modal: Rejected — breaks wizard flow.
- Chart only on results page (Step 4): Rejected — doesn't help the
  pre-analysis decision the user described.
