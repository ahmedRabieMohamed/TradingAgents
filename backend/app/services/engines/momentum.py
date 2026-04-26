"""Momentum engine — rate of change + trend strength."""

import numpy as np


def compute(prices: np.ndarray) -> dict:
    """Calculate momentum score from price rate of change and trend strength.

    Args:
        prices: Array of historical closing prices (oldest first).

    Returns:
        Dict with score (0-100), verdict, roc_5d, roc_20d, trend_strength.
    """
    if len(prices) < 25:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<25 days)"}

    current = prices[-1]

    # Rate of change
    roc_5d = ((current / prices[-6]) - 1) * 100 if len(prices) >= 6 else 0
    roc_20d = ((current / prices[-21]) - 1) * 100 if len(prices) >= 21 else 0

    # Trend strength: count days price is above its 10-day SMA in last 20 days
    sma_10 = np.convolve(prices, np.ones(10) / 10, mode="valid")
    if len(sma_10) >= 20:
        recent_prices = prices[-20:]
        recent_sma = sma_10[-20:]
        trend_strength = int((recent_prices > recent_sma).sum() / 20 * 100)
    else:
        trend_strength = 50

    # Combined score
    # ROC contribution: positive ROC = higher score
    roc_score = 50 + (roc_5d * 3) + (roc_20d * 1)  # weight short-term more
    roc_score = max(0, min(100, roc_score))

    # Blend ROC and trend strength
    score = int(roc_score * 0.6 + trend_strength * 0.4)
    score = max(0, min(100, score))

    if score >= 65:
        verdict = "BULLISH"
    elif score <= 35:
        verdict = "BEARISH"
    else:
        verdict = "NEUTRAL"

    return {
        "score": score,
        "verdict": verdict,
        "roc_5d": round(roc_5d, 2),
        "roc_20d": round(roc_20d, 2),
        "trend_strength": trend_strength,
    }
