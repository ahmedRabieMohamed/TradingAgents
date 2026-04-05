# Feature Specification: Market Overview & Hot News

**Feature Branch**: `002-market-overview-news`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "I want also to add the hot news section. When selecting a market should see its stock list, also some analytics and grid for losers and most profits etc"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Market Overview Dashboard (Priority: P1)

As a trader, when I select a market (US or EGX), I want to see a dashboard with a list of key stocks, their current prices, and daily performance so I can quickly assess the market landscape before choosing a stock to analyze.

**Why this priority**: This is the core request — seeing the stock list with performance data when a market is selected. It replaces the current blank stock-entry screen with an informative overview that helps users make better stock selection decisions.

**Independent Test**: Can be tested by selecting a market and verifying the dashboard loads with stock names, prices, and daily change percentages. Delivers value as a standalone market snapshot even without analysis.

**Acceptance Scenarios**:

1. **Given** I select the US Market, **When** the market overview loads, **Then** I see a list of key stocks (at minimum the major indices and popular tickers) with their current price, daily change amount, and daily change percentage.
2. **Given** I select the Egypt Market (EGX), **When** the market overview loads, **Then** I see the EGX-listed stocks (EGX30 constituents and key EGX70 stocks) with prices in EGP, daily change, and daily change percentage.
3. **Given** I am on the market overview, **When** I click on any stock in the list, **Then** I am taken to that stock's analysis configuration screen (pre-filled with the selected ticker).
4. **Given** the market overview is displayed, **When** I search or filter by stock name or ticker, **Then** the list narrows to matching stocks.

---

### User Story 2 - Top Movers Grid (Priority: P1)

As a trader, I want to see at-a-glance grids showing today's top gainers and top losers so I can quickly identify which stocks are moving the most and potentially worth analyzing.

**Why this priority**: Top movers are the most actionable market data — traders scan gainers/losers first to find momentum opportunities. This is the "analytics and grid for losers and most profits" the user requested.

**Independent Test**: Can be tested by viewing the market overview and verifying the gainers/losers grids show stocks ranked by percentage change. Delivers value by surfacing the most active stocks immediately.

**Acceptance Scenarios**:

1. **Given** I am on the market overview for any market, **When** I view the top movers section, **Then** I see two grids: "Top Gainers" (sorted by highest positive % change) and "Top Losers" (sorted by largest negative % change), each showing at least 5 stocks.
2. **Given** the top gainers grid is displayed, **When** I look at a stock entry, **Then** I see the ticker, stock name, current price, change amount, and change percentage with green color coding.
3. **Given** the top losers grid is displayed, **When** I look at a stock entry, **Then** I see the same fields with red color coding.
4. **Given** I click on any stock in the gainers or losers grid, **When** the action completes, **Then** I am taken to that stock's analysis configuration screen.

---

### User Story 3 - Hot News Section (Priority: P1)

As a trader, I want to see a "Hot News" section with the latest market-relevant news for the selected market so I can stay informed about events that may affect my trading decisions.

**Why this priority**: News is a primary driver of stock movement. The user explicitly requested a hot news section, and the project already has robust news infrastructure (yfinance, Google News RSS, Serper.dev) that can be surfaced in the UI.

**Independent Test**: Can be tested by selecting a market and verifying the hot news section displays recent articles with headlines, sources, and publication dates. Delivers value as a standalone news aggregator for the selected market.

**Acceptance Scenarios**:

1. **Given** I am on the US Market overview, **When** I view the hot news section, **Then** I see at least 10 recent news articles about the US stock market, Federal Reserve, and economic outlook, each showing headline, source, publication date, and a snippet.
2. **Given** I am on the Egypt Market overview, **When** I view the hot news section, **Then** I see recent news about the Egyptian exchange, Central Bank of Egypt, and Egyptian economy — including both English and Arabic-sourced articles.
3. **Given** I see a news article in the hot news section, **When** I click on it, **Then** I am taken to the original article in a new browser tab.
4. **Given** the hot news section is loaded, **When** I click a refresh button, **Then** the news is updated with the latest articles.

---

### User Story 4 - Market Analytics Summary (Priority: P2)

As a trader, I want to see high-level market analytics (market index performance, sector breakdown, overall market sentiment) so I can understand the broader market context before drilling into individual stocks.

**Why this priority**: Analytics provide context that makes stock-level decisions more informed. However, the stock list (P1) and news (P1) already deliver significant standalone value.

**Independent Test**: Can be tested by selecting a market and verifying the analytics section shows index performance and summary statistics. Delivers value by providing market context at a glance.

**Acceptance Scenarios**:

1. **Given** I am on the US Market overview, **When** I view the analytics section, **Then** I see key market indices (S&P 500, NASDAQ Composite, Dow Jones) with their current value and daily change.
2. **Given** I am on the Egypt Market overview, **When** I view the analytics section, **Then** I see the EGX 30 index value and daily change.
3. **Given** I am on any market overview, **When** I view the analytics section, **Then** I see summary statistics: total stocks tracked, number of gainers vs losers, and market breadth (percentage advancing).

---

### User Story 5 - Ticker-Specific News (Priority: P3)

As a trader, I want to view news specific to a particular stock from the market overview so I can research a stock before starting a full analysis.

**Why this priority**: Ticker-level news adds depth but requires the market overview (P1) and hot news (P1) to be in place first. It extends the existing news section with focused drill-down capability.

**Independent Test**: Can be tested by clicking a "News" action on any stock in the list and seeing news specific to that ticker. Delivers value by providing pre-analysis research.

**Acceptance Scenarios**:

1. **Given** I am on the market overview and I see a stock in the list, **When** I click the news icon or "View News" action for that stock, **Then** I see a panel or section showing recent news articles specifically about that company.
2. **Given** I am viewing ticker-specific news for an EGX stock (e.g., COMI), **When** the news loads, **Then** I see articles in both English and Arabic sources matching the company's English and Arabic names.
3. **Given** no recent news exists for a particular ticker, **When** I view its news section, **Then** I see a message saying "No recent news found for [ticker]" rather than an empty screen.

---

### Edge Cases

- What happens when market data is unavailable (e.g., data provider down)? The app should show a clear error with cached/stale data indicated by a timestamp label showing when data was last fetched.
- How does the system handle stocks that have been suspended or halted? Display the stock with a "Halted" or "Suspended" badge and last known price.
- What happens when the news API key (Serper.dev) is not configured for the Egypt market? Fall back to RSS feed sources (Google News RSS, Daily News Egypt) which don't require API keys.
- How does the app handle market data outside of trading hours? Show the last closing prices with a label indicating "Market Closed" and the closing time.
- What happens when a stock has no price change data (e.g., newly listed)? Display the stock with "N/A" for change fields and exclude from gainers/losers grids.
- How are the stock lists maintained? EGX stocks use the existing ticker mapping (egypt_tickers.py); US stocks use a curated watchlist of popular tickers since yfinance cannot enumerate exchange listings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a market overview dashboard when a market (US or EGX) is selected, showing a list of stocks with current price, daily change, and daily change percentage.
- **FR-002**: System MUST display a "Top Gainers" grid showing the stocks with the highest positive daily percentage change, sorted descending, showing at least 5 stocks.
- **FR-003**: System MUST display a "Top Losers" grid showing the stocks with the largest negative daily percentage change, sorted ascending, showing at least 5 stocks.
- **FR-004**: System MUST display a "Hot News" section with at least 10 recent market-relevant news articles for the selected market, each showing headline, source, date, and snippet.
- **FR-005**: System MUST use market-appropriate news sources: yfinance news for US market; Google News RSS (fallback) and Serper.dev (when configured) for Egypt market.
- **FR-006**: System MUST allow users to click on any stock in the overview to navigate to that stock's analysis configuration screen with the ticker pre-filled.
- **FR-007**: System MUST allow users to search and filter the stock list by ticker symbol or company name.
- **FR-008**: System MUST display market indices (S&P 500, NASDAQ, Dow Jones for US; EGX 30 for Egypt) with current value and daily change.
- **FR-009**: System MUST show summary analytics: count of tracked stocks, number of gainers vs losers, and market breadth percentage.
- **FR-010**: System MUST allow users to click a news article to open the original source in a new browser tab.
- **FR-011**: System MUST allow users to view news specific to a single stock from the market overview.
- **FR-012**: System MUST handle Egypt-specific display conventions: EGP currency, Sunday-Thursday trading week, Arabic company names alongside English names.
- **FR-013**: System MUST indicate when the market is closed and show last closing data with appropriate labeling.
- **FR-014**: System MUST allow users to refresh news and stock data on demand.
- **FR-015**: System MUST fall back gracefully when optional news API keys (Serper.dev) are not configured, using free RSS-based sources instead.

### Key Entities

- **Market Stock**: A stock tracked in a specific market, including its ticker, company name (English + Arabic for EGX), current price, daily change, daily change percentage, and sector.
- **Market Index**: A market-level index (e.g., S&P 500, EGX 30) with its current value and daily performance.
- **News Article**: A single news item with headline, snippet/summary, source name, publication date, and original URL. Can be market-level or ticker-specific.
- **Market Summary**: Aggregate statistics for a market: total stocks tracked, gainers count, losers count, unchanged count, and market breadth percentage.
- **Stock Watchlist**: The curated list of stocks tracked per market. For EGX: derived from the existing ticker mapping (EGX30 + key EGX70). For US: a curated list of popular/major tickers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Market overview dashboard loads within 5 seconds of selecting a market, displaying at least 20 stocks with current prices.
- **SC-002**: Top gainers and top losers grids each display at least 5 stocks, correctly sorted by daily percentage change.
- **SC-003**: Hot news section displays at least 10 articles less than 24 hours old for the selected market.
- **SC-004**: Users can navigate from market overview to a stock's analysis screen in 1 click.
- **SC-005**: 90% of users identify the day's top-performing and worst-performing stocks within 10 seconds of viewing the market overview.
- **SC-006**: Egypt market news includes articles from both English and Arabic sources.
- **SC-007**: Stock search/filter returns matching results within 1 second of typing.
- **SC-008**: Market overview remains functional (showing stock data) even when news APIs are unavailable or unconfigured — degrading gracefully.

## Assumptions

- Stock lists are curated and predefined: EGX stocks come from the existing `egypt_tickers.py` mapping (~30 stocks); US stocks use a curated watchlist of ~50 popular tickers (major indices, FAANG, etc.) since yfinance cannot enumerate exchange listings.
- Price data for all stocks in the watchlist is fetched via the existing yfinance integration — no new data providers needed.
- Top gainers/losers are computed from the curated watchlist's daily price changes, not from the entire exchange (which is unavailable via yfinance).
- News for the US market uses yfinance's built-in news functionality (no API key required). News for Egypt uses the existing tiered approach: Serper.dev if configured, Google News RSS as fallback.
- Market index data (S&P 500, EGX 30) is fetched by known index ticker symbols (e.g., ^GSPC, ^EGX30) via yfinance.
- This feature is an enhancement to the Trading Web Application (001-trading-web-app) and depends on the web app's backend and frontend being in place.
- Real-time streaming of stock prices is not required — data is fetched on page load and on manual refresh. Near-real-time (within 15-minute delay typical of free yfinance data) is acceptable.
