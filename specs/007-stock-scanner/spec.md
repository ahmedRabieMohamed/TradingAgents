# Feature Specification: Daily Stock Scanner & Opportunity Detector

**Feature Branch**: `007-stock-scanner`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: User description: "Daily stock scanner that screens all EGX stocks using technical signals (unusual volume, breakouts, RSI reversal, Bollinger squeeze, sector momentum) to score and rank stocks by opportunity potential. Shows top opportunities on a dedicated Scanner page. Users click any stock to run full AI analysis."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Today's Top Opportunities (Priority: P1)

A trader opens the Scanner page and sees a ranked list of the top 15-20 EGX stocks with the highest opportunity scores for today. Each stock shows its ticker, company name, opportunity score (0-100), the primary signal that triggered it (e.g., "Volume Surge 3.2x", "Breakout above 200-SMA", "RSI Reversal"), current price, weekly price change, and a quick action button to run a full AI analysis. The list is sorted by score descending. The trader can see at a glance which stocks are worth investigating today.

**Why this priority**: This is the core value proposition — answering "what should I look at today?" before the user even knows which stock to analyze. Without this, users are guessing blindly.

**Independent Test**: Open the Scanner page — it should display a ranked list of EGX stocks with scores, signals, and prices. Each row should have an "Analyze" button that navigates to the analysis page with the stock pre-filled.

**Acceptance Scenarios**:

1. **Given** the scanner has run for today, **When** a user opens the Scanner page, **Then** they see a ranked list of stocks sorted by opportunity score with the highest-scoring stock at the top.
2. **Given** the scanner results are displayed, **When** a user views a stock row, **Then** they see: ticker, company name (in the user's language), score (0-100), primary signal description, current price, 5-day change %, and an "Analyze" button.
3. **Given** the user clicks "Analyze" on a stock, **When** the analysis page opens, **Then** the stock ticker and market are pre-filled and the user can immediately configure and start analysis.
4. **Given** no scanner results exist yet (first visit or stale data), **When** the user opens the Scanner page, **Then** they see a "Run Scan" button that triggers a fresh scan.

---

### User Story 2 - On-Demand Scan Execution (Priority: P1)

A trader clicks "Run Scan" or "Refresh" to trigger a fresh scan of all EGX stocks. The system fetches the latest price and volume data for all 228 EGX stocks, calculates technical indicators, scores each stock, and returns the ranked results. A progress indicator shows during the scan (which may take 30-60 seconds due to data fetching). The results are cached so subsequent page loads are instant until the next scan.

**Why this priority**: Equal to P1 because without scan execution, there's no data to display. The scan must work reliably and show progress.

**Independent Test**: Click "Run Scan" — progress indicator appears, results load within 90 seconds, and the ranked list is displayed.

**Acceptance Scenarios**:

1. **Given** a user is on the Scanner page, **When** they click "Run Scan", **Then** a progress indicator appears showing the scan is in progress.
2. **Given** the scan is running, **When** it completes, **Then** the results are displayed immediately as a ranked list.
3. **Given** a scan completed within the last 4 hours, **When** the user revisits the Scanner page, **Then** the cached results are shown instantly without re-scanning.
4. **Given** a scan fails (e.g., network error), **When** the error occurs, **Then** an error message is shown with a "Retry" button.

---

### User Story 3 - Signal Breakdown & Filtering (Priority: P2)

A trader wants to understand WHY a stock was flagged and filter by specific signal types. Each stock in the scanner results can be expanded to show a detailed breakdown of its score: which signals fired, their individual scores, and a mini technical summary. The trader can also filter the list by signal type (e.g., show only "Volume Surge" or only "Breakout" signals) and by sector.

**Why this priority**: Adds depth to the scanner but not required for MVP. The ranked list alone delivers value.

**Independent Test**: Click a stock row to expand its signal breakdown — see individual scores for volume, momentum, breakout, etc. Use the filter dropdowns to narrow results by signal type or sector.

**Acceptance Scenarios**:

1. **Given** scanner results are displayed, **When** a user clicks on a stock row, **Then** an expandable detail panel shows the score breakdown: volume score, momentum score, breakout score, RSI score, sector score.
2. **Given** the filter options are visible, **When** a user selects "Volume Surge" filter, **Then** only stocks with a volume signal above threshold are shown.
3. **Given** the sector filter is available, **When** a user selects "Banking", **Then** only banking stocks are shown, still sorted by opportunity score.

---

### User Story 4 - Dashboard Integration (Priority: P2)

The main Dashboard page shows a compact "Top Opportunities" widget displaying the top 5 stocks from the latest scan. This gives users immediate value on the landing page without navigating to the Scanner. Each stock in the widget shows ticker, score, and primary signal with a link to the full Scanner page.

**Why this priority**: Surfaces scanner value on the default landing page, but the dedicated Scanner page (P1) must work first.

**Independent Test**: Open Dashboard — the "Top Opportunities" card shows 5 stocks from the latest scan with scores. Clicking "View All" navigates to the full Scanner page.

**Acceptance Scenarios**:

1. **Given** a scan has been completed, **When** the user opens the Dashboard, **Then** a "Top Opportunities" card shows the top 5 ranked stocks.
2. **Given** no scan has been run, **When** the Dashboard loads, **Then** the widget shows "Run your first scan" with a link to the Scanner page.

---

### Edge Cases

- What happens when yfinance rate-limits during a scan of 228 stocks? The scanner should batch requests and retry failed tickers, reporting partial results rather than failing entirely.
- What happens when a stock has no trading data for the last 5 days (suspended/halted)? It should be excluded from results with no error.
- What happens when all stocks score below the minimum threshold? The page should show "No strong opportunities detected today" rather than an empty list.
- What happens when the user switches language to Arabic? All signal descriptions, sector names, and company names should display in Arabic.
- What happens when the market is closed (weekend/holiday)? The scanner still works using the last available trading data, with a note showing the data date.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST scan all 228 EGX stocks and calculate an opportunity score (0-100) for each based on technical signals.
- **FR-002**: System MUST rank stocks by opportunity score and display the top results in a sortable list.
- **FR-003**: System MUST calculate the following signals for each stock: unusual volume (vs 20-day average), price relative to 50-day and 200-day SMA, RSI momentum, Bollinger Band position, and 5-day price change.
- **FR-004**: System MUST display for each stock: ticker, company name, opportunity score, primary signal description, current price, and 5-day change percentage.
- **FR-005**: System MUST allow users to trigger a scan on-demand with a visible progress indicator.
- **FR-006**: System MUST cache scan results so subsequent page loads are instant (cache duration: 4 hours).
- **FR-007**: System MUST provide a one-click path from any scanner result to start a full AI analysis for that stock.
- **FR-008**: System MUST handle partial failures gracefully — if some tickers fail to fetch, report results for the successful ones.
- **FR-009**: System MUST calculate a sector strength score based on how many stocks in the same sector are trending positively.
- **FR-010**: System MUST support both English and Arabic for all displayed text, signal descriptions, and company names.

### Key Entities

- **Scan Result**: A snapshot of all scored stocks from a single scan execution. Contains timestamp, market ID, and the list of scored stocks.
- **Stock Score**: Individual stock scoring with ticker, overall score (0-100), individual signal scores (volume, momentum, breakout, RSI, sector), primary signal label, current price, and price change metrics.
- **Signal**: A detected technical pattern (Volume Surge, Breakout, RSI Reversal, Bollinger Squeeze, Sector Momentum) with its strength value.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Scanner completes a full scan of 228 stocks in under 90 seconds.
- **SC-002**: Users can identify and start analyzing a stock within 10 seconds of viewing scanner results (one click from scanner to analysis).
- **SC-003**: Scanner results display at least 10 stocks with scores above 50 on an average trading day.
- **SC-004**: Cached results load in under 1 second on subsequent page visits.
- **SC-005**: 100% of scanner UI text displays correctly in both English and Arabic.
- **SC-006**: Scanner handles yfinance failures gracefully with at least 80% of stocks returning valid results even under rate limiting.

## Assumptions

- yfinance provides sufficient technical data (OHLCV) for all calculations — no additional paid API required.
- The scanner runs on-demand (user-triggered), not as a background cron job — to avoid unnecessary API calls.
- EGX market data on yfinance is delayed by end-of-day (not real-time intraday) — this is acceptable for daily opportunity screening.
- The scoring algorithm uses fixed weights initially — no machine learning or backtesting in v1.
- US market scanning is out of scope for v1 — focus on EGX first since that's the primary user base.
- The scanner uses the existing 228-ticker database from `egypt_tickers.py` — no additional ticker discovery needed.
