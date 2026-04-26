"""Mean Reversion engine — distance from moving average."""

import numpy as np


def compute(prices: np.ndarray) -> dict:
    """Detect mean reversion signals based on distance from 50-SMA.

    Args:
        prices: Array of historical closing prices (oldest first).

    Returns:
        Dict with score (0-100), verdict, distance_pct, is_oversold, is_overbought.
    """
    if len(prices) < 55:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<55 days)"}

    current = float(prices[-1])

    # 50-day Simple Moving Average
    sma_50 = float(prices[-50:].mean())

    # Distance from SMA as percentage
    distance_pct = ((current / sma_50) - 1) * 100

    # Thresholds for oversold/overbought
    is_oversold = distance_pct < -8  # more than 8% below SMA
    is_overbought = distance_pct > 8  # more than 8% above SMA

    # Score: oversold = high score (likely bounce), overbought = low score
    # Centered at 50 when at SMA
    if is_oversold:
        # The more oversold, the higher the score (reversion opportunity)
        score = min(100, int(80 + abs(distance_pct) * 1.5))
        verdict = "BULLISH"
    elif is_overbought:
        # The more overbought, the lower the score (likely pullback)
        score = max(0, int(20 - abs(distance_pct) * 1.5))
        verdict = "BEARISH"
    elif distance_pct < -3:
        score = 65
        verdict = "BULLISH"
    elif distance_pct > 3:
        score = 35
        verdict = "NEUTRAL"
    else:
        # Near the mean — neutral
        score = 50
        verdict = "NEUTRAL"

    return {
        "score": max(0, min(100, score)),
        "verdict": verdict,
        "distance_pct": round(distance_pct, 2),
        "sma_50": round(sma_50, 2),
        "current": round(current, 2),
        "is_oversold": is_oversold,
        "is_overbought": is_overbought,
    }
