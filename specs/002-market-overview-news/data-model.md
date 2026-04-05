# Data Model: Market Overview & Hot News

**Feature**: 002-market-overview-news  
**Date**: 2026-04-05

## Data Structures (API Response Shapes)

These are not database entities — they are computed on each request from live market data.

### MarketOverview

The complete response for a market overview request.

| Field | Type | Description |
|-------|------|-------------|
| market_id | string | "us" or "egypt" |
| market_status | string | "open" or "closed" |
| last_updated | datetime | When data was last fetched |
| indices | list[IndexData] | Market indices (S&P 500, EGX 30, etc.) |
| summary | MarketSummary | Aggregate statistics |
| stocks | list[StockSnapshot] | All tracked stocks with prices |
| gainers | list[StockSnapshot] | Top 7 gainers by % change |
| losers | list[StockSnapshot] | Top 7 losers by % change |

### StockSnapshot

A point-in-time view of a stock's price and performance.

| Field | Type | Description |
|-------|------|-------------|
| ticker | string | Symbol (e.g., "AAPL", "COMI") |
| name | string | English company name |
| name_ar | string | Nullable — Arabic name (EGX only) |
| sector | string | Sector classification |
| price | float | Current/last price |
| currency | string | "USD" or "EGP" |
| change | float | Daily change amount |
| change_pct | float | Daily change percentage |

### IndexData

Market-level index performance.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Display name (e.g., "S&P 500") |
| symbol | string | yfinance symbol (e.g., "^GSPC") |
| value | float | Current index value |
| change | float | Daily change amount |
| change_pct | float | Daily change percentage |

### MarketSummary

Aggregate market statistics.

| Field | Type | Description |
|-------|------|-------------|
| total_stocks | int | Number of tracked stocks |
| gainers_count | int | Stocks with positive change |
| losers_count | int | Stocks with negative change |
| unchanged_count | int | Stocks with zero change |
| breadth_pct | float | Percentage of stocks advancing |

### NewsArticle

A single news item.

| Field | Type | Description |
|-------|------|-------------|
| title | string | Headline |
| snippet | string | Summary/snippet text |
| source | string | Publisher name |
| url | string | Link to original article |
| published_at | string | Publication date/time |
| is_hot | boolean | Whether article is considered "hot" (recent + high relevance) |

### MarketNewsResponse

| Field | Type | Description |
|-------|------|-------------|
| market_id | string | "us" or "egypt" |
| articles | list[NewsArticle] | News articles |
| ticker | string | Nullable — if ticker-specific |
