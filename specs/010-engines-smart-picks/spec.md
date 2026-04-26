# Feature Specification: 7 Trading Engines + News-Driven Smart Picks + Danger Alerts

**Feature Branch**: `010-engines-smart-picks`  
**Created**: 2026-04-25  
**Status**: Draft  
**Input**: "7 trading engines (Monte Carlo, momentum, volume confirmation, support/resistance, mean reversion, Bollinger squeeze, correlation) combined with news-driven stock discovery to produce Smart Picks and Danger Alerts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smart Picks: Today's Best Chances (Priority: P1)

A trader opens the app and sees "Today's Best Chances" — a ranked list of 5-10 stocks that have the highest combined scores from all engines + news. Each stock shows its overall score (0-100), Monte Carlo probability, news sentiment, technical verdict, and a one-click "Analyze" button. The list answers the question: **"What should I look at today?"**

Stocks are NOT found by scanning all 228 tickers. Instead, they come from **news mentions + EGX top movers** — only stocks where something is actually happening get scored.

**Why this priority**: This is the #1 user need — "tell me what to buy." Everything else supports this.

**Independent Test**: Open Smart Picks page. See 5-10 ranked stocks with scores, news catalysts, and MC probabilities. Click "Analyze" on any stock → full AI analysis starts.

**Acceptance Scenarios**:

1. **Given** a user opens the Smart Picks page, **When** the page loads, **Then** they see a ranked list of stocks sorted by combined score with the highest score first.
2. **Given** each stock in the list, **When** the user reads a row, **Then** they see: rank, ticker, company name, combined score (0-100), MC probability (%), news sentiment (+/-), technical verdict (Bullish/Bearish/Neutral), and an Analyze button.
3. **Given** the user clicks "Analyze" on a stock, **When** the analysis page opens, **Then** the stock and market are pre-filled for immediate analysis.
4. **Given** no stocks have news or unusual activity today, **When** the page loads, **Then** it shows "No strong opportunities detected today — markets are quiet."

---

### User Story 2 - 7 Trading Engines on Each Stock (Priority: P1)

When a user views any analysis result (or any stock in the Smart Picks list), they can see the full 7-engine breakdown. Each engine provides its own score (0-100) and a verdict. The engines combine into one overall score. Users can expand each engine to see the detailed data behind its score.

The 7 engines are:
1. **Monte Carlo** — 10,000 simulations → probability up/down, expected return, range
2. **Momentum** — rate of change, trend strength, trend duration
3. **Volume Confirmation** — today's volume vs 20-day average, confirms if move is real
4. **Support/Resistance** — key price levels, risk/reward ratio
5. **Mean Reversion** — distance from moving average, bounce probability
6. **Bollinger Bands** — squeeze detection, breakout direction
7. **Correlation** — sector peers moving together confirmation

**Why this priority**: The engines are what make the scores meaningful. Without them, Smart Picks is just news sentiment — with them, it's a quantitative system.

**Independent Test**: Open any stock's engine breakdown. All 7 engines show their individual score and verdict. Click each to expand details (histograms, charts, gauges). The combined score matches the weighted average.

**Acceptance Scenarios**:

1. **Given** the user views a stock's engine breakdown, **When** all 7 engines have data, **Then** each shows a score (0-100), a verdict (Bullish/Bearish/Neutral), and an expand button.
2. **Given** the user clicks to expand Monte Carlo, **When** the detail opens, **Then** they see: probability up %, expected change %, best case (95th percentile), worst case (5th percentile), and a distribution histogram.
3. **Given** the user clicks to expand Volume, **When** the detail opens, **Then** they see a 6-day volume bar chart and "Real Move ✅" or "Fake Move ❌" verdict.
4. **Given** one engine has no data (e.g., correlation for a stock with no sector peers), **When** the breakdown renders, **Then** that engine shows "N/A" and is excluded from the combined score.
5. **Given** the combined score is displayed, **When** the user hovers or clicks, **Then** they see the formula: Score = MC×40% + News×30% + Technicals×30%.

---

### User Story 3 - Danger Alerts on Open Positions (Priority: P1)

A trader who has open positions in their portfolio sees a "Danger Alerts" section that continuously monitors each position using the 7 engines. When a position's combined score drops below a threshold, it triggers a color-coded alert:
- 🔴 **RED (Score < 35)**: "SELL NOW" — multiple engines show danger
- 🟡 **YELLOW (Score 35-55)**: "WATCH CAREFULLY" — mixed signals
- 🟢 **GREEN (Score > 55)**: "SAFE" — engines confirm the position

**Why this priority**: Equal to P1 because protecting money is as important as finding opportunities. Users asked specifically: "how to get profit before it collapses."

**Independent Test**: Open Danger Alerts with 4 open positions. Each shows its alert level (red/yellow/green) with the specific reasons. A full engine breakdown table shows all scores for all positions.

**Acceptance Scenarios**:

1. **Given** the user has open positions, **When** they view Danger Alerts, **Then** each position shows a color-coded alert (red/yellow/green) with a score and the top reason for the alert level.
2. **Given** a position score drops below 35, **When** the alert renders, **Then** it shows 🔴 RED with "SELL NOW" and specific reasons (e.g., "Broke below support, volume selling 4x").
3. **Given** a position is safe (score > 55), **When** the alert renders, **Then** it shows 🟢 GREEN with "SAFE" and confirms which engines agree.
4. **Given** the user clicks a position's alert, **When** the detail expands, **Then** they see the full 7-engine breakdown for that specific stock.

---

### User Story 4 - News-Driven Stock Discovery (Priority: P2)

Instead of scanning all 228 stocks, the system discovers candidates through news. Every hour, it fetches news from financial sources, extracts company/ticker mentions, scores sentiment, and produces a list of "stocks in the news today." This list feeds into Smart Picks as candidates to score.

Additional candidates come from the EGX top movers list (top gainers, losers, most active by volume) — stocks where something unusual is happening.

**Why this priority**: P2 because it's the discovery mechanism that feeds P1 (Smart Picks). Can be built incrementally — start with a manual "Score This Stock" button, add automatic news discovery later.

**Independent Test**: Open the news feed. See 5-15 stocks mentioned in today's news with sentiment scores. These same stocks appear in Smart Picks ranked by their combined engine scores.

**Acceptance Scenarios**:

1. **Given** news articles are fetched this hour, **When** company names/tickers are extracted, **Then** unique stocks mentioned are listed with article count and average sentiment.
2. **Given** the EGX top movers data is available, **When** combined with news mentions, **Then** the union of both lists (deduplicated) becomes the candidate set for scoring.
3. **Given** a stock appears in news with strong sentiment, **When** the 7 engines score it, **Then** the combined score appears in Smart Picks.

---

### User Story 5 - Engine Results in Analysis Page (Priority: P2)

When a user runs a full AI analysis on any stock, the 7 engine scores are computed automatically and displayed alongside the AI agent reports. The engine section appears above the agent reports, providing quantitative backing to the qualitative AI analysis.

**Why this priority**: Integrates engines into the existing analysis workflow — users who already use the analysis feature get engines for free.

**Independent Test**: Run a full analysis on ETEL. After completion, the results page shows the combined score + 7-engine breakdown above the agent reports.

**Acceptance Scenarios**:

1. **Given** an analysis completes, **When** the user views results, **Then** the combined score and engine breakdown appear above the Detailed Reports section.
2. **Given** the engines run during analysis, **When** any engine fails (e.g., not enough history), **Then** it shows N/A without blocking the rest.
3. **Given** the engine scores are computed, **When** stored with the session, **Then** viewing the analysis from History shows the same engine scores.

---

### Edge Cases

- What happens when yfinance returns incomplete history (< 50 days)? Engines requiring longer history (200-SMA, Correlation) show "Insufficient data" and are excluded from the combined score. Engines needing less data (RSI, Volume) still work.
- What happens when all news is in Arabic? The ticker extraction works on both Arabic company names and Latin ticker symbols using the existing 228-ticker database for matching.
- What happens when a stock has no sector peers for correlation? The correlation engine returns N/A and the combined score reweights the remaining 6 engines.
- What happens when the market is closed? Engines use the last available trading data with a "Data from: [date]" indicator.
- What happens when a user has no open positions? Danger Alerts shows "No positions to monitor — open trades to activate alerts."
- What happens when the combined score is exactly 50? Classified as NEUTRAL/HOLD — no strong signal either way.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute 7 individual engine scores (0-100) for any given stock: Monte Carlo, Momentum, Volume Confirmation, Support/Resistance, Mean Reversion, Bollinger Bands, Correlation.
- **FR-002**: System MUST combine engine scores into one overall score using weighted averaging: Monte Carlo 40%, News Sentiment 30%, Technical Average (from remaining 6 engines) 30%.
- **FR-003**: System MUST display a "Smart Picks" page showing stocks ranked by combined score, sourced from news mentions and market movers.
- **FR-004**: System MUST display "Danger Alerts" for all open portfolio positions with red/yellow/green color coding based on combined score thresholds.
- **FR-005**: System MUST run Monte Carlo simulations (10,000 paths) using historical daily returns to compute probability of price increase, expected return, and 5th/95th percentile range.
- **FR-006**: System MUST detect volume spikes relative to 20-day average and confirm whether price moves are backed by volume ("Real Move" vs "Fake Move").
- **FR-007**: System MUST identify support and resistance levels from price history and show the stock's position relative to these levels with risk/reward ratio.
- **FR-008**: System MUST calculate mean reversion signals based on distance from 50-day moving average.
- **FR-009**: System MUST detect Bollinger Band squeezes (low band width) and expansions (breakout signals).
- **FR-010**: System MUST compute correlation between a stock and its sector peers to confirm sector-wide moves.
- **FR-011**: System MUST allow users to expand each engine to see detailed data (histograms, charts, gauges, raw values).
- **FR-012**: System MUST fetch news hourly, extract ticker/company mentions, and score sentiment to discover candidate stocks.
- **FR-013**: System MUST persist engine scores with analysis sessions so historical results are viewable.
- **FR-014**: System MUST support both English and Arabic for all engine labels, verdicts, and descriptions.
- **FR-015**: System MUST compute all 7 engines using only free historical price data — no paid APIs required.

### Key Entities

- **Engine Score**: A single engine's output for one stock — score (0-100), verdict (Bullish/Bearish/Neutral), detailed metrics, and timestamp.
- **Combined Score**: The weighted aggregate of all available engine scores for one stock — overall score, signal (BUY/HOLD/SELL), confidence level, and contributing engine scores.
- **Smart Pick**: A ranked stock entry combining combined score, news catalyst, MC probability, and technical verdict.
- **Danger Alert**: A monitoring result for an open position — alert level (red/yellow/green), combined score, primary reason, and full engine breakdown.
- **News Mention**: An extracted ticker reference from a news article with sentiment score, source, and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 engines compute scores for any stock with 200+ days of price history in under 5 seconds total.
- **SC-002**: Smart Picks page displays 5-10 ranked stocks within 10 seconds of loading (using cached news + on-demand engine computation).
- **SC-003**: Danger Alerts correctly classify positions as red/yellow/green matching the threshold rules 100% of the time.
- **SC-004**: Monte Carlo simulations run 10,000 paths in under 2 seconds per stock.
- **SC-005**: Users can see the full 7-engine breakdown with expandable details for any stock within 2 clicks from Smart Picks or Analysis.
- **SC-006**: News-driven discovery identifies at least 5 stocks with news mentions on an average EGX trading day.
- **SC-007**: All engine labels and verdicts display correctly in both English and Arabic.
- **SC-008**: Engine scores persist with analysis sessions — viewing a past analysis shows the same engine scores that were computed at the time.

## Assumptions

- All engine calculations use only free yfinance historical OHLCV data — no additional paid data sources needed.
- Engine computation is lightweight (numpy math on ~500 data points per stock) — no GPU or special infrastructure required.
- The combined score formula (MC 40% + News 30% + Tech 30%) is fixed in v1 — user-customizable weights are out of scope.
- News discovery reuses existing news fetching infrastructure (Google News RSS, Serper, Arabic news sources).
- Smart Picks candidates come from news mentions + EGX top movers (not a full 228-stock scan).
- Danger Alerts check positions each time the page is loaded — not real-time push notifications (v1).
- Correlation engine uses 90-day rolling correlation with stocks in the same sector from the EGX ticker database.
- The system displays a disclaimer that scores are quantitative tools, not financial advice.
