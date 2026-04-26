# Feature Specification: Candlestick Chart & Analysis State Persistence

**Feature Branch**: `004-candlestick-analysis-view`
**Created**: 2026-04-07
**Status**: Draft
**Input**: User description: "Add candlestick chart when selecting a ticker in the analysis view; fix bug where navigating away and returning loses the in-progress analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candlestick Chart on Ticker Selection (Priority: P1)

As a trader, I want to see a candlestick (OHLC) chart for the selected stock immediately after I pick a ticker in the analysis wizard, so I can visually assess recent price action before deciding to run analysis.

**Why this priority**: The chart gives traders the visual context they rely on to make informed decisions. Without it, the user must leave the app to check price history elsewhere, breaking the workflow.

**Independent Test**: Select any valid ticker (e.g., AAPL on US market), confirm a candlestick chart renders showing recent price history with open/high/low/close candles and volume bars.

**Acceptance Scenarios**:

1. **Given** I have selected US market and entered "AAPL", **When** the ticker is validated successfully, **Then** I see a candlestick chart showing recent daily price history (default: last 3 months) alongside the existing stock info card.
2. **Given** the candlestick chart is displayed, **When** I hover over a candle, **Then** I see a tooltip with the date, open, high, low, close prices, and volume for that day.
3. **Given** the chart is displayed, **When** I select a different time range (1 week, 1 month, 3 months, 6 months, 1 year), **Then** the chart updates to show the selected period with appropriate candle granularity (intraday for 1W, daily for 1M+).
4. **Given** I select an EGX ticker (e.g., COMI), **When** the ticker is validated, **Then** the candlestick chart displays with prices in EGP currency.
5. **Given** the ticker validation fails or price history is unavailable, **When** the chart area would normally render, **Then** I see a graceful empty state message instead of a broken chart.

---

### User Story 2 - Persist Analysis State Across Tab Navigation (Priority: P1)

As a trader, I want my in-progress or completed analysis to be preserved when I navigate to another tab (History, Portfolio, etc.) and come back, so I don't lose my work or have to restart the analysis.

**Why this priority**: This is a bug fix. Losing analysis state is a broken user experience that wastes the user's time and the LLM compute spent on the analysis. It makes the app feel unreliable.

**Independent Test**: Start an analysis, navigate to the History tab mid-analysis, navigate back to the analysis tab — the analysis should still be running (or completed) with all progress visible.

**Acceptance Scenarios**:

1. **Given** I am on Step 3 (analysis running) with live agent progress, **When** I click "History" in the sidebar and then click "New Analysis" again, **Then** I return to Step 3 with the analysis still running and all previous agent messages visible.
2. **Given** I am on Step 4 (results displayed) with a completed analysis, **When** I navigate to Portfolio and then return to the analysis tab, **Then** I see the same results (recommendation, confidence, reports) without having to reload.
3. **Given** I am on Step 2 (configuration) with a ticker selected and parameters chosen, **When** I navigate away and return, **Then** the selected market, ticker, and configuration are preserved — I can continue from where I left off.
4. **Given** I have a persisted in-progress analysis and I explicitly click a "New Analysis" button, **When** I confirm, **Then** the previous state is cleared and I start fresh from Step 0.

---

### Edge Cases

- What happens when the chart data API is slow or times out? The chart should show a loading skeleton, and the user should still be able to proceed to configure analysis without waiting.
- What happens if the user navigates away during WebSocket streaming and the connection drops? On return, the app should attempt to reconnect or fetch the latest state from the backend.
- What happens if the user opens the app in a new browser tab? Each tab maintains its own independent analysis state (no cross-tab sync required).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a candlestick (OHLC) chart after a ticker is successfully validated in the analysis wizard.
- **FR-002**: Chart MUST show open, high, low, close prices as candlestick bars and volume as a secondary bar chart below.
- **FR-003**: Chart MUST support time range selection: 1 week, 1 month, 3 months (default), 6 months, 1 year.
- **FR-004**: Chart MUST display a tooltip on hover with date, OHLC values, and volume.
- **FR-005**: Chart MUST display prices in the correct currency for the selected market (USD for US, EGP for EGX).
- **FR-006**: System MUST preserve the full analysis wizard state (current step, selected market, ticker, configuration, running analysis, results) when the user navigates to a different tab and returns.
- **FR-007**: System MUST preserve WebSocket connection and live agent messages when the user navigates away from the analysis page during an active analysis.
- **FR-008**: System MUST provide an explicit "New Analysis" action to clear persisted state and start fresh.
- **FR-009**: Chart MUST show a loading state while price data is being fetched and a graceful empty state if data is unavailable.

### Key Entities

- **OHLC Price Data**: Represents historical price bars — date, open, high, low, close, volume for a given ticker over a time range.
- **Analysis Wizard State**: The full state of the multi-step analysis form — current step, market, ticker, stock info, configuration parameters, session ID, agent progress, and results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After selecting a valid ticker, the candlestick chart is visible within 3 seconds on a standard connection.
- **SC-002**: Users can navigate away from the analysis page and return without losing any analysis state — 100% of the time for in-memory sessions.
- **SC-003**: Chart correctly renders for both US and EGX tickers with appropriate currency labels.
- **SC-004**: Time range switching updates the chart within 2 seconds.
- **SC-005**: Users no longer need to restart analysis after accidental navigation — zero occurrences of lost in-progress analyses.

## Assumptions

- Historical OHLC data is available from the same data provider already used for stock validation (yfinance or equivalent) — no new external service needed.
- The candlestick chart is displayed within the existing analysis wizard layout (e.g., alongside or below the stock info card on Step 1), not as a separate page.
- State persistence is in-memory only (Zustand store lifetime) — a full browser refresh will still reset state. This is acceptable for MVP.
- The volume sub-chart uses the same color scheme as the candlestick chart (green for up days, red for down days).
- Candle granularity adapts to the selected time range: intraday (5-min or 15-min) for 1W, daily for 1M+.
