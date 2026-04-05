"""Market data service -- batch-fetches prices via yfinance with in-memory caching."""

import datetime
import logging
import time
from typing import Any

import yfinance as yf

from app.data.watchlists import get_watchlist, get_indices
from tradingagents.default_config import MARKET_REGIONS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_yf_ticker(ticker: str, market_id: str) -> str:
    """Append the appropriate exchange suffix for yfinance."""
    if market_id == "egypt":
        return ticker + ".CA"
    return ticker


def _extract_closes(df, symbol: str, single_ticker: bool):
    """Extract the last two closing prices for *symbol* from a yfinance DataFrame.

    Returns ``(last_close, prev_close)`` or ``(None, None)`` on failure.
    """
    try:
        if single_ticker:
            ticker_data = df
        else:
            # Multi-ticker download uses MultiIndex columns: (field, ticker)
            if symbol not in df.columns.get_level_values(0):
                return None, None
            ticker_data = df[symbol]

        if ticker_data is None or ticker_data.empty:
            return None, None

        closes = ticker_data["Close"].dropna()
        if len(closes) < 2:
            return None, None

        return float(closes.iloc[-1]), float(closes.iloc[-2])
    except Exception:
        return None, None


def _market_status(market_id: str) -> str:
    """Simple open/closed heuristic based on day-of-week and hour."""
    region = MARKET_REGIONS.get(market_id, {})
    weekend_days = region.get("weekend_days", [5, 6])
    now = datetime.datetime.now()
    if now.weekday() in weekend_days:
        return "closed"
    # Rough trading window -- good enough for a UI badge
    if 9 <= now.hour < 16:
        return "open"
    return "closed"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def get_market_overview(market_id: str) -> dict[str, Any]:
    """Return a full market overview dict (stocks, indices, movers, summary).

    Results are cached for ``CACHE_TTL`` seconds.
    """
    # --- cache check ---
    if market_id in _cache:
        ts, data = _cache[market_id]
        if time.time() - ts < CACHE_TTL:
            return data

    stocks = get_watchlist(market_id)
    indices_def = get_indices(market_id)

    # Build yfinance symbol lists
    yf_tickers = [_to_yf_ticker(s["ticker"], market_id) for s in stocks]
    index_symbols = [idx["symbol"] for idx in indices_def]
    all_symbols = yf_tickers + index_symbols

    # --- batch download ---
    single_ticker = len(all_symbols) == 1
    try:
        df = yf.download(
            all_symbols,
            period="5d",
            group_by="ticker",
            threads=True,
            progress=False,
        )
    except Exception:
        logger.exception("yfinance download failed for market=%s", market_id)
        df = None

    currency = "EGP" if market_id == "egypt" else "USD"

    # --- process stocks ---
    stock_snapshots: list[dict] = []
    if df is not None and not df.empty:
        for stock, yf_sym in zip(stocks, yf_tickers):
            last, prev = _extract_closes(df, yf_sym, single_ticker and len(index_symbols) == 0)
            if last is None or prev is None:
                continue
            change = last - prev
            change_pct = (change / prev) * 100 if prev else 0.0

            snapshot: dict[str, Any] = {
                "ticker": stock["ticker"],
                "name": stock["name"],
                "name_ar": stock.get("name_ar"),
                "sector": stock["sector"],
                "price": round(last, 2),
                "currency": currency,
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
            }
            stock_snapshots.append(snapshot)

    # --- process indices ---
    index_data: list[dict] = []
    if df is not None and not df.empty:
        for idx_def in indices_def:
            sym = idx_def["symbol"]
            last, prev = _extract_closes(df, sym, single_ticker and len(yf_tickers) == 0)
            if last is None or prev is None:
                continue
            change = last - prev
            change_pct = (change / prev) * 100 if prev else 0.0
            index_data.append({
                "name": idx_def["name"],
                "symbol": sym,
                "value": round(last, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
            })

    # --- summary & movers ---
    gainers = [s for s in stock_snapshots if s["change_pct"] > 0]
    losers = [s for s in stock_snapshots if s["change_pct"] < 0]
    unchanged = [s for s in stock_snapshots if s["change_pct"] == 0]
    total = len(stock_snapshots)

    sorted_by_pct = sorted(stock_snapshots, key=lambda s: s["change_pct"], reverse=True)
    top_gainers = sorted_by_pct[:7]
    top_losers = [s for s in reversed(sorted_by_pct[-7:]) if s["change_pct"] < 0] if len(sorted_by_pct) > 7 else []

    now = datetime.datetime.now()

    result: dict[str, Any] = {
        "market_id": market_id,
        "market_status": _market_status(market_id),
        "last_updated": now.isoformat(),
        "indices": index_data,
        "summary": {
            "total_stocks": total,
            "gainers_count": len(gainers),
            "losers_count": len(losers),
            "unchanged_count": len(unchanged),
            "breadth_pct": round(len(gainers) / total * 100, 1) if total else 0.0,
        },
        "stocks": stock_snapshots,
        "gainers": top_gainers,
        "losers": top_losers,
    }

    _cache[market_id] = (time.time(), result)
    return result
