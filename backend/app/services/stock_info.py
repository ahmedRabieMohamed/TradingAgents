"""Stock validation service using yfinance."""

from fastapi import HTTPException

from tradingagents.default_config import MARKET_REGIONS


async def validate_stock(ticker: str, market_id: str) -> dict:
    """Validate a stock ticker against a market using yfinance.

    For the Egypt market the ".CA" suffix is appended automatically.

    Returns a dict with keys:
        valid, ticker, name, price, currency, change_pct, market_id

    Raises HTTPException(404) when the ticker cannot be found.
    """
    import yfinance  # lazy import — heavy dependency

    region_cfg = MARKET_REGIONS.get(market_id)
    if region_cfg is None:
        raise HTTPException(status_code=400, detail=f"Unknown market: {market_id}")

    suffix = region_cfg.get("ticker_suffix", "")
    symbol = f"{ticker.upper()}{suffix}"

    try:
        yticker = yfinance.Ticker(symbol)
        info: dict = yticker.info or {}
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for ticker '{ticker}' in market '{market_id}'",
        )

    # yfinance returns a mostly-empty dict for invalid tickers.
    # A valid ticker will have at least a shortName or longName.
    name = info.get("shortName") or info.get("longName")
    if not name:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' not found in market '{market_id}'",
        )

    price = info.get("regularMarketPrice") or info.get("currentPrice")
    change_pct = info.get("regularMarketChangePercent")
    currency = info.get("currency", region_cfg["currency"])

    return {
        "valid": True,
        "ticker": ticker.upper(),
        "name": name,
        "price": price,
        "currency": currency,
        "change_pct": round(change_pct, 4) if change_pct is not None else None,
        "market_id": market_id,
    }
