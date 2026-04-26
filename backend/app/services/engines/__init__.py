"""Trading Engines — orchestrator for all 7 quantitative engines."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import numpy as np

from . import (
    bollinger,
    correlation,
    mean_reversion,
    momentum,
    monte_carlo,
    support_resistance,
    volume,
)

logger = logging.getLogger(__name__)


def _fetch_price_data(ticker: str, market_id: str, days: int = 250) -> tuple[np.ndarray, np.ndarray]:
    """Fetch OHLCV data from yfinance. Returns (prices, volumes) arrays."""
    import yfinance as yf

    from tradingagents.default_config import MARKET_REGIONS

    suffix = MARKET_REGIONS.get(market_id, {}).get("ticker_suffix", "")
    symbol = f"{ticker.upper()}{suffix}"

    hist = yf.Ticker(symbol).history(period=f"{days}d")
    if hist.empty:
        return np.array([]), np.array([])

    prices = hist["Close"].dropna().values.astype(float)
    volumes = hist["Volume"].dropna().values.astype(float)

    # Align lengths
    min_len = min(len(prices), len(volumes))
    return prices[:min_len], volumes[:min_len]


def batch_fetch_price_data(
    tickers: list[str], market_id: str, days: int = 250
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Batch download price data for multiple tickers in ONE yfinance call.

    Returns dict of {ticker: (prices, volumes)}.
    """
    import yfinance as yf

    from tradingagents.default_config import MARKET_REGIONS

    suffix = MARKET_REGIONS.get(market_id, {}).get("ticker_suffix", "")
    symbols = [f"{t.upper()}{suffix}" for t in tickers]

    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    if not symbols:
        return result

    try:
        data = yf.download(
            " ".join(symbols),
            period=f"{days}d",
            progress=False,
            threads=True,
        )

        if data.empty:
            return result

        close = data["Close"] if "Close" in data.columns else None
        vol = data["Volume"] if "Volume" in data.columns else None

        if close is None:
            return result

        # Handle single ticker (no MultiIndex)
        if not hasattr(close, "columns"):
            ticker = tickers[0]
            prices = close.dropna().values.astype(float)
            volumes = vol.dropna().values.astype(float) if vol is not None else np.zeros_like(prices)
            min_len = min(len(prices), len(volumes))
            if min_len > 0:
                result[ticker] = (prices[:min_len], volumes[:min_len])
            return result

        # Multiple tickers
        for sym in close.columns:
            clean_ticker = str(sym).replace(suffix, "")
            prices = close[sym].dropna().values.astype(float)
            volumes_col = vol[sym].dropna().values.astype(float) if vol is not None and sym in vol.columns else np.zeros_like(prices)
            min_len = min(len(prices), len(volumes_col))
            if min_len > 10:
                result[clean_ticker] = (prices[:min_len], volumes_col[:min_len])

    except Exception as exc:
        logger.warning("Batch download failed: %s", exc)

    return result


def compute_all_engines_from_data(
    ticker: str,
    prices: np.ndarray,
    volumes: np.ndarray,
    market_id: str = "egypt",
    mc_days: int = 7,
    news_score: int | None = None,
    peer_changes: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Run all 7 engines using pre-fetched price data (no API calls).

    This is the fast path used by smart picks to avoid individual fetches.
    """
    if len(prices) < 10:
        return {
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "combined_score": 0,
            "combined_signal": "N/A",
            "error": f"Insufficient data for {ticker} ({len(prices)} days)",
            "engines": {},
        }

    engines: dict[str, dict] = {}

    try:
        engines["monte_carlo"] = monte_carlo.compute(prices, days=mc_days)
    except Exception as e:
        engines["monte_carlo"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["momentum"] = momentum.compute(prices)
    except Exception as e:
        engines["momentum"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["volume"] = volume.compute(prices, volumes)
    except Exception as e:
        engines["volume"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["support_resistance"] = support_resistance.compute(prices)
    except Exception as e:
        engines["support_resistance"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["mean_reversion"] = mean_reversion.compute(prices)
    except Exception as e:
        engines["mean_reversion"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["bollinger"] = bollinger.compute(prices)
    except Exception as e:
        engines["bollinger"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["correlation"] = correlation.compute(prices, ticker, peer_changes)
    except Exception as e:
        engines["correlation"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    combined = _compute_combined_score(engines, news_score)

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "combined_score": combined["score"],
        "combined_signal": combined["signal"],
        "engines": engines,
        "news_sentiment": {"score": news_score},
    }


def _fetch_peer_changes(peers: list[str], market_id: str) -> dict[str, float]:
    """Fetch 5-day price changes for sector peers."""
    import yfinance as yf

    from tradingagents.default_config import MARKET_REGIONS

    suffix = MARKET_REGIONS.get(market_id, {}).get("ticker_suffix", "")
    symbols = [f"{t.upper()}{suffix}" for t in peers[:5]]  # limit to 5 peers

    changes: dict[str, float] = {}
    try:
        data = yf.download(" ".join(symbols), period="6d", progress=False)
        if data.empty or "Close" not in data.columns:
            return changes
        close = data["Close"]
        if hasattr(close, "columns"):
            for sym in close.columns:
                col = close[sym].dropna()
                if len(col) >= 2:
                    change = ((col.iloc[-1] / col.iloc[0]) - 1) * 100
                    clean_ticker = str(sym).replace(suffix, "")
                    changes[clean_ticker] = float(change)
    except Exception:
        pass
    return changes


def compute_all_engines(
    ticker: str,
    market_id: str,
    mc_days: int = 7,
    news_score: int | None = None,
) -> dict[str, Any]:
    """Run all 7 engines on a single stock and return combined results.

    Args:
        ticker: Stock ticker (e.g., "ETEL").
        market_id: Market identifier (e.g., "egypt").
        mc_days: Monte Carlo simulation horizon.
        news_score: Optional news sentiment score (-100 to 100). If None, excluded from combined.

    Returns:
        Dict with combined_score, combined_signal, engines dict, news_sentiment.
    """
    prices, volumes = _fetch_price_data(ticker, market_id)

    if len(prices) < 10:
        return {
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "combined_score": 0,
            "combined_signal": "N/A",
            "error": f"Insufficient price data for {ticker} ({len(prices)} days)",
            "engines": {},
        }

    # Run all 7 engines
    engines: dict[str, dict] = {}

    try:
        engines["monte_carlo"] = monte_carlo.compute(prices, days=mc_days)
    except Exception as e:
        logger.warning("Monte Carlo failed for %s: %s", ticker, e)
        engines["monte_carlo"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["momentum"] = momentum.compute(prices)
    except Exception as e:
        logger.warning("Momentum failed for %s: %s", ticker, e)
        engines["momentum"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["volume"] = volume.compute(prices, volumes)
    except Exception as e:
        logger.warning("Volume failed for %s: %s", ticker, e)
        engines["volume"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["support_resistance"] = support_resistance.compute(prices)
    except Exception as e:
        logger.warning("Support/Resistance failed for %s: %s", ticker, e)
        engines["support_resistance"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["mean_reversion"] = mean_reversion.compute(prices)
    except Exception as e:
        logger.warning("Mean Reversion failed for %s: %s", ticker, e)
        engines["mean_reversion"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        engines["bollinger"] = bollinger.compute(prices)
    except Exception as e:
        logger.warning("Bollinger failed for %s: %s", ticker, e)
        engines["bollinger"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    try:
        # Correlation needs peer data
        sector_info = correlation._find_sector(ticker)
        peers = sector_info[1]
        peer_changes = _fetch_peer_changes(peers, market_id) if peers else {}
        engines["correlation"] = correlation.compute(prices, ticker, peer_changes if peer_changes else None)
    except Exception as e:
        logger.warning("Correlation failed for %s: %s", ticker, e)
        engines["correlation"] = {"score": 50, "verdict": "NEUTRAL", "error": str(e)}

    # Compute combined score
    combined = _compute_combined_score(engines, news_score)

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "combined_score": combined["score"],
        "combined_signal": combined["signal"],
        "engines": engines,
        "news_sentiment": {
            "score": news_score if news_score is not None else None,
        },
    }


def _compute_combined_score(engines: dict[str, dict], news_score: int | None) -> dict:
    """Compute weighted combined score from engine results.

    Weights: Monte Carlo 40%, News 30%, Technical Average 30%.
    When news is unavailable, MC gets 55% and Tech gets 45%.
    """
    mc_score = engines.get("monte_carlo", {}).get("score", 50)

    # Technical average from the 6 non-MC engines
    tech_engines = ["momentum", "volume", "support_resistance", "mean_reversion", "bollinger", "correlation"]
    tech_scores = []
    for name in tech_engines:
        eng = engines.get(name, {})
        if "error" not in eng or eng.get("score", 50) != 50:
            tech_scores.append(eng.get("score", 50))
    tech_avg = sum(tech_scores) / len(tech_scores) if tech_scores else 50

    if news_score is not None:
        # Normalize news_score from (-100,100) to (0,100)
        news_normalized = (news_score + 100) / 2
        combined = mc_score * 0.40 + news_normalized * 0.30 + tech_avg * 0.30
    else:
        # No news — redistribute weight
        combined = mc_score * 0.55 + tech_avg * 0.45

    score = max(0, min(100, int(combined)))

    if score >= 65:
        signal = "BUY"
    elif score >= 55:
        signal = "HOLD"
    elif score >= 45:
        signal = "NEUTRAL"
    else:
        signal = "SELL"

    if score >= 75:
        signal = "STRONG BUY"
    elif score <= 25:
        signal = "STRONG SELL"

    return {"score": score, "signal": signal}
