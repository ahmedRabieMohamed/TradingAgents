"""Volume Confirmation engine — confirms if price moves are real."""

import numpy as np


def compute(prices: np.ndarray, volumes: np.ndarray) -> dict:
    """Check if price movements are backed by volume.

    Args:
        prices: Array of historical closing prices (oldest first).
        volumes: Array of historical volumes (same length as prices).

    Returns:
        Dict with score (0-100), verdict, volume_ratio, is_real_move.
    """
    if len(prices) < 21 or len(volumes) < 21:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<21 days)"}

    # Volume ratio: today vs 20-day average
    avg_volume_20d = volumes[-21:-1].mean()
    today_volume = volumes[-1]

    if avg_volume_20d == 0:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Zero average volume"}

    volume_ratio = float(today_volume / avg_volume_20d)

    # Price direction today
    price_change = (prices[-1] / prices[-2]) - 1 if len(prices) >= 2 else 0
    price_up = price_change > 0

    # Real move = price and volume agree
    # Price up + volume up = real bullish
    # Price down + volume up = real bearish (selling pressure)
    # Price up + volume down = fake (no conviction)
    # Price down + volume down = fake (no panic)
    high_volume = volume_ratio > 1.5
    is_real_move = high_volume  # simplified: high volume = real move

    if price_up and high_volume:
        verdict = "BULLISH"
        score = min(100, int(50 + volume_ratio * 15))
    elif not price_up and high_volume:
        verdict = "BEARISH"
        score = max(0, int(50 - volume_ratio * 15))
    elif price_up and not high_volume:
        verdict = "NEUTRAL"
        score = 55  # slight positive but unconfirmed
    else:
        verdict = "NEUTRAL"
        score = 45

    return {
        "score": max(0, min(100, score)),
        "verdict": verdict,
        "volume_ratio": round(volume_ratio, 2),
        "is_real_move": is_real_move,
        "price_change_pct": round(price_change * 100, 2),
    }
