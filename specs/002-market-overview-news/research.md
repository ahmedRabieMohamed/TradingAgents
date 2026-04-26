# Research: Market Overview & Hot News

**Feature**: 002-market-overview-news  
**Date**: 2026-04-05

## Decision 1: Stock Price Fetching Strategy

**Decision**: Batch fetch via yfinance `download()` with in-memory caching (5-minute TTL)

**Rationale**:
- yfinance `download()` can fetch multiple tickers in a single call, much faster than individual `Ticker().info` calls
- For 50 US stocks, batch download takes ~2-3 seconds vs ~50 seconds for individual calls
- 5-minute cache avoids hammering yfinance on page refreshes
- Data is 15 minutes delayed anyway (yfinance free tier), so caching is acceptable

**Alternatives Considered**:
- Individual `Ticker().info` per stock: Too slow for 50+ stocks
- Alpha Vantage batch: Requires API key, limited to 5 symbols per call on free tier
- WebSocket streaming: Overkill for near-real-time needs; yfinance doesn't support it

## Decision 2: Stock Watchlist Management

**Decision**: Hardcoded Python lists — EGX from existing `egypt_tickers.py`, US curated manually

**Rationale**:
- EGX stocks already mapped in `tradingagents/dataflows/egypt_tickers.py` with English/Arabic names and sectors
- US stocks need a curated ~50 ticker list (S&P 500 top components + popular retail stocks)
- Watchlists change infrequently — no need for dynamic management in v1
- Stored as a Python module `backend/app/data/watchlists.py` for easy editing

**Alternatives Considered**:
- Database-stored watchlists: Overkill for static lists; adds migration complexity
- User-configurable watchlists: Future feature, not in this spec

## Decision 3: News Fetching Architecture

**Decision**: Reuse existing `tradingagents.dataflows` news functions directly

**Rationale**:
- `get_global_news_yfinance()` already works for US market news
- `egypt_news.get_global_news()` already handles tiered Egypt news (Serper → RSS fallback)
- `get_news_yfinance(ticker)` and `egypt_news.get_news(ticker)` handle ticker-specific news
- No new news infrastructure needed — just wrap existing functions in async endpoints

**Alternatives Considered**:
- New news aggregation service: Unnecessary duplication of existing code
- Caching news in DB: News is ephemeral; in-memory cache with 10-minute TTL is sufficient

## Decision 4: Market Index Data

**Decision**: Fetch via yfinance using known index symbols

**Rationale**:
- US: ^GSPC (S&P 500), ^IXIC (NASDAQ), ^DJI (Dow Jones)
- Egypt: ^CASE (EGX 30) — this is the yfinance symbol for the Cairo SE index
- Same batch download approach as stock prices
- Include in the market overview response alongside stock data

## Decision 5: Frontend Integration Approach

**Decision**: New step inserted between market selection (step 1) and stock input (step 2) in the wizard

**Rationale**:
- The market overview is a natural intermediate step: select market → browse overview → pick stock
- Clicking a stock in the overview skips the manual ticker input and goes straight to configuration
- Users can still access manual ticker input via a "Enter custom ticker" link
- The wizard step indicator updates: Market → Overview → Configure → Analyze → Results
