"""Curated stock watchlists and market indices for the Market Overview feature."""

from tradingagents.dataflows.egypt_tickers import EGX_TICKERS

# ---------------------------------------------------------------------------
# US Stocks (~48 popular tickers)
# ---------------------------------------------------------------------------

US_STOCKS: list[dict] = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Semiconductors"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer"},
    {"ticker": "META", "name": "Meta Platforms", "sector": "Technology"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"},
    {"ticker": "BRK-B", "name": "Berkshire Hathaway", "sector": "Financial"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Banking"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financial"},
    {"ticker": "UNH", "name": "UnitedHealth", "sector": "Healthcare"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Retail"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer"},
    {"ticker": "MA", "name": "Mastercard", "sector": "Financial"},
    {"ticker": "HD", "name": "Home Depot", "sector": "Retail"},
    {"ticker": "XOM", "name": "Exxon Mobil", "sector": "Energy"},
    {"ticker": "BAC", "name": "Bank of America", "sector": "Banking"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Semiconductors"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},
    {"ticker": "COST", "name": "Costco Wholesale", "sector": "Retail"},
    {"ticker": "DIS", "name": "Walt Disney", "sector": "Entertainment"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Entertainment"},
    {"ticker": "AMD", "name": "AMD Inc.", "sector": "Semiconductors"},
    {"ticker": "CRM", "name": "Salesforce", "sector": "Technology"},
    {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Technology"},
    {"ticker": "INTC", "name": "Intel Corp.", "sector": "Semiconductors"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
    {"ticker": "T", "name": "AT&T Inc.", "sector": "Telecom"},
    {"ticker": "NKE", "name": "Nike Inc.", "sector": "Consumer"},
    {"ticker": "KO", "name": "Coca-Cola Co.", "sector": "Consumer"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer"},
    {"ticker": "ABT", "name": "Abbott Labs", "sector": "Healthcare"},
    {"ticker": "MRK", "name": "Merck & Co.", "sector": "Healthcare"},
    {"ticker": "LLY", "name": "Eli Lilly", "sector": "Healthcare"},
    {"ticker": "ORCL", "name": "Oracle Corp.", "sector": "Technology"},
    {"ticker": "GS", "name": "Goldman Sachs", "sector": "Banking"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Banking"},
    {"ticker": "BA", "name": "Boeing Co.", "sector": "Industrial"},
    {"ticker": "CAT", "name": "Caterpillar", "sector": "Industrial"},
    {"ticker": "GE", "name": "GE Aerospace", "sector": "Industrial"},
    {"ticker": "RTX", "name": "RTX Corp.", "sector": "Defense"},
    {"ticker": "UBER", "name": "Uber Technologies", "sector": "Technology"},
    {"ticker": "SQ", "name": "Block Inc.", "sector": "Fintech"},
    {"ticker": "PYPL", "name": "PayPal Holdings", "sector": "Fintech"},
    {"ticker": "COIN", "name": "Coinbase Global", "sector": "Fintech"},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "sector": "ETF"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "sector": "ETF"},
]

# ---------------------------------------------------------------------------
# EGX Stocks - derived from tradingagents.dataflows.egypt_tickers
# ---------------------------------------------------------------------------

EGX_STOCKS: list[dict] = [
    {
        "ticker": ticker,
        "name": info["name_en"],
        "name_ar": info["name_ar"],
        "sector": info["sector"],
    }
    for ticker, info in EGX_TICKERS.items()
]

# ---------------------------------------------------------------------------
# Market indices
# ---------------------------------------------------------------------------

US_INDICES: list[dict] = [
    {"name": "S&P 500", "symbol": "^GSPC"},
    {"name": "NASDAQ", "symbol": "^IXIC"},
    {"name": "Dow Jones", "symbol": "^DJI"},
]

EGX_INDICES: list[dict] = [
    {"name": "EGX 30", "symbol": "^CASE"},
]

# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

_WATCHLISTS: dict[str, list[dict]] = {
    "us": US_STOCKS,
    "egypt": EGX_STOCKS,
}

_INDICES: dict[str, list[dict]] = {
    "us": US_INDICES,
    "egypt": EGX_INDICES,
}


def get_watchlist(market_id: str) -> list[dict]:
    """Return the curated stock watchlist for a given market.

    Raises ``ValueError`` if the market_id is unknown.
    """
    if market_id not in _WATCHLISTS:
        raise ValueError(f"Unknown market: {market_id}. Available: {list(_WATCHLISTS)}")
    return _WATCHLISTS[market_id]


def get_indices(market_id: str) -> list[dict]:
    """Return the index definitions for a given market.

    Raises ``ValueError`` if the market_id is unknown.
    """
    if market_id not in _INDICES:
        raise ValueError(f"Unknown market: {market_id}. Available: {list(_INDICES)}")
    return _INDICES[market_id]
