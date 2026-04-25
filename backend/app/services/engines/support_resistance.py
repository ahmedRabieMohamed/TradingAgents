"""Support/Resistance engine — find key price levels."""

import numpy as np


def compute(prices: np.ndarray) -> dict:
    """Identify support and resistance levels from price history.

    Args:
        prices: Array of historical closing prices (oldest first).

    Returns:
        Dict with score (0-100), verdict, support, resistance, risk_reward.
    """
    if len(prices) < 50:
        return {"score": 50, "verdict": "NEUTRAL", "error": "Insufficient data (<50 days)"}

    current = float(prices[-1])
    recent = prices[-50:]

    # Simple S/R: use rolling min/max over different windows
    # Support: recent lows that held multiple times
    # Resistance: recent highs that rejected multiple times

    # Find local minima and maxima using rolling windows
    window = 5
    supports = []
    resistances = []

    for i in range(window, len(recent) - window):
        # Local minimum
        if recent[i] == recent[i - window:i + window + 1].min():
            supports.append(float(recent[i]))
        # Local maximum
        if recent[i] == recent[i - window:i + window + 1].max():
            resistances.append(float(recent[i]))

    # Take the nearest support below current price
    support_levels = [s for s in supports if s < current]
    resistance_levels = [r for r in resistances if r > current]

    support = max(support_levels) if support_levels else float(recent.min())
    resistance = min(resistance_levels) if resistance_levels else float(recent.max())

    # Risk/reward ratio
    upside = resistance - current
    downside = current - support

    if downside > 0:
        risk_reward = round(upside / downside, 2)
    else:
        risk_reward = 0.0

    # Score: closer to support = more upside room = higher score
    total_range = resistance - support
    if total_range > 0:
        position_pct = (current - support) / total_range  # 0 = at support, 1 = at resistance
        score = int((1 - position_pct) * 100)  # near support = high score
    else:
        score = 50

    # Adjust for risk/reward
    if risk_reward > 2:
        score = min(100, score + 10)
    elif risk_reward < 0.5:
        score = max(0, score - 10)

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
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "current": round(current, 2),
        "risk_reward": risk_reward,
        "upside_pct": round((upside / current) * 100, 2) if current > 0 else 0,
        "downside_pct": round((downside / current) * 100, 2) if current > 0 else 0,
    }
