"""Bollinger Bands engine — squeeze detection and breakout signals."""

import numpy as np


def compute(prices: np.ndarray) -> dict:
    """Detect Bollinger Band squeezes and breakouts.

    Args:
        prices: Array of historical closing prices (oldest first).

    Returns:
        Dict with score (0-100), verdict, band_width, position,
        upper_band, lower_band, middle_band.
    """
    if len(prices) < 25:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<25 days)"}

    current = float(prices[-1])
    period = 20

    # Calculate Bollinger Bands
    sma_20 = float(prices[-period:].mean())
    std_20 = float(prices[-period:].std())

    upper_band = sma_20 + 2 * std_20
    lower_band = sma_20 - 2 * std_20

    # Band width (normalized)
    band_width = (upper_band - lower_band) / sma_20 * 100 if sma_20 > 0 else 0

    # Historical band width for squeeze detection (compare to 6-month avg)
    if len(prices) >= 120:
        hist_widths = []
        for i in range(120, len(prices)):
            chunk = prices[i - period:i]
            w = (chunk.std() * 4) / chunk.mean() * 100 if chunk.mean() > 0 else 0
            hist_widths.append(w)
        avg_width = np.mean(hist_widths) if hist_widths else band_width
        is_squeeze = band_width < avg_width * 0.7
        is_expanding = band_width > avg_width * 1.2
    else:
        is_squeeze = band_width < 4  # rough threshold
        is_expanding = band_width > 8
        avg_width = band_width

    # Position within bands
    if upper_band != lower_band:
        position_pct = (current - lower_band) / (upper_band - lower_band)
    else:
        position_pct = 0.5

    # Determine position label
    if position_pct > 0.9:
        position = "above_upper"
    elif position_pct > 0.7:
        position = "upper"
    elif position_pct < 0.1:
        position = "below_lower"
    elif position_pct < 0.3:
        position = "lower"
    else:
        position = "middle"

    # Score
    if is_expanding and position in ("upper", "above_upper"):
        score = 80  # breakout upward
        verdict = "BULLISH"
        band_status = "expanding"
    elif is_expanding and position in ("lower", "below_lower"):
        score = 20  # breakout downward
        verdict = "BEARISH"
        band_status = "expanding"
    elif is_squeeze:
        score = 60  # squeeze = big move coming (slightly bullish bias)
        verdict = "NEUTRAL"
        band_status = "squeeze"
    elif position in ("lower", "below_lower"):
        score = 65  # near lower band = potential bounce
        verdict = "BULLISH"
        band_status = "normal"
    elif position in ("upper", "above_upper"):
        score = 35  # near upper band = potential pullback
        verdict = "NEUTRAL"
        band_status = "normal"
    else:
        score = 50
        verdict = "NEUTRAL"
        band_status = "normal"

    return {
        "score": max(0, min(100, score)),
        "verdict": verdict,
        "band_width": band_status,
        "position": position,
        "upper_band": round(upper_band, 2),
        "lower_band": round(lower_band, 2),
        "middle_band": round(sma_20, 2),
        "band_width_pct": round(band_width, 2),
    }
